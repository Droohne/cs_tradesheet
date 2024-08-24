### Where to get items id

Use this [link](https://github.com/ModestSerhat/cs2-marketplace-ids/tree/main) and download items_id from here

## Adding items or changing fixed_items

Modify ** json_manipulations.py ** to match your needs or any other way to change initial pack of IDs. Make sure structure of **fixed_items.json** is not changed

## Format of .json file

My code will result in a **1-liner** .json file auto-format it to make it human readable.

# Speed of programm

W/o time.sleep() it makes 1 iteration per 1 seconds on my end. With time.sleep() it takes close to 2 seconds time per iteration.
**Disabling time.sleep() or redusing time sleept will eventually result in getting "TO MANY REQUESTS"**