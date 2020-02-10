import datetime

from tornado import gen

from apps.goods import Goods
from utils.baseMosquittoClient import BaseMosquittoClient
from apps.meetingRoom import MeetingRoom
from setting.setting import DEBUG, DATABASES, QOSLOCAL
from utils.MysqlClient import  mysqlClient
from utils.logClient import logClient

class MosquittoClient(BaseMosquittoClient):
    def __init__(self,eslCloudClient,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.eslCloudClient = eslCloudClient
        self.heartTopic = '/aaiot/inkScreen/send/controlbus/system/heartbeat'
        self.heartInterval = 15

        self.meeting_room_list = []
        self.GuidToMeetingRoom = {}
        self.goods_dict = {}
        # 获取所有的会议室
        self.ioloop.add_timeout(self.ioloop.time(), self.updateAllMeetingRoom)

    # todo:获取所有的会议室
    @gen.coroutine
    def updateAllMeetingRoom(self):
        '''获取所有的会议室'''
        #todo:首先获取所有的商品
        yield self.updateGoods()
        #todo:然后获取取所有的会议室
        for DATABASE in DATABASES:
            db = DATABASE['name']
            data = {
                'database': db,
                'fields': [
                    'd_meeting_room.guid',
                    'd_meeting_room.room_name',
                    'd_meeting_room.sin_minute',
                    'd_meeting_room.status_group_guid_id as schedule_status',
                    'd_company.name as company_name'
                ],
                'eq': {
                    'd_meeting_room.is_delete': False,
                    'd_company.is_delete': False,
                    'd_meeting_room.company_guid_id':{'key':'d_company.guid'}
                },
            }
            msg = yield mysqlClient.tornadoSelectAll('d_meeting_room,d_company', data)
            if msg['ret'] != '0':
                yield logClient.tornadoErrorLog('获取数据库:会议室信息失败')
                break
            meeting_rooms = msg['msg']
            for meeting_room in meeting_rooms:
                # 把每一个会议室转换为会议室对象
                meeting_room_ = MeetingRoom(company_db=db,ioloop=self.ioloop,mqttClient=self.connectObject,eslCloudClient=self.eslCloudClient,goods_dict=self.goods_dict,**meeting_room)
                self.meeting_room_list.append(meeting_room_)
                # 添加会议室guid和mqtt_name的转换对象
                self.GuidToMeetingRoom[meeting_room_.guid] = meeting_room_
            else:
                yield logClient.tornadoInfoLog('公司：{}会议室初始化完成'.format(db))

    @gen.coroutine
    def updateGoods(self):
        for DATABASE in DATABASES:
            db = DATABASE['name']
            data = {
                'database': db,
                'fields': ['barcode', 'qrcode', 'label1', 'label2', 'label3','label4','label5','label6','label7','label8',
                           'label9','label10','label11','label12','label13','label14','label15','label16','label17','label18',
                           'photo1','photo2','photo3','photo4','photo5'
                           ],
                'eq': {
                    'is_delete': False
                },
            }
            msg = yield mysqlClient.tornadoSelectAll('d_shop_goods', data)
            if msg['ret'] != '0':
                yield logClient.tornadoErrorLog('获取数据库:商品信息失败')
                break
            goods_list = msg['msg']
            for goods in goods_list:
                self.goods_dict[goods['barcode']] = Goods(**goods,ioloop=self.ioloop,aioloop=self.aioloop,eslCloudClient=self.eslCloudClient)

    @gen.coroutine
    def handleOnMessage(self,ReceiveMessageObject):
        topic = ReceiveMessageObject.topic
        data = ReceiveMessageObject.data
        topic_list = ReceiveMessageObject.topicList

        # if DEBUG:
        #     print('\033[1;37;0m[{}] [DEBUG]:  \033[0m'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + '\033[1;47;0m {} \033[0m'.format(topic),'\033[1;35;46m {} \033[0m'.format(data))

        if topic_list[1] in self.GuidToMeetingRoom.keys():
            self.ioloop.add_timeout(self.ioloop.time(),self.GuidToMeetingRoom[topic_list[1]].MeetingRoomOnMessage(ReceiveMessageObject))
        elif topic == '/aaiot/0/send/controlbus/event/time/0/0':
            self.ioloop.add_timeout(self.ioloop.time(), self.allMeetingRoomTask(ReceiveMessageObject))

    @gen.coroutine
    def allMeetingRoomTask(self, ReceiveMessageObject):
        for meeting_room in self.meeting_room_list:
            yield meeting_room.MeetingRoomOnMessage(ReceiveMessageObject)

    @gen.coroutine
    def handle_on_connect(self):
        topic = '/aaiot/mqttService/receive/controlbus/system/heartbeat'
        qos_type = QOSLOCAL
        self.connectObject.subscribe(topic, qos=qos_type)
        yield logClient.tornadoInfoLog('添加订阅主题为:{},订阅等级为:{}'.format(topic, qos_type))

        # 订阅排程信息
        topic = '/aaiot/+/send/controlbus/event/schedule/schedule_info/0'
        qos_type = QOSLOCAL
        self.connectObject.subscribe(topic, qos=qos_type)
        yield logClient.tornadoInfoLog('添加订阅主题为:{},订阅等级为:{}'.format(topic, qos_type))
        # 订阅时间事件信息
        topic = '/aaiot/0/send/controlbus/event/time/#'
        qos_type = QOSLOCAL
        self.connectObject.subscribe(topic, qos=qos_type)
        yield logClient.tornadoInfoLog('添加订阅主题为:{},订阅等级为:{}'.format(topic, qos_type))
