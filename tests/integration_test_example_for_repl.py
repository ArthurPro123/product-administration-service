import requests

session = requests.Session()
session.verify = False  # Disable SSL verification for local testing

# from requests.packages.urllib3.exceptions import InsecureRequestWarning
# requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# Set these variables after login
token = None
base_url = "https://localhost:5000/api/v1"

def helper_login(email, password):
    global token
    login_url = f"{base_url}/auth/login"
    credentials = {"email": email, "password": password}
    response = session.post(login_url, json=credentials)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("Login successful! Token set.")
    else:
        print("Login failed:", response.json())

def helper_create_category():
    """Create a test category (admin-only)."""
    headers = {"Authorization": f"Bearer {token}"}
    response = session.post(
        f"{base_url}/categories",
        json={"name": "Integration Test Category"},
        headers=headers
    )
    return response.json()["id"]

def helper_get_products():
    headers = {"Authorization": f"Bearer {token}"}
    response = session.get(f"{base_url}/products", headers=headers)
    return response.json()

def helper_create_product(product_data):
    headers = {"Authorization": f"Bearer {token}"}
    response = session.post(f"{base_url}/products", json=product_data, headers=headers)
    return response.json()

def helper_update_product(product_id, product_data):
    headers = {"Authorization": f"Bearer {token}"}
    response = session.put(f"{base_url}/products/{product_id}", json=product_data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Update failed with status code {response.status_code}: {response.text}")
        return {"status": "error", "message": response.text}

def helper_delete_product(product_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = session.delete(f"{base_url}/products/{product_id}", headers=headers)
    if response.status_code == 204:
        return {"status": "success", "message": "Product deleted successfully"}
    elif response.status_code == 200:
        return response.json()
    else:
        return {"status": "error", "message": response.text}


# Usage
# from integration_test_example_for_repl import *

# Step 1: Login and set the token
helper_login("admin@example.com", "admin_pass")

# Step 2: Use the helper functions
print(helper_get_products())

new_product = helper_create_product({
        "name": "Integration Test Product",
        "description": "Test description",
        "price": 9.99,
        "category_id": helper_create_category(),
        "available": True,
    }
)

print(new_product)
product_id = new_product["id"]  # Use the ID of the newly created product
print(helper_update_product(product_id, {"price": 899.99}))
print(helper_delete_product(product_id))
"""
"""
