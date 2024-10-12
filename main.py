from fastapi import FastAPI
from routers.items import router as item_router
from routers.clock_in import router as clock_in_router
app = FastAPI()

app.include_router(item_router)
app.include_router(clock_in_router)

