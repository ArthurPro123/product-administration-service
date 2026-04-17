from flask import Flask 

from models.product import Product
from models.category import Category
from models.user import *

from routes import register_blueprints

from flask_sqlalchemy import SQLAlchemy

from common.logging_config import helper_setup_logging
logger = helper_setup_logging()  # Set your desired log level

from routes.auth import jwt

from flask_talisman import Talisman
from flask_cors import CORS

import os

# logger.info('JWT_SECRET_KEY: ' + os.environ.get('JWT_SECRET_KEY'))


# ****************************** #
# ************ Init ************ # {{{


def create_app(custom_config=None):

    """
    Application factory function to create and configure the Flask app.

    Args:
        custom_config (dict, optional): Configuration overrides for the app.

    Returns:
        Flask: Configured Flask application instance.
    """

    default_config = {

        'ENV': os.getenv('ENV', 'production'),

        'SQLALCHEMY_DATABASE_URI': 'sqlite:///app.db?foreign_keys=1',
            #                                                   |
            # ?foreign_keys=1 in the connection string enables foreign key constraints for SQLite.
                
        'TESTING': False,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': os.environ.get('JWT_SECRET_KEY'),
        'JWT_TOKEN_LOCATION': ['headers'],  # Use 'headers' for Authorization: Bearer <token>
        'JWT_HEADER_NAME': 'Authorization',
        'JWT_HEADER_TYPE': 'Bearer',
        'API_BASE_PREFIX': '/api/v1'
    }

    app = Flask(__name__)
    app.config.update(default_config)

    if custom_config:
        app.config.update(custom_config)  # Override with any custom config

    jwt.init_app(app)

    db.init_app(app)

    if app.config['ENV'] == 'development':

        # Create tables
        with app.app_context():
            db.drop_all()  # Drop all tables
            db.create_all()

            init_create_default_roles_and_permissions()
            init_create_default_users()

            init_create_default_categories()
            init_create_default_products()


    # Register the blueprint
    register_blueprints(app)

    from extensions import cache
    cache.init_app(app)


    csp = {  # {{{
        'default-src': '\'self\'',  # Fallback for all resource types not explicitly defined.
        'script-src': [
            '\'self\'',
            'https://cdn.jsdelivr.net',
            'https://code.jquery.com',
        ],
        'style-src': [
            '\'self\'',
            'https://cdn.jsdelivr.net'
        ],
        'font-src': [
            '\'self\'',
            'https://fonts.bunny.net'
        ],
        'img-src': [
            '\'self\'',
            'data:',   # Allows inline images (e.g., base64-encoded images) via 'data:'.
            'https://your-image-cdn.example.com'
        ],
        'connect-src': [  # Specifies trusted sources for fetch/XHR/AJAX requests.
            '\'self\'',
            'https://your-api.example.com',
            'https://another-trusted-service.example.com'
        ],
        'frame-src': '\'none\'',  # Block iframes unless needed
        'object-src': '\'none\'',  # Block plugins
        'base-uri': '\'self\'',   # Prevent base tag hijacking
        'form-action': '\'self\'', # Restrict form submissions to your domain
    }  # }}}

    if os.getenv('DISABLE_HTTPS', 'False').lower() != 'true':
        Talisman(
            app,
            force_https=True,
            content_security_policy=csp,
            strict_transport_security=True,  # Enables HSTS
            session_cookie_secure=True,      # Ensures cookies are only sent over HTTPS
        )


    # Enable Cross Origin Resource Sourcing (CORS) policies
    # Define allowed origins
    ALLOWED_ORIGINS = [
        "http://localhost:5000",
        "https://your-production-frontend.com",
        "https://your-staging-frontend.com"
    ]

    # Apply CORS to the /products/* route
    CORS( app, resources={r"/products/*": {"origins": ALLOWED_ORIGINS}})


    return app


def init_create_default_users():
    # Check if any users exist
    if not User.query.first():
        try:
            helper_create_user(email="admin@example.com", username="admin", password="admin_pass", role_name="Admin")
            logger.info("Created default user: admin")

            helper_create_user('sales@example.com', 'sales_manager_1', 'sales_pass', 'Sales Manager')
            logger.info("Created default user: sales_manager_1")

            helper_create_user('customer@example.com', 'customer_1', 'customer_pass', 'Customer')
            logger.info("Created default user: customer_1")

        except ValueError as e:
            logger.error(f"Failed to create default user: {e}")
            raise


def init_create_default_categories():

    """Create default categories"""

    categories = ['CLOTHS', 'FOOD', 'HOUSEWARES', 'AUTOMOTIVE', 'TOOLS', 'UNKNOWN']
    
    for category_name in categories:
        if not Category.query.filter_by(name=category_name).first():
            category = Category(name=category_name)
            db.session.add(category)
            logger.info(f"Created category: {category_name}")
    
    db.session.commit()


def init_create_default_products():

    category = Category.query.order_by(Category.id.asc()).first()
    category_id = category.id

    default_products = [
        {
            "name": "Product 1",
            "description": "Description of product 1",
            "price": 9.99,
            "category_id": category_id,
            "available": True,
        },
        {
            "name": "Product 2",
            "description": "Description of product 2",
            "price": 20.99,
            "category_id": category_id,
            "available": True,
        }
    ]
    for product_data in default_products:
        if not Product.query.filter_by(name=product_data["name"]).first():
            product = Product(**product_data)
            db.session.add(product)
    db.session.commit()


# ************ Init ************ # }}}
# ****************************** #



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
