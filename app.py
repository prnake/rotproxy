import time
import random
import redis
import schedule
import requests

import asyncio
import aiohttp
import aiohttp_socks
import os
import re
import json
import multiprocessing
import traceback

PROXY_URL = os.environ.get("PROXY_URL", "")
PROXY_TIME = os.environ.get("PROXY_TIME", 30)
ROTARY_TIME = os.environ.get("ROTARY_TIME", 11)
EXTRA_REPORT_TIME = os.environ.get("EXTRA_REPORT_TIME", 20)
PROXY_TYPE = os.environ.get("PROXY_TYPE", "socks")

if not PROXY_URL:
    print("No PROXY_URL")
    exit()

async def validate(ip):
    #return {"proxy": ip}
    async with aiohttp.ClientSession(connector=aiohttp_socks.ProxyConnector.from_url(f'socks5://{ip}')) as session:
        try:
            #async with session.get(f'https://pubstatic.b0.upaiyun.com/?_upnode&t={int(time.time())}', timeout=3) as response:
            #    if response.status == 200:
            #        content = await response.text()
            #        data = json.loads(content)
            #        data["proxy"] = ip
            #        return data
            # in case of api broken
            async with session.get('https://myip.ipip.net/', timeout=3) as response:
                if response.status == 200:
                    content = await response.text()
                    #pattern = r'IPCallBack\((.*?)\)'  # 定义正则表达式模式
                    #match = re.search(pattern, content)  # 在字符串中搜索匹配的内容
                    #data = json.loads(match.group(1))
                    data = {}
                    data["info"] = content
                    data["proxy"] = ip
                    return data
        except Exception as e:
            traceback.print_exc()

async def filter_valid_ips(ip_list):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for ip in ip_list:
            tasks.append(validate(ip))
        valid_ips = await asyncio.gather(*tasks)
    return [ip for ip in valid_ips if ip]


def ip_to_gost():
    try:
        nodes = []
        keys = r.keys("ip:*")
        for key in keys:
            key = key.decode()
            ip = key.split(":", 1)[1]
            nodes.append({
                'addr': ip,
                'connector': {
                    'type': PROXY_TYPE,
                },
                'name': ip.split(":")[0],
            })
        requests.put('http://127.0.0.1:18080/api/config/hops/hop-0', headers={ 'Content-Type': 'application/json' }, json={'nodes': nodes})
    except:
        traceback.print_exc()

def ip_to_redis():
    try:
        nodes = []
        keys = r.keys("ip:*")
        for key in keys:
            key = key.decode()
            ip = key.split(":", 1)[1]
            nodes.append({
                'addr': ip,
                'connector': {
                    'type': PROXY_TYPE,
                },
                'name': ip.split(":")[0],
            })
        
        r.set("gost:hops:hop-0:nodes", json.dumps(nodes))
    except:
        traceback.print_exc()

def job():
    try:
        data = requests.get(PROXY_URL).text
        
        ip_list = data.splitlines()

        valid_ips = loop.run_until_complete(filter_valid_ips(ip_list))

        for ip in valid_ips:
            r.setex("ip:" + ip["proxy"], PROXY_TIME, 1)
        
        print(json.dumps(valid_ips, ensure_ascii=False))

        #ip_to_gost()
        ip_to_redis()

    except:
        traceback.print_exc()

if __name__ == '__main__':
    r = redis.Redis(host='localhost', port=6379, db=0)
    loop = asyncio.get_event_loop()

    pool = multiprocessing.Pool(processes=10)

    schedule.every(ROTARY_TIME).seconds.do(pool.apply_async, job)
    schedule.every(EXTRA_REPORT_TIME).seconds.do(pool.apply_async, ip_to_gost)
    
    ip_to_gost()
    while True:
        schedule.run_pending()
