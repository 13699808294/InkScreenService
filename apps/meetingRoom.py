import copy
import datetime
import json
import time
from concurrent.futures import ThreadPoolExecutor

from tornado import gen
from tornado.concurrent import run_on_executor

from setting.setting import MY_SQL_SERVER_HOST, DATABASES
from utils.MysqlClient import mysqlClient
from utils.asyncRequest import asyncTornadoRequest
from utils.logClient import logClient


class MeetingRoom(object):
    executor = ThreadPoolExecutor(max_workers=10)
    def __init__(self,
                 company_db,
                 ioloop,
                 mqttClient,
                 eslCloudClient,
                 goods_dict,
                 guid,
                 room_name,
                 sin_minute,
                 schedule_status,
                 company_name
                 ):
        '''会议室信息'''
        self.guid = guid
        self.name = room_name
        self.sin_minute = int(sin_minute)
        self.company_db = company_db
        self.ioloop = ioloop
        self.mqttClient = mqttClient
        self.eslCloudClient = eslCloudClient
        self.goods_dict = goods_dict
        #应用
        self.labelDeviceDict = {}
        self.updating = None
        self.subscribeInfoBuffer = []
        self.schedule_status = schedule_status         #0:空闲中  1:准备中   2:会议中
        self.company_name = company_name
        self.ioloop.add_timeout(self.ioloop.time(),self.initSelfLabelDevice)

    @gen.coroutine
    def MeetingRoomOnMessage(self,ReceiveMessageObject):
        self.subscribeInfoBuffer.append(ReceiveMessageObject)
        if self.updating:
            return

        for ReceiveMessageObject in self.subscribeInfoBuffer:
            topic = ReceiveMessageObject.topic
            topic_list = ReceiveMessageObject.topicList
            data = ReceiveMessageObject.data

            if topic_list[5] == 'schedule':    #排程更换
                if topic_list[6] == 'schedule_info':
                    # 重新获取会议室所有排程
                    yield self.updateLabelSchedule(data)
                    # yield self.updateMeetingStatus(data)
                #推送排除信息给use_type = 1的LabelDevice
            elif topic_list[5] == 'station':   #工位更换
                pass
            elif topic == '/aaiot/0/send/controlbus/event/time/0/0':
                #更新日期事件
                yield self.updateLabelDate()
        else:
            self.subscribeInfoBuffer = []

    #todo:更新所有标签日期
    @gen.coroutine
    def updateLabelDate(self):
        date_ = datetime.datetime.now().strftime('%Y.%m.%d')
        for mac,label_dict in self.labelDeviceDict.items():
            barcode_id = label_dict.get('barcode_id')
            goodsObject = self.goods_dict.get(barcode_id)
            use_type = label_dict.get('use_type')
            #更新工位日期
            if use_type == 0:
                # 获取标签绑定的商品条码
                if goodsObject == None:
                    continue
                if goodsObject.label12 != date_:
                    goodsObject.label12 = date_
                    yield self.handleBrushGoodsInfo(goodsObject)
            #更新会议预览日期
            elif use_type == 1:
                if goodsObject == None:
                    continue
                if goodsObject.label4 != date_:
                    goodsObject.label4 = date_
                    yield self.handleBrushGoodsInfo(goodsObject)

    #todo:更新use_type=1的标签排程信息
    @gen.coroutine
    def updateLabelSchedule(self,data):
        '''
        获取当前会议室将来时间的六条排程信息
        更新本会议室type=1的标签
        '''
        try:
            msg = json.loads(data)
        except:
            return
        # schedule_status = msg.get('schedule_status')
        schedule_list = msg.get('other_schedule')
        now_schedule = msg.get('now_schedule')
        next_schedule = msg.get('next_schedule')
        if schedule_list == None or now_schedule == None or next_schedule == None:
            return
        if next_schedule:
            schedule_list.insert(0,next_schedule)
        if now_schedule:
            schedule_list.insert(0,now_schedule)
        #获取标签对应的商品条码guid
        for mac,labelDeviceInfo in self.labelDeviceDict.items():
            barcode_id = labelDeviceInfo.get('barcode_id')  #条码id
            goodsObject = self.goods_dict.get(barcode_id)   #商品对象
            if goodsObject == None:
                return
            use_type = labelDeviceInfo.get('use_type')      #标签用途

            if use_type == 1:
                update_goods_info = {}
                update_goods_info['label3'] = self.name+'排程'
                update_goods_info['label4'] = datetime.datetime.now().strftime('%Y.%m.%d')
                #插入排程信息
                count = 5
                for schedule in schedule_list:
                    update_goods_info['label%d'%(count)] = datetime.datetime.strptime(schedule['start_time'], "%Y-%m-%d %H:%M:%S").replace(second=0).strftime("%H:%M:%S") + '-' + datetime.datetime.strptime(schedule['stop_time'], "%Y-%m-%d %H:%M:%S").replace(second=0).strftime("%H:%M:%S")
                    count += 1
                    title = schedule.get('title','')
                    #汉字20像素,字符12像素,总长度180
                    char_count = 0
                    new_title = ''
                    for char in title:
                        if ord(char) >= 128:
                            char_count += 20
                        else:
                            char_count += 12
                        if char_count <= 180:
                            new_title += char
                            continue
                        else:
                            new_title += '...'
                            break
                    update_goods_info['label%d'%(count)] = new_title
                    count += 1
                    update_goods_info['label%d' % (count)] = schedule.get('sender','')
                    count += 1
                    if count >= 17:
                        break

                for i in range(count,17):
                    if i%2 == 0:
                        update_goods_info['label%d' % (i)] = ' '
                    elif i%3 == 0 :
                        update_goods_info['label%d' % (i)] = ' '
                    else:
                        update_goods_info['label%d' % (i)] = ' '
                else:
                    company_name = self.company_name[:13]
                    for i in range(len(company_name),13):
                        company_name = '　' + company_name
                    update_goods_info['label17'] = company_name

                    # if schedule_status == 1:
                    #     update_goods_info['label18'] = '准备中...'
                    # elif schedule_status == 2:
                    #     update_goods_info['label18'] = '进行中...'
                    # else:
                    update_goods_info['label18'] = ''

                    update_goods_info['photo1'] = ''
                    update_goods_info['photo2'] = ''
                    update_goods_info['photo3'] = ''
                    update_goods_info['photo4'] = ''
                    update_goods_info['photo5'] = ''
                #获取更新的模板
                template_point = len(schedule_list)
                if template_point >= 4:
                    template_point = 4
                try:
                    template_id = labelDeviceInfo['template'][template_point]
                except:
                    try:
                        template_id = labelDeviceInfo['template'][0]
                    except:
                        template_id = None
                #获取标签绑定的商品条码
                update_goods_info['barcode'] = update_goods_info['label1'] = barcode_id
                update_goods_info['qrcode'] = update_goods_info['label2'] = ' '
                #比较原商品信息,与更新商品信息的内容是否一致,不一致则更新
                yield goodsObject.updateSelfInfo(update_goods_info)
                yield self.handleBrushGoodsInfo(goodsObject,mac,template_id)

    @gen.coroutine
    def handleBrushGoodsInfo(self,goodsObject,mac=None,template_id=None):
        if mac != None and template_id != None:
            mac_info = goodsObject.bindingDict.get(mac)
            if mac_info == None:
                goodsObject.bindingDict[mac] = {}
                goodsObject.bindingDict[mac]['now_template_id'] = None

            if goodsObject.bindingDict.get(mac).get('now_template_id') != template_id:
                goodsObject.bindingDict[mac]['new_template_id'] = template_id
        yield goodsObject.updateLabelInfo(self.name,self.company_db)

    #todo:获取本会议室标签设备
    @gen.coroutine
    def initSelfLabelDevice(self):
        self.updating = True
        self.labelDeviceDict = {}
        data = {
            'fields': ['mac',
                       'meeting_room_guid_id',
                       'size_type',
                       'use_type',
                       'barcode_id',
                       'template'
                       ],
            'eq': {
                'is_delete': False,
                'meeting_room_guid_id': self.guid
            },
            'sortInfo': [
                {'update_time': ''},
            ]
        }
        data['database'] = 'aura'
        msg = yield mysqlClient.tornadoSelectAll('d_label_device', data)
        if msg['ret'] != '0':
            yield logClient.tornadoErrorLog('获取数据库:标签信息失败',company=self.company_name)
            return
        labelDeviceList = msg['msg']
        for labelDeviceInfo in labelDeviceList:
            labelDeviceMac = labelDeviceInfo['mac']
            labelDeviceInfo['template'] = labelDeviceInfo.get('template','').split(',')
            while '' in labelDeviceInfo['template']:
                labelDeviceInfo['template'].remove('')
            # 获取设备
            self.labelDeviceDict[labelDeviceMac] = labelDeviceInfo
        self.updating = False


    #******************************************************************************************************************#
    #todo:更新会议状态
    @gen.coroutine
    def updateMeetingStatus(self,data):
        '''
        推送LED状态给墨水屏
        data = {
                'now_schedule':now_schedule,
                'next_schedule':next_schedule,
                'schedule_status':meeting_room_info['status']
            }
        '''
        try:
            msg = json.loads(data)
        except:
            return
        status = msg.get('schedule_status')
        try:
            #会议室状态转换为LED显示状态
            status = int(status)
        except:
            return
        for label in self.labelDevice_dict.values():
            if label['use_type'] == 1:
                if self.schedule_status != status:
                    result = yield self.brushLed(label['mac'], status)
                    if not result:
                        self.ioloop.add_timeout(self.ioloop.time()+5,self.updateMeetingStatus,status)
                        return

    #todo:推送LED显示
    @gen.coroutine
    def brushLed(self,mac:str,color:int,total:int=1500,period:int=500,interval:int=1000,brigthness:int=5):
        if color == 0:
            real_color = 2
        elif color == 1:
            real_color = 1
        elif color == 2:
            real_color = 3
        else:
            real_color = 2
        STATUS_TO_NAME = {
            0: '空闲中',
            1: '准备中',
            2: '进行中',
        }
        yield logClient.tornadoInfoLog('{}:状态切换为{}'.format(self.name, STATUS_TO_NAME[color]),company=self.company_name)
        headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.eslCloudClient.token
        }
        data = {
            'storeUuid': self.eslCloudClient.storeCode,
            'mac': mac,
            'color': real_color,
            'total': total,
            'period': period,
            'interval': interval,
            'brigthness': brigthness,
        }
        url = self.eslCloudClient.controlLedUrl
        result = yield asyncTornadoRequest(url, method='PUT', headers=headers, params=data, body=data)
        yield logClient.tornadoInfoLog('会议室:{},led控制推送结果:{}'.format(self.name,result),company=self.company_name)
        status = result.get('status')
        if status == 200:
            self.schedule_status = color
            return True
        else:
            yield logClient.tornadoErrorLog('{}的led推送失败'.format(self.name),company=self.company_name)
            yield self.eslCloudClient.tokenError()
            self.ioloop.add_timeout(self.ioloop.time() + 60, self.brushLed, mac, color)
            return False
