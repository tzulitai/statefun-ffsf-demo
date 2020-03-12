#!/usr/bin/python3

import sys

from confluent_kafka import Producer
from shopping_cart_pb2 import CartEvent
from shopping_cart_pb2 import AddToCart
from shopping_cart_pb2 import Checkout

def main(args):
    user_id = args[0]
    event_type = args[1]

    if event_type == "add":
        cart_event = add_to_cart(user_id, args[2], int(args[3]))
    elif event_type == "checkout":
        cart_event = checkout(user_id)

    p = Producer({'bootstrap.servers': 'localhost:9092'})
    p.produce(
        topic='user-cart-events',
        key=user_id.encode('utf-8'),
        value=cart_event.SerializeToString()
    )
    p.flush()

def add_to_cart(user_id, item_id, quantity):
    cart_event = CartEvent()
    cart_event.user_id = user_id
    cart_event.add_to_cart.item_id = item_id
    cart_event.add_to_cart.quantity = quantity
    return cart_event

def checkout(user_id):
    cart_event = CartEvent()
    cart_event.user_id = user_id
    cart_event.checkout.CopyFrom(Checkout())
    return cart_event

if __name__ == "__main__":
    main(sys.argv[1:])