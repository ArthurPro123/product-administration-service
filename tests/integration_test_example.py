import pytest
import requests
import logging

# --- Configuration ---
BASE_URL = "https://app:5000" + "/api/v1"  # When running in a container.

session = requests.Session()
session.verify = False  # Disable SSL verification for local testing

# --- User Credentials ---
USERS = {
    "admin": {"email": "admin@example.com", "password": "admin_pass"},
    "sales": {"email": "sales@example.com", "password": "sales_pass"},
    "customer": {"email": "customer@example.com", "password": "customer_pass"},
}


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# --- Helper Functions ---

def helper_login(user_role):
    """Log in as a user and return the auth token."""
    response = session.post(
        f"{BASE_URL}/auth/login",
        json=USERS[user_role]
    )
    return response.json()["access_token"]


def helper_create_category():
    """Create a test category (admin-only)."""
    token = helper_login("admin")
    headers = {"Authorization": f"Bearer {token}"}
    response = session.post(
        f"{BASE_URL}/categories",
        json={"name": "Integration Test Category"},
        headers=headers
    )
    return response.json()["id"]


def helper_add_product(user_role, product_data):
    """Add a product as a specific user role."""
    token = helper_login(user_role)
    headers = {"Authorization": f"Bearer {token}"}
    return session.post(f"{BASE_URL}/products", json=product_data, headers=headers)


def helper_cleanup():
    """Clean up test data (admin-only)."""
    token = helper_login("admin")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Delete all products
        for product in session.get(f"{BASE_URL}/products", headers=headers).json():
            session.delete(f"{BASE_URL}/products/{product['id']}", headers=headers)

        # Delete all categories
        for category in session.get(f"{BASE_URL}/categories", headers=headers).json():
            session.delete(f"{BASE_URL}/categories/{category['id']}", headers=headers)

    except Exception as e:
            print(f"Error during cleanup: {e}")
            raise  # Re-raise to fail the test if cleanup fails


# --- Fixtures (local to this file) ---

@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown():
    """Run once per module: Clean up before/after all tests."""
    helper_cleanup()
    yield
    # helper_cleanup()


@pytest.fixture(scope="function")
def test_product_data():
    """Provide default product data for tests."""
    return {
        "name": "Integration Test Product",
        "description": "Test description",
        "price": 9.99,
        "category_id": helper_create_category(),
        "available": True,
    }


# --- Tests ---

@pytest.mark.parametrize("user_role, expected_status", [
    ("admin", 201),
    ("sales", 201),
    ("customer", 403),
])
def test_add_product_integration(user_role, expected_status, test_product_data):

    """Test product creation for all roles (integration test)."""

    response = helper_add_product(user_role, test_product_data)

    assert response.status_code == expected_status

    if expected_status == 201:
        logger.info(f"Product created: {response.json()}")
        assert response.json()["name"] == test_product_data["name"]


@pytest.mark.parametrize("user_role, expected_status", [
    ("admin", 200),
    ("sales", 200),
    ("customer", 200),
])
def test_get_products_integration(user_role, expected_status, test_product_data):

    """Test product retrieval for all roles (integration test)."""

    # Add product first
    add_response = helper_add_product("admin", test_product_data)
    assert add_response.status_code == 201

    # Test retrieval
    token = helper_login(user_role)
    headers = {"Authorization": f"Bearer {token}"}

    response = session.get(f"{BASE_URL}/products", headers=headers)

    assert response.status_code == expected_status
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0  # Ensure the list is not empty


@pytest.mark.parametrize("user_role, expected_status", [
    ("admin", 200),
    ("sales", 200),
    ("customer", 403),
])
def test_update_product_integration(user_role, expected_status, test_product_data):
    """Test product updates for all roles (integration test)."""

    # Add a product as admin first
    product_response = helper_add_product("admin", test_product_data)
    product_id = product_response.json()["id"]

    # Update as the specified user
    token = helper_login(user_role)
    headers = {"Authorization": f"Bearer {token}"}

    updated_data = {
        "name": "Updated Product Name",
        "description": "Updated product description"
    }
    response = session.put(
        f"{BASE_URL}/products/{product_id}",
        json=updated_data,
        headers=headers
    )
    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json()["name"] == updated_data["name"]
        assert response.json()["description"] == updated_data["description"]


@pytest.mark.parametrize("user_role, expected_status", [
    ("admin", 204),
    ("sales", 403),
    ("customer", 403),
])
def test_delete_product_integration(user_role, expected_status, test_product_data):
    """Test product deletion for all roles (integration test)."""
    # Add a product as admin first
    product_response = helper_add_product("admin", test_product_data)
    product_id = product_response.json()["id"]

    # Delete as the specified user
    token = helper_login(user_role)
    headers = {"Authorization": f"Bearer {token}"}
    response = session.delete(f"{BASE_URL}/products/{product_id}", headers=headers)
    assert response.status_code == expected_status

