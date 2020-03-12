#!/usr/bin/python3

from confluent_kafka import Consumer

from shopping_cart_pb2 import Receipt

def main():
    conf = {'bootstrap.servers': 'localhost:9092',
            'group.id': 'demo',
            'auto.offset.reset': 'earliest'}

    c = Consumer(conf)
    c.subscribe(["receipts"])

    while True:
        try:
            for msg in c.consume(timeout=0.1):
                receipt = Receipt()
                receipt.ParseFromString(msg.value())
                print(receipt)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()