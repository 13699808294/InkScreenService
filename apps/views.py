import datetime
import json
import uuid

import requests
from tornado import web, gen

from setting.setting import MY_SQL_SERVER_HOST
from utils.MysqlClient import mysqlClient
from utils.agreement import RET
from utils.asyncRequest import asyncTornadoRequest
from utils.my_json import json_dumps
from utils.logClient import logClient

class UseSceneView(web.RequestHandler):

    def initialize(self,server):
        self.eslCloudClient = server.eslCloudClient
        self.ioloop = server.ioloop
        self.storeCode = server.eslCloudClient.storeCode

    #todo:获取使用场景            ==>测试ok
    @gen.coroutine
    def get(self,*args,**kwargs):
        self.headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.eslCloudClient.token
        }

        url = self.eslCloudClient.useSceneUrl
        result = yield asyncTornadoRequest(url,method='GET',headers=self.headers)
        self.write(json_dumps(result))

class GoodsView(web.RequestHandler):
    def initialize(self, server):
        self.eslCloudClient = server.eslCloudClient
        self.ioloop = server.ioloop
        self.storeCode = server.eslCloudClient.storeCode

    #todo:根据标签查询绑定商品        ==>测试ok
    @gen.coroutine
    def get(self,*args,**kwargs):
        #todo:公共数据
        self.headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.eslCloudClient.token
        }
        transaction_info = yield mysqlClient.tornadoOpenTransaction('aura')
        transactionPoint = transaction_info.get('point')
        #todo: 获取参数
        mac = self.get_argument('mac', '')  # 条形码
        if not all([mac]):
            content = {
                'ret':RET.PARAMERR,
                'msg':'标签未知'
            }
            return self.write(json_dumps(content))
        data = {
            'mac':mac,
        }
        url = self.eslCloudClient.queryGoodsUrl
        result = yield asyncTornadoRequest(url, method='GET', headers=self.headers, params=data)
        status = result.get('status')
        if status == 200:
            content = {
                'goods':result,
                'ret': RET.OK,
                'msg': '商品添加成功'
            }
        elif status == 210:
            content = {
                'ret': RET.PARAMERR,
                'msg': '标签没有绑定商品'
            }
        else:
            content = {
                'ret': RET.PARAMERR,
                'msg': '未知错误'
            }
        self.write(json_dumps(content))

    #todo:新增商品信息                ==>测试ok
    @gen.coroutine
    def post(self,*args,**kwargs):
        self.headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.eslCloudClient.token
        }
        transaction_info = yield mysqlClient.tornadoOpenTransaction('aura')
        transactionPoint = transaction_info.get('point')
        #todo:获取参数
        barcode = self.get_argument('barcode','')       #条形码
        qrcode = self.get_argument('qrcode','')         #二维码
        label1 = barcode
        label2 = qrcode
        label3 = self.get_argument('label3', '')
        label4 = self.get_argument('label4', '')
        label5 = self.get_argument('label5', '')
        label6 = self.get_argument('label6', '')
        label7 = self.get_argument('label7', '')
        label8 = self.get_argument('label8', '')
        label9 = self.get_argument('label9', '')
        label10 = self.get_argument('label10', '')
        label11 = self.get_argument('label11', '')
        label12 = self.get_argument('label12', '')
        label13 = self.get_argument('label13', '')
        label14 = self.get_argument('label14', '')
        label15 = self.get_argument('label15', '')
        label16 = self.get_argument('label16', '')
        label17 = self.get_argument('label17', '')
        label18 = self.get_argument('label18', '')
        photo1 = self.get_argument('photo1', '')
        photo2 = self.get_argument('photo2', '')
        photo3 = self.get_argument('photo3', '')
        photo4 = self.get_argument('photo4', '')
        photo5 = self.get_argument('photo5', '')
        if not all([barcode]):
            content = {
                'ret':RET.PARAMERR,
                'msg':'条形码参数未知'
            }
            return self.write(json_dumps(content))
        #todo:判断数据库中是否有barcode的记录,is_delete=Ture
        data = {
            'fields': ['barcode'],
            'eq': {
                'barcode': barcode
            },
        }
        data['database'] = 'aura'
        msg = yield mysql_client.tornadoSelectOnly('d_shop_goods', data)
        if not isinstance(msg, dict):
            content = {
                'ret': RET.PARAMERR,
                'msg': msg
            }
            return self.write(json_dumps(content))
        if msg['ret'] != '0':
            content = {
                'ret': RET.PARAMERR,
                'msg': '数据库查询错误'
            }
            return self.write(json_dumps(content))
        else:
            # todo:若不存在,新增商品信息
            if msg['lenght'] == 0:
                # todo:保存至数据库
                data = {
                    'transactionPoint': transactionPoint,
                    'msg': {
                        "barcode": barcode,
                        'create_time': datetime.datetime.now(),
                        'update_time': datetime.datetime.now(),
                        'is_delete': False,
                        "qrcode": qrcode,
                        "label1": label1,
                        "label2": label2,
                        "label3": label3,
                        "label4": label4,
                        "label5": label5,
                        "label6": label6,
                        "label7": label7,
                        "label8": label8,
                        "label9": label9,
                        "label10": label10,
                        "label11": label11,
                        "label12": label12,
                        "label13": label13,
                        "label14": label14,
                        "label15": label15,
                        "label16": label16,
                        "label17": label17,
                        "label18": label18,
                        "photo1": photo1,
                        "photo2": photo2,
                        "photo3": photo3,
                        "photo4": photo4,
                        "photo5": photo5,
                    },
                }
                data['database'] = 'aura'
                msg = yield mysql_client.tornadoInsertOne('d_shop_goods', data)
                if not isinstance(msg, dict):
                    content = {
                        'ret': RET.DBERR,
                        'msg': msg
                    }
                    return self.write(json_dumps(content))
                if msg['ret'] != '0':
                    content = {
                        'ret': RET.DBERR,
                        'msg': '数据库插入错误'
                    }
                    return self.write(json_dumps(content))
            # todo:若存在,修改商品信息
            else:
                data = {
                    'transactionPoint': transactionPoint,
                    'msg': {
                        'update_time': datetime.datetime.now(),
                        'is_delete': False,
                        "qrcode": qrcode,
                        "label1": label1,
                        "label2": label2,
                        "label3": label3,
                        "label4": label4,
                        "label5": label5,
                        "label6": label6,
                        "label7": label7,
                        "label8": label8,
                        "label9": label9,
                        "label10": label10,
                        "label11": label11,
                        "label12": label12,
                        "label13": label13,
                        "label14": label14,
                        "label15": label15,
                        "label16": label16,
                        "label17": label17,
                        "label18": label18,
                        "photo1": photo1,
                        "photo2": photo2,
                        "photo3": photo3,
                        "photo4": photo4,
                        "photo5": photo5,
                    },
                    'eq': {
                        "barcode": barcode,
                    }
                }
                data['database'] = 'aura'
                msg = yield mysql_client.tornadoUpdateMany('d_shop_goods', data)
                if not isinstance(msg, dict):
                    content = {
                        'ret': RET.DBERR,
                        'msg': msg
                    }
                    return self.write(json_dumps(content))
                if msg['ret'] != '0':
                    content = {
                        'ret': RET.DBERR,
                        'msg': '数据库修改错误'
                    }
                    return self.write(json_dumps(content))
        #todo:同步至WSL云
        shopGoods = {
            "goods": [
                {
                    "barcode": barcode,
                    "qrcode": qrcode,
                    "label1": label1,
                    "label2": label2,
                    "label3": label3,
                    "label4": label4,
                    "label5": label5,
                    "label6": label6,
                    "label7": label7,
                    "label8": label8,
                    "label9": label9,
                    "label10": label10,
                    "label11": label11,
                    "label12": label12,
                    "label13": label13,
                    "label14": label14,
                    "label15": label15,
                    "label16": label16,
                    "label17": label17,
                    "label18": label18,
                    "photo1": photo1,
                    "photo2": photo2,
                    "photo3": photo3,
                    "photo4": photo4,
                    "photo5": photo5,
                },
            ],
            "storeUuid": self.storeCode         #必填参数 门店编码
        }
        url = self.eslCloudClient.goodsUrl
        result = yield asyncTornadoRequest(url,method='POST',headers=self.headers,body=shopGoods)
        status = result.get('status')
        if status == 200:
            #todo:数据提交
            yield mysql_client.asyncioCommitTransaction(transactionPoint)
            content = {
                'ret':RET.OK,
                'msg':'商品添加成功'
            }
        elif status == 400:
            #todo:回滚
            yield mysql_client.asyncioRollbackTransaction(transactionPoint)
            content = {
                'ret': RET.PARAMERR,
                'msg': '没有此门店编码'
            }
        elif status == 401:
            # todo:回滚
            yield mysql_client.asyncioRollbackTransaction(transactionPoint)
            content = {
                'ret': RET.PARAMERR,
                'msg': '门店编码为空'
            }
        elif status == 404:
            # todo:回滚
            yield mysql_client.asyncioRollbackTransaction(transactionPoint)
            content = {
                'ret': RET.PARAMERR,
                'msg': '没有权限'
            }
        else:
            # todo:回滚
            yield mysql_client.asyncioRollbackTransaction(transactionPoint)
            content = {
                'ret': RET.PARAMERR,
                'msg': '未知错误'
            }
        self.write(json_dumps(content))

    #todo:修改商品信息              ==>测试ok
    @gen.coroutine
    def put(self,*args,**kwargs):
        self.headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.eslCloudClient.token
        }
        transaction_info = yield mysqlClient.tornadoOpenTransaction('aura')
        transactionPoint = transaction_info.get('point')
        # todo:获取参数
        barcode = self.get_argument('barcode', '')  # 条形码
        qrcode = self.get_argument('qrcode', '')  # 二维码
        label1 = barcode
        label2 = qrcode
        label3 = self.get_argument('label3', '')
        label4 = self.get_argument('label4', '')
        label5 = self.get_argument('label5', '')
        label6 = self.get_argument('label6', '')
        label7 = self.get_argument('label7', '')
        label8 = self.get_argument('label8', '')
        label9 = self.get_argument('label9', '')
        label10 = self.get_argument('label10', '')
        label11 = self.get_argument('label11', '')
        label12 = self.get_argument('label12', '')
        label13 = self.get_argument('label13', '')
        label14 = self.get_argument('label14', '')
        label15 = self.get_argument('label15', '')
        label16 = self.get_argument('label16', '')
        label17 = self.get_argument('label17', '')
        label18 = self.get_argument('label18', '')
        photo1 = self.get_argument('photo1', '')
        photo2 = self.get_argument('photo2', '')
        photo3 = self.get_argument('photo3', '')
        photo4 = self.get_argument('photo4', '')
        photo5 = self.get_argument('photo5', '')
        #todo:判断商品是否存在
        data = {
            'fields': ['barcode'],
            'eq': {
                'barcode': barcode
            },
        }
        data['database'] = 'aura'
        msg = yield mysql_client.tornadoSelectOnly('d_shop_goods', data)
        if not isinstance(msg, dict):
            content = {
                'ret': RET.PARAMERR,
                'msg': msg
            }
            return self.write(json_dumps(content))
        if msg['ret'] != '0':
            content = {
                'ret': RET.PARAMERR,
                'msg': '数据库查询错误'
            }
            return self.write(json_dumps(content))
        else:
            # todo:若不存在,新增商品信息

            if msg['lenght'] == 0:
                data = {
                    'transactionPoint': transactionPoint,
                    'msg': {
                        "barcode": barcode,
                        'create_time': datetime.datetime.now(),
                        'update_time': datetime.datetime.now(),
                        'is_delete': False,
                        "qrcode": qrcode,
                        "label1": label1,
                        "label2": label2,
                        "label3": label3,
                        "label4": label4,
                        "label5": label5,
                        "label6": label6,
                        "label7": label7,
                        "label8": label8,
                        "label9": label9,
                        "label10": label10,
                        "label11": label11,
                        "label12": label12,
                        "label13": label13,
                        "label14": label14,
                        "label15": label15,
                        "label16": label16,
                        "label17": label17,
                        "label18": label18,
                        "photo1": photo1,
                        "photo2": photo2,
                        "photo3": photo3,
                        "photo4": photo4,
                        "photo5": photo5,
                    },
                }
                data['database'] = 'aura'
                msg = yield mysql_client.tornadoInsertOne('d_shop_goods', data)
                if not isinstance(msg, dict):
                    content = {
                        'ret': RET.DBERR,
                        'msg': msg
                    }
                    return self.write(json_dumps(content))
                if msg['ret'] != '0':
                    content = {
                        'ret': RET.DBERR,
                        'msg': '数据库插入错误'
                    }
                    return self.write(json_dumps(content))
            # todo:若存在,修改数据库信息
            else:
                data = {
                    'transactionPoint': transactionPoint,
                    'msg': {
                        'update_time': datetime.datetime.now(),
                        'is_delete': False,
                        "qrcode": qrcode,
                        "label1": label1,
                        "label2": label2,
                        "label3": label3,
                        "label4": label4,
                        "label5": label5,
                        "label6": label6,
                        "label7": label7,
                        "label8": label8,
                        "label9": label9,
                        "label10": label10,
                        "label11": label11,
                        "label12": label12,
                        "label13": label13,
                        "label14": label14,
                        "label15": label15,
                        "label16": label16,
                        "label17": label17,
                        "label18": label18,
                        "photo1": photo1,
                        "photo2": photo2,
                        "photo3": photo3,
                        "photo4": photo4,
                        "photo5": photo5,
                    },
                    'eq': {
                        "barcode": barcode,
                    }
                }
                data['database'] = 'aura'
                msg = yield mysql_client.tornadoUpdateMany('d_shop_goods', data)
                if not isinstance(msg, dict):
                    content = {
                        'ret': RET.DBERR,
                        'msg': msg
                    }
                    return self.write(json_dumps(content))
                if msg['ret'] != '0':
                    content = {
                        'ret': RET.DBERR,
                        'msg': '数据库修改错误'
                    }
                    return self.write(json_dumps(content))
        #todo:同步商品信息至ESL云
        shopGoods = {
            "goods": [
                {
                    "barcode": barcode,
                    "qrcode": qrcode,
                    "label1": label1,
                    "label2": label2,
                    "label3": label3,
                    "label4": label4,
                    "label5": label5,
                    "label6": label6,
                    "label7": label7,
                    "label8": label8,
                    "label9": label9,
                    "label10": label10,
                    "label11": label11,
                    "label12": label12,
                    "label13": label13,
                    "label14": label14,
                    "label15": label15,
                    "label16": label16,
                    "label17": label17,
                    "label18": label18,
                    "photo1": photo1,
                    "photo2": photo2,
                    "photo3": photo3,
                    "photo4": photo4,
                    "photo5": photo5,
            },
            ],
            "storeUuid": self.storeCode            # 必填参数门店编码
        }
        url = self.eslCloudClient.goodsUrl
        result = yield asyncTornadoRequest(url, method='PUT', headers=self.headers, body=shopGoods)
        status = result.get('status')
        if status == 200:
            # todo:数据提交
            yield mysql_client.asyncioCommitTransaction(transactionPoint)
            content = {
                'ret': RET.OK,
                'msg': '商品修改成功'
            }
        elif status == 400:
            # todo:回滚
            yield mysql_client.asyncioRollbackTransaction(transactionPoint)
            content = {
                'ret': RET.PARAMERR,
                'msg': '没有此门店编码'
            }
        elif status == 401:
            # todo:回滚
            yield mysql_client.asyncioRollbackTransaction(transactionPoint)
            content = {
                'ret': RET.PARAMERR,
                'msg': '门店编码为空'
            }
        elif status == 404:
            # todo:回滚
            yield mysql_client.asyncioRollbackTransaction(transactionPoint)
            content = {
                'ret': RET.PARAMERR,
                'msg': '没有权限'
            }
        else:
            # todo:回滚
            yield mysql_client.asyncioRollbackTransaction(transactionPoint)
            content = {
                'ret': RET.PARAMERR,
                'msg': '未知错误'
            }
        # todo:判断商品是否绑定标签
        data = {
            'fields': ['mac'],
            'eq': {
                'is_delete': False,
                'barcode': barcode
            },
        }
        msg = yield mysql_client.tornadoSelectOnly('d_label_binding_goods', data)
        if not isinstance(msg, dict):
            content = {
                'ret': RET.PARAMERR,
                'msg': msg
            }
            return self.write(json_dumps(content))
        if msg['ret'] != '0':
            content = {
                'ret': RET.PARAMERR,
                'msg': '数据库查询错误'
            }
            return self.write(json_dumps(content))
        else:
            # todo:若已绑定标签,推送商品信息
            if msg['lenght'] != 0:
                shopGoods = {
                    "information": {
                        "barcode": barcode,
                        'create_time': datetime.datetime.now(),
                        'update_time': datetime.datetime.now(),
                        'is_delete': False,
                        "qrcode": qrcode,
                        "label1": label1,
                        "label2": label2,
                        "label3": label3,
                        "label4": label4,
                        "label5": label5,
                        "label6": label6,
                        "label7": label7,
                        "label8": label8,
                        "label9": label9,
                        "label10": label10,
                        "label11": label11,
                        "label12": label12,
                        "label13": label13,
                        "label14": label14,
                        "label15": label15,
                        "label16": label16,
                        "label17": label17,
                        "label18": label18,
                        "photo1": photo1,
                        "photo2": photo2,
                        "photo3": photo3,
                        "photo4": photo4,
                        "photo5": photo5,
                    },
                    "storeUuid": self.storeCode  # 必填参数 门店编码
                }
                url = self.eslCloudClient.goodBrushUrl
                result = yield asyncTornadoRequest(url, method='POST', headers=self.headers, body=shopGoods)
                status = result.get('status')
                data = result.get('data')
                if status == 200:
                    content = []
                    for d in data:
                        code = d.get('code')
                        if code == '201':
                            content_info = {
                                'msg': '商品修改成功,标签没有绑定网关'
                            }
                            content.append(content_info)
                        elif code == '202':
                            content_info = {
                                'msg': '商品修改成功,标签没有导入'
                            }
                            content.append(content_info)
                        elif code == '203':
                            content_info = {
                                'msg': '商品修改成功,刷图异常'
                            }
                            content.append(content_info)
                        else:
                            content_info = {
                                'msg': '商品修改成功,未知信息'
                            }
                            content.append(content_info)
                elif status == 400:
                    content = {
                        'ret': RET.PARAMERR,
                        'msg': '商品修改成功,没有此门店编码'
                    }
                elif status == 401:
                    content = {
                        'ret': RET.PARAMERR,
                        'msg': '商品修改成功,门店编码为空'
                    }
                elif status == 404:
                    content = {
                        'ret': RET.PARAMERR,
                        'msg': '商品修改成功,没有权限'
                    }
                elif status == 405:
                    content = {
                        'ret': RET.PARAMERR,
                        'msg': '商品修改成功,条形码错误'
                    }
                elif status == 406:
                    content = {
                        'ret': RET.PARAMERR,
                        'msg': '商品修改成功,商品没有绑定标签'
                    }
                else:
                    content = {
                        'ret': RET.PARAMERR,
                        'msg': '商品修改成功,未知错误'
                    }
        self.write(json_dumps(content))

    #todo:删除商品信息                ==>测试ok
    @gen.coroutine
    def delete(self,*args,**kwargs):
        self.headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.eslCloudClient.token
        }
        transaction_info = yield mysqlClient.tornadoOpenTransaction('aura')
        transactionPoint = transaction_info.get('point')
        #todo:获取参数
        barcodes = self.get_argument('barcodes', '')  # 条形码
        barcode_list = barcodes.split('%')
        while '' in barcode_list:
            barcode_list.remove('')
        if not all([barcodes]):
            content = {
                'ret':RET.PARAMERR,
                'msg':'条形码参数未知'
            }
            return self.write(json_dumps(content))
        shopGoods = {
            "goods": [],
            "storeUuid": self.storeCode
        }

        for barcode in barcode_list:
            shopGoods['goods'] = [{'barcode':barcode}]
            # todo:判断barcode是否存在
            data = {
                'fields': ['barcode'],
                'eq': {
                    'is_delete': False,
                    'barcode': barcode
                },
            }
            data['database'] = 'aura'
            msg = yield mysql_client.tornadoSelectOnly('d_shop_goods', data)
            if not isinstance(msg, dict):
                content = {
                    'ret': RET.PARAMERR,
                    'msg': msg
                }
                return self.write(json_dumps(content))
            if msg['ret'] != '0':
                content = {
                    'ret': RET.PARAMERR,
                    'msg': '数据库查询错误'
                }
                return self.write(json_dumps(content))
            else:
                if msg['lenght'] != 0:
                    #todo:数据库删除商品
                    data = {
                        'transactionPoint': transactionPoint,
                        'msg': {
                            'update_time': datetime.datetime.now(),
                            'is_delete': True,
                        },
                        'eq': {
                            "barcode": barcode,
                        }
                    }
                    data['database'] = 'aura'
                    msg = yield mysql_client.tornadoUpdateMany('d_shop_goods', data)
                    if not isinstance(msg, dict):
                        content = {
                            'ret': RET.DBERR,
                            'msg': msg
                        }
                        return self.write(json_dumps(content))
                    if msg['ret'] != '0':
                        content = {
                            'ret': RET.DBERR,
                            'msg': '数据库修改错误'
                        }
                        return self.write(json_dumps(content))
                    #todo:ESL云删除
                    url = self.eslCloudClient.goodsUrl
                    result = yield asyncTornadoRequest(url, method='DELETE', headers=self.headers, body=shopGoods,allow_nonstandard_methods=True)
                    status = result.get('status')
                    if status == 200:
                        # todo:数据提交
                        yield mysql_client.asyncioCommitTransaction(transactionPoint)
                    elif status == 400:
                        # todo:回滚
                        yield mysql_client.asyncioRollbackTransaction(transactionPoint)
                        content = {
                            'ret': RET.PARAMERR,
                            'msg': '没有此门店编码'
                        }
                        self.write(json_dumps(content))
                    elif status == 401:
                        # todo:回滚
                        yield mysql_client.asyncioRollbackTransaction(transactionPoint)
                        content = {
                            'ret': RET.PARAMERR,
                            'msg': '门店编码为空'
                        }
                        self.write(json_dumps(content))
                    elif status == 404:
                        # todo:回滚
                        yield mysql_client.asyncioRollbackTransaction(transactionPoint)
                        content = {
                            'ret': RET.PARAMERR,
                            'msg': '没有权限'
                        }
                        self.write(json_dumps(content))
                    else:
                        # todo:回滚
                        yield mysql_client.asyncioRollbackTransaction(transactionPoint)
                        content = {
                            'ret': RET.PARAMERR,
                            'msg': '未知错误'
                        }
                        self.write(json_dumps(content))
        else:
            content = {
                'ret': RET.OK,
                'msg': '商品删除成功'
            }
            self.write(json_dumps(content))

