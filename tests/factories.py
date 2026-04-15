# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.

# pylint: disable=too-few-public-methods

"""
Test Factory to make objects with fake data for testing
"""
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDecimal
from app import Product, Category
from models.user import User


# Category names (used to determine how many categories we have)
CATEGORY_NAMES = [
    "Unknown",
    "Cloths",
    "Food",
    "Housewares",
    "Automotive",
    "Tools",
]


class CategoryFactory(factory.Factory):
    class Meta:
        model = Category

    ## id = factory.Sequence(lambda n: n)
    name = FuzzyChoice(choices=CATEGORY_NAMES)


class ProductFactory(factory.Factory):
    """Creates fake products for testing"""

    class Meta:
        """Maps factory to data model"""

        model = Product

    ## id = factory.Sequence(lambda n: n)

    name = FuzzyChoice(
        choices=[
            "Hat",
            "Pants",
            "Shirt",
            "Apple",
            "Banana",
            "Pots",
            "Towels",
            "Ford",
            "Chevy",
            "Hammer",
            "Wrench"
        ]
    )

    description = factory.Faker("text")
    price = FuzzyDecimal(0.5, 2000, 2)
    available = FuzzyChoice(choices=[True, False])

    category_id = FuzzyChoice(choices=list(range(1, len(CATEGORY_NAMES) + 1)))  # 1, 2, 3...



class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Faker('email')
    username = factory.Sequence(lambda n: f'user{n}')

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = model_class(*args, **kwargs)
        user.set_password('test_pass')
        return user
