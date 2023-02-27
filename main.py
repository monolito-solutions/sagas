from fastapi import FastAPI
import uvicorn
from api.orders.endpoints import router as api_router
from api.errors.exceptions import BaseAPIException
from api.errors.handlers import api_exeption_handler

app = FastAPI()
app.include_router(api_router)
app.add_exception_handler(BaseAPIException, api_exeption_handler)


if __name__ == "__main__":
   uvicorn.run(app, host="localhost", port=6969)