# coding=utf-8
import orjson as json
import queue
import random
import re
import time
import uuid
import requests
from libs.exception import IotException
from libs.exception import AccountInvalidException, ResponseException
from libs.iot.client import MqttClient
from libs.iot.msgBuilder import IotMsgBuilder
from libs.logger import log
from libs.timeUtil import TimeUtil
from libs.eventReport import EventReport
from libs.myRedis import getRedisSession, RedisDbIndexEnum


def singleton(cls, *args, **kwargs):
    instances = dict()

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return _singleton


@singleton
class BackendLogin(object):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.username = "chenjian"
        self.password = "P@ssw0rd!"
        self._token = ""

    def getToken(self):
        if not self._token:
            self._token = self._login()
        return self._token

    def _login(self):
        url = "http://keycloak.dev.fiture.com/auth/realms/fiture/protocol/openid-connect/token"
        payload = dict(username=self.username, password=self.password, client_id="cms", grant_type="password")
        s = requests.session()
        r = s.post(url=url, data=payload, verify=False, timeout=5)
        resp = r.json()
        access_token = resp['access_token']
        return f'Bearer {access_token}'


def getBackendSession():
    session = requests.session()
    session.headers.update(dict(Authorization=BackendLogin().getToken()))
    return session


@singleton
class TAAS(object):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.session = getBackendSession()
        self.grayAccounts = ["1447865512723996673",
                             "1243119293250707458",
                             "1397480131638046721",
                             "1243104244116553729",
                             "1224525651508146177",
                             "1411936740961939457",
                             "1411257674067865602",
                             "1327072609363685378",
                             "1334113618671251458",
                             "1313668713202364417",
                             "1439115865343909889",
                             "1206767025362608129",
                             "1411198900615507969",
                             "1395640047130431489",
                             "1392742857907163137",
                             "1423116463548641281",
                             "1410519905569861633",
                             "1415857359415521282",
                             "1411878843762601985",
                             "1395955227823493122",
                             "1411877276221173761",
                             "1410489836629651458",
                             "1330770978313846785",
                             "1407649427795972097",
                             "1410218893687885826",
                             "1396729582006358018",
                             "1402638793416691714",
                             "1230076189637734401",
                             "1374339964333617153",
                             "1410440690484088833",
                             "1313668713202364417",
                             "1403190247651069954",
                             "1334481902075547649",
                             "1403298475894427649",
                             "1280072188809256961",
                             "1402951710288695297",
                             "1402929410478755841",
                             "1402927422076669953",
                             "1402917034471772161",
                             "1331556444902506497",
                             "1402884490535686145",
                             "1402875711345709057",
                             "1377905680479809538",
                             "1402573153875730434",
                             "1402577502387511298",
                             "1248156870148816898",
                             "1354742845300695042",
                             "1354671204144148481",
                             "1318488730106396674",
                             "1319530678011490305",
                             "1300679637602197505",
                             "138",
                             "1328898405194964994",
                             "1348834479333486593",
                             "1",
                             "1331152262781452290",
                             "1331556444902506497",
                             "1328670771427586049",
                             "1317005302800973825",
                             "1280848579145363458",
                             "1334113618671251458",
                             "1338322222190071809",
                             "1336952671036674050",
                             "1328668822774919169",
                             "1275258980293918721",
                             "40",
                             "1265207318087921666",
                             "20",
                             "1331152262781452290",
                             "1243114045580812290",
                             "1266031400582561794",
                             "1265828727348719618",
                             "1270301122437095426",
                             "1270610553179774977",
                             "1265836350630457346",
                             "211",
                             "1219169005911093250",
                             "22",
                             "1286208082419703809",
                             "1237987738169679873",
                             "40",
                             "1275734031803858945",
                             "1300724611521765377",
                             "1300726665145278466",
                             "1300740772963606529",
                             "195",
                             "1300985846028886017",
                             "1301047799388626946",
                             "1301048523531018241",
                             "1281203500193542145",
                             "1301053878537347074",
                             "1301060896073506818",
                             "1269839274393063426",
                             "58",
                             "1300410589958168577",
                             "1269888493829083138",
                             "1280848579145363458",
                             "1310155998537646082",
                             "1248172654447230978",
                             "1310512446861934593",
                             "1310515587263168514",
                             "1305341567435522050",
                             "1269895518852075522",
                             "1269839274393063426",
                             "1308976284259254274",
                             "1310551722619822081",
                             "1310770524593258498",
                             "1280410157692821506",
                             "1243110323387670530",
                             "1265888331862294530",
                             "19",
                             "1310867003362181121",
                             "1309020129000882177",
                             "1310839743080554498",
                             "1310891283131072513",
                             "1310892613081956354",
                             "65",
                             "1290837909502431234",
                             "1311151344139042817",
                             "1295202896880394241",
                             "1297806114051383298",
                             "1275775375191355394",
                             "1326437793990877185",
                             "1316259989840408578",
                             "1310468440325029890",
                             "22",
                             "1327125117938606081",
                             "1328885996724809729",
                             "1323894607412510721",
                             "1268036287650258946",
                             "1328985884249989122",
                             "1326411519880511489",
                             "65",
                             "1331501692822994945",
                             "1332202065263050754",
                             "1333620618595528705",
                             "1336192421903896577",
                             "1336552690630955009",
                             "1338330849986646017",
                             "1338331606597144578",
                             "1308325726389207042",
                             "1338415146177302530",
                             "1338671634888167425",
                             "1339820710887329794",
                             "1326423348384276481",
                             "1329256951306711042",
                             "1329328176648404993",
                             "1321649614828134402",
                             "1244886536752701442",
                             "211",
                             "1327220767155265538",
                             "1340519433174945793",
                             "1342369308950573057",
                             "1343446429949145089",
                             "1343483313714802689",
                             "1343510405559005185",
                             "1338424316721008641",
                             "1344114476003401730",
                             "1344119399545872385",
                             "1347488757791109121",
                             "1306065826629414913",
                             "1228157438303117313",
                             "1328982361265315841",
                             "1329338837965193218",
                             "1347062293357436930",
                             "1349552916070445058",
                             "1348958862286319618",
                             "1362595078516137985",
                             "1358721755348623362",
                             "1349557002798936066",
                             "1",
                             "1364390639112183809",
                             "1364391407588368385",
                             "1338757022109569026",
                             "1368870148050538498",
                             "1366650642258878466",
                             "2",
                             "1369602052529868802",
                             "1369121440006164481",
                             "1369476368352432130",
                             "1257215180855496706",
                             "1374268293870415873",
                             "1311244470263996418",
                             "1369122395888046081",
                             "1300996626468102145",
                             "1334113618671251458",
                             "1328670771427586049",
                             "1197351338557546497",
                             "65",
                             "1374697651823079426",
                             "1371659089820536834",
                             "1384044881264115713",
                             "1377897856345436161",
                             "1379317331523579906",
                             "1384040346852392962",
                             "1384023570806603778",
                             "1384389136633430018",
                             "1314082729301159938",
                             "1332271968498204673",
                             "1384404322614378497",
                             "1384440680078770177",
                             "1339408540907245570",
                             "1369936179552604162",
                             "1395698008095772673",
                             "15",
                             "1394563630393249794",
                             "1395706453582729218",
                             "1331556444902506497",
                             "1331152262781452290",
                             "1390220370772733953",
                             "1395698008095772673",
                             "1338682168584867841",
                             "1338379384002088962",
                             "1397071516587118593",
                             "1402519341769105410",
                             "1340148629882966017",
                             "1399639622952153090",
                             "1383992129282322433",
                             "1319933934961356801",
                             "1319959863167217666",
                             "1401098007073538050",
                             "1374262627499929602",
                             "3",
                             "1349233472978350082",
                             "0000",
                             "1407969549777604609",
                             "1411877940980609026",
                             "1417040135254683650",
                             "1418458873833172993",
                             "1427185937566380033",
                             "1432182009040166914",
                             "1394930817700253697",
                             "1432565763466289154",
                             "1432565806545985537",
                             "1419477783571312642",
                             "1418465925850705922",
                             "1435540142392086529",
                             "1337301673435369474",
                             "1437617384179621890",
                             "1438084895526346754",
                             "1435877043535876097",
                             "1351050379848044546",
                             "1328982361265315841",
                             "1328982447001083905",
                             "1425641017298890753",
                             "1453189925550841857",
                             "1422115002576515074",
                             "1461598160789172225",
                             "1479285891308703745",
                             "1455010249451921410",
                             "1447526086697279489",
                             "1410778802763329538",
                             "1339824427569156097",
                             "1482989004284211202",
                             "1507234248295067649",
                             "1419492694305255425",
                             "1441318348543746049"
                             ]

    def make_user_queue(self, name="locust"):
        # url = "http://localhost:8086/taas/enable-user/list/v3"
        url = "http://taas.qa.fiture.com/taas/api/taas/enable-user/list/v3"
        payload = dict(name=name, maxLimit=10000)
        data = self._push_once(url, payload)
        return data

    def get_user(self, name="locust", ignoreGrayAccount=False):
        start = TimeUtil.now()
        redisCli = getRedisSession(redisDbIndex=RedisDbIndexEnum.local)
        while True:
            s = redisCli.lpop(name)
            session = json.loads(s)
            accountId = session.get("accountId").strip()
            if ignoreGrayAccount and (accountId in self.grayAccounts):
                log.warning(f"??????????????????: {accountId}")
                continue
            session['virgo']['appClient']['deviceSN'] = uuid.uuid4().hex[:12]
            session['taurus']['appClient']['deviceSN'] = uuid.uuid4().hex[:12]
            data = {
                "authentication": dict(accountId=str(accountId),
                                       sessionId=str(session['taurus']['id']),
                                       sessionToken=str(session['taurus']['token'])),
                "virgo_headers": session['virgo']['appClient'],
                "taurus_headers": session['taurus']['appClient'],
                "expire": session.get("expire"),
                "phone": session.get("phone"),
                "accountId": str(accountId)
            }
            log.debug(f"???Redis????????????????????????: {TimeUtil.now() - start} ms")
            return data

    def get_user_info(self, accountCount, ignoreGrayAccount=False):
        # url = "http://localhost:8086/taas/enable-user/list/v2"
        url = "http://taas.qa.fiture.com/taas/api/taas/enable-user/list/v2"
        payload = dict(accountCount=int(accountCount * 1.2), forceUpdate=False, ignoreExpire=True)
        start = time.time()
        data = self._push(url, payload)[::-1]
        random.shuffle(data)
        q = queue.Queue()
        availableCount = 0
        for i in data:
            if ignoreGrayAccount and (i.get("accountId").strip() in self.grayAccounts):
                continue
            i['virgo']['appClient']['deviceSN'] = uuid.uuid4().hex[:12]
            i['taurus']['appClient']['deviceSN'] = uuid.uuid4().hex[:12]
            data = {
                "authentication": dict(accountId=str(i['taurus']['accountId']),
                                       sessionId=str(i['taurus']['id']),
                                       sessionToken=str(i['taurus']['token'])),
                "virgo_headers": i['virgo']['appClient'],
                "taurus_headers": i['taurus']['appClient'],
                "expire": i.get("expire"),
                "phone": i.get("phone"),
                "accountId": str(i['taurus']['accountId'])
            }
            q.put(data)
            availableCount += 1

        if availableCount >= accountCount:
            log.info(f"??????????????????: {availableCount}???")
        else:
            log.warning(f"??????????????????: {availableCount}/{accountCount}???")
        log.info(f"Cost: {time.time() - start}")

        return q

    def _push_once(self, url, payload):
        try:
            r = self.session.post(url, json=payload, timeout=300)
            resp = r.json()
            return resp.get("data")
        except Exception as err:
            log.error(f"????????????Queue??????: {err}")

    def _push(self, url, payload):
        sleepTimes = [2, 3, 5, 8, 13, 21, 34]
        for s in sleepTimes:
            try:
                r = self.session.post(url, json=payload, timeout=300)
                resp = r.json()
                log.debug(f"response-body: {json.dumps(resp)}")
            except Exception as err:
                time.sleep(s)
                log.error(f"POST??????????????????: {err}")
            else:
                data = resp.get("data")
                if isinstance(data, list) and data:
                    return data
                else:
                    time.sleep(s)

        log.warning(f"??????????????????: {r.text}")

    def _get_content_info(self, data):
        info_list = []
        for i in data['data']:
            for d in i['result_detail']:
                if 'contentId' in d['message'] and 'courseId' in d['message']:
                    result = d['message']
                    contentId = [int(i) for i in re.findall(".*'contentId': (.*), 'name'.*", result)]
                    courseId = [int(i) for i in re.findall(".*'courseId': (.*), 'contentId'.*", result)]
                    get_info = {
                        'courseId': courseId[0],
                        "contentId": contentId[0]
                    }
                    info_list.append(get_info)
        info_list = sorted(info_list, key=lambda keys: keys['courseId'])
        log.debug(f'??????content???{info_list}')
        log.info(f'???????????????content???{info_list[-1]}')
        return info_list[-1]

    def create_live(self):
        """
        ???????????????
        :return:
        :rtype:
        """
        # url = 'http://taas.qa.fiture.com/taas/api/task/batch-exec'
        url = 'http://10.1.20.103:8086/task/batch-exec'
        payload = [
            {
                "create_time": TimeUtil.current_time(),
                "create_user": "?????????",
                "description": "????????????334",
                "id": 446,
                "is_delete": 0,
                "name": "????????????334",
                "update_time": TimeUtil.current_time(),
                "update_user": "?????????"
            }
        ]
        log.debug(f"Request: {payload}")
        r = self.session.post(url, json=payload, timeout=300)
        try:
            resp = r.json()
            log.debug(f"response-body: {json.dumps(resp)}")
            if resp['code'] == 200:
                return True
        except Exception as err:
            log.error(f"error: {err}")
            log.error(r.text)
            resp = None
        return resp

    def get_live_content(self):
        """
        ????????????????????????contentId
        :return:
        :rtype:
        """
        # url = 'http://taas.qa.fiture.com/taas/api/task/record/list'
        url = 'http://10.1.20.103:8086/task/record/list'
        payload = {
            "create_time": TimeUtil.current_time(),
            "create_user": "?????????",
            "description": "????????????334",
            "id": 446,
            "is_delete": 0,
            "name": "????????????334",
            "update_time": TimeUtil.current_time(),
            "update_user": "?????????",
            "execNum": None
        }
        log.debug(f"Request: {payload}")
        r = self.session.post(url, json=payload, timeout=300)
        try:
            resp = r.json()
            if resp['code'] != 200:
                raise ResponseException(resp)
            info = self._get_content_info(resp)
            log.debug(f"response-body: {json.dumps(resp)}")
            return info
        except Exception as err:
            log.error(f"error: {err}")
            log.error(r.text)
            resp = None
        return resp

    def return_content_info(self):
        for d in range(10):
            time.sleep(5)
            contentInfo = self.get_live_content()
            if contentInfo:
                log.debug(f'????????? contentInfo???{contentInfo}')
                return contentInfo
            else:
                time.sleep(2)


