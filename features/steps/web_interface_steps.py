# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa

"""
Web Steps - Playwright Version
"""
import logging
from behave import when, then, given
from playwright.sync_api import expect

# ============================================
# STEP DEFINITIONS
# ============================================

@when('I visit the "Home Page"')
def step_impl(context):
    """Navigate to the home page"""
    context.page.goto(context.base_url)
    context.page.wait_for_load_state("networkidle")


@then('I should see "{expected_text}" in the title')
def step_impl(context, expected_text):
    """Check page title contains text"""
    assert expected_text in context.page.title()


@then('I should not see "{unexpected_text}"')
def step_impl(context, unexpected_text):
    """Check text is not present on page"""
    assert unexpected_text not in context.page.locator('body').inner_text()


@when('I set the "{element_name}" to "{provided_text}"')
def step_impl(context, element_name, provided_text):
    """Fill a form field"""
    element_id = context.helper_get_element_id(element_name)
    context.page.fill(f"#{element_id}", provided_text)


@when('I select "{provided_text}" in the "{element_name}" dropdown')
def step_impl(context, provided_text, element_name):
    """Select dropdown option by visible text"""
    element_id = context.helper_get_element_id(element_name)
    context.page.select_option(f"#{element_id}", label=provided_text)


@when('I press the "{button_name}" button')
def step_impl(context, button_name):
    """Click a button"""
    button_id = context.helper_get_button_id(button_name)
    context.page.click(f"#{button_id}")

    # Wait for any network requests to complete
    context.page.wait_for_load_state("networkidle")


@then('I should see the message "{expected_text}"')
def step_impl(context, expected_text):
    """Verify flash message appears"""
    expect(context.page.locator("#flash_message")).to_contain_text(expected_text)


@then('I should see "{expected_text}" in the "{element_name}" dropdown')
def step_impl(context, expected_text, element_name):
    """Verify dropdown has specific value selected"""
    element_id = context.helper_get_element_id(element_name)
    selected = context.page.locator(f"#{element_id} option:checked").text_content()
    assert selected == expected_text, f"Expected '{expected_text}', got '{selected}'"


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    """Verify form field is empty"""
    element_id = context.helper_get_element_id(element_name)
    expect(context.page.locator(f"#{element_id}")).to_have_value("")


@when('I copy the "{element_name}" field')
def step_impl(context, element_name):

    """Copy field value to clipboard (simulated)"""

    element_id = context.helper_get_element_id(element_name)
    context.page.wait_for_selector(f"#{element_id}", state="visible")
    context.clipboard = context.page.input_value(f"#{element_id}")
    logging.info('Clipboard contains: %s', context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context, element_name):

    """Paste simulated clipboard value into field"""

    element_id = context.helper_get_element_id(element_name)
    context.page.fill(f"#{element_id}", context.clipboard)


@then('I should see "{expected_text}" in the "{element_name}" field')
def step_impl(context, expected_text, element_name):
    """Verify form field contains expected value"""
    element_id = context.helper_get_element_id(element_name)
    expect(context.page.locator(f"#{element_id}")).to_have_value(expected_text)


@given('I am logged in as an admin')
def step_impl(context):
    """Login as admin user"""
    # Check if already logged in
    is_logged_in = context.page.evaluate("""
        () => localStorage.getItem('authToken') !== null
    """)
    
    if is_logged_in:
        print("Already logged in, skipping...")
        return
    
    # Perform login
    context.page.goto(context.base_url)
    context.page.fill("#login_email", "admin@example.com")
    context.page.fill("#login_password", "admin_pass")
    context.page.click("#login-btn")
    
    # Wait for login to complete
    expect(context.page.locator("#flash_message")).to_have_text("Login successful!")
    
    # Wait for token to be stored
    import time
    for _ in range(10):
        token_set = context.page.evaluate("""
            () => localStorage.getItem('authToken') !== null
        """)
        if token_set:
            break
        time.sleep(0.5)
    
    print("Login complete")
