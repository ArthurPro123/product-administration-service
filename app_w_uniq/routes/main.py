from flask import Blueprint

### main_bp = Blueprint('main', __name__)

### @main_bp.route('/')
### def main():
###     return "Product Catalog Administration"


main_api_bp = Blueprint('main_api', __name__)

@main_api_bp.route('/')
def main():
    return "Product Catalog Administration"


main_web_bp = Blueprint('home_page', __name__)

@main_web_bp.route('/')
def index():
    """Web interface at root URL"""

    from flask import send_from_directory
    return send_from_directory('static', 'index.html')