class ControlView(web.RequestHandler):
    @gen.coroutine
    def initialize(self, server):
        self.eslCloudClient = server.eslCloudClient
        self.ioloop = server.ioloop
        self.storeCode = server.eslCloudClient.storeCode

    #todo:获取模板id
    @gen.coroutine
    def get(self,*args,**kwargs):
        self.headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.eslCloudClient.token
        }
        transaction_info = yield mysqlClient.tornadoOpenTransaction('aura')
        transactionPoint = transaction_info.get('point')
        page = self.get_argument('page','')
        size = self.get_argument('size','')
        name = self.get_argument('name','')
        if not all([page,size]):
            content = {
                'ret': RET.PARAMERR,
                'msg': '参数错误'
            }
            return self.write(json_dumps(content))
        data = {
            'page': page,
            'size': size,
            'storeUuid':self.storeCode,
            'name':name
        }
        url = self.eslCloudClient.templateUrl
        result = yield asyncTornadoRequest(url, method='GET', headers=self.headers,params=data)
        self.write(json_dumps(result))

    #todo:绑定标签                  ==>测试ok
    @gen.coroutine
    def post(self,*args,**kwargs):
        #todo:公共参数
        self.headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.eslCloudClient.token
        }
        transaction_info = yield mysqlClient.tornadoOpenTransaction('aura')
        transactionPoint = transaction_info.get('point')
        #todo:获取参数
        barcode = self.get_argument('barcode', '')          # 条形码
        template = self.get_argument('template','')            # 模板id
        mac = self.get_argument('mac', '')                  # 标签mac
        if not all([barcode,template,mac]):
            content = {
                'ret': RET.PARAMERR,
                'msg': '参数不全'
            }
            return self.write(json_dumps(content))
        #todo:查询标签和商品是否绑定
        data = {
            'fields': ['guid'],
            'eq': {
                'barcode': barcode,
                'mac':mac
            },
        }
        data['database'] = 'aura'
        msg = yield mysql_client.tornadoSelectOnly('d_label_binding_goods', data)
        if not isinstance(msg, dict):
            content = {
                'ret': RET.PARAMERR,
                'msg': msg
            }
            return self.write(json_dumps(content))
        if msg['ret'] != '0':
            content = {
                'ret': RET.PARAMERR,
                'msg': '数据库查询错误'
            }
            return self.write(json_dumps(content))
        else:
            guid_list = [x['guid'] for x in msg['msg']]
            # todo:若没有绑定,则新增绑定关系
            if msg['lenght'] == 0:
                data = {
                    'transactionPoint': transactionPoint,
                    'msg': {
                        'guid': uuid.uuid1().urn.split(':')[2],
                        'create_time': datetime.datetime.now(),
                        'update_time': datetime.datetime.now(),
                        'is_delete': False,
                        "barcode": barcode,
                        'mac':mac,
                        'template':template,
                    },
                }
                data['database'] = 'aura'
                msg = yield mysql_client.tornadoInsertOne('d_label_binding_goods', data)
                if not isinstance(msg, dict):
                    content = {
                        'ret': RET.DBERR,
                        'msg': msg
                    }
                    return self.write(json_dumps(content))
                if msg['ret'] != '0':
                    content = {
                        'ret': RET.DBERR,
                        'msg': '数据库插入错误'
                    }
                    return self.write(json_dumps(content))
            # todo:若绑定,则修改绑定规则(模板id)
            else:
                data = {
                    'transactionPoint': transactionPoint,
                    'msg': {
                        'update_time': datetime.datetime.now(),
                        'is_delete': False,
                        "barcode": barcode,
                        'mac': mac,
                        'template': template,
                    },
                    'eq': {
                        "guid": guid_list,
                    }
                }
                data['database'] = 'aura'
                msg = yield mysql_client.tornadoUpdateMany('d_label_binding_goods', data)
                if not isinstance(msg, dict):
                    content = {
                        'ret': RET.DBERR,
                        'msg': msg
                    }
                    return self.write(json_dumps(content))
                if msg['ret'] != '0':
                    content = {
                        'ret': RET.DBERR,
                        'msg': '数据库修改错误'
                    }
                    return self.write(json_dumps(content))
        data = {
            "procBindings": [
                {
                    "barcode": barcode,             #条形码
                    "demoId": template,          #模板id
                    "mac": mac                      #标签Mac地址
                },
                ],
                "storeUuid": self.storeCode     # 必填参数 门店编码
        }
        url = self.eslCloudClient.bindingUrl
        result = yield asyncTornadoRequest(url, method='POST', headers=self.headers, body=data)
        status = result.get('status')
        data = result.get('data')
        if status == 200:
            content = []
            for d in data:
                code = d.get('code')
                if code == '200':
                    # todo:数据提交
                    yield mysql_client.asyncioCommitTransaction(transactionPoint)
                    content_info = {
                        '标签':d.get('message'),
                        'msg': '商品绑定成功'
                    }
                    content.append(content_info)
                elif code == '205':
                    # todo:数据提交
                    yield mysql_client.asyncioCommitTransaction(transactionPoint)
                    content_info = {
                        '标签':d.get('message'),
                        'msg': '商品已绑定'
                    }
                    content.append(content_info)
                elif code == '206':
                    # todo:回滚
                    yield mysql_client.asyncioRollbackTransaction(transactionPoint)
                    content_info = {
                        '标签': d.get('message'),
                        'msg': '没有此商品信息,请先导入或添加'
                    }
                    content.append(content_info)
                elif code == '207':
                    # todo:回滚
                    yield mysql_client.asyncioRollbackTransaction(transactionPoint)
                    content_info = {
                        '标签': d.get('message'),
                        'msg': '没有此标签信息，请先导入'
                    }
                    content.append(content_info)
                elif code == '208':
                    content_info = {
                        '标签': d.get('message'),
                        'msg': '商品绑定成功'
                    }
                    content.append(content_info)
                else:
                    # todo:回滚
                    yield mysql_client.asyncioRollbackTransaction(transactionPoint)
                    content_info = {
                        'msg': '未知信息'
                    }
                    content.append(content_info)
        elif status == 400:
            # todo:回滚
            yield mysql_client.asyncioRollbackTransaction(transactionPoint)
            content = {
                'ret': RET.PARAMERR,
                'msg': '没有此门店编码'
            }
        else:
            # todo:回滚
            yield mysql_client.asyncioRollbackTransaction(transactionPoint)
            content = {
                'ret': RET.PARAMERR,
                'msg': '未知错误'
            }
        self.write(json_dumps(content))

    #todo:删除绑定                  ==>测试ok
    @gen.coroutine
    def delete(self,*args,**kwargs):
        #todo:公共参数
        self.headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.eslCloudClient.token
        }
        transaction_info = yield mysqlClient.tornadoOpenTransaction('aura')
        transactionPoint = transaction_info.get('point')
        #todo:获取参数
        macs = self.get_argument('macs')
        mac_list = macs.split('%')
        while '' in mac_list:
            mac_list.remove('')
        if not all([mac_list]):
            content = {
                'ret':RET.PARAMERR,
                'msg':'mac地址错误'
            }
            return self.write(json_dumps(content))
        for mac in mac_list:
            #todo:判断mac标签是否存在
            data = {
                'fields': ['mac'],
                'eq': {
                    'is_delete': False,
                    'mac': mac
                },
            }
            data['database'] = 'aura'
            msg = yield mysql_client.tornadoSelectOnly('d_label_device', data)
            if not isinstance(msg, dict):
                content = {
                    'ret': RET.PARAMERR,
                    'msg': msg
                }
                return self.write(json_dumps(content))
            if msg['ret'] != '0':
                content = {
                    'ret': RET.PARAMERR,
                    'msg': '数据库查询错误'
                }
                return self.write(json_dumps(content))
            #todo:删除标签绑定关系
            data = {
                'transactionPoint': transactionPoint,
                'msg': {
                    'update_time': datetime.datetime.now(),
                    'is_delete': True,
                },
                'eq': {
                    "mac": mac,
                }
            }
            data['database'] = 'aura'
            msg = yield mysql_client.tornadoUpdateMany('d_label_binding_goods', data)
            if not isinstance(msg, dict):
                content = {
                    'ret': RET.DBERR,
                    'msg': msg
                }
                return self.write(json_dumps(content))
            if msg['ret'] != '0':
                content = {
                    'ret': RET.DBERR,
                    'msg': '数据库修改错误'
                }
                return self.write(json_dumps(content))

            data = {
                "storeUuid": self.storeCode  # 必填参数 门店编码
            }
            data['macs'] = [mac]
            url = self.eslCloudClient.removeBindingUrl
            result = yield asyncTornadoRequest(url, method='DELETE', headers=self.headers, body=data,allow_nonstandard_methods=True)
            status = result.get('status')
            if status == 200:
                # todo:数据提交
                yield mysql_client.asyncioCommitTransaction(transactionPoint)
            elif status == 400:
                # todo:回滚
                yield mysql_client.asyncioRollbackTransaction(transactionPoint)
                content = {
                    'ret': RET.PARAMERR,
                    'msg': '没有此门店编码'
                }
                self.write(json_dumps(content))
            else:
                # todo:回滚
                yield mysql_client.asyncioRollbackTransaction(transactionPoint)
                content = {
                    'ret': RET.PARAMERR,
                    'msg': '未知错误'
                }
                self.write(json_dumps(content))
        content = {
            'ret': RET.OK,
            'msg': '标签删除绑定成功'
        }
        self.write(json_dumps(content))

