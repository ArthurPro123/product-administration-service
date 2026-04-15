######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
######################################################################
"""
Product API Service Test Suite
"""
from tests.conftest import DATABASE_URI, BASE_API_URL, PRODUCTS_BASE_API_URL, logger
from app import db  # Used to add a category only.
from tests.factories import CategoryFactory, ProductFactory, UserFactory
import common.status_codes as status
from urllib.parse import quote_plus

import pytest

# pylint: disable=too-many-public-methods


NUM_OF_PRODUCTS_FOR_TEST = 5


#######################################################################
## Utility functions
#######################################################################

def _get_product_count_with_api(client):
    """get the current number of products"""
    response = client.get(PRODUCTS_BASE_API_URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.get_json()
    logger.info("The current number of products: %s", len(data))
    return len(data)


from decimal import Decimal, ROUND_HALF_UP
def _assert_prices_equal(fetched_price, test_price):

    """Assert that two prices are equal after rounding to two decimal places."""

    fetched = Decimal(str(fetched_price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    test = Decimal(str(test_price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    assert fetched == test, f"Price mismatch: {fetched} != {test}"


def _assert_product_equal(fetched_product, expected_product):
    assert fetched_product["name"] == expected_product.name
    assert fetched_product["description"] == expected_product.description
    _assert_prices_equal(fetched_product["price"], expected_product.price)
    assert fetched_product["available"] == expected_product.available
    assert fetched_product["category_id"] == expected_product.category_id


def _assert_no_duplicates_and_index(response_json):

    # Check for duplicate IDs in the response
    fetched_ids = [p["id"] for p in response_json]
    assert len(fetched_ids) == len(set(fetched_ids)), "Duplicate product IDs found in response"

    return {p["id"]: p for p in response_json}


# ----------------------------------------------------------
# Utility function to bulk create products
# ----------------------------------------------------------
def _create_products_for_testing(count: int = 1) -> list:
    """Factory method to create products in bulk"""

    category = CategoryFactory()
    db.session.add(category)
    db.session.commit()

    products = ProductFactory.create_batch(count, category_id=category.id)
    db.session.add_all(products)
    db.session.commit()

    return products


#############################################################
##  T E S T   C A S E S
#############################################################

def test_index(client):
    """It should return the index page"""

    api_base_prefix = client.application.config['API_BASE_PREFIX']
    response = client.get(f"{BASE_API_URL}/")

    assert response.status_code == status.HTTP_200_OK
    assert b"Product Catalog Administration" == response.data
           #
           # The b prefix ensures the comparison is done at the byte level,
           # which is correct for raw HTTP responses.


# ----------------------------------------------------------
# TEST CREATE
# ----------------------------------------------------------

def test_create_product_without_auth(client):
    """It should not Create a Product without authentication"""
    post_response = client.post(PRODUCTS_BASE_API_URL, json={'name': 'Test Product'})
    assert post_response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_product_with_insufficient_permissions(helper_make_request):
    test_product = _create_products_for_testing(1)[0]
    post_response = helper_make_request(
        'POST',
        PRODUCTS_BASE_API_URL,
        role_name='Customer',
        json=test_product.serialize(),
    )
    assert post_response.status_code == status.HTTP_403_FORBIDDEN


# [mark:good] A thoroughly devised test:


@pytest.mark.parametrize("role_name", ["Admin", "Sales Manager"])
def test_create_product(client, helper_make_request, role_name):

    category = CategoryFactory()
    db.session.add(category)
    db.session.commit()

    test_product = ProductFactory()
    test_product.category_id = category.id
    logger.info("Test Product: %s", test_product.serialize())


    post_response = helper_make_request(
        'POST',
        PRODUCTS_BASE_API_URL,
        role_name=role_name,
        json=test_product.serialize(),
    )
    logger.info("Response body: %s", post_response.json)  # Log the full response
    assert post_response.status_code == status.HTTP_201_CREATED

    # Make sure location header is set
    logger.info(f"post_response.headers: {post_response.headers}")

    location = post_response.headers.get("Location", None)
    logger.info(f"Location of the product created: {location}")
    assert location != None

    # Check the data is correct
    fetched_product = post_response.get_json()

    _assert_product_equal(fetched_product, test_product)

    # Check that the location header was correct
    get_response = client.get(location)
    assert get_response.status_code == status.HTTP_200_OK

    fetched_product_via_location = get_response.get_json()
    _assert_product_equal(fetched_product_via_location, test_product)


@pytest.mark.parametrize("role_name", ["Admin", "Sales Manager"])
def test_create_product_with_no_name(helper_make_request, role_name):
    """It should not Create a Product without a name"""
    product = _create_products_for_testing()[0]
    new_product = product.serialize()

    del new_product["name"]

    logger.info("Product with no name: %s", new_product)

    ### response = client.post(PRODUCTS_BASE_API_URL, json=new_product)

    response = helper_make_request(
        'POST', 
        PRODUCTS_BASE_API_URL, 
        role_name=role_name,
        json=new_product
    )

    logger.info("response: %s", response.status_code)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("role_name", ["Admin", "Sales Manager"])
def test_create_product_with_no_price(helper_make_request, role_name):
    product = _create_products_for_testing()[0]
    new_product = product.serialize()

    del new_product["price"]

    logger.info("Product with no price: %s", new_product)

    response = helper_make_request(
        'POST', 
        PRODUCTS_BASE_API_URL, 
        role_name=role_name,
        json=new_product
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("role_name", ["Admin", "Sales Manager"])
def test_create_product_with_no_category_id(helper_make_request, role_name):
    product = _create_products_for_testing(1)[0]
    new_product = product.serialize()

    del new_product["category_id"]

    response = helper_make_request(
        'POST', 
        PRODUCTS_BASE_API_URL, 
        role_name=role_name,
        json=new_product
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("role_name", ["Admin", "Sales Manager"])
def test_create_product_with_a_nonexistent_category_id(helper_make_request, role_name):
    product = _create_products_for_testing(1)[0]
    new_product = product.serialize()

    new_product["category_id"] = 999

    response = helper_make_request(
        'POST', 
        PRODUCTS_BASE_API_URL, 
        role_name=role_name,
        json=new_product
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize("role_name", ["Admin", "Sales Manager"])
def test_create_product_no_content_type(helper_make_request, role_name):
    """It should not Create a Product with no Content-Type"""
    response = helper_make_request(
        'POST', 
        PRODUCTS_BASE_API_URL, 
        role_name=role_name,
        data="bad data"
    )


    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


@pytest.mark.parametrize("role_name", ["Admin", "Sales Manager"])
def test_create_product_wrong_content_type(helper_make_request, role_name):
    """It should not Create a Product with wrong Content-Type"""
    response = helper_make_request(
        'POST', 
        PRODUCTS_BASE_API_URL, 
        role_name=role_name,
        data={},
        content_type="plain/text"
    )
    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


##
## ADD YOUR TEST CASES HERE
##

@pytest.mark.parametrize("role_name", ["Admin", "Sales Manager"])
def test_create_multiple_products(client, helper_make_request, role_name):
    products = _create_products_for_testing(NUM_OF_PRODUCTS_FOR_TEST)

    for test_product in products:
        post_response = helper_make_request(
            'POST',
            PRODUCTS_BASE_API_URL,
            role=role_name,
            json=test_product.serialize(),
        )

    logger.info("Test Products: %s", products)
    assert _get_product_count_with_api(client) == NUM_OF_PRODUCTS_FOR_TEST


def test_get_product(client):
    test_product = _create_products_for_testing(1)[0]

    response = client.get(f"{PRODUCTS_BASE_API_URL}/{test_product.id}")
    assert response.status_code == status.HTTP_200_OK

    # Check the data is correct
    fetched_product = response.get_json()
    _assert_product_equal(fetched_product, test_product)


def test_get_product_not_found(client):
    """It should not Get a Product thats not found"""
    response = client.get(f"{PRODUCTS_BASE_API_URL}/0")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.get_json() is None


def test_update_product(client):

    # test_product = _create_products_for_testing(1)[0]
    # --- Or: ------------------------------------
    category = CategoryFactory()
    db.session.add(category)
    db.session.commit()

    test_product = ProductFactory(category_id=category.id)
    db.session.add(test_product)
    db.session.commit()
    # --------------------------------------------


    test_product.name = "Updated Name"
    test_product.description = "Updated Description"
    test_product.price = "10.00"
    test_product.available = True

    client.put(f"{PRODUCTS_BASE_API_URL}/{test_product.id}", json=test_product.serialize())

    response = client.get(f"{PRODUCTS_BASE_API_URL}/{test_product.id}")
    assert response.status_code == status.HTTP_200_OK

    fetched_product = response.get_json()
    _assert_product_equal(fetched_product, test_product)


def test_delete_product(client):
    """It should Delete a Product"""

    # It also verifies that the total number of products in the database 
    # decreases by one after deletion.

    products = _create_products_for_testing(NUM_OF_PRODUCTS_FOR_TEST)
    product_count = _get_product_count_with_api(client)
    assert product_count == NUM_OF_PRODUCTS_FOR_TEST

    test_product = products[0]

    response = client.delete(f"{PRODUCTS_BASE_API_URL}/{test_product.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert len(response.data) == 0

    response = client.get(f"{PRODUCTS_BASE_API_URL}/{test_product.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.get_json() is None

    new_count = _get_product_count_with_api(client)
    assert new_count == product_count - 1


def test_get_product_list(client):
    products = _create_products_for_testing(NUM_OF_PRODUCTS_FOR_TEST)

    response = client.get(f"{PRODUCTS_BASE_API_URL}")
    assert response.status_code == status.HTTP_200_OK
    fetched_products = response.get_json()
    assert len(fetched_products) == NUM_OF_PRODUCTS_FOR_TEST

    indexed_fetched_products = _assert_no_duplicates_and_index(fetched_products)

    for test_product in products:
        assert test_product.id in indexed_fetched_products
        _assert_product_equal(indexed_fetched_products[test_product.id], test_product)


def test_query_by_name(client):
    """It should Query Products by name"""

    products = _create_products_for_testing(NUM_OF_PRODUCTS_FOR_TEST)

    first_product_name = products[0].name

    # Collect all products with the target name for comparison
    expected_products = [p for p in products if p.name == first_product_name]

    get_response = client.get(
        PRODUCTS_BASE_API_URL,
        query_string={"name": first_product_name}
    )
    assert get_response.status_code == status.HTTP_200_OK

    found_products = get_response.get_json()
    assert len(found_products) == len(expected_products)

    indexed_found_products = _assert_no_duplicates_and_index(found_products)

    for expected_product in expected_products:
        assert expected_product.id in indexed_found_products
        _assert_product_equal(indexed_found_products[expected_product.id], expected_product)


def test_query_by_category(client):

    """It should Query Products by category"""

    categories = CategoryFactory.create_batch(4)
    db.session.add_all(categories)
    db.session.commit()  # Commit to generate IDs
  
    category_ids = [cat.id for cat in categories]
  
    import random

    products = ProductFactory.create_batch(NUM_OF_PRODUCTS_FOR_TEST, category_id=random.choice(category_ids))
    db.session.add_all(products)
    db.session.commit()
    # --- Or: ------------------------------------
    # products = []
    # for _ in range(NUM_OF_PRODUCTS_FOR_TEST):
    #     test_product = ProductFactory(category_id=random.choice(category_ids))
    #     db.session.add(test_product)
    #     products.append(test_product)
    # db.session.commit()
    # --------------------------------------------

    some_category_id = random.choice(category_ids)
    category_id_count = sum(1 for product in products if product.category_id == some_category_id)
    logger.info(f"Number of products with category_id {some_category_id}: {category_id_count}")

    get_response = client.get(
      PRODUCTS_BASE_API_URL,
      query_string={"category_id": some_category_id}
    )
    assert get_response.status_code == status.HTTP_200_OK

    found_products = get_response.get_json()
    assert len(found_products) == category_id_count

    indexed_found_products = _assert_no_duplicates_and_index(found_products)

    for found_product in found_products:
        assert found_product["category_id"] == some_category_id 
        # Optionally validate other fields
        assert "name" in found_product
        assert "price" in found_product 


    # Collect all products with the target category_id for comparison
    expected_products = [p for p in products if p.category_id == some_category_id]

    for expected_product in expected_products:
        assert expected_product.id in indexed_found_products, \
            f"Product with id {expected_product.id} not found in response"

        _assert_product_equal(indexed_found_products[expected_product.id], expected_product)


def test_query_by_availability(client):
    """It should Query Products by availability"""

    products = _create_products_for_testing(NUM_OF_PRODUCTS_FOR_TEST)

    first_product_available = products[0].available

    # Collect all products with the target availability for comparison
    expected_products = [p for p in products if p.available == first_product_available]

    get_response = client.get(PRODUCTS_BASE_API_URL, query_string={"available": first_product_available})
    assert get_response.status_code == status.HTTP_200_OK

    found_products = get_response.get_json()
    assert len(found_products) == len(expected_products)

    indexed_found_products = _assert_no_duplicates_and_index(found_products)

    for expected_product in expected_products:
        assert expected_product.id in indexed_found_products, \
            f"Product with id {expected_product.id} not found in response"

        _assert_product_equal(indexed_found_products[expected_product.id], expected_product)
