# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa

"""
Web Steps - Playwright Version
"""
import logging
from behave import when, then, given
from playwright.sync_api import expect

from steps.common import *


# ============================================
# STEP DEFINITIONS
# ============================================

# --- Core Definitions --- #

@when('I visit the "Home Page"')
def step_impl(context):
    """Navigate to the home page"""
    context.page.goto(context.base_url)
    context.page.wait_for_load_state("networkidle")


@given('I am logged in as an admin')
def step_impl(context):
    """Login as admin user"""
    helper_perform_admin_login(context)


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
    element_id = helper_get_element_id(element_name)
    context.page.fill(f"#{element_id}", provided_text)

@when('I leave the "{element_name}" field empty')
def step_impl(context, element_name):
    """Ensure a field is empty"""
    element_id = helper_get_element_id(element_name)
    context.page.fill(f"#{element_id}", "")


@when('I select "{provided_text}" in the "{element_name}" dropdown')
def step_impl(context, provided_text, element_name):
    """Select dropdown option by visible text"""
    element_id = helper_get_element_id(element_name)
    context.page.select_option(f"#{element_id}", label=provided_text)


@when('I press the "{button_name}" button')
def step_impl(context, button_name):
    """Click a button"""
    button_id = helper_get_button_id(button_name)
    context.page.click(f"#{button_id}")

    # Wait for any network requests to complete
    context.page.wait_for_load_state("networkidle")


@then('I should see the message "{expected_text}"')
def step_impl(context, expected_text):
    """Verify flash message appears"""
    expect(context.page.locator("#flash_message")).to_contain_text(expected_text)

@then('I should not see the message "{unexpected_text}"')
def step_impl(context, unexpected_text):
    """Verify flash message does NOT contain text"""
    expect(context.page.locator("#flash_message")).not_to_contain_text(unexpected_text)


@then('I should see "{expected_text}" in the "{element_name}" dropdown')
def step_impl(context, expected_text, element_name):
    """Verify dropdown has specific value selected"""
    element_id = helper_get_element_id(element_name)
    selected = context.page.locator(f"#{element_id} option:checked").text_content()
    assert selected == expected_text, f"Expected '{expected_text}', got '{selected}'"


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    """Verify form field is empty"""
    element_id = helper_get_element_id(element_name)
    expect(context.page.locator(f"#{element_id}")).to_have_value("")


@when('I copy the "{element_name}" field')
def step_impl(context, element_name):

    """Copy field value to clipboard (simulated)"""

    element_id = helper_get_element_id(element_name)
    context.page.wait_for_selector(f"#{element_id}", state="visible")
    context.clipboard = context.page.input_value(f"#{element_id}")
    logging.info('Clipboard contains: %s', context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context, element_name):

    """Paste simulated clipboard value into field"""

    element_id = helper_get_element_id(element_name)
    context.page.fill(f"#{element_id}", context.clipboard)


@then('I should see "{expected_text}" in the "{element_name}" field')
def step_impl(context, expected_text, element_name):
    """Verify form field contains expected value"""
    element_id = helper_get_element_id(element_name)
    expect(context.page.locator(f"#{element_id}")).to_have_value(expected_text)


# --- Additional Definitions --- #

@given('a product named "{product_name}" already exists')
def step_impl(context, product_name):
    """Create a product using UI to set up test data"""
    
    # Create the product
    product_id = helper_ensure_product_exists(context, product_name)
    
    # Store for potential later use
    context.stored_product_id = product_id



# --- Additional Definitions for Removing a Product --- #


@when('I press the "Delete" button and cancel')
def step_impl(context):
    """Press Delete button and cancel the confirmation dialog"""

    def handle_dialog(dialog):
        dialog.dismiss()

    context.page.once('dialog', handle_dialog)

    context.page.click("#delete-btn")
    context.page.wait_for_load_state("networkidle")
    import time
    time.sleep(0.5)


@when('I press the "Delete" button and accept')
def step_impl(context):
    """Press Delete button and accept the confirmation dialog"""

    def handle_dialog(dialog):
        dialog.accept()

    context.page.once('dialog', handle_dialog)

    context.page.click("#delete-btn")
    context.page.wait_for_load_state("networkidle")
    import time
    time.sleep(0.5)


@then('the "{element_name}" field should contain the ID of the product named "{product_name}"')
def step_impl(context, element_name, product_name):

    """Verify the ID field contains the expected product ID"""

    element_id = helper_get_element_id(element_name)
    actual_id = context.page.input_value(f"#{element_id}")
    
    # Get the product ID from the stored product (from helper_ensure_product_exists)
    # You may need to store product IDs during creation
    assert actual_id == context.stored_product_id, \
        f"Expected ID '{context.stored_product_id}', got '{actual_id}'"


@then('the retrieved product should be "{product_name}"')
def step_impl(context, product_name):
    """Verify the retrieved product matches expected product"""
    name_field_id = helper_get_element_id("Name")
    actual_name = context.page.input_value(f"#{name_field_id}")
    
    assert actual_name == product_name, \
        f"Expected product '{product_name}', got '{actual_name}'"


@then('the product named "{product_name}" should still exist')
@then('the product "{product_name}" should still exist')
def step_impl(context, product_name):
    """Verify product still exists in the system"""
    # Search for the product
    context.page.fill("#product_name", product_name)
    context.page.click("#search-btn")
    context.page.wait_for_load_state("networkidle")
    
    flash_message = context.page.locator("#flash_message").text_content()
    assert "Found" in flash_message, \
        f"Product '{product_name}' should still exist but was not found"


@then('the product named "{product_name}" should no longer exist')
def step_impl(context, product_name):
    """Verify product has been deleted"""
    # Search for the product
    context.page.fill("#product_name", product_name)
    context.page.click("#search-btn")
    context.page.wait_for_load_state("networkidle")
    
    flash_message = context.page.locator("#flash_message").text_content()
    assert "No products found" in flash_message or "Found 0" in flash_message, \
        f"Product '{product_name}' should not exist but was found"
