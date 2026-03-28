import os
from typing import Dict

from app.utils.other import _tuple_from_env

# configuration loaded from environment with sane defaults
DATA_DIRECTORY = os.getenv("DATA_DIRECTORY", "data/")
SLIDES_DIRECTORY = os.getenv("SLIDES_DIRECTORY", DATA_DIRECTORY + "slides/")
PRESENTATION_DIRECTORY = os.getenv(
    "PRESENTATION_DIRECTORY", DATA_DIRECTORY + "presentations/",
)
BASE_DB = os.getenv("DATABASE_STORAGE_PATH", "database/")
DB_PATH = os.path.join(BASE_DB, "database.db")
HUEY_DB_PATH = os.path.join(BASE_DB, "huey.db")


TIME_BEFORE_CLEANUP = int(
    os.getenv("TIME_BEFORE_CLEANUP", str(60 * 5)))  # 5 min
BROWSER_DIMENTIONS = _tuple_from_env("BROWSER_DIMENTIONS", (1920, 1080))
WAIT_BETWEEN_ACTIONS = int(
    os.getenv("WAIT_BETWEEN_ACTIONS", "300"))  # ms between actions
# ms to wait for animations after slide change
WAIT_FOR_ANIMATIONS = int(os.getenv("WAIT_FOR_ANIMATIONS", "1000"))
# how much to scale up the browser for better resolution (1 = no scaling, 2 = double size, etc.)
SCALE_FACTOR = int(os.getenv("SCALE_FACTOR", "2"))

# how long to wait for the slide element to become visible before giving up
SLIDE_VISIBLE_TIMEOUT = int(
    os.getenv("SLIDE_VISIBLE_TIMEOUT", "10000"))  # milliseconds
NAVIGATION_TIMEOUT = int(
    os.getenv("NAVIGATION_TIMEOUT", "30000"))  # milliseconds

# selectors are static, not expected to change often but you could also allow environment overrides if needed
SELECTORS: Dict[str, str] = {
    "slide": ".genially-view-slide",
    "elements_to_hide": "nav, a[title='Genially home page'], div[class*='SocialViewstyled']",
    "next_button": "button[aria-label='Next page']",
    "accept_cookies": "#onetrust-accept-btn-handler",
    "total_slides": ".genially-view-navigation-pagination-total-slides",
    "current_slide_input": "input[data-cy='slidePaginationInput']",
}

HIDE_NAVIGATION_STYLES = f" {SELECTORS["elements_to_hide"]} {{ display: none !important; }}"
SHOW_NAVIGATION_STYLES = f" {SELECTORS["elements_to_hide"]} {{ display: block !important; }}"

PREPARE_SLIDES_STYLES = f"""
.genially-view-slide-container {{
    width: inherit !important;
    align-items: center;
    bottom: 0;
    display: flex;
    justify-content: center;
    left: 0;
    position: absolute;
    right: 0;
    top: 0;
    transform: translateZ(0);
    z-index: 1;
    overflow: visible !important;
}}
@page {{
    size: A4 landscape;
    margin: 0;
}}

#root {{
    height: 100vh !important;
    width: 100vw !important;
    padding-top: 4vh !important;
    box-sizing: border-box !important;
    display: block !important;
    overflow: visible !important;
}}
{SELECTORS["elements_to_hide"]} {{ display: none !important; }}
"""

RESET_STYLES = f"""
#root {{
    padding-top: 0 !important;
}}
{SELECTORS["elements_to_hide"]} {{ display: block !important; }}
"""

DISABLE_ANIMATIONS = """
/* Instant CSS animations/transitions */
*, *::before, *::after {
    animation-duration: 0.001s !important;
    animation-delay: 0s !important;
    filter: initial !important;
    animation-fill-mode: forwards !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001s !important;
    transition-delay: 0s !important;
}

/* Force Genially animated wrappers to final state */
.genially-animated-wrapper {
    opacity: 1 !important;
    visibility: visible !important;
    transform: none !important;
    filter: initial !important;
}
"""


DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

ALLOWED_ORIGINS = [
    "http://localhost:8000" if DEV_MODE else "https://app.leon135.xyz",
]