class BrushView(web.RequestHandler):
    def initialize(self, server):
        self.eslCloudClient = server.eslCloudClient
        self.ioloop = server.ioloop
        self.storeCode = server.eslCloudClient.storeCode

    #todo:单个商品推送
    @gen.coroutine
    def post(self,*args,**kwargs):
        self.headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.eslCloudClient.token
        }
        transaction_info = yield mysqlClient.tornadoOpenTransaction('aura')
        transactionPoint = transaction_info.get('point')
        barcode = self.get_argument('barcode', '')  # 条形码
        if not all([barcode]):
            content = {
                'ret':RET.PARAMERR,
                'msg':'条形码参数未知'
            }
            return self.write(json_dumps(content))
        #todo:获取商品信息
        data = {
            'fields': ['barcode', 'qrcode', 'label1', 'label2', 'label3', 'label4', 'label5', 'label6', 'label7',
                       'label8',
                       'label9', 'label10', 'label11', 'label12', 'label13', 'label14', 'label15', 'label16', 'label17',
                       'label18',
                       'photo1', 'photo2', 'photo3', 'photo4', 'photo5'],
            'eq': {
                'is_delete': False,
                'barcode':barcode,
            },
            'sortInfo': [
                {'update_time': ''},
            ]
        }
        data['database'] = 'aura'
        msg = yield mysqlClient.tornadoSelectOnly('d_shop_goods', data)
        if not isinstance(msg, dict):
            content = {
                'ret': RET.DBERR,
                'msg': msg
            }
            return self.write(json_dumps(content))
        if msg['ret'] != '0':
            content = {
                'ret': RET.DBERR,
                'msg': '数据库查询错误'
            }
            return self.write(json_dumps(content))
        else:
            if msg['lenght'] == 0:
                content = {
                    'ret': RET.DBERR,
                    'msg': '商品不存在'
                }
                return self.write(json_dumps(content))
            goods_info = msg['msg'][0]
        #todo:推送商品信息到标签
        shopGoods = {
            "information": {
                    "barcode": goods_info['barcode'],
                    "qrcode": goods_info['qrcode'],
                    "label1": goods_info['label1'],
                    "label2": goods_info['label2'],
                    "label3": goods_info['label3'],
                    "label4": goods_info['label4'],
                    "label5": goods_info['label5'],
                    "label6": goods_info['label6'],
                    "label7": goods_info['label7'],
                    "label8": goods_info['label8'],
                    "label9": goods_info['label9'],
                    "label10": goods_info['label10'],
                    "label11": goods_info['label11'],
                    "label12": goods_info['label12'],
                    "label13": goods_info['label13'],
                    "label14": goods_info['label14'],
                    "label15": goods_info['label15'],
                    "label16": goods_info['label16'],
                    "label17": goods_info['label17'],
                    "label18": goods_info['label18'],
                    "photo1": goods_info['photo1'],
                    "photo2": goods_info['photo2'],
                    "photo3": goods_info['photo3'],
                    "photo4": goods_info['photo4'],
                    "photo5": goods_info['photo5'],
                },
            "storeUuid": self.storeCode         #必填参数 门店编码
        }
        url = self.eslCloudClient.goodBrushUrl
        result = yield asyncTornadoRequest(url, method='POST', headers=self.headers, body=shopGoods)
        status = result.get('status')
        data = result.get('data')
        if status == 200:
            content = []
            for d in data:
                code = d.get('code')
                if code == '201':
                    content_info = {
                        'msg': '标签没有绑定网关'
                    }
                    content.append(content_info)
                elif code == '202':
                    content_info = {
                        'msg': '标签没有导入'
                    }
                    content.append(content_info)
                elif code == '203':
                    content_info = {
                        'msg': '刷图异常'
                    }
                    content.append(content_info)
                else:
                    content_info = {
                        'msg': '未知信息'
                    }
                    content.append(content_info)
            content = {
                'ret': RET.OK,
                'msg': '商品推送成功'
            }
        elif status == 400:
            content = {
                'ret': RET.PARAMERR,
                'msg': '没有此门店编码'
            }
        elif status == 401:
            content = {
                'ret': RET.PARAMERR,
                'msg': '门店编码为空'
            }
        elif status == 404:
            content = {
                'ret': RET.PARAMERR,
                'msg': '没有权限'
            }
        elif status == 405:
            content = {
                'ret': RET.PARAMERR,
                'msg': '条形码错误'
            }
        elif status == 406:
            content = {
                'ret': RET.PARAMERR,
                'msg': '商品没有绑定标签'
            }
        elif status == 201:
            content = {
                'ret': RET.PARAMERR,
                'msg': '标签没有绑定网关'
            }
        elif status == 202:
            content = {
                'ret': RET.PARAMERR,
                'msg': '标签没有导入'
            }
        elif status == 203:
            content = {
                'ret': RET.PARAMERR,
                'msg': '刷图异常'
            }
        else:
            content = {
                'ret': RET.PARAMERR,
                'msg': '未知错误'
            }
        self.write(json_dumps(content))

    #todo:标签灯控制接口
    @gen.coroutine
    def put(self,*args,**kwargs):
        self.headers = {
            'content-type': 'application/json',
            'Authorization': 'Bearer ' + self.eslCloudClient.token
        }
        transaction_info = yield mysqlClient.tornadoOpenTransaction('aura')
        transactionPoint = transaction_info.get('point')
        # storeUuid = self.get_argument('storeUuid', '')      # 门店编码
        mac = self.get_argument('mac', '')                  # 标签mac
        color = self.get_argument('color','')               # 灯的颜色 0 关闭,1:蓝色,2:绿色,3:红色
        total = self.get_argument('total','')               # 控制灯的总时间,单位s
        period = self.get_argument('period','')             #灯一次亮多久，单位ms
        interval = self.get_argument('interval','')         #灯多久亮一次，单位ms
        brigthness = self.get_argument('brigthness','')     #灯的亮度，1~100,亮度太低效果不明显
        # if not all([storeUuid,mac]):
        #     content = {
        #         'ret': RET.PARAMERR,
        #         'msg': '门店编码或标签mac为空'
        #     }
        #     return self.write(json_dumps(content))
        try:
            color = int(color)
            total = int(total)
            period = int(period)
            interval = int(interval)
            brigthness = int(brigthness)
        except:
            content = {
                'ret': RET.PARAMERR,
                'msg': '控制参数错误'
            }
            return self.write(json_dumps(content))
        data = {
            'storeUuid':self.storeCode,
            'mac':mac,
            'color':color,
            'total':total,
            'period':period,
            'interval':interval,
            'brigthness':brigthness,
        }
        url = self.eslCloudClient.controlLedUrl
        result = yield asyncTornadoRequest(url, method='PUT', headers=self.headers, params=data,body=data)
        status = result.get('status')
        if status == 200:
            content = {
                'ret': RET.OK,
                'msg': 'LED控制成功成功'
            }
        elif status == 400:
            content = {
                'ret': RET.PARAMERR,
                'msg': '没有此门店编码'
            }
        elif status == 401:
            content = {
                'ret': RET.PARAMERR,
                'msg': '此mac地址错误或标签不存在'
            }
        elif status == 402:
            content = {
                'ret': RET.PARAMERR,
                'msg': '标签没有绑定网关'
            }
        else:
            content = {
                'ret': RET.PARAMERR,
                'msg': '未知错误'
            }
        self.write(json_dumps(content))

