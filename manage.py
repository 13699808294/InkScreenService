import asyncio
import time

import uvloop
from tornado.platform.asyncio import BaseAsyncIOLoop

from apps.ESLCloudClient import ESLCloudClient
from apps.httpService import HttpService
from apps.mosquittoClient import MosquittoClient
from setting.setting import MQTT_SERVICE_HOST

async def hello_world():
    await asyncio.sleep(1)
    print('{}:hello world'.format(time.time()))

if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())  # 修改循环策略为uvloop
    aioloop = asyncio.get_event_loop()  # 获取aioloop循环事件
    ioloop = BaseAsyncIOLoop(aioloop)  # 使用aioloop创建ioloop

    eslCloudClient = ESLCloudClient(ioloop)
    mosquittoClient = MosquittoClient(host=MQTT_SERVICE_HOST, ioloop=ioloop,aioloop=aioloop, eslCloudClient=eslCloudClient)

    HttpService(ioloop=ioloop,aioloop=aioloop,eslCloudClient=eslCloudClient,meeting_room_list = mosquittoClient.meeting_room_list)
    print('**********************启动ioloop××××××××××××××××××××')
    ioloop.start()