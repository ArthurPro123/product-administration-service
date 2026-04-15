import common.status_codes as status
from common.logging_config import helper_setup_logging

logger = helper_setup_logging()  # Set your desired log level


# Section 1 {{{

#  This section manages JWT authentication, user identity, token creation, and
#  permission-based access control for the application.


from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from models.user import User, helper_user_has_permission


# --- Helper: Create JWT Token ---
def helper_create_auth_token(email, password):  # Used in app.py
    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        return create_access_token(identity=user)  # Pass user instance directly
    return None


# Initialize JWT
jwt = JWTManager()

# --- JWT Callbacks ---
@jwt.user_identity_loader
def user_identity_lookup(user):
    return str(user.id)  # Return the user's ID as a string

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


## # --- Decorator ---
## def auth_required():  # Doesn't deal with roles.
##     """
##     Decorator to enforce authentication on routes.
##     Currently uses JWT, but can be extended for OAuth or other methods.
##     """
##     return jwt_required()


from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import abort

from extensions import cache



def permission_required(permission_name):
    """Decorator to restrict access to users with a specific permission."""

    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            if not current_user_id:
                abort(status.HTTP_401_UNAUTHORIZED, description="Unauthorized: No user identity found.")

            # Cache key for the permission check
            cache_key = f"permission:{current_user_id}:{permission_name}"
            logger.info(f"Cache key: {cache_key}")
            has_permission = cache.get(cache_key)

            if has_permission is None:
                user = User.query.filter_by(id=current_user_id).first()
                # Debug: Log the user's role and permissions
                logger.info(f"User {current_user_id} has role: {user.role.name}")
                logger.info(f"User permissions: {[p.name for p in user.role.permissions]}")

                has_permission = helper_user_has_permission(current_user_id, permission_name)
                cache.set(cache_key, has_permission, timeout=300)  # Cache for 5 minutes

            if not has_permission:
                abort(status.HTTP_403_FORBIDDEN, description=f"Forbidden: '{permission_name}' permission required.")

            return f(*args, **kwargs)
        return decorated_function
    return decorator
# }}}



# Section 2 - Routes

from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('auth/login', methods=['POST'])
def login():
    data = request.get_json()
    logger.info(f"Login attempt with data: {data}")
    email = data.get('email')
    password = data.get('password')
    token = helper_create_auth_token(email, password)
    if token:
        return jsonify(access_token=token), status.HTTP_200_OK
    return jsonify(error="Invalid credentials"), status.HTTP_401_UNAUTHORIZED
