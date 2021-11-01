# User/consumers.py
import json
from channels.generic.websocket import WebsocketConsumer
from .browser import Browser


class SearchConsumer(WebsocketConsumer):
    browserArr = {}

    def connect(self):
        self.user = self.scope["user"]
        self.request_url = self.scope['path']
        self.accept()

    def disconnect(self, close_code):
        # browser = self.browserArr[self.scope['session']['user']]
        # browser.quit()
        self.close()

    def receive(self, text_data):
        json_data = json.loads(text_data)
        browser = self.browserArr.get(self.scope['session']['customer']['id'])
        if not browser:
            new_brow = Browser()
            if new_brow.driver:
                self.browserArr[self.scope['session']['customer']['id']] = new_brow
                browser = new_brow
            else:
                self.send(text_data=json.dumps({'code':0,'msg':'请稍后重试'}))
                return

        print(self.browserArr)

        print(json_data)
        data = {}
        if json_data.get('scene') in ['hot_words','hot_videos','hot_experts']:
            data = browser.search(json_data['scene'],json_data['keyword'])
        elif json_data.get('scene') in ['commentPage','userPage']:
            print(f'--------------------------consumer {json_data["id"]}----------------------------')
            data = browser.haveALook(json_data['scene'],json_data['id'],json_data.get('page',1))

        self.send(text_data=json.dumps(data))

