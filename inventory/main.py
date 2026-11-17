from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['http://localhost:3000'],
    allow_methods=["*"],
    allow_headers=['*']
)

# Fetch and cast environment variables properly
redis = get_redis_connection(
    host=os.getenv("INVENTORY_REDIS_URL", "localhost"),
    port=os.getenv("INVENTORY_REDIS_PORT"),
    password=os.getenv("INVENTORY_REDIS_PASSWORD", None),
    decode_responses=True
)

class Product(HashModel):
    name: str
    price: float
    quantity_available: int
    
    class Meta:
        database = redis
    
@app.get('/products')
def all():
    return [format(pk) for pk in Product.all_pks()]

def format(pk: str):
    product = Product.get(pk)
    return {
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }

@app.post('/products')
def create(product: Product):
    return product.save()

@app.get('/products/{pk}')
def get(pk: str):
    return Product.get(pk)
    
@app.delete('/products/{pk}')
def delete(pk: str):
    return Product.delete(pk)