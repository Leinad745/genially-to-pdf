from cloakbrowser import launch

from app.config import (
    BROWSER_DIMENTIONS,
    DISABLE_ANIMATIONS,
    HEADLESS,
    HIDE_NAVIGATION_STYLES,
    NAVIGATION_TIMEOUT,
    PREPARE_SLIDES_STYLES,
    RESET_STYLES,
    SCALE_FACTOR,
    SELECTORS,
    SLIDE_VISIBLE_TIMEOUT,
    SLIDES_DIRECTORY,
    WAIT_BETWEEN_ACTIONS,
    WAIT_FOR_ANIMATIONS,
)
from app.db.models import Task
from app.utils.directory import create_directory
from app.utils.task_status import TaskStatus

# JS helpers evaluated in the page context. Genially obfuscates its CSS class
# names, so navigation relies on stable data-cy attributes and the view API.
_JS_CURRENT_SLIDE_ID = """
() => {
    const transversal = %(transversal)r;
    const ids = Array.from(
        document.querySelectorAll(%(container)r)
    )
        .map((el) => el.getAttribute('data-cy'))
        .filter((dc) => dc && dc !== transversal);
    return ids.length ? ids[ids.length - 1] : null;
}
""" % {"container": SELECTORS["slide_container"], "transversal": SELECTORS["transversal_id"]}

_JS_HAS_NEXT = """
() => !!document.querySelector(%(next)r)
""" % {"next": SELECTORS["next_button"]}

# A full-page overlay intercepts real mouse clicks on the nav controls after the
# first transition, so the click handler is dispatched directly instead. This
# also works while the control is hidden by the print styles.
_JS_CLICK_NEXT = """
() => {
    const btn = document.querySelector(%(next)r);
    if (!btn) return false;
    btn.click();
    return true;
}
""" % {"next": SELECTORS["next_button"]}

_JS_TOTAL_SLIDES = """
async () => {
    try {
        const id = location.pathname.split('/').filter(Boolean).pop();
        const res = await fetch(`/api/view/${id}`, {
            headers: { accept: 'application/json' },
        });
        if (!res.ok) return null;
        const data = await res.json();
        const slides = data.Slides || data.slides || [];
        return Array.isArray(slides) && slides.length ? slides.length : null;
    } catch (e) {
        return null;
    }
}
"""


def _current_slide_id(page):
    try:
        return page.evaluate(_JS_CURRENT_SLIDE_ID)
    except Exception:
        return None


def _wait_for_slide_change(page, previous_id: str) -> bool:
    """Poll until the active slide id differs from previous_id."""
    for _ in range(int(SLIDE_VISIBLE_TIMEOUT / 200) or 1):
        page.wait_for_timeout(200)
        if _current_slide_id(page) != previous_id:
            return True
    return False


def capture_slides(task_id: str, url: str, slides_directory: str) -> None:
    task = None
    if task_id:
        try:
            task = Task.get_or_none(Task.task_id == task_id)
        except Exception:
            pass
    if task is None:
        return
    create_directory(slides_directory)
    # --no-sandbox is required when running as root inside a container; it is
    # harmless when running locally as a normal user.
    browser = launch(
        headless=HEADLESS, args=["--no-sandbox", "--disable-dev-shm-usage"]
    )
    context = browser.new_context(
        viewport={"width": BROWSER_DIMENTIONS[0], "height": BROWSER_DIMENTIONS[1]},
        reduced_motion="reduce",
        device_scale_factor=SCALE_FACTOR,
    )

    page = context.new_page()
    try:
        page.goto(url, timeout=NAVIGATION_TIMEOUT)
        page.wait_for_load_state("networkidle")
    except Exception as exc:
        if task:
            task.update_status(
                status=TaskStatus.ERROR,
                error_message=f"Navigation failed: {exc}",
            )
        browser.close()
        return

    try:
        cookies_button = page.locator(SELECTORS["accept_cookies"])
        cookies_button.wait_for(state="visible", timeout=3000)
        cookies_button.click()
        page.wait_for_timeout(500)
    except:
        pass

    slide = page.locator(SELECTORS["slide"]).first

    # total slide count comes from the view API; may be None if unavailable
    try:
        total_slides = page.evaluate(_JS_TOTAL_SLIDES)
    except Exception:
        total_slides = None

    captured = 0
    # hard cap so a navigation bug can never loop forever
    max_slides = (total_slides or 500) + 5

    while True:
        try:
            if task:
                task = Task.get_or_none(Task.task_id == task_id)
                if task is None:
                    browser.close()
                    return

            if page.is_closed():
                raise RuntimeError("Page closed unexpectedly")

            current_id = _current_slide_id(page)

            page.add_style_tag(content=DISABLE_ANIMATIONS)
            page.add_style_tag(content=HIDE_NAVIGATION_STYLES)
            page.wait_for_timeout(WAIT_BETWEEN_ACTIONS)
            page.add_style_tag(content=PREPARE_SLIDES_STYLES)
            page.wait_for_timeout(WAIT_FOR_ANIMATIONS)

            # Wait for DOM to stabilize
            try:
                page.wait_for_function(
                    """(sel) => {
                        const el = document.querySelector(sel);
                        if (!el) return false;
                        const html = el.innerHTML;
                        if (window._lastHtml === html) return true;
                        window._lastHtml = html;
                        return false;
                    }""",
                    arg=SELECTORS["slide"],
                    timeout=SLIDE_VISIBLE_TIMEOUT,
                )
            except Exception:
                pass

            captured += 1
            slide_path = f"{SLIDES_DIRECTORY}/{task_id}/{captured}.pdf"
            try:
                page.emulate_media(media="print")

                slide.wait_for(state="visible", timeout=SLIDE_VISIBLE_TIMEOUT)
                page.pdf(
                    path=slide_path,
                    format="A4",
                    print_background=True,
                    landscape=True,
                    scale=1,
                )
            except Exception:
                page.pdf(
                    path=slide_path,
                    format="A4",
                    print_background=True,
                    landscape=True,
                    scale=1,
                )
            finally:
                page.add_style_tag(content=RESET_STYLES)

            if task:
                if total_slides:
                    progress = 10 + int((captured / total_slides) * 65)
                else:
                    progress = min(74, 10 + captured * 2)
                task.update_status(
                    status=TaskStatus.CAPTURING_SLIDES,
                    progress=progress,
                    current_step=f"Slide {captured}/{total_slides or '?'}",
                )

            # last slide reached when the next control is gone
            if not page.evaluate(_JS_HAS_NEXT):
                break

            if captured >= max_slides:
                raise RuntimeError(
                    f"Captured {captured} slides without reaching the end"
                )

            # advance; a page overlay blocks real clicks, so dispatch via JS and
            # confirm the active slide actually changed (retry a couple of times)
            changed = False
            for _ in range(3):
                page.evaluate(_JS_CLICK_NEXT)
                page.wait_for_timeout(WAIT_BETWEEN_ACTIONS)
                if _wait_for_slide_change(page, current_id):
                    changed = True
                    break
            if not changed:
                raise RuntimeError(
                    f"Slide did not change after clicking next "
                    f"(stuck at slide {captured})"
                )
        except Exception as exc:
            if task:
                task.update_status(
                    status=TaskStatus.ERROR,
                    error_message=str(exc),
                )
            try:
                browser.close()
            except:
                pass
            return

    if total_slides and captured != total_slides:
        if task:
            task.update_status(
                status=TaskStatus.ERROR,
                error_message=f"Expected {total_slides} slides but captured {captured}",
            )
    browser.close()
