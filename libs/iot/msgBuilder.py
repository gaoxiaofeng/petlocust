import hashlib
import orjson as json
import time
import uuid
from paho.mqtt.client import Client, MQTTMessage
from libs.iot.fitureEnum import IotMsgTypeEnum, BusinessTypeEnum, IotAppTypeEnum
from libs.logger import log
from libs.timeUtil import TimeUtil


class IotMsgBuilder:
    def __init__(self):
        pass

    @staticmethod
    def build_tpl():
        return {
            "v": None,
            "sessionId": None,
            "msgType": None,
            "msgId": None,
            "destType": None,
            "destId": None,
            "ack": None,
            "ts": None,
            "tag": None,
            "payload": None,
            "destApp": None,
            "srcApp": None,
            "ext": None,
            "sign": None,
        }

    @staticmethod
    def wrap_sign(m, secret):
        sign_plain = ''
        sign_plain += str(m["v"]) if m["v"] is not None else ""
        sign_plain += str(m["sessionId"]) if m["sessionId"] is not None else ""
        sign_plain += str(m["msgType"]) if m["msgType"] is not None else ""
        sign_plain += str(m["msgId"]) if m["msgId"] is not None else ""
        sign_plain += str(m["destType"]) if m["destType"] is not None else ""
        sign_plain += str(m["destId"]) if m["destId"] is not None else ""
        sign_plain += str(m["tag"]) if m["tag"] is not None else ""
        sign_plain += str(m["payload"]) if m["payload"] is not None else ""
        sign_plain += str(m["ack"]) if m["ack"] is not None else ""
        sign_plain += str(m["ts"]) if m["ts"] is not None else ""
        sign_plain += str(m["srcApp"]) if m["srcApp"] is not None else ""
        sign_plain += str(m["destApp"]) if m["destApp"] is not None else ""
        sign_plain += str(m["ext"]) if m["ext"] is not None else ""
        sign_plain += secret
        sign = hashlib.md5(sign_plain.encode(encoding='UTF-8')).hexdigest()
        m['sign'] = sign
        return m

    @staticmethod
    def build_HB(client: Client):
        try:
            m = IotMsgBuilder.build_tpl()
            m["v"] = 2
            m["sessionId"] = client.cfg["sessionId"]
            m["msgType"] = IotMsgTypeEnum.HB.value
            m["ts"] = str(int(round(time.time() * 1000)))
            m = IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
            return m
        except Exception as e:
            log.error(f'创建心跳消息异常 clientId={client.clientId} e={e}')
            raise Exception('创建心跳消息异常')

    @staticmethod
    def build_HI(client: Client):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.HI.value
        m['msgId'] = str(uuid.uuid4())
        m['destType'] = BusinessTypeEnum.SESSION.value
        m['destId'] = client.cfg.get("sessionId")
        m['tag'] = 'INIT'
        m['ack'] = 1
        m['ts'] = int(round(time.time() * 1000))
        m['srcApp'] = IotAppTypeEnum.taurus.value
        m['destApp'] = IotAppTypeEnum.virgo.value
        m['ext'] = None
        m['payload'] = None
        IotMsgBuilder.wrap_sign(m, client.cfg.get("secret"))
        return m

    @staticmethod
    def build_request_connect(client: Client):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 1
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.MSG.value
        m['msgId'] = str(uuid.uuid4())
        m['destType'] = BusinessTypeEnum.SESSION.value
        m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'MSG'
        m['ack'] = 1
        m['ts'] = int(round(time.time() * 1000))
        content = {
            "env": "qa",
            "appKey": "qEaLKIrIIgabW9znqnXIvaWopI6BVbm2",
            "token": client.token,
            "weight": "65.0",
            "height": 170.00,
            "userName": "Locust测试",
            "avatarUrl": "http://dev-oss1.fiture.com/avatarUrl/b5ab248c87774cf6b90d7e3dd9e64417.jpg",
            "accountId": client.userinfo.get("authentication").get("accountId"),
            "age": 31,
            "gender": 0,
            "forceConnect": True,
            "connectType": "manual",
            "versionCode": "30200",
            "versionName": "3.2.0",
            "client": "taurus_android"
        }
        payload = {"ac": "request_connect", "content": content, "number": 1}
        m['payload'] = json.dumps(payload).decode("utf-8")
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m

    @staticmethod
    def build_RTS(client: Client, ext: dict):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.EVENT.value
        m['msgId'] = str(uuid.uuid4())
        # m['destType'] = BusinessTypeEnum.SESSION.value
        # m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'STADIUM'
        m['srcApp'] = ".virgo"
        m['ack'] = 0
        m['ts'] = TimeUtil.now()
        content = dict(
            accountId=str(ext.get("accountId")),
            calories=ext.get("calories"),
            currentTimestamp=TimeUtil.now(),
            duration=ext.get("duration"),
            effectiveDuration=ext.get("effectiveDuration"),
            playDuration=ext.get("playDuration"),
            roomId=ext.get("roomId"),
            score=ext.get("score"),
            trainingRecordId=str(ext.get("trainingRecordId")),
            unit="score",
            verseId=str(ext.get("verseId")),
            wearHrmEffectiveDuration=0
        )
        payload = dict(tag="VERSE_REALTIME", version=1379, content=content)
        m['payload'] = json.dumps(payload).decode("utf-8")
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m

    @staticmethod
    def build_Bones(client: Client, ext: dict):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.EVENT.value
        m['msgId'] = str(uuid.uuid4())
        # m['destType'] = BusinessTypeEnum.SESSION.value
        # m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'STADIUM'
        m['srcApp'] = ".virgo"
        m['ack'] = 0
        m['ts'] = TimeUtil.now()
        content = dict(
            accountId=str(ext.get("accountId")),
            contentId=ext.get("contentId"),
            bonesData=ext.get("bonesData"),
            currentTimestamp=TimeUtil.now(),
        )
        payload = dict(tag="STAGE_REPORT_SKELETON", version=1430, content=content)
        m['payload'] = json.dumps(payload).decode("utf-8")
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m

    @staticmethod
    def build_Bones_v2(client: Client, ext: dict):
        m = IotMsgBuilder.build_tpl()
        m['v'] = 2
        m['sessionId'] = client.cfg.get("sessionId")
        m['msgType'] = IotMsgTypeEnum.EVENT.value
        m['msgId'] = str(uuid.uuid4())
        # m['destType'] = BusinessTypeEnum.SESSION.value
        # m['destId'] = client.cfg["sessionId"]
        m['tag'] = 'STADIUM'
        m['srcApp'] = ".virgo"
        m['ack'] = 0
        m['ts'] = TimeUtil.now()
        content = dict(
            accountId=str(ext.get("accountId")),
            contentId=ext.get("contentId"),
            bonesData=ext.get("bonesData"),
            currentTimestamp=TimeUtil.now(),
        )
        payload = dict(tag="STAGE_REPORT_SKELETON_V2", version=1430, content=content)
        m['payload'] = json.dumps(payload).decode("utf-8")
        IotMsgBuilder.wrap_sign(m, client.cfg["secret"])
        return m
