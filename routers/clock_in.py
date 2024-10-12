from fastapi import FastAPI, HTTPException, status, APIRouter
from fastapi.responses import JSONResponse
from bson import ObjectId
from datetime import datetime
from typing import List

# custom imports
from models.clock_in import ClockIn as ClockInModel
from schemas.clock_in import individual_clock_in_serial, list_clock_in_serial
from database.database import clockin_collection

router = APIRouter()


# POST /clock-in: Create a new clock-in entry
@router.post("/clock-in")
def create_clock_in(clock_in: ClockInModel):
    try:
        clock_in_dict = clock_in.model_dump(exclude_none=True)
        result = clockin_collection.insert_one(clock_in_dict)
        return JSONResponse(content={"id": str(result.inserted_id)}, status_code=status.HTTP_201_CREATED)

    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# GET /clock-in/filter: Filter clock-in records
@router.get("/clock-in/filter")
def filter_clock_ins(email: str = None, location: str = None, insert_datetime: datetime = None):
    try:
        query = {}
        if email:
            query["email"] = email
        if location:
            query["location"] = location
        if insert_datetime:
            query["insert_datetime"] = {"$gt": insert_datetime}

        result = list(clockin_collection.find(query))
        if not result:
            return JSONResponse(content="no records found", status_code=status.HTTP_404_NOT_FOUND)
        return JSONResponse(content=list_clock_in_serial(result), status_code=status.HTTP_200_OK)
    #
    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# GET /clock-in/<id>: Retrieve a clock-in record by ID
@router.get("/clock-in/{clock_in_id}")
def get_clock_in(clock_in_id: str):
    try:
        if not ObjectId.is_valid(clock_in_id):
            raise HTTPException(status_code=400, detail="Invalid ID")
        clock_in = clockin_collection.find_one({"_id": ObjectId(clock_in_id)})
        if clock_in is None:
            raise HTTPException(status_code=404, detail="Clock-in record not found")
        return individual_clock_in_serial(clock_in)

    except HTTPException as he:
        return JSONResponse(content=str(he), status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


#
# DELETE /clock-in/<id>: Delete a clock-in record by ID
@router.delete("/clock-in/{clock_in_id}")
def delete_clock_in(clock_in_id: str):
    try:
        if not ObjectId.is_valid(clock_in_id):
            raise HTTPException(status_code=400, detail="Invalid ID")
        result = clockin_collection.delete_one({"_id": ObjectId(clock_in_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Clock-in record not found")
        return JSONResponse(content={"detail": "Clock-in record deleted"}, status_code=status.HTTP_200_OK)
    except HTTPException as he:
        return JSONResponse(content=str(he), status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# PUT /clock-in/<id>: Update a clock-in record by ID
@router.put("/clock-in/{clock_in_id}")
def update_clock_in(clock_in_id: str, clock_in: ClockInModel):
    try:
        if not ObjectId.is_valid(clock_in_id):
            raise HTTPException(status_code=400, detail="Invalid ID")
        updated_clock_in = clock_in.model_dump(exclude_none=True)
        result = clockin_collection.update_one({"_id": ObjectId(clock_in_id)}, {"$set": updated_clock_in})
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Clock-in record not found or no changes made")
        result = clockin_collection.find_one({"_id": ObjectId(clock_in_id)})

        return JSONResponse(content=individual_clock_in_serial(result), status_code=status.HTTP_200_OK)
    except HTTPException as he:
        return JSONResponse(content=str(he), status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JSONResponse(content=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
