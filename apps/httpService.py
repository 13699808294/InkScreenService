import asyncio

import uvloop
from tornado.ioloop import IOLoop
from tornado import web, httpserver, gen
from tornado.platform.asyncio import BaseAsyncIOLoop

from apps.ESLCloudClient import ESLCloudClient
from apps.views import UseSceneView, GoodsView, ControlView, BrushView, Callback, TokenChangeView

from setting.setting import MQTT_SERVICE_HOST,ESL_CLOUD_LOCAL_HOST




class HttpService():
    def __init__(self,ioloop=None,aioloop=None,eslCloudClient=None,meeting_room_list=[]):
        self.ioloop = ioloop
        self.aioloop = aioloop
        if self.aioloop == None:
            raise TypeError('aioloop type error')
        if self.ioloop == None:
            raise TypeError('ioloop type error')
        self.eslCloudClient = eslCloudClient
        self.meeting_room_list = meeting_room_list

        # 最后 :todo:启动服务
        httpApp = web.Application([
            (r'/inkScreen/useScene', UseSceneView, {'server': self}),
            (r'/inkScreen/goods', GoodsView, {'server': self}),
            (r'/inkScreen/control', ControlView, {'server': self}),
            (r'/inkScreen/brush', BrushView, {'server': self}),
            (r'/inkScreen/callback', Callback, {'server': self}),
            (r'/inkScreen/token_change',TokenChangeView,{'server': self})
        ])

        httpServer = httpserver.HTTPServer(httpApp)
        httpServer.listen(8009)