class Callback(web.RedirectHandler):

    def initialize(self, server):
        self.eslCloudClient = server.eslCloudClient
        self.ioloop = server.ioloop
        self.storeCode = server.eslCloudClient.storeCode
        self.meeting_room_list = server.meeting_room_list

    @gen.coroutine
    def post(self,*args,**kwargs):
        try:
            result = json.loads(self.request.body)
        except:
            content = {
                'ret': 1,
                'status': '错误'
            }
            self.write(json_dumps(content))
            return
        username = result.get('username')
        code = result.get('code')                   #返回码
        commodity = result.get('commodity')          #商品条码
        mac = result.get('mac')                      #标签mac码
        operationType = result.get('operationType')  #操作
        storeUuid = result.get('storeUuid')          #门店id
        result = result.get('result')                #回调说明
        if commodity == None or mac == None:
            return

        for meeting_room in self.meeting_room_list:
            for mac_id,lableDeviceInfo in meeting_room.labelDeviceDict.items():
                if mac == mac_id:
                    meeting_room_object = meeting_room
                    for good_id, good in meeting_room_object.goods_dict.items():
                        if commodity == good_id:
                            goodObject = good
                            if code == 301 or code == '301':  # 刷图成功
                                yield logClient.tornadoInfoLog('会议室:{},用户:{},进行对门店{},商品{},标签{},{}操作,结果为:{},编码为{}'.format(meeting_room_object.name,username, storeUuid,commodity, mac,operationType, result,code))
                            else:  # 刷图失败
                                yield logClient.tornadoErrorLog('会议室:{},用户:{},进行对门店{},商品{},标签{},{}操作,结果为:{},编码为{}'.format(meeting_room_object.name,username, storeUuid,commodity, mac,operationType, result,code))
                                yield goodObject.updateLabelInfo(meeting_room_object.name,meeting_room_object.company_db,1,1)
                            return

class TokenChangeView(web.RedirectHandler):

    def initialize(self,server):
        self.eslCloudClient = server.eslCloudClient

    @gen.coroutine
    def post(self,*args,**kwargs):
        result = json.loads(self.request.body)
        token = result.get('token')
        self.eslCloudClient.token = token
        content = {
            'ret':0
        }
        self.write(json_dumps(content))