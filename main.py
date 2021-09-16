from enum import Enum
from typing import List, Optional

import aiohttp
from aiohttp import ClientError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from apartments import apartments_predict

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


class MaterialEnum(str, Enum):
    unset = "unset"
    brick = "brick"
    wood = "wood"
    monolith = "monolith"
    panel = "panel"
    block = "block"
    brick_monolith = "monolithBrick"
    stalin = "stalin"


class Coordinates(BaseModel):
    lon: float
    lat: float


class Address(BaseModel):
    label: str
    coords: Coordinates


class EstateModel(BaseModel):
    rooms: float
    floor: float
    material: MaterialEnum
    story: float
    area_total: float
    area_living: float
    address: Address
    year: float
    area_kitchen: float


class ResultModel(BaseModel):
    text: str
    uri: Optional[str]


class YModel(BaseModel):
    part: str
    results: List[ResultModel]


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/estate")
def read_item(params: EstateModel):
    prediction = apartments_predict(
        params.material, params.floor, params.story, params.area_total, params.area_kitchen, 50, 10)
    return {"prediction": prediction}


@app.get("/y-proxy", response_model=YModel)
async def get_suggestions(part: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('https://suggest-maps.yandex.com/suggest-geo', params={
                "fullpath": 1,
                "lang": "ru_RU",
                "outformat": "json",
                "v": 9,
                "part": "Москва, " + part
            }) as resp:
                return await resp.json()
        except ClientError:
            raise HTTPException
    pass
