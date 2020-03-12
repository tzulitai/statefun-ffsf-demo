#!/usr/bin/python3

import sys

from confluent_kafka import Producer
from inventory_pb2 import RestockItem

def main(args):
    inventory_id = args[0]
    restock_quantity = args[1]

    restock_event = RestockItem()
    restock_event.item_id = inventory_id
    restock_event.quantity = int(restock_quantity)

    p = Producer({'bootstrap.servers': 'localhost:9092'})
    p.produce(
        topic='inventory-restock-events',
        key=inventory_id.encode('utf-8'),
        value=restock_event.SerializeToString()
    )
    print(p.flush(timeout=2))

if __name__ == "__main__":
    main(sys.argv[1:])