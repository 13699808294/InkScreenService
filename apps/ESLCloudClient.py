import time
from tornado import gen

from setting.setting import CALLBACK_ADDRESS, ESL_CLOUD_LOCAL_HOST, TOKEN_CHANGE_ADDRESS, TOKEN_SERVICE_ADDRESS
from utils.asyncRequest import asyncTornadoRequest
from utils.logClient import logClient
from utils.my_json import json_dumps


class ESLCloudClient():
    def __init__(self,ioloop):
        self.ioloop = ioloop
        self.localHost = ESL_CLOUD_LOCAL_HOST
        self.loginUrl = self.localHost + '/V1/Login'
        self.token = None

        self.useSceneUrl = self.localHost + '/V2/sence/using'

        self.goodsUrl = self.localHost + '/V2/good'

        self.removeBindingUrl = self.localHost + '/V2/removed'

        self.bindingUrl = self.localHost + '/V2/binding'

        self.templateUrl = self.localHost + '/V2/template'

        self.templateBindUpdate = self.localHost + '/V2/pub/bind/update'

        self.goodBrushUrl = self.localHost + '/V2/good/brush'

        self.controlLedUrl = self.localHost + '/V2/label/led'

        self.queryGoodsUrl = self.localHost + '/V2/label/query'

        self.updateCallbackUrl = self.localHost + '/V2/pub/updatePushUrl'

        self.ioloop.add_timeout(self.ioloop.time(),self.login)

        self.storeCode = 'aa809'
        # self.storeCode = 'test729'



    #todo:登录
    @gen.coroutine
    def login(self):
        url = TOKEN_SERVICE_ADDRESS
        data = {
            'callback':TOKEN_CHANGE_ADDRESS,
            'method':'POST'
        }
        while True:
            result = yield asyncTornadoRequest(url,method='GET',params=data)
            if result.get('ret') == 0:
                self.token = result.get('token')
                if self.token != None:
                    yield logClient.tornadoInfoLog('登录成功,token:{}'.format(self.token))
                    break
            yield logClient.tornadoWarningLog('登录失败')
            yield gen.sleep(5)
        yield self.updateCallback()

    @gen.coroutine
    def tokenError(self):
        url = TOKEN_SERVICE_ADDRESS
        data = {
            'token_error':1
        }
        while True:
            result = yield asyncTornadoRequest(url, method='GET', params=data)
            if result.get('ret') == 0:
                token = result.get('token')
                if token != None:
                    self.token = token
                    break
            yield gen.sleep(5)

    @gen.coroutine
    def updateCallback(self):
        url = self.updateCallbackUrl
        body = {
            'pushUrl':CALLBACK_ADDRESS
        }
        self.headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.token
        }
        while True:
            result = yield asyncTornadoRequest(url, method='POST', headers=self.headers, params=body,allow_nonstandard_methods=True)
            if result.get('status') == '200' or result.get('status') == 200:
                yield logClient.tornadoInfoLog('设定回调地址成功')
                return
            else:
                yield logClient.tornadoErrorLog('设定回调地址失败')
                yield self.tokenError()
                yield gen.sleep(10)



