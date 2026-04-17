from flask import Blueprint

from .auth import auth_bp
from .products import products_bp
from .categories import categories_bp

### from .main import main_bp
from .main import main_web_bp, main_api_bp


# Register all blueprints
def register_blueprints(app):

    # Register web UI at root (without prefix)
    app.register_blueprint(main_web_bp)
    
    url_prefix = app.config['API_BASE_PREFIX'] 

    app.register_blueprint(main_api_bp, url_prefix=url_prefix)
    ### app.register_blueprint(main_bp, url_prefix=url_prefix)
    app.register_blueprint(auth_bp, url_prefix=url_prefix)
    app.register_blueprint(products_bp, url_prefix=url_prefix)
    app.register_blueprint(categories_bp, url_prefix=url_prefix)
