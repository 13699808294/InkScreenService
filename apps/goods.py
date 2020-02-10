import datetime
import time

from tornado import gen

from setting.setting import DEBUG
from utils.asyncRequest import asyncTornadoRequest
from utils.logClient import logClient
from utils.MysqlClient import mysqlClient

class Goods():
    def __init__(self,
                 barcode,
                 qrcode,
                 label1,
                 label2,
                 label3,
                 label4,
                 label5,
                 label6,
                 label7,
                 label8,
                 label9,
                 label10,
                 label11,
                 label12,
                 label13,
                 label14,
                 label15,
                 label16,
                 label17,
                 label18,
                 photo1,
                 photo2,
                 photo3,
                 photo4,
                 photo5,
                 ioloop,
                 aioloop,
                 eslCloudClient
                 ):
        self.barcode = barcode
        self.qrcode = qrcode
        self.label1 = label1
        self.label2 = label2
        self.label3 = label3
        self.label4 = label4
        self.label5 = label5
        self.label6 = label6
        self.label7 = label7
        self.label8 = label8
        self.label9 = label9
        self.label10 = label10
        self.label11 = label11
        self.label12 = label12
        self.label13 = label13
        self.label14 = label14
        self.label15 = label15
        self.label16 = label16
        self.label17 = label17
        self.label18 = label18
        self.photo1 = photo1
        self.photo2 = photo2
        self.photo3 = photo3
        self.photo4 = photo4
        self.photo5 = photo5

        self.ioloop = ioloop
        self.aioloop = aioloop
        self.eslCloudClient = eslCloudClient
        self.bindingDict = {}
        self.waitBrushTask = None
        self.lastBrushTime = time.time()
        self.lastBrushInfo = None
        self.ioloop.add_timeout(self.ioloop.time(),self.initGetSelfBrushInfo)

    @gen.coroutine
    def initGetSelfBrushInfo(self):
        self_info = yield self.getSelfInfo()
        yield self.keepNowBrushInfo(self_info)
    @gen.coroutine
    def getSelfInfo(self):
        info = {
            'barcode':self.barcode,
            'qrcode':self.qrcode,
            'label1':self.label1,
            'label2':self.label2,
            'label3':self.label3,
            'label4':self.label4,
            'label5':self.label5,
            'label6':self.label6,
            'label7':self.label7,
            'label8':self.label8,
            'label9':self.label9,
            'label10':self.label10,
            'label11':self.label11,
            'label12':self.label12,
            'label13':self.label13,
            'label14':self.label14,
            'label15':self.label15,
            'label16':self.label16,
            'label17':self.label17,
            'label18':self.label18,
            'photo1':self.photo1,
            'photo2':self.photo2,
            'photo3':self.photo3,
            'photo4':self.photo4,
            'photo5':self.photo5,
        }
        return info

    @gen.coroutine
    def updateSelfInfo(self,new_info:dict):
        self.barcode = new_info.get('barcode','')
        self.qrcode = new_info.get('qrcode','')
        self.label1 = new_info.get('label1','')
        self.label2 = new_info.get('label2','')
        self.label3 = new_info.get('label3','')
        self.label4 = new_info.get('label4','')
        self.label5 = new_info.get('label5','')
        self.label6 = new_info.get('label6','')
        self.label7 = new_info.get('label7','')
        self.label8 = new_info.get('label8','')
        self.label9 = new_info.get('label9','')
        self.label10 = new_info.get('label10','')
        self.label11 = new_info.get('label11','')
        self.label12 = new_info.get('label12','')
        self.label13 = new_info.get('label13','')
        self.label14 = new_info.get('label14','')
        self.label15 = new_info.get('label15','')
        self.label16 = new_info.get('label16','')
        self.label17 = new_info.get('label17','')
        self.label18 = new_info.get('label18','')
        self.photo1 = new_info.get('photo1','')
        self.photo2 = new_info.get('photo2','')
        self.photo3 = new_info.get('photo3','')
        self.photo4 = new_info.get('photo4','')
        self.photo5 = new_info.get('photo5','')

    @gen.coroutine
    def checkSelfLabelTemplate(self,name):
        for mac,mac_template_info in self.bindingDict.items():
            new_template_id = mac_template_info.get('new_template_id')
            now_template_id = mac_template_info.get('now_template_id')
            fault_count = 0
            if new_template_id != now_template_id:
                while True:
                    result = yield self.updateLabelTemplate(mac, new_template_id)
                    if result == True:
                        self.bindingDict[mac]['now_template_id'] = new_template_id
                        yield logClient.tornadoInfoLog('会议室：{},标签:{},更新模板:{},成功'.format(name, mac, new_template_id))
                        break
                    elif result == 501:
                        yield self.eslCloudClient.tokenError()
                        yield logClient.tornadoErrorLog('会议室：{},更新模板:token失效'.format(name))
                    else:
                        yield logClient.tornadoErrorLog('会议室：{},标签:{},更新模板:{},失败'.format(name, mac, new_template_id))
                    yield gen.sleep(10)
                    fault_count += 1
                    if fault_count >= 10:
                        break
        else:
            yield gen.sleep(30)

    @gen.coroutine
    def updateLabelInfo(self,name,company_db,delayFlag=None,callback=None):
        now_time = time.time()
        brush_info = yield self.getSelfInfo()
        if callback == None:
            if brush_info == self.lastBrushInfo:
                yield logClient.tornadoInfoLog('会议室:{},两次推送内容相同,取消推送'.format(name))
                return
        if now_time - self.lastBrushTime < 60:
            yield logClient.tornadoInfoLog('会议室:{},两次推送间隔太短,启动延时推送'.format(name))
            if self.waitBrushTask != None:
                #有任务
                yield logClient.tornadoDebugLog('会议室:{},存在相同任务,删除任务'.format(name))
                self.ioloop.remove_timeout(self.waitBrushTask)
            else:
                yield logClient.tornadoDebugLog('会议室:{},无相同任务,添加任务'.format(name))
            if callback == None:
                self.waitBrushTask = self.ioloop.add_timeout(self.ioloop.time() + 60-int((now_time - self.lastBrushTime)), self.updateLabelInfo, name,company_db, delayFlag)
            else:
                self.waitBrushTask = self.ioloop.add_timeout(self.ioloop.time() + 60-int((now_time - self.lastBrushTime)), self.updateLabelInfo, name,company_db, delayFlag, callback)
            return None

        self.lastBrushTime = now_time
        self.waitBrushTask = None
        yield self.checkSelfLabelTemplate(name)
        fault_count = 0
        while True:
            result = yield self.brushSelfInfo(brush_info)
            if result == True:
                yield logClient.tornadoInfoLog('会议室:{},{}推送商品成功'.format(name,'延时' if delayFlag else ''))
                yield self.keepNowBrushInfo(brush_info)
                yield self.storageSelf(company_db)
                yield self.printNowBrushInfo(brush_info)
                break
            elif result == 501:
                yield logClient.tornadoErrorLog('会议室:{},推送商品token失效'.format(name))
                yield self.eslCloudClient.tokenError()
            else:
                yield logClient.tornadoErrorLog('会议室:{},{}推送商品失败'.format(name,'延时' if delayFlag else ''))
            yield gen.sleep(10)
            fault_count += 1
            if fault_count >= 10:
                break

    @gen.coroutine
    def keepNowBrushInfo(self,brush_info):
        self.lastBrushInfo = brush_info

    @gen.coroutine
    def printNowBrushInfo(self,brush_info):
        yield logClient.tornadoInfoLog('')
        yield logClient.tornadoInfoLog('***********************************************')
        yield logClient.tornadoInfoLog('{}'.format(datetime.datetime.now()))
        yield logClient.tornadoInfoLog('会议室名称：{}'.format(brush_info['label3']))
        yield logClient.tornadoInfoLog('日期：{}'.format(brush_info['label4']))
        yield logClient.tornadoInfoLog('排程一 > 时间:{},主题:{},发起人:{}'.format(brush_info['label5'],brush_info['label6'],brush_info['label7']))
        yield logClient.tornadoInfoLog('排程二 > 时间:{},主题:{},发起人:{}'.format(brush_info['label8'],brush_info['label9'],brush_info['label10']))
        yield logClient.tornadoInfoLog('排程三 > 时间:{},主题:{},发起人:{}'.format(brush_info['label11'],brush_info['label12'],brush_info['label13']))
        yield logClient.tornadoInfoLog('排程四 > 时间:{},主题:{},发起人:{}'.format(brush_info['label14'],brush_info['label15'],brush_info['label16']))
        yield logClient.tornadoInfoLog('公司名称:{}'.format(brush_info['label17']))
        yield logClient.tornadoInfoLog('***********************************************')
        yield logClient.tornadoInfoLog('')
    @gen.coroutine
    def brushSelfInfo(self,brush_info):
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.eslCloudClient.token
        }
        shopGoods = {
            'information': brush_info,
            "storeUuid": self.eslCloudClient.storeCode  # 必填参数 门店编码
        }
        url = self.eslCloudClient.goodBrushUrl
        result = yield asyncTornadoRequest(url, method='POST', headers=headers, body=shopGoods)
        status = result.get('status')
        if status == 200 or status == '200':
            # if DEBUG:
            return True
        else:
            return status

    @gen.coroutine
    def updateLabelTemplate(self,mac,template):
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.eslCloudClient.token
        }
        specify = {
            'mac':mac,
            'demoId':template,
            'barcode':self.barcode,
            'storeId':self.eslCloudClient.storeCode
        }
        url = self.eslCloudClient.templateBindUpdate
        result = yield asyncTornadoRequest(url, method='POST', headers=headers, body=specify)
        status = result.get('status')
        if status == 200 or status == '200':
            return True
        else:
            return status

    # todo:同步商品信息至数据库   -   20190902
    @gen.coroutine
    def storageSelf(self, company_db):
        goods_info = yield self.getSelfInfo()
        data = {
            'database': company_db,
            'msg': {
                'update_time': datetime.datetime.now(),
                'is_delete': False,
            },
            'eq': {
                'barcode': goods_info.get('barcode')
            }
        }
        data['msg'] = {**goods_info, **data['msg']}
        msg = yield mysqlClient.tornadoUpdateMany('d_shop_goods', data)
        if msg['ret'] != '0':
            yield logClient.tornadoDebugLog('更新数据库:商品:{}信息失败'.format(goods_info.get('barcode')))
            return