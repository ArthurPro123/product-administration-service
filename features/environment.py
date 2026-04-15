
"""
Environment for Behave Testing with Playwright
"""
from os import getenv
from playwright.sync_api import sync_playwright, expect

# ============================================
# TO SWITCH BROWSERS
# ============================================

# For Chrome/Chromium:
# behave -D browser=chromium

# For Safari/WebKit:
# behave -D browser=webkit

# For Firefox (default):
# behave -D browser=firefox

# For Chrome (installed version):
# behave -D browser=chrome

# For Microsoft Edge:
# behave -D browser=msedge



# ============================================
# CONFIGURATION
# ============================================

WAIT_SECONDS = int(getenv('WAIT_SECONDS', '30'))
BASE_URL = getenv('BASE_URL', 'http://localhost:5000')
ID_PREFIX = 'product_'

# Firefox executable path (your specific version)
# FIREFOX_PATH = getenv('HOME') + "/PROGRAMS/firefox_for_dev/firefox-bin"
FIREFOX_PATH = ''

import os
if FIREFOX_PATH and not os.path.exists(FIREFOX_PATH):
    print(f"Warning: Firefox not found at {FIREFOX_PATH}, using Playwright's Firefox")
    FIREFOX_PATH = None



# ============================================
# HELPER FUNCTIONS
# ============================================

def helper_get_element_id(element_name):
    """'Product Name' → 'product_name'"""
    return ID_PREFIX + element_name.lower().replace(' ', '_')

def helper_get_button_id(button_name):
    """'Create' → 'create-btn'"""
    return button_name.lower().replace(' ', '_') + '-btn'

def helper_get_category_id(category_name):
    """'FOOD' → 2"""
    category_map = {
        'CLOTHS': 1, 'FOOD': 2, 'HOUSEWARES': 3,
        'AUTOMOTIVE': 4, 'TOOLS': 5, 'UNKNOWN': 6
    }
    return category_map.get(category_name.upper(), 6)


# ============================================
# BROWSER LAUNCHER
# ============================================

def launch_browser(playwright, browser_name, ui_mode):
    """Launch specified browser"""
    browsers = {
        'chromium': lambda: playwright.chromium.launch(headless=not ui_mode),
        'chrome': lambda: playwright.chromium.launch(
            headless=not ui_mode,
            channel='chrome'  # Uses installed Chrome
        ),
        'firefox': lambda: playwright.firefox.launch(
            headless=not ui_mode,
            executable_path=FIREFOX_PATH if FIREFOX_PATH and os.path.exists(FIREFOX_PATH) else None
        ),
        'webkit': lambda: playwright.webkit.launch(headless=not ui_mode),
        'msedge': lambda: playwright.chromium.launch(
            headless=not ui_mode,
            channel='msedge'  # Uses Microsoft Edge
        ),
    }
    
    if browser_name not in browsers:
        print(f"Warning: Unknown browser '{browser_name}', defaulting to firefox")
        browser_name = 'firefox'
    
    print(f"Launching: {browser_name}")
    return browsers[browser_name]()


# ============================================
# SETUP
# ============================================

def before_all(context):
    """Executed once before all tests"""
    
    context.base_url = BASE_URL
    context.wait_seconds = WAIT_SECONDS
    
    # Get UI mode from behave command line: behave -D ui=true
    ui_mode_raw = context.config.userdata.get('ui', 'false')
    ui_mode = ui_mode_raw.lower() == 'true'
    
    # Get browser from command line: behave -D browser=chromium
    browser_name = context.config.userdata.get('browser', 'firefox').lower()

    # Make helpers available
    context.helper_get_element_id = helper_get_element_id
    context.helper_get_button_id = helper_get_button_id
    context.helper_get_category_id = helper_get_category_id
    
    # Setup Playwright with selected browser
    context.playwright = sync_playwright().start()
    context.browser = launch_browser(context.playwright, browser_name, ui_mode)
    context.page = context.browser.new_page()
    context.page.set_default_timeout(WAIT_SECONDS * 1000)

    print(f"BASE_URL: {context.base_url}")
    print(f"Browser: {browser_name}")
    print(f"UI Mode: {ui_mode} (headed={ui_mode}, headless={not ui_mode})")
    print(f"WAIT_SECONDS: {context.wait_seconds}")

def after_all(context):
    """Executed after all tests"""

    if hasattr(context, 'browser') and context.browser:
        context.browser.close()
    if hasattr(context, 'playwright') and context.playwright:
        context.playwright.stop()


