import asyncio
import functools
import sys
from concurrent.futures import ThreadPoolExecutor
from random import randint

import ansa
import uvicorn
from ansa import base, constants
from fastapi import FastAPI

from env import ANSA_ENV, API_PORT
sys.path.append(ANSA_ENV)
from schemas import LSDYNAType, NodeEntityModel


app = FastAPI()
deck = constants.LSDYNA


def get_entity_card_values(entity, fields=None, deck=None):
    deck = deck or constants.LSDYNA
    fields = fields or entity.card_fields(deck)
    return entity.get_entity_values(deck, fields=fields)


def _create_node(node: NodeEntityModel):
    ent = ansa.base.CreateEntity(deck, LSDYNAType.NODE, node.dict())
    return get_entity_card_values(ent)


def _get_nodes():
    return ansa.base.CollectEntities(deck, None, LSDYNAType.NODE)


def _get_all_ents():
    return ansa.base.CollectEntities(deck, None, LSDYNAType.ALL)


@app.get('/', status_code=200)
async def home():
    return {'Hello': f'current deck : {deck=}'}


@app.post('/create-node', status_code=201)
async def create_node(node: NodeEntityModel):
    return _create_node(node)


@app.post('/create-nodes', status_code=201)
async def create_nodes(n: int = 100):
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        tasks = [loop.run_in_executor(pool,
                                      functools.partial(_create_node,
                                                        NodeEntityModel(**{'X': randint(0, 10),
                                                                           'Y': randint(0, 10),
                                                                           'Z': randint(0, 10)})))
                 for _ in range(n)]
        results = await asyncio.gather(*tasks)
    return len(results)


@app.get('/cal-nodes-len', status_code=200)
async def cal_nodes_len():
    return len(_get_nodes())


@app.get('/show-ents', status_code=200)
async def show_ents():
    content = []
    ents = _get_all_ents()
    for ent in ents:
        try:
            content.append(get_entity_card_values(ent))
        except:
            print(f'Can not get the card values of {ent}')
    return content


@app.delete('/delete-ents', status_code=204)
async def delete_ents():
    ents = _get_all_ents()
    base.DeleteEntity(ents)

if __name__ == '__main__':
    uvicorn.run('api:app', port=API_PORT, workers=1)
