# Polyglot Shopping Cart Demo

## Building

- Make sure you've built the latest Stateful Functions base Docker image + Python SDK wheel file.

- Build the Inventory module (stored Java functions):
```
statefun-ffsf-demo $ cd inventory/
inventory $ mvn clean install -DskipTests
```

- Build the Shopping Cart module (remote Python function run with AWS Lambda + AWS API Gateway):
```
statefun-ffsf-demo $ cd shopping-cart/aws-lambda-function/
aws-lambda-function $ STATEFUN_PYTHON_SDK_WHL=/path/to/statefun-python-sdk.whl ./build_package.sh
```

- The above builds a zip package under `shopping-cart/aws-lambda-function/package` that can be uploaded to AWS Lambda.

- Finally:
```
statefun-ffsf-demo $ docker-compose build
```

## Running

- Start the application:
```
statefun-ffsf-demo $ docker-compose up
```

- Start consuming checkout receipts:
```
statefun-ffsf-demo $ python demo/consume_receipts.py
```

- Restock some inventory:
```
statefun-ffsf-demo $ python demo/restock_inventory.py <inventory_id> <restock_quantity>
# e.g.
statefun-ffsf-demo $ python demo/restock_inventory.py dope_pants 10
```

- Add some items to user cart:
```
statefun-ffsf-demo $ python demo/user_cart_events.py <user_id> add <inventory_id> <add_quantity>
# e.g.
statefun-ffsf-demo $ python demo/user_cart_events.py gordon add dope_pants 2
```

- Checkout user cart:
```
statefun-ffsf-demo $ python demo/user_cart_events.py <user_id> checkout
# e.g.
statefun-ffsf-demo $ python demo/user_cart_events.py gordon checkout
```

- On checkout, you'll see the corresponding receipt event:
```
user_id: "gordon"
user_cart {
  items {
    key: "dope_pants"
    value: 2
  }
}
```
