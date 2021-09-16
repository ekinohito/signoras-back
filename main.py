from enum import Enum

import aiohttp
from aiohttp import ClientError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from apartments import apartments_predict

app = FastAPI()


class MaterialEnum(str, Enum):
    unset = "unset"
    brick = "brick"
    wood = "wood"
    monolith = "monolith"
    panel = "panel"
    block = "block"
    brick_monolith = "monolithBrick"
    stalin = "stalin"


class EstateModel(BaseModel):
    rooms: float
    floor: float
    material: MaterialEnum
    story: float
    area_total: float
    area_living: float
    address: str
    year: float
    area_kitchen: float


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/estate")
def read_item(params: EstateModel):
    prediction = apartments_predict(
        params.material, params.floor, params.story, params.area_total, params.area_kitchen, 50, 10)
    return {"prediction": prediction}


@app.get("/y-proxy")
async def get_suggestions(part: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('https://suggest-maps.yandex.com/suggest-geo', params={
                "fullpath": 1,
                "lang": "en_RU",
                "outformat": "json",
                "v": 9,
                "part": part
            }) as resp:
                return {"response": await resp.json()}
        except ClientError:
            raise HTTPException
    pass
