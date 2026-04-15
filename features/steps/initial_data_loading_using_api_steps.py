######################################################################
# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Steps file for products.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204


CATEGORY_MAP = {
    'CLOTHS': 1,
    'FOOD': 2,
    'HOUSEWARES': 3,
    'AUTOMOTIVE': 4,
    'TOOLS': 5,
    'UNKNOWN': 0
}

# Auth token storage (shared across steps) # {{{
_auth_token = None

def get_auth_token(context):
    """Get auth token, caching it after first login"""
    global _auth_token
    
    if _auth_token:
        return _auth_token
    
    login_url = f"{context.base_url}/api/v1/auth/login"
    response = requests.post(
        login_url,
        json={"email": "admin@example.com", "password": "admin_pass"},
        verify=False
    )
    
    if response.status_code == 200:
        _auth_token = response.json().get('access_token')
        return _auth_token
    return None

def auth_headers(context):
    """Get headers with auth token"""
    token = get_auth_token(context)
    return {"Authorization": f"Bearer {token}"} if token else {}

# }}}



@given('the following products')  # {{{
def step_impl(context):

    headers = auth_headers(context)

    """ Delete all Products and load new ones """

    #
    # List all of the products and delete them one by one
    #
    rest_endpoint = f"{context.base_url}/api/v1/products"
    response = requests.get(rest_endpoint)

    assert(response.status_code == HTTP_200_OK)


    for product in response.json():
        response = requests.delete(
            f"{rest_endpoint}/{product['id']}",
            headers=headers,
        )
        assert(response.status_code == HTTP_204_NO_CONTENT)


    #
    # load the database with new products
    #
    for row in context.table:

        category_id = CATEGORY_MAP.get(row['category'])

        payload = {
            "name": row['name'],
            "description": row['description'],
            "price": row['price'],
            "available": row['available'] in ['True', 'true', '1'],
            "category_id": category_id
        }
        response = requests.post(rest_endpoint, json=payload, headers=headers)

        print(f"POST Status: {response.status_code}")
        print(f"POST Response: {response.text}")
        print(f"POST Headers: {response.request.headers}")

        assert response.status_code == HTTP_201_CREATED

# }}}
