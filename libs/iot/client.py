import orjson as json
import time

from paho.mqtt.client import Client
from libs.iot.fitureEnum import IotProtocol, IotTransport, MQTTClientStatus
from libs.iot.callback import IotCallback
from libs.iot.msgBuilder import IotMsgBuilder
from libs.exception import IotException
from libs.logger import log
from libs.timeUtil import TimeUtil
from libs.crypto import Crypto


class MqttClient(object):
    """
    cfg:
    {
   "sessionId":"c2xb6858-5306-4c85-9312-7a889fe8e9d3",
   "secret":"25900dbf-ebee-4006-ab30-d979193228cc",
   "mqttPassport":{
      "username":"user",
      "password":"fake-password1",
      "clientId":"1c4cfa92-a890-4d79-b0e9-4cdd1345abed",
      "subscribeTopic":"session/c2xb6858-5306-4c85-9312-7a889fe8e9d3",
      "publishTopic":"machine/msg04",
      "sslEndPoints":[
         {
            "protocol":"ssl",
            "host":"ttp02.qa.fiture.com",
            "port":8883
         },
         {
            "protocol":"wss",
            "host":"ttp02.qa.fiture.com",
            "port":443
         }
      ]
   },
   "node":"server-plugin04",
   "version":1,
   "businessType":"SLIM",
   "businessId":"878793ce8024",
   "ts":1647942094568,
   "refresh":true
}
    """

    def __init__(self, cfg: dict, userinfo: dict):
        self.cfg = cfg
        self.userinfo = userinfo
        self.client = None
        self.clientId = None
        self.defaultTopic = None
        self.extTopics = []
        self.host = None

    def subscribeTopic(self, *topics):
        self.extTopics.extend(topics)

    def connect(self, msgHandler=None, closeCallback=None):
        log.debug(f"IOT device({self.userinfo.get('virgo_headers').get('deviceSN')}) Connecting...")
        sessionId = self.cfg.get("sessionId")
        mqttPassport = self.cfg.get("mqttPassport")
        username = mqttPassport.get("username")
        password = mqttPassport.get("password")
        sslEndPoints = mqttPassport.get("sslEndPoints")
        EndPointsSSL = list(filter(lambda ed: ed.get("protocol") == "ssl", sslEndPoints))
        EndPointsWSS = list(filter(lambda ed: ed.get("protocol") == "wss", sslEndPoints))
        sslHost = EndPointsSSL[0].get("host")
        wssHost = EndPointsWSS[0].get("host")
        sslPort = EndPointsSSL[0].get("port")
        wssPort = EndPointsWSS[0].get("port")
        self.clientId = mqttPassport.get("clientId")
        self.defaultTopic = mqttPassport.get("publishTopic")
        self.client = Client(client_id=self.clientId, protocol=IotProtocol.MQTTv5.value,
                             transport=IotTransport.tcp.value,
                             userdata=dict(userinfo=self.userinfo, cfg=self.cfg))
        self.client.host = sslHost if sslHost else wssHost
        self.client.port = sslPort if sslPort else wssPort
        self.client.status = MQTTClientStatus.CS_BROKER_INITED
        self.client.cfg = self.cfg
        self.client.extTopics = self.extTopics
        self.client.token = Crypto.aes_encrypt(data=json.dumps(self.userinfo.get("authentication")))
        self.client.userinfo = self.userinfo
        self.client.connect_device = self.connect_device
        self.client.messageHandler = msgHandler
        self.client.closeCallback = closeCallback

        self.client.username_pw_set(username, password)
        self.client.on_connect = IotCallback.connect_callback
        self.client.on_disconnect = IotCallback.disconnect_callback
        self.client.on_subscribe = IotCallback.subscribe_callback
        self.client.on_message = IotCallback.on_message_callback
        self.client.on_publish = IotCallback.on_publish_callback
        self.client.tls_set()
        self.client.reconnect_delay_set(9999, 9999)
        try:
            if EndPointsSSL:
                self.client.connect(EndPointsSSL[0].get("host"), EndPointsSSL[0].get("port"), 60)
            elif EndPointsWSS:
                self.client.connect(EndPointsWSS[0].get("host"), EndPointsWSS[0].get("port"), 60)
            else:
                raise IotException(f"MQTT ??????????????? Endpoint??????: {sslEndPoints}")
        except Exception as err:
            raise IotException(
                f"connect failed: {EndPointsSSL[0].get('host')}:{EndPointsWSS[0].get('port')}, reason:{err}")
        self.client.loop_start()
        start = TimeUtil.now()
        while TimeUtil.now() - start < 2 * 60 * 1000:
            if self.client.status == MQTTClientStatus.CS_PAIR_YES:
                log.debug("IOT ?????????????????????????????????. ")
                return
            time.sleep(1)
        log.warning("IOT ????????????????????????????????????. ")
        raise IotException(
            f"connect timeout: {EndPointsSSL[0].get('host')}:{EndPointsWSS[0].get('port')}, timeout=60s. ??????????????????: {self.client.status}")

    def subscribe(self, *topics):
        if self.client:
            for topic in topics:
                self.client.subscribe(topic, 0)

    def disconnect(self):
        if self.client:
            self.client.disconnect()
            self.client.loop_stop()
            self.client = None
        else:
            log.warning(f"IOT ??????????????????????????????")

    def publish(self, topic: str, msg: dict, qos=0):
        if self.client:
            self.client.publish(topic, payload=json.dumps(msg).decode("utf-8"), qos=qos)
            log.debug(f"IOT ??????????????????: {msg}")

    def connect_device(self):
        try:
            m_HI = IotMsgBuilder.build_HI(self.client)
            log.debug(f'IOT ???????????? HI :{m_HI}')
            self.publish(self.defaultTopic, msg=m_HI, qos=1)
            m_request_connect = IotMsgBuilder.build_request_connect(self.client)
            log.debug(f'IOT ???????????? request_connect :{m_request_connect}')
            self.publish(self.defaultTopic, msg=m_request_connect, qos=1)
        except Exception as e:
            log.error(f'{self.clientId} IOT ???????????? ?????? clientId={self.clientId} e={e}')
            self.client.status = MQTTClientStatus.CS_PAIR_NO
        else:
            self.client.status = MQTTClientStatus.CS_PAIR_YES
