################################################################################
#  Licensed to the Apache Software Foundation (ASF) under one
#  or more contributor license agreements.  See the NOTICE file
#  distributed with this work for additional information
#  regarding copyright ownership.  The ASF licenses this file
#  to you under the Apache License, Version 2.0 (the
#  "License"); you may not use this file except in compliance
#  with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

import base64

from google.protobuf.any_pb2 import Any

from statefun import StatefulFunctions
from statefun import RequestReplyHandler
from statefun import kafka_egress_builder

from shopping_cart_pb2 import UserCart
from shopping_cart_pb2 import Receipt
from shopping_cart_pb2 import CartEvent

from inventory_pb2 import ItemAvailability
from inventory_pb2 import RequestItem

functions = StatefulFunctions()

@functions.bind("org.ffsf.demo/shopping-cart")
def greet(context, message):
    if message.Is(CartEvent.DESCRIPTOR):
        handle_cart_event(context, message)
    elif message.Is(ItemAvailability.DESCRIPTOR):
        handle_item_availability(context, message)

handler = RequestReplyHandler(functions)

def lambda_handler(request, context):
    message_bytes = base64.b64decode(request["body"])
    response_bytes = handler(message_bytes)
    return build_response(response_bytes)

# Message handlers

def handle_cart_event(context, message):
    cart_event = CartEvent()
    message.Unpack(cart_event)
    event_type = cart_event.WhichOneof("event")
    if event_type == "add_to_cart":
        handle_add_to_cart(context, cart_event.add_to_cart)
    elif event_type == "checkout":
        handle_checkout(context)

def handle_add_to_cart(context, add_to_cart):
    item_request = RequestItem()
    item_request.quantity = add_to_cart.quantity
    context.pack_and_send(
        "org.ffsf.demo/inventory",
        add_to_cart.item_id,
        item_request
    )

def handle_checkout(context):
    receipt = Receipt()
    receipt.user_cart.CopyFrom(get_user_cart_state(context))
    clear_user_cart_state(context)
    context.pack_and_send_egress(
        "org.ffsf.demo/receipts",
        kafka_egress_builder(
            topic="receipts",
            key=context.address.identity,
            value=receipt
        )
    )

def handle_item_availability(context, message):
    item_availability = ItemAvailability()
    message.Unpack(item_availability)
    if item_availability.status == ItemAvailability.IN_STOCK:
        user_cart = get_user_cart_state(context)
        user_cart.items[context.caller.identity] = item_availability.quantity
        update_user_cart_state(context, user_cart)

def get_user_cart_state(context):
    state = context["user-cart"]
    user_cart = UserCart()
    if state is not None:
        state.Unpack(user_cart)
    return user_cart

def update_user_cart_state(context, new_user_cart):
    state = Any()
    state.Pack(new_user_cart)
    context["user-cart"] = state

def clear_user_cart_state(context):
    del context["user-cart"]

# Aux functions

def build_response(response_bytes):
    response_base64 = base64.b64encode(response_bytes).decode('ascii')
    response = {
        "isBase64Encoded": True,
        "statusCode": 200,
        "headers": { "Content-Type": "application/octet-stream"},
        "multiValueHeaders": {},
        "body": response_base64
    }
    return response
