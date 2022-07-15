#!/usr/bin/env python
import orjson as json
import time
import requests
import logging


class Logger(object):
    logger = logging.getLogger("Logger")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    error_count = 0

    @classmethod
    def info(cls, message):
        if isinstance(message, dict):
            message = json.dumps(message)
        message = message.strip()
        cls.logger.info(message)

    @classmethod
    def error(cls, message):
        if isinstance(message, dict):
            message = json.dumps(message)
        message = message.strip()
        cls.logger.error(message)
        cls.error_count += 1

    @classmethod
    def debug(cls, message):
        if isinstance(message, dict):
            message = json.dumps(message)
        message = message.strip()
        cls.logger.debug(message)

    @classmethod
    def warning(cls, message):
        if isinstance(message, dict):
            message = json.dumps(message)
        message = message.strip()
        cls.logger.warning(message)

    @classmethod
    def set_debug_level(cls):
        cls.logger.setLevel(logging.DEBUG)

    @classmethod
    def set_info_level(cls):
        cls.logger.setLevel(logging.INFO)


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

    def partflush(self):
        # url = "http://localhost:8086/taas/enable-user/list/v2"
        # url = "http://taas.qa.fiture.com/taas/api/taas/enable-user/list/v2"
        url = "http://localhost:8086/taas/enable-user/flush"
        payload = dict(accountIds=["1499293952350687233"])
        start = time.time()
        self._push(url, payload)
        Logger.info(f"Cost: {time.time() - start}")

    def getSessions(self, accountCount=1, ignoreExpire=True):
        # url = "http://localhost:8086/taas/enable-user/list/v2"
        url = "http://taas.qa.fiture.com/taas/api/taas/enable-user/list/v2"
        payload = dict(accountCount=accountCount, ignoreExpire=ignoreExpire)
        start = time.time()
        resp = self._push(url, payload)
        Logger.info(f"Cost: {time.time() - start}")
        return resp.get("data")

    def createSessionsQueue(self):
        # url = "http://localhost:8086/taas/enable-user/list/v3"
        url = "http://taas.qa.fiture.com/taas/api/taas/enable-user/list/v3"
        payload = dict(name="locust", maxLimit=10000)
        start = time.time()
        resp = self._push(url, payload)
        return resp.get("data")

    def getUsers(self):
        url = "http://taas.qa.fiture.com/taas/api/taas/enable-user/list"
        payload = dict()
        start = time.time()
        resp = self._push(url, payload)
        Logger.info(f"Cost: {time.time() - start}")
        return resp.get("data")

    def forceUpdate(self):
        # url = "http://localhost:8086/taas/enable-user/list/v2"
        url = "http://taas.qa.fiture.com/taas/api/taas/enable-user/list/v2"
        payload = dict(accountCount=1, ignoreExpire=True, forceUpdate=True)
        start = time.time()
        resp = self._push(url, payload)
        Logger.info(f"Cost: {time.time() - start}")
        return resp.get("data")

    def checkSessions(self, ignoreExpire=False):
        sessions = self.getSessions(accountCount=100000, ignoreExpire=ignoreExpire)
        Logger.info(f"return : {len(sessions)} sessions")
        count = 0
        for s in sessions:
            Logger.info(
                f"phone: {s.get('phone')} taurus: {'OK' if 'taurus' in s else 'NOK'}, virgo: {'OK' if 'virgo' in s else 'NOK'}, expire: {s.get('expire')}")
            if not s:
                Logger.warning("empty seesion")
            elif "taurus" in s and "virgo" in s:
                count += 1
            elif "taurus" in s:
                Logger.warning(f"virgo session error: {s}")
            elif "virgo" in s:
                Logger.warning(f"taurus session error: {s}")
            else:
                Logger.warning(f"unkonw error: {s}")
        Logger.info(f"checked successful, available session: {count}")

    def _push(self, url, payload):
        Logger.debug(f"Request: POST {url}")
        Logger.debug(f"Request-body :{payload}")
        r = self.session.post(url, json=payload)
        Logger.debug(f"requests-headers: {r.request.headers}")
        Logger.debug(f"requests-body: {r.request.body}")
        try:
            resp = r.json()
        except Exception as err:
            Logger.error(f"error: {err}")
            Logger.error(r.text)
        return resp


if __name__ == "__main__":
    # sessions = TAAS().getSessions(accountCount=10000, ignoreExpire=False)
    # sessions = list(filter(lambda s: s.get("accountId") == "1427889425896157186", sessions))
    # print(sessions)
    # sessions = TAAS().forceUpdate()
    # print(sessions)
    sessions = TAAS().getSessions(accountCount=1, ignoreExpire=True)
    print(sessions)
    # resp = TAAS().createSessionsQueue()
    # print(resp)
    # print(len(sessions))
    # TAAS().forceUpdate()

    # users = TAAS().getUsers()
    # users = list(filter(lambda u: u.get("accountId") == "1427889425896157186", users))
    # print(users)
