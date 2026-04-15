from extensions import db
from common.logging_config import helper_setup_logging
logger = helper_setup_logging()

# Define Category model
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, nullable=False)

    def __repr__(self):
        return f'<Category {self.name}>'

