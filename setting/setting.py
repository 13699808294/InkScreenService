import configparser
import datetime
import os

TEST_SERVER_HOST = 'alc01.aa-iot.com'
BUILD_SERVER_HOST = 'alcpd01.aa-iot.com'
# BUILD_SERVER_HOST = 'tencentclub.aa-iot.com'
# TEST_SERVER_HOST = 'tencentclub.aa-iot.com'
LOCAL_SERVER_HOST = '127.0.0.1'

# 运行环境设置
ENVIRONMENT = 'build'       #生产环境
# ENVIRONMENT = 'test'        # 测试环境
# ENVIRONMENT = 'local'       #本地
# ENVIRONMENT = 'local_test'  #本地测试环境

#路径获取
SERVICE_NAME = 'inkScreenService'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#
LOG_DIR = os.path.join('/alog',SERVICE_NAME)
LOG_TOPIC = 'inkScreenService'
DATABASE_FILE = '/company_info/database.conf'

# 多数据库获取
database_config = configparser.ConfigParser()
database_config.read(DATABASE_FILE, encoding='utf-8')
DATABASES = []
for k, database_info in database_config.items():
    DATABASE = {}
    for key, value in database_info.items():
        DATABASE[key] = value
    else:
        DATABASES.append(DATABASE)

#按照服务,工程生成日志目录
if ENVIRONMENT == 'test' or ENVIRONMENT == 'build' or ENVIRONMENT == 'local_test':
    for DATABASE in DATABASES:
        company_name = DATABASE.get('company_name')
        if not os.path.exists(os.path.join(LOG_DIR,company_name,'debug')):
            os.makedirs(os.path.join(LOG_DIR,company_name,'debug'))
            print('日志目录:{}'.format(os.path.join(LOG_DIR,company_name,'debug')))
        if not os.path.exists(os.path.join(LOG_DIR,company_name,'info')):
            os.makedirs(os.path.join(LOG_DIR,company_name,'info'))
            print('日志目录:{}'.format(os.path.join(LOG_DIR, company_name, 'info')))
        if not os.path.exists(os.path.join(LOG_DIR,company_name,'warning')):
            os.makedirs(os.path.join(LOG_DIR,company_name,'warning'))
            print('日志目录:{}'.format(os.path.join(LOG_DIR, company_name, 'warning')))
        if not os.path.exists(os.path.join(LOG_DIR,company_name,'error')):
            os.makedirs(os.path.join(LOG_DIR,company_name,'error'))
            print('日志目录:{}'.format(os.path.join(LOG_DIR, company_name, 'error')))
    else:
        company_name = 'default'
        if not os.path.exists(os.path.join(LOG_DIR,company_name,'debug')):
            os.makedirs(os.path.join(LOG_DIR,company_name,'debug'))
            print('日志目录:{}'.format(os.path.join(LOG_DIR,company_name,'debug')))
        if not os.path.exists(os.path.join(LOG_DIR,company_name,'info')):
            os.makedirs(os.path.join(LOG_DIR,company_name,'info'))
            print('日志目录:{}'.format(os.path.join(LOG_DIR, company_name, 'info')))
        if not os.path.exists(os.path.join(LOG_DIR,company_name,'warning')):
            os.makedirs(os.path.join(LOG_DIR,company_name,'warning'))
            print('日志目录:{}'.format(os.path.join(LOG_DIR, company_name, 'warning')))
        if not os.path.exists(os.path.join(LOG_DIR,company_name,'error')):
            os.makedirs(os.path.join(LOG_DIR,company_name,'error'))
            print('日志目录:{}'.format(os.path.join(LOG_DIR, company_name, 'error')))


#生产环境
if ENVIRONMENT == 'build':
    DEBUG = False
    # log等级定义
    LOG_LEVEL = 'INFO'
    #直接访问本地数据库
    for DATABASE in DATABASES:
        DATABASE['host'] = LOCAL_SERVER_HOST
    #连接本地运行的mysql服务
    MY_SQL_SERVER_HOST = LOCAL_SERVER_HOST
    #连接本地运行的log服务
    LOG_SERVICE_HOST = LOCAL_SERVER_HOST
    #连接本地运行的MQTT broker
    MQTT_SERVICE_HOST = LOCAL_SERVER_HOST
    #MQTT qos等级为0,最多发送一次,不进行确认
    QOS = 2
    QOSLOCAL = 0
    #回调地址
    CALLBACK_ADDRESS = 'https://{}/inkScreen/callback'.format(BUILD_SERVER_HOST)

