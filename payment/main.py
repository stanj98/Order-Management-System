from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
from time import time
import os
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['http://localhost:3000'],
    allow_methods=["*"],
    allow_headers=['*']
)

redis = get_redis_connection(
    host=os.getenv("PRODUCT_REDIS_URL", "localhost"),
    port=os.getenv("PRODUCT_REDIS_PORT"),
    password=os.getenv("PRODUCT_REDIS_PASSWORD", None),
    decode_responses=True
)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str
    
    class Meta:
        database=redis
        
@app.post('/orders')
async def create(request: Request):
    body = await request.json()
    
    req = requests.get(f"http://localhost:8000/product/{body['id']}")
    product = req.json()
    
    order = Order(
        product_id= body['id'],
        price= product['price'],
        fee= 0.2 * product['price'],
        total= 1.2 * product['price'],
        quantity= body['quantity'],
        status= 'pending'
    )
    
    order.save()
    
    order_completed(order)
    
    return order

def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    order.save()
    
