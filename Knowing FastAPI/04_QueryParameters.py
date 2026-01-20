'''
Query Parameters in FastAPI

Query parameters are optional values sent in the URL after ?.
They are mainly used for filtering, sorting, pagination, or optional configuration.
'''

from fastapi import FastAPI
from typing import Optional

app = FastAPI()

products = [
    {"id": 1, "name": "Pen", "category": "Stationery", "price": 30},
    {"id": 2, "name": "Notebook", "category": "Stationery", "price": 120},
    {"id": 3, "name": "T-shirt", "category": "Clothing", "price": 250},
    {"id": 4, "name": "Eraser", "category": "Stationery", "price": 10},
    {"id": 5, "name": "Mouse", "category": "Electronics", "price": 400},
]

@app.get("/products")
def get_items(category:Optional[str]=None, max_price:Optional[int]=None):
    filter_products = []
    
    # if category:
    #     filtered_products = [p for p in filtered_products if p["category"].lower() == category.lower()]
    # if max_price is not None:
    #     filtered_products = [p for p in filtered_products if p["price"] <= max_price]

    for product in products:
        # Apply category filter
        if category is not None:
            if product["category"].lower() != category.lower():
                continue

        # Apply max_price filter
        if max_price is not None:
            if product["price"] > max_price:
                continue

        filter_products.append(product)

    return filter_products