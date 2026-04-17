from flask import Blueprint, request, jsonify, url_for, abort
from models.product import Product
from models.category import Category
from extensions import db
from sqlalchemy.exc import IntegrityError
from routes.auth import permission_required
import common.status_codes as status
from common.logging_config import helper_setup_logging

logger = helper_setup_logging()

products_bp = Blueprint('products', __name__)



@products_bp.route('/products', methods=['GET'])
def get_products():

    products = []

    name = request.args.get("name")
    category_id = request.args.get("category_id")
    available = request.args.get("available")

    if name:
        products = Product.find_by_name(name)

    elif category_id:
        try:
            category_id = int(category_id)
        except ValueError:
            return {"error": "category_id must be an integer"}, status.HTTP_400_BAD_REQUEST
        products = Product.find_by_category_id(category_id)

    elif available:
        available_value = available.lower() in ["true", "yes", "1"]
        products = Product.find_by_availability(available_value)

    else:
        products = Product.all()

    products = list(reversed(products))

    return jsonify([product.serialize() for product in products]), status.HTTP_200_OK


@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):

    logger.info("Request to Retrieve a product with id [%s]", product_id)

    product = Product.find_by_id(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found.")

    logger.info("Returning product: %s", product.name)
    return jsonify(product.serialize()), status.HTTP_200_OK


@products_bp.route('/products', methods=['POST'])
@permission_required('PRODUCT.CREATE')  # Check permission, not role
def create_product():
    data = request.get_json()
    logger.info("Processing: %s", data)

    if data.get('name') is None:
        logger.error("No product name specified.")
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Product name must be specified",
        )

    # Check for duplicate name
    existing_product = Product.query.filter_by(name=data['name']).first()
    if existing_product:
        return jsonify({"message": "Product with this name already exists"}), status.HTTP_409_CONFLICT


    if data.get('price') is None:
        logger.error("No product price specified.")
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Product price must be specified",
        )

    category_id = data.get('category_id')

    if not isinstance(category_id, int) or category_id < 1:
        logger.error("No valid category_id specified")
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"category_id must be an integer greater than 0"
        )
    
    if Category.query.get(category_id) is None:
        logger.error(f"Could not find category with id {category_id} when creating product")
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Category with id {category_id} not found"
        )
        

    if "Content-Type" not in request.headers:
        logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] != "application/json":
        logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )


    product = Product(
        name=data['name'],
        description=data.get('description', ''),
        available=data.get('available'),
        price=data['price'],
        category_id=data['category_id']
    )
    try:
        db.session.add(product)
        db.session.commit()

    except IntegrityError as error:
        db.session.rollback()
        error_msg = str(error.orig).lower()

        # Check if the error is due to a duplicate name
        if "unique constraint" in error_msg and "name" in error_msg:
            abort(status.HTTP_409_CONFLICT, "Product with this name already exists")

        elif "foreign key constraint" in error_msg:

            if "category_id" in error_msg:
                abort(status.HTTP_400_BAD_REQUEST, "Category does not exist")

            elif "supplier_id" in error_msg:
                abort(status.HTTP_400_BAD_REQUEST, "Supplier does not exist")

            elif "warehouse_id" in error_msg:
                abort(status.HTTP_400_BAD_REQUEST, "Warehouse does not exist")

            else:
                abort(
                    status.HTTP_400_BAD_REQUEST,
                    "Invalid foreign key: Related resource does not exist"
                )
        else:
            # Handle other unexpected integrity errors
            abort(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "An error occurred while creating the product"
            )
        

    # Create response:
    response = jsonify(product.serialize())
    response.status_code = status.HTTP_201_CREATED

    location_url = url_for("products.get_product", product_id=product.id, _external=True)
    response.headers['Location'] = location_url
    return response


@products_bp.route('/products/<int:product_id>', methods=['PUT'])
@permission_required('PRODUCT.UPDATE')
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json() or {}

    # Define valid fields and update only those provided in the request
    valid_fields = {'name', 'description', 'price', 'available', 'category_id'}
    for key, value in data.items():
        if key in valid_fields and value is not None:
            setattr(product, key, value)

    product.update()
    return jsonify(product.serialize())


@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
@permission_required('PRODUCT.DELETE')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return '', status.HTTP_204_NO_CONTENT

