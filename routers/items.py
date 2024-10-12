from fastapi import HTTPException, APIRouter, status
from fastapi.responses import JSONResponse
from bson import ObjectId
from datetime import datetime, date
from typing import List

# custom imports
from models.items import Item as ItemModel, ItemUpdate as ItemUpdateModel
from database.database import items_collection
from schemas.item import item_serial, list_item_serial

router = APIRouter()


# POST /items: Create a new item
@router.post("/items")
def create_item(item: ItemModel):
    try:
        item_dict = item.model_dump(exclude_none=True)
        item_dict['expiry_date'] = datetime.combine(item.expiry_date, datetime.min.time())
        result = items_collection.insert_one(item_dict)
        return JSONResponse(content={"id": str(result.inserted_id)}, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# MongoDB Aggregation: Count items for each email
@router.get("/items/count-by-email")
def count_items_by_email():
    try:
        pipeline = [
            {"$group": {"_id": "$email", "count": {"$sum": 1}}}
        ]
        result = list(items_collection.aggregate(pipeline))
        for item in result:
            item["_id"] = str(item["_id"])

        return JSONResponse(content=result, status_code=status.HTTP_200_OK)

    except HTTPException as he:
        return JSONResponse(content=str(he), status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/items/filter")
def filter_items(email: str = None, expiry_date: date = None, insert_date: datetime = None, quantity: int = None):
    try:
        query = {}
        if email:
            query["email"] = email
        if expiry_date:
            query["expiry_date"] = {"$gt": expiry_date}
        if insert_date:
            query["insert_date"] = {"$gt": insert_date}
        if quantity:
            query["quantity"] = {"$gte": quantity}

        items = list(items_collection.find(query))

        return JSONResponse(content=list_item_serial(items), status_code=status.HTTP_200_OK)

    except HTTPException as he:
        return JSONResponse(content=str(he), status_code=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# GET /items/<id>: Retrieve an item by ID
@router.get("/items/{item_id}")
def get_item(item_id: str):
    try:
        if not ObjectId.is_valid(item_id):
            raise HTTPException(status_code=400, detail="Invalid ID")
        item = items_collection.find_one({"_id": ObjectId(item_id)})
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return item_serial(item)
    except HTTPException as he:
        return JSONResponse(content=str(he), status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# DELETE /items/<id>: Delete an item by ID
@router.delete("/items/{item_id}")
async def delete_item(item_id: str):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    result = items_collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "Item deleted"}


# PUT /items/<id>: Update an item by ID
@router.put("/items/{item_id}")
async def update_item(item_id: str, item: ItemUpdateModel):
    if not ObjectId.is_valid(item_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    updated_item = item.model_dump(exclude_none=True)
    updated_item['expiry_date'] = datetime.combine(item.expiry_date, datetime.min.time())
    result = items_collection.update_one({"_id": ObjectId(item_id)}, {"$set": updated_item})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Item not found or no changes made")
    res = items_collection.find_one({"_id": ObjectId(item_id)})
    return item_serial(res)