class LocustPublic:
    timeout = 30
    isGray = False

    # ipAndAccountId = False

    @staticmethod
    def post(client, url, headers, payload, desc):
        if LocustPublic.isGray:
            headers.update(dict(_GRAY_REQUEST="true"))
        else:
            headers.update(dict(_GRAY_REQUEST="false"))
        # if LocustPublic.ipAndAccountId:
        #     headers.update(dict(_GRAY_REQUEST="true"))
        # headers.update(dict(_http_SESSION_OBJECT=json.dumps({"accountId": 1447865512723996673})))
        with client.post(url, headers=headers, json=payload,
                         catch_response=True,
                         timeout=LocustPublic.timeout,
                         name=url + desc) as response:
            try:
                result = response.json()
                errorCode = result.get('errorCode')
                errorMsg = result.get("errorMsg")
                status = result.get("status")
                if status != "SUCCESS":
                    response.failure(errorMsg)
                    if errorCode.startswith("SSO_") or "??????" in errorMsg:
                        raise AccountInvalidException(response)
                    else:
                        raise ResponseException(response)
                else:
                    log.info(f'{desc}???????????????')
            except Exception as msgs:
                response.failure(f'{desc}??????????????????{msgs}, Response-Code:{response.status_code}: body: ({response.text})')
                if "SSO_" in response.text or "?????????" in response.text:
                    raise AccountInvalidException(response)
                else:
                    raise ResponseException(response)
            else:
                return result

    @staticmethod
    def taurus_headers(client, session):
        return {
            "_APP_CLIENT_OBJECT": json.dumps(client).decode("utf-8"),
            "_SESSION_OBJECT": json.dumps(session).decode("utf-8")
        }

    @staticmethod
    def virgo_headers(client, session=None):
        headers = {"_APP_CLIENT_OBJECT": json.dumps(client).decode("utf-8")}
        if session:
            headers.update({"_SESSION_OBJECT": json.dumps(session).decode("utf-8")})
        return headers


