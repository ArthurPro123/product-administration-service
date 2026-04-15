"""
Test cases for Product Model
"""
import pytest
from tests.conftest import logger
from app import db, Product, Category
from decimal import Decimal
from tests.factories import ProductFactory, CategoryFactory, CATEGORY_NAMES
from sqlalchemy.exc import IntegrityError
    # 
    # Needed to test when a product is created with an invalid category_id.

# pylint: disable=too-many-public-methods


def _add_category_with_fake_data(test_app):
    category = CategoryFactory()
    db.session.add(category)
    db.session.commit()
    return category


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################


# (ZOM) Zero
def test_create_a_product_without_db():
    """It should Create a product and assert its attributes (no database interaction)"""

    # Create a product with a hardcoded category_id
    product = Product(
        name="Fedora",
        description="A red hat",
        price='12.50',
        available=True,
        category_id=1
    )

    assert str(product) == "<Product Fedora id=[None]>"

    # Test basic attributes
    assert product.id is None
    assert product.name == "Fedora"
    assert product.description == "A red hat"
    assert product.available is True
    assert product.price == '12.50'
    assert product.category_id == 1  # Verify the hardcoded category_id


# (ZOM) One
def test_add_a_product_using_dict(test_app):

    category = Category(name="Test Category")
    db.session.add(category)
    db.session.commit()
    assert category.id == 1

    product_dict = {  # Added for flexibility, it is used in a few places.
        "name": "Test Product",
        "description": "Test Description",
        "price": 9.99,
        "category_id": category.id,
        "available": False,
    }

    product = Product(**product_dict)
    product.save()
    # --- Or: ------------------------------------
    ## db.session.add(product)
    ## db.session.commit()
    # --------------------------------------------

    products = Product.all()
    assert len(products) == 1
    fetched_product = Product.find_by_id(product.id)

    assert fetched_product.id == product.id  # Required, as product_dict doesn't include 'id'

    # Loop over the product dictionary and compare
    for key, value in product_dict.items():
        assert getattr(fetched_product, key) == value, f"Mismatch in {key}"

    # --- Or simply: -----------------------------
    assert fetched_product.id == product.id
    assert fetched_product.category_id == category.id
    assert fetched_product.name == product.name
    assert Decimal(fetched_product.price) == Decimal(product.price)
    assert fetched_product.description == product.description
    assert fetched_product.available is False
    # --------------------------------------------


# (ZOM) Many
def test_add_multiple_products_using_factory(test_app):
    """It should Create multiple products and add them to the database"""

    # Pre-populate the database with all possible categories
    for name in CATEGORY_NAMES:
        category = Category(name=name)
        db.session.add(category)
    db.session.commit()

    products = Product.all()
    assert products == []

    # Create multiple products
    num_of_products = 10

    created_products = []

    for _ in range(num_of_products):

        # Create a new product
        product = ProductFactory()
        logger.info("In 'test_add_a_product_using_factory()', 'product.category_id': %s", product.category_id) 
        product.save()
        created_products.append(product)  # Store each created product

    # Assert that all products were assigned an id and show up in the database
    fetched_products = Product.all()
    assert len(fetched_products) == num_of_products

    # Check that each fetched product matches the original
    for i, created_product in enumerate(created_products):
        fetched_product = fetched_products[i]

        # Auto-populate attrs_to_compare, excluding internal fields
        attrs_to_compare = [
            attr for attr in created_product.__dict__
            if not attr.startswith('_') and attr != 'id'
        ]
        logger.info("Attributes to compare (from __dict__): %s", attrs_to_compare)

        for attr in attrs_to_compare:
            assert getattr(fetched_product, attr) == getattr(created_product, attr)

        ## assert fetched_product.name == created_product.name
        ## assert fetched_product.description == created_product.description
        ## assert Decimal(fetched_product.price) == created_product.price
        ## assert fetched_product.available == created_product.available
        ## assert fetched_product.category_id == created_product.category_id


