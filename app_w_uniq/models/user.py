from sqlalchemy.orm import relationship
from extensions import db

from werkzeug.security import generate_password_hash, check_password_hash

from common.logging_config import helper_setup_logging
logger = helper_setup_logging()  # Set your desired log level

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)  # Direct foreign key

    role = relationship('Role', back_populates='users')  # One-to-many: Role → Users

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(255))

    users = relationship('User', back_populates='role')  # One-to-many: Role → Users
    permissions = relationship('Permission', secondary='role_permissions', back_populates='roles')

class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))

    roles = relationship('Role', secondary='role_permissions', back_populates='permissions')

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), primary_key=True)


# ---

def init_create_default_roles_and_permissions():

    # Check if roles already exist
    if not Role.query.filter_by(name='Admin').first():

        # Create permissions if they don't exist

        permissions = [
            'PRODUCT.CREATE', 'PRODUCT.UPDATE', 'PRODUCT.DELETE', 'PRODUCT.VIEW',
            'PRODUCT.*', 'CATEGORY.*', 'SUPPLIER.*', 'ARTICLE.*'
        ]
        for perm_name in permissions:
            if not Permission.query.filter_by(name=perm_name).first():
                perm = Permission(name=perm_name)
                db.session.add(perm)
        db.session.commit()


        # Create roles

        # Assign to Admin role
        admin_role = Role(name='Admin', description='Full access to the admin panel.')
        admin_role.permissions.extend(
            Permission.query.filter(Permission.name.in_(['PRODUCT.*', 'CATEGORY.*', 'SUPPLIER.*', 'ARTICLE.*'])).all()
        )

        sales_manager_role = Role(name='Sales Manager', description='Access for sales management.')
        sales_manager_role.permissions.extend(
            Permission.query.filter(Permission.name.in_(['PRODUCT.CREATE', 'PRODUCT.UPDATE', 'PRODUCT.VIEW'])).all()
        )

        customer_role = Role(name='Customer', description='Access for regular customers.')
        customer_role.permissions.extend(
            Permission.query.filter(Permission.name.in_(['PRODUCT.VIEW'])).all()
        )

        db.session.add_all([admin_role, sales_manager_role, customer_role])
        db.session.commit()

# ---

def helper_create_user(email, username, password, role_name="Customer"):
    user = User(email=email, username=username)
    user.set_password(password)
    role = Role.query.filter_by(name=role_name).first()
    if not role:
        raise ValueError(f"Role '{role_name}' does not exist.")
    user.role = role
    db.session.add(user)
    db.session.commit()
    return user

# ---

def helper_user_has_permission(user_id, permission_name):
    user = User.query.filter_by(id=user_id).first()
    if not user or not user.role:
        return False

    # Convert to uppercase for consistency
    permission_name = permission_name.upper()

    # Check for exact match or wildcard
    parts = permission_name.split('.')
    wildcard = f"{parts[0]}.*"
    return any(
        p.name.upper() == permission_name or p.name.upper() == wildcard
        for p in user.role.permissions
    )