class LocustMqttPublit(object):
    def __init__(self):
        super(LocustMqttPublit, self).__init__()

    @classmethod
    def _establishOnssl(cls, client, userinfo):
        desc = "(virgo establish on ssl)"
        # url = "http://stable.up-iot-device.nt.qa.fiture.com/machine/establish-ssl"
        url = "http://stable-up-machine-nt.qa.fiture.com/machine/establish-ssl"
        # ?????????up-machine????????????????????????dms?????????SN????????????????????????????????????????????????????????????
        virgo_headers = LocustPublic.virgo_headers(userinfo['virgo_headers'])
        payload = dict(businessType="SLIM", businessId=userinfo['virgo_headers'].get("deviceSN"),
                       refresh=False, protocolVersion=1)
        resp = LocustPublic.post(client, url, virgo_headers, payload, desc)
        return resp.get("content")

    @classmethod
    def getClientConnected(cls, httpClient, userinfo: dict, msgHandler=None, closeCallback=None, extTopics=[]):
        mqttConfig = cls._establishOnssl(httpClient, userinfo)
        mqttClient = MqttClient(mqttConfig, userinfo)
        mqttClient.subscribeTopic(*extTopics)
        startTimeStamp = TimeUtil.now()
        try:
            mqttClient.connect(msgHandler=msgHandler, closeCallback=closeCallback)
        except IotException as err:
            endTimeStamp = TimeUtil.now()
            EventReport.failure(request_type="MQTT",
                                name="Connected",
                                response_time=endTimeStamp - startTimeStamp,
                                response_length=0,
                                exception=err)
            raise IotException(f"{err}")
        else:
            endTimeStamp = TimeUtil.now()
            EventReport.success(request_type="MQTT",
                                name="Connected",
                                response_time=endTimeStamp - startTimeStamp,
                                response_length=0)
            return mqttClient

    @staticmethod
    def sendHeartbeat(mqttClient):
        startTimeStamp = TimeUtil.now()
        hbMsg = IotMsgBuilder.build_HB(mqttClient)
        mqttClient.publish(mqttClient.defaultTopic, hbMsg, qos=1)
        endTimeStamp = TimeUtil.now()
        EventReport.success(request_type="MQTT",
                            name="Heartbeat",
                            response_time=endTimeStamp - startTimeStamp,
                            response_length=len(json.dumps(hbMsg)))

    @staticmethod
    def sendRoundRealtimeScore(mqttClient, ext: dict):
        startTimeStamp = TimeUtil.now()
        scoreMsg = IotMsgBuilder.build_RTS(mqttClient, ext=ext)
        mqttClient.publish(ext.get("topic"), scoreMsg, qos=0)
        endTimeStamp = TimeUtil.now()
        EventReport.success(request_type="MQTT",
                            name="RoundScore",
                            response_time=endTimeStamp - startTimeStamp,
                            response_length=len(json.dumps(scoreMsg)))

    @staticmethod
    def sendBonesData(mqttClient, ext: dict):
        startTimeStamp = TimeUtil.now()
        bonesMsg = IotMsgBuilder.build_Bones(mqttClient, ext=ext)
        mqttClient.publish(ext.get("topic"), bonesMsg, qos=0)
        endTimeStamp = TimeUtil.now()
        EventReport.success(request_type="MQTT",
                            name="Bones",
                            response_time=endTimeStamp - startTimeStamp,
                            response_length=len(json.dumps(bonesMsg)))

    @staticmethod
    def sendBonesDataV2(mqttClient, ext: dict):
        startTimeStamp = TimeUtil.now()
        bonesMsg = IotMsgBuilder.build_Bones_v2(mqttClient, ext=ext)
        mqttClient.publish(ext.get("topic"), bonesMsg, qos=0)
        endTimeStamp = TimeUtil.now()
        EventReport.success(request_type="MQTT",
                            name="BonesV2",
                            response_time=endTimeStamp - startTimeStamp,
                            response_length=len(json.dumps(bonesMsg)))


class Serialization(object):
    def __init__(self):
        super(self.__class__, self).__init__()

    @staticmethod
    def queue(data: list):
        q = queue.Queue()
        for o in data:
            q.put(o)
        return q


if __name__ == "__main__":
    # print(TAAS().return_content_info())
    # print(NACOS.get_config())
    TAAS().make_user_queue()
    print(TAAS().get_user())
