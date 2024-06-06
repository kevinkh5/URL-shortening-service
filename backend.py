from fastapi import FastAPI, Request, HTTPException
from generate_short_key import generate_random_string, URLService
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from datetime import datetime
from pymongo import MongoClient
import redis

# FastAPI
app = FastAPI()
host_url = "http://localhost:8000"

# MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["url_shorten_service"]
url_key_col = db["url_key"]
url_key_col.create_index('expiration_date', expireAfterSeconds=0)# 만기일에 자동삭제

# Redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

class Urlinfo(BaseModel):
    short_key: str = Field(default='')
    short_url: str = Field(default='')
    url: str
    access_count: int = Field(default=0)
    expiration_date: datetime
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

service = URLService()
@app.post("/shorten")
async def shorten_key(urlinfo: Urlinfo):
    # --------------------------------------------------
    # # 키 생성 알고리즘 1 - 랜덤으로 short key 생성
    # generated_key = generate_random_string()
    # # 동일한 key가 이미 있을 경우 키 한글자씩 늘리고 중복피해서 저장한다.
    # while url_key_col.find_one({"short_key": generated_key}):
    #     generated_key += generate_random_string(1)
    # --------------------------------------------------
    #
    # --------------------------------------------------
    # 키 생성 알고리즘 2 - 유니크하게 short key 생성
    generated_key = service.long_to_short(urlinfo.url)
    # --------------------------------------------------

    urlinfo.short_key = generated_key
    urlinfo.short_url = host_url+'/redirect/'+generated_key
    url_key_col.insert_one(urlinfo.dict())
    return urlinfo

def get_url(short_key):
    url = redis_client.get(short_key)
    try:
        if url is None:
            print('No data in Cache -> Get data from DB')
            data_from_short_key = url_key_col.find_one({"short_key": short_key})
            url = data_from_short_key['url']
            redis_client.setex(short_key, 600, url) # 600초(10분) 동안 캐시 저장
    except Exception as e:
        print(e)
        return None
    return url

def get_access_count(short_key):
    access_count = redis_client.get(f"{short_key}:count")
    try:
        if access_count is None:
            print('No data in Cache -> Get data from DB')
            data_from_short_key = url_key_col.find_one({"short_key": short_key})
            access_count = data_from_short_key['access_count']
    except Exception as e:
        print(e)
        return None
    redis_client.setex(f"{short_key}:count", 600, access_count)  # 600초(10분) 동안 캐시 저장
    return access_count

def increase_access_count(short_key):
    access_count = redis_client.get(f"{short_key}:count")
    try:
        if access_count is None:
            print('No data in Cache -> Get data from DB')
            data_from_short_key = url_key_col.find_one({"short_key": short_key})
            access_count = data_from_short_key['access_count']
    except Exception as e:
        print(e)
        return None
    redis_client.setex(f"{short_key}:count", 600, access_count)  # 600초(10분) 동안 캐시 저장
    redis_client.incr(f"{short_key}:count")
    return redis_client.get(f"{short_key}:count")

@app.get("/redirect/{short_key}")
async def redirect_page(short_key: str):
    url = get_url(short_key)
    print(url)
    if url == None:
        raise HTTPException(status_code=404, detail="Url not found")
    increase_access_count(short_key)
    print('접속')
    return RedirectResponse("https://"+f"{url}", status_code=301)

@app.get("/access_count/{short_key}")
async def check_access_count(short_key: str):
    access_count = get_access_count(short_key)
    # if access_count == None:
    #     raise HTTPException(status_code=404, detail="Url not found")
    return access_count