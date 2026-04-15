# Product Store Testing Framework

BDD test automation for product catalog management using Behave + Playwright.

## Features

- Cross-browser testing (Chromium, Firefox, WebKit...)
- JWT authentication handling
- UI + API testing combined
- Visible browser toggle with -D ui=true/false

## Quick Start

1. Run tests (headed, Firefox default):
   behave

2. Use specific browser:
   behave -D browser=chromium

3. No UI mode (for CI):
   behave -D ui=false

## Environment Variables

- BASE_URL (default: http://localhost:5000) - Application URL
- WAIT_SECONDS (default: 30) - Timeout in seconds

## Project Structure

- features/products.feature - Gherkin scenarios
- environment.py - Behave hooks and browser config
- steps/initial_data_loading_using_api_steps.py - API steps
- steps/web_interface_steps.py - UI step definitions

## Test Coverage

- Database seeding via REST API
- Server status verification
- Creating a product via UI
- Retrieving a product by ID
