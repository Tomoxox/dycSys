# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models


class AliSMS:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
        access_key_id: str,
        access_key_secret: str,
    ) -> Dysmsapi20170525Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 您的AccessKey ID,
            access_key_id=access_key_id,
            # 您的AccessKey Secret,
            access_key_secret=access_key_secret
        )
        # 访问的域名
        config.endpoint = 'dysmsapi.aliyuncs.com'
        return Dysmsapi20170525Client(config)

    @staticmethod
    def sendCode(phone_numbers,code):
        client = AliSMS.create_client('LTAI5t8KZfnx1yiHwf2ktiZR', 'y0MjFEXShIzVdg4kdBOfxUZnR64M0n')
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers=str(phone_numbers),
            sign_name='创鼎科技',
            template_code='SMS_225394580',
            template_param="{'code':'"+ str(code)+"'}"
        )
        # 复制代码运行请自行打印 API 的返回值
        return client.send_sms(send_sms_request)
