from app.config import (
    SLIDES_DIRECTORY,
    SELECTORS,
    BROWSER_DIMENTIONS,
    WAIT_BETWEEN_ACTIONS,
    WAIT_FOR_ANIMATIONS,
    HIDE_NAVIGATION_STYLES,
    SLIDE_VISIBLE_TIMEOUT,
    NAVIGATION_TIMEOUT,
    PREPARE_SLIDES_STYLES,
    SCALE_FACTOR,
    RESET_STYLES,
    DISABLE_ANIMATIONS,
    HEADLESS,
)
from playwright.sync_api import sync_playwright

from app.db.models import Task
from app.utils.task_status import TaskStatus
from app.utils.directory import create_directory

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
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, args=["--disable-dev-shm-usage"])
        context = browser.new_context(viewport={"width": BROWSER_DIMENTIONS[0], "height": BROWSER_DIMENTIONS[1]}, reduced_motion="reduce", device_scale_factor=SCALE_FACTOR)

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
        next_slide_button = page.locator(
            SELECTORS["next_button"])

        total_slides = int(page.locator(
            SELECTORS["total_slides"]).inner_text())
        
        current_slide_input = page.locator(SELECTORS["current_slide_input"])

        while True:
            try:
                if task:
                    task = Task.get_or_none(Task.task_id == task_id)
                    if task is None:
                        browser.close()
                        return

                if page.is_closed():
                    raise RuntimeError("Page closed unexpectedly")
                
                current_slide = int(current_slide_input.input_value())
                
                page.add_style_tag(content=DISABLE_ANIMATIONS)
                page.add_style_tag(content=HIDE_NAVIGATION_STYLES)
                page.wait_for_timeout(WAIT_BETWEEN_ACTIONS)
                page.add_style_tag(content=PREPARE_SLIDES_STYLES)
                # page.wait_for_timeout(WAIT_FOR_ANIMATIONS)

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
                
                try:
                    page.emulate_media(media="print")

                    slide.wait_for(state="visible", timeout=SLIDE_VISIBLE_TIMEOUT)
                    page.pdf(path=f"{SLIDES_DIRECTORY}/{task_id}/{current_slide}.pdf", format='A4', print_background=True, landscape=True, scale=1 )
                except Exception:
                    page.pdf(path=f"{SLIDES_DIRECTORY}/{task_id}/{current_slide}.pdf", format='A4', print_background=True, landscape=True, scale=1 )
                finally:
                    page.add_style_tag(content=RESET_STYLES)

                if task:
                    progress = 10 + int((current_slide / total_slides) * 65)
                    task.update_status(status=TaskStatus.CAPTURING_SLIDES,
                                       progress=progress, current_step=f"Slide {current_slide}/{total_slides}")

                if not next_slide_button.is_visible() or next_slide_button.is_disabled():
                    break

                # Zapisz obecny slajd przed kliknięciem
                old_slide_number = current_slide
                next_slide_button.click()
                page.mouse.move(0, 0)
                
                # Sprawdź czy slajd się zmienił (max 3 próby)
                for retry in range(3):
                    page.wait_for_timeout(WAIT_BETWEEN_ACTIONS)
                    new_slide_number = int(current_slide_input.input_value())
                    
                    if new_slide_number > old_slide_number:
                        break  # Slajd się zmienił, kontynuuj
                    
                    if retry < 2:  # Nie retry na ostatniej próbie
                        next_slide_button.click()  # Spróbuj ponownie
                else:
                    # Po 3 próbach slajd się nie zmienił
                    raise RuntimeError(f"Slide did not change after clicking next (stuck at slide {old_slide_number})")
            except Exception as exc:
                # catch any of the above RuntimeErrors or other exceptions
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
        if current_slide != total_slides:
            if task:
                task.update_status(
                    status=TaskStatus.ERROR,
                    error_message=f"Expected {total_slides} slides but captured {current_slide}",
                )
        browser.close()
