from fastapi import FastAPI, Body
from starlette import status
from starlette.responses import JSONResponse

from app import schemas
from .crud import find_all_active_coin_pair, inactivate_coin_pair, create_coin_pair, \
    update_coin_pair
from fastapi_utils.tasks import repeat_every
from .update_prices import update_prices_task

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Home"}


@app.post("/coin_pair/", response_description="Add new Coin Pair")
async def add_coin_pair(coin_pair: schemas.CoinPairModel = Body(...)):
    inserted = await create_coin_pair(coin_pair)
    if not inserted:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "message": "Coin Pair already exists"
        })
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={
        "message": "Coin Pair created successfully"
    })


@app.patch("/coin_pair/", response_description="Update Coin Pair")
async def api_update_coin_pair(coin_pair: schemas.CoinPairModel = Body(...)):
    updated = await update_coin_pair(coin_pair)
    if not updated:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "message": "Coin Pair does not exist"
        })
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        "message": "Coin Pair updated successfully"
    })


@app.get("/coin_pair/", response_description="Get all Coin Pair")
async def get_all_coin_pair(skip: int = 0, limit: int = 100):
    return await find_all_active_coin_pair(skip=skip, limit=limit)


@app.delete("/coin_pair/{symbol}", response_description="Delete Coin Pair")
async def delete_coin_pair(symbol: str):
    await inactivate_coin_pair(symbol)
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        "message": "Coin Pair deleted successfully"
    })


@app.on_event("startup")
@repeat_every(seconds=300)
async def save_price_changes() -> None:
    await update_prices_task()
