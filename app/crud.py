from datetime import datetime

from .database import db
from .schemas import CoinPairModel

coin_pair_collection = db.get_collection("coin_pair")


async def update_price_for_coin_pair(mongo_id, last_price, target_up_percentage, target_down_percentage):
    query = {"_id": mongo_id}
    update = {"$set": {"last_price": last_price, "target_up_percentage": target_up_percentage,
                       "target_down_percentage": target_down_percentage}}
    await coin_pair_collection.find_one_and_update(query, update)


async def create_coin_pair(coin_pair: CoinPairModel):
    coin_pair = coin_pair.dict()
    coin_pair["active"] = True
    coin_pair["date_created"] = datetime.now()
    coin_pair["modified"] = datetime.now()
    coin_pair["last_price"] = None
    coin_pair["last_price_change_percentage"] = None
    coin_pair["target_up_percentage"] = None
    coin_pair["target_down_percentage"] = None
    test_active = await find_active_coin_pair(coin_pair["symbol"])
    if test_active:
        return False
    await coin_pair_collection.insert_one(coin_pair)
    return True


async def update_coin_pair(coin_pair: CoinPairModel):
    coin_pair = coin_pair.dict()
    coin_pair["active"] = True
    coin_pair["modified"] = datetime.now()
    test_active = await find_active_coin_pair(coin_pair["symbol"])
    if test_active:
        await coin_pair_collection.update_one({"symbol": coin_pair["symbol"], "active": True},
                                              {"$set": coin_pair})
        return True
    return False


async def find_active_coin_pair(symbol: str):
    return await coin_pair_collection.find_one({"active": True, "symbol": symbol})


async def find_all_active_coin_pair(skip: int = 0, limit: int = 100):
    return await coin_pair_collection.find({"active": True}, {'_id': 0}).skip(skip).limit(limit).to_list(length=limit)


async def inactivate_coin_pair(symbol: str):
    return await coin_pair_collection.update_many({"active": True, "symbol": symbol}, {"$set": {"active": False}})
