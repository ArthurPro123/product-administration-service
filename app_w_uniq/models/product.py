from extensions import db
from common.logging_config import helper_setup_logging
logger = helper_setup_logging()


# Define Product model
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, nullable=False, unique=True)
    description = db.Column(db.String(256))
    price = db.Column(db.Float, nullable=False)
    available = db.Column(db.Boolean(), nullable=False, default=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    def __repr__(self):
        return f"<Product {self.name} id=[{self.id}]>"


    def save(self):
        """
        Persists the current Product instance to the database.
        """
        logger.info("Saving %s", self.name)
        # id must be none to generate next primary key
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()


    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'available': self.available,
            'category_id': self.category_id
        }


    def update(self):
        """
        Updates a Product to the database
        """
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()


    def delete(self):
        """Removes a Product from the data store"""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()


    @classmethod
    def all(cls) -> list:
        """Returns all of the Products in the database"""
        logger.info("Processing all Products")
        return cls.query.all()


    @classmethod
    def find_by_id(cls, product_id: int):
        """Finds a Product by it's ID

        :param product_id: the id of the Product to find
        :type product_id: int

        :return: an instance with the product_id, or None if not found
        :rtype: Product

        """
        logger.info("Processing lookup for id %s ...", product_id)
        return cls.query.get(product_id)


    @classmethod
    def find_by_name(cls, name: str) -> list:
        """Returns all Products with the given name

        :param name: the name of the Products you want to match
        :type name: str

        :return: a collection of Products with that name
        :rtype: list

        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name).all()


    @classmethod
    def find_by_availability(cls, available: bool = True) -> list:
        """Returns all Products by their availability

        :param available: True for products that are available
        :type available: str

        :return: a collection of Products that are available
        :rtype: list

        """
        logger.info("Processing available query for %s ...", available)
        return cls.query.filter(cls.available == available).all()

    @classmethod
    def find_by_category_id(cls, category_id: int) -> list:
        """Returns all Products by their Category ID

        :param category_id: the id of the category
        :type category_id: int

        :return: a collection of Products
        :rtype: list

        """
        logger.info("Processing category_id for %s ...", category_id)
        return cls.query.filter(cls.category_id == category_id).all()



