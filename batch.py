from apscheduler.schedulers.background import BackgroundScheduler
import redis
from pymongo import MongoClient
from datetime import datetime

# MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["url_shorten_service"]
url_key_col = db["url_key"]

# Redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def sync_access_counts():
    keys = redis_client.keys('*:count')
    for key in keys:
        short_key = key.split(':')[0]
        access_count = int(redis_client.get(key))
        print(f"{short_key}:{access_count}")
        url_key_col.update_one(
            {'short_key': short_key},
            {'$set': {'access_count': access_count,
                      'updated_at': datetime.now()}}
        )
    print(f"캐시에 저장된 short_key {len(keys)}개의 access_count를 동기화하였습니다.")
    print()

sync_access_counts()
scheduler = BackgroundScheduler()
scheduler.add_job(sync_access_counts, 'interval', minutes=5)  # 5분마다 실행
scheduler.start()

# 프로그램이 종료되지 않도록 유지
try:
    while True:
        pass
except (KeyboardInterrupt, SystemExit):
    # 스케줄러 종료
    scheduler.shutdown()