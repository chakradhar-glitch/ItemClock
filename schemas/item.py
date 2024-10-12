def item_serial(item):
    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "item_name": item["item_name"],
        "quantity": item["quantity"],
        "expiry_date": item["expiry_date"].strftime("%Y-%m-%d"),
        "insert_date": item["insert_date"].strftime("%Y-%m-%d %H:%M:%S")
    }


def list_item_serial(items):
    return [item_serial(item) for item in items]