#todo:测试环境
elif ENVIRONMENT == 'test':
    DEBUG = False
    # log等级定义
    LOG_LEVEL = 'INFO'
    # 测试环境,直接访问本地数据库
    for DATABASE in DATABASES:
        DATABASE['host'] = LOCAL_SERVER_HOST
    # 连接本地运行的mysql服务
    MY_SQL_SERVER_HOST = LOCAL_SERVER_HOST
    # 连接本地运行的log服务
    LOG_SERVICE_HOST = LOCAL_SERVER_HOST
    # 连接本地运行的MQTT broker
    MQTT_SERVICE_HOST = LOCAL_SERVER_HOST
    # MQTT qos等级为0,最多发送一次,不进行确认
    QOS = 2
    QOSLOCAL = 0
    # 回调地址
    CALLBACK_ADDRESS = 'https://{}/inkScreen/callback'.format(TEST_SERVER_HOST)

#todo:本地环境
elif ENVIRONMENT == 'local':
    DEBUG = True
    # log等级定义
    LOG_LEVEL = 'DEBUG'
    # 本地环境,直接访问测试环境数据库
    for DATABASE in DATABASES:
        DATABASE['host'] = BUILD_SERVER_HOST
    # 连接测试服务器运行的mysql服务
    MY_SQL_SERVER_HOST = BUILD_SERVER_HOST
    # 连接测试服务器运行的log服务
    LOG_SERVICE_HOST = BUILD_SERVER_HOST
    # 连接测试服务器运行的MQTT broker
    MQTT_SERVICE_HOST = BUILD_SERVER_HOST
    # MQTT qos等级为2,只有一次,通过四步握手后发送一次数据
    QOS = 2
    QOSLOCAL = 0
    # 回调地址
    CALLBACK_ADDRESS = 'https://{}/inkScreen/callback'.format(TEST_SERVER_HOST)

elif ENVIRONMENT == 'local_test':
    DEBUG = False
    # log等级定义
    LOG_LEVEL = 'INFO'
    # 测试环境,直接访问本地数据库
    for DATABASE in DATABASES:
        DATABASE['host'] = LOCAL_SERVER_HOST
    # 连接本地运行的mysql服务
    MY_SQL_SERVER_HOST = LOCAL_SERVER_HOST
    # 连接本地运行的log服务
    LOG_SERVICE_HOST = LOCAL_SERVER_HOST
    # 连接本地运行的MQTT broker
    MQTT_SERVICE_HOST = LOCAL_SERVER_HOST
    # MQTT qos等级为0,最多发送一次,不进行确认
    QOS = 2
    QOSLOCAL = 0
    # 回调地址
    CALLBACK_ADDRESS = 'https://{}/inkScreen/callback'.format(TEST_SERVER_HOST)

else:
    raise IndexError('运行环境错误')

# DEBUG = True

# MY_SQL_SERVER_HOST = LOCAL_SERVER_HOST
# MQTT_SERVICE_HOST = BUILD_SERVER_HOST
# MY_SQL_SERVER_HOST = BUILD_SERVER_HOST
# LOG_SERVICE_HOST = BUILD_SERVER_HOST
# MQTT_SERVICE_HOST = LOCAL_SERVER_HOST
print('[{}]:×××××××{}×××××××：服务启动'.format(datetime.datetime.now(),SERVICE_NAME))
print('服务启动场景:({})'.format(ENVIRONMENT))
print('调试模式:({})'.format(DEBUG))
print('输出日志等级:({})'.format(LOG_LEVEL))
print('日志服务器地址:({})'.format(LOG_SERVICE_HOST))
print('数据库服务器地址:({})'.format(MY_SQL_SERVER_HOST))
print('MQTT服务器地址:({})'.format(MQTT_SERVICE_HOST))
print('回调地址:({})'.format(CALLBACK_ADDRESS))

# ESL_CLOUD_USERNAME = 'anmasi'
# ESL_CLOUD_PASSWORD = 'Ams666'
ESL_CLOUD_LOCAL_HOST = 'http://118.190.208.103:9191'
TOKEN_CHANGE_ADDRESS = 'http://{}:8009/inkScreen/token_change'.format(BUILD_SERVER_HOST)    #token变更通知本服务
TOKEN_SERVICE_ADDRESS = 'http://{}:8016/inkScreenToken/get_token'.format(BUILD_SERVER_HOST) #token服务地址
#

# ESL_CLOUD_USERNAME = 'zzq'
# ESL_CLOUD_PASSWORD = '123456'
# ESL_CLOUD_LOCAL_HOST = 'http://192.168.0.254:9191'