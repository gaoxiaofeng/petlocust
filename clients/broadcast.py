import os
import random

from libs.public import LocustPublic

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)


class BroadcastClient(object):
    def __init__(self):
        super(BroadcastClient, self).__init__()
        self.timeout = 5 * 60
        LocustPublic.isGray = False

    def live_barrage_audit(self, client, userinfo):
        desc = '(直播弹幕审核接口)'
        taurus_headers = LocustPublic.taurus_headers(userinfo['taurus_headers'], userinfo['authentication'])
        payload = {"bizCode": "cp-training-interact", "bizType": "live-barrage-audit",
                   "serialId": 1540000000000000000 + random.randint(1, 8888888888),
                   "operator": userinfo['accountId'], "content": "山中相送罢，日暮掩柴扉。",
                   "extraData": {"contentId": userinfo['contentUniqueId']}}
        url = 'http://stable-up-nachi-nt.qa.fiture.com/sync-audit'
        LocustPublic.post(client, url, taurus_headers, payload, desc)

    def carnival_barrage_audit(self, client, userinfo):
        desc = '(嘉年华弹幕审核接口)'
        taurus_headers = LocustPublic.taurus_headers(userinfo['taurus_headers'], userinfo['authentication'])
        payload = {"bizCode": "cp-training-interact", "bizType": "stadium-barrage-audit",
                   "serialId": 1540000000000000000 + random.randint(1, 8888888888),
                   "operator": userinfo['accountId'], "content": "晚来天欲雪，能饮一杯无？",
                   "extraData": {"contentId": userinfo['contentUniqueId']}}
        url = 'http://stable-up-nachi-nt.qa.fiture.com/sync-audit'
        LocustPublic.post(client, url, taurus_headers, payload, desc)

    def custom_barrage(self, client, userinfo):
        desc = '(自定义弹幕)'
        taurus_headers = LocustPublic.taurus_headers(userinfo['taurus_headers'], userinfo['authentication'])
        payload = {"barrageLabel": "ugc_word", "contentId": userinfo['contentUniqueId'], "barrageText": "我是性能测试自定义弹幕",
                   "barrageType": "ugc_word"}
        url = 'http://stable-cp-recording-bff-nt.qa.fiture.com/taurus/barrage/send'
        LocustPublic.post(client, url, taurus_headers, payload, desc)

    def quick_barrage(self, client, userinfo):
        desc = '(快捷弹幕)'
        taurus_headers = LocustPublic.taurus_headers(userinfo['taurus_headers'], userinfo['authentication'])
        payload = {"barrageLabel": "preset_word", "contentId": userinfo['contentUniqueId'],
                   "barrageText": "老师太赞，每周必来！哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈哈",
                   "barrageType": "preset_word"}
        url = 'http://stable-cp-recording-bff-nt.qa.fiture.com/taurus/barrage/send'
        LocustPublic.post(client, url, taurus_headers, payload, desc)

    def like_barrage(self, client, userinfo):
        desc = '(直播点赞)'
        taurus_headers = LocustPublic.taurus_headers(userinfo['taurus_headers'], userinfo['authentication'])
        payload = {"contentId": userinfo['contentUniqueId'], "accountId": userinfo['accountId'],
                   "receiveAccountId": 1337301673435369474,
                   "barrageType": "mutual", "barrageLabel": "upvote"}
        url = 'http://stable-cp-recording-bff-nt.qa.fiture.com/taurus/barrage/send'
        LocustPublic.post(client, url, taurus_headers, payload, desc)

    def bullet_barrage(self, client, userinfo):
        desc = '(直播体式弹幕)'
        taurus_headers = LocustPublic.taurus_headers(userinfo['taurus_headers'], userinfo['authentication'])
        payload = {"bodyBarrage":{"label":"body_namaste","text":"这节课很棒，谢谢【书瑶】"}, "contentId": userinfo['contentUniqueId']}
        url = 'http://stable-cp-content-nt.qa.fiture.com/virgo/training/live/barrage/send'
        LocustPublic.post(client, url, taurus_headers, payload, desc)

    # def follow(self, client, userinfo):
    #     desc = '(关注)'
    #     taurus_headers = LocustPublic.taurus_headers(userinfo['taurus_headers'], userinfo['authentication'])
    #     payload = {"event": "FOLLOW", "followId": 1337301673435369474}
    #     url = 'http://stable-up-aldebaran-nt.qa.fiture.com/follow/submit'
    #     LocustPublic.post(client, url, taurus_headers, payload, desc)


if __name__ == "__main__":
    BroadcastClient().live_barrage_audit(None, dict(virgo_headers=None, authentication=None))