#
# ADD YOUR TEST CASES HERE
#
def test_create_product_with_invalid_category_id(test_app):
    """It should raise an error when a product is created with an invalid category_id"""

    # Attempt to create a product with a non-existent category_id
    invalid_product = Product(
        name="Invalid Product",
        description="This product has an invalid category",
        price=9.99,
        available=True,
        category_id=999  # Assume this ID does not exist
    )

    # Add and commit to trigger the error
    db.session.add(invalid_product)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_update_a_product(test_app):
    """It should Update a Product"""

    category = _add_category_with_fake_data(test_app)

    product = ProductFactory()
    product.category_id = category.id  # Replaces the randomly chosen number.
    logger.info("In test_update_a_product(). Created a product : %s", str(product)) 
    product.save()
    logger.info("In test_update_a_product(). Added the product : %s to the database", str(product)) 
    assert product.id is not None

    product.price = Decimal(50.00)
    product.name = 'Bag'
    product.description="A green travel bag"
    product.available = True
    product.update()

    fetched_product = Product.find_by_id(product.id)
    assert fetched_product.price == product.price
    assert fetched_product.name == product.name
    assert fetched_product.description == product.description
    assert fetched_product.available == product.available

    assert len(Product.all()) == 1


def test_remove_a_product(test_app):
    """It should Delete a Product"""

    category = _add_category_with_fake_data(test_app)

    product = ProductFactory()
    product.category_id = category.id  # Replaces the randomly chosen number.
    logger.info("In test_remove_a_product(). Created a product : %s", str(product)) 
    product.save()
    logger.info("In test_remove_a_product(). Added the product : %s to the database", str(product)) 
    assert product.id is not None

    assert len(Product.all()) == 1
    product.delete()
    assert len(Product.all()) == 0


def test_practice(test_app):

    category = _add_category_with_fake_data(test_app)

    assert len(Product.all()) == 0

    num_of_products = 5

    # 1. Using a loop:
    for _ in range(num_of_products):
        product = ProductFactory()
        product.category_id = category.id  # Ensures the category_id is assigned an existing value,
                                           # not a randomly chosen one.
        product.save()
        logger.info("Number of products in the database is %s", len(Product.all())) 

    assert len(Product.all()) == num_of_products


# A good one:
def test_find_a_product_by_name(test_app):
    """It should Find a Product by Name"""

    category = _add_category_with_fake_data(test_app)

    # 2. Using create_batch():
    created_products = ProductFactory.create_batch(100, category_id=category.id)
                                       #                  /
                                       # Ensures the category_id is assigned an existing value, 
                                       # not a randomly chosen one.

    # Save all products to the database
    for created_product in created_products:
        logger.info('created product name: ' + created_product.name)
        created_product.save()

    first_product_name = created_products[0].name
    logger.info(f"The name of the first product created: {first_product_name}")

    # Count how many products in 'created_products' have the same name as the first product:
    count = sum(1 for created_product in created_products if created_product.name == first_product_name)
    # ---
    # Or:
    ##count = 0
    ##for created_product in created_products:
    ##    if first_product_name == created_product.name:
    ##        count += 1

    logger.info(f"Products created with the same name '{first_product_name}': {count}")

    found_products = Product.find_by_name(first_product_name)
    logger.info("Found %s products with the name '%s' in the database", len(found_products), first_product_name)

    assert count == len(found_products)

    for found_product in found_products:
        assert found_product.name == first_product_name



def test_find_a_product_by_availability(test_app):
    """It should Find Products by Availability"""

    category = _add_category_with_fake_data(test_app)

    created_products = ProductFactory.create_batch(10, category_id=category.id)
    for created_product in created_products:
        created_product.save()

    first_product_availability = created_products[0].available
    count = sum(1 for created_product in created_products if created_product.available == first_product_availability)
    found_products = Product.find_by_availability(first_product_availability)
    assert len(found_products) == count
    for found_product in found_products:
        assert found_product.available == first_product_availability

def test_find_a_product_by_category(test_app):
    """It should Find Products by Category"""

    category = _add_category_with_fake_data(test_app)

    created_products = ProductFactory.create_batch(10, category_id=category.id)
    for created_product in created_products:
        created_product.save()

    first_product_category_id = created_products[0].category_id
    count = sum(1 for created_product in created_products if created_product.category_id == first_product_category_id)

    fetched_products = Product.find_by_category_id(category.id)
    assert len(fetched_products) == count

    for fetched_product in fetched_products:
        assert fetched_product.category_id == first_product_category_id
