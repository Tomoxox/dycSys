from browsermobproxy import Server
from seleniumwire import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import requests
import brotli
import json
from selenium.webdriver.common.proxy import Proxy, ProxyType

# server = Server('/Users/tomoxox/Desktop/DYCommentSys/browsermob-proxy-2.1.4/bin/browsermob-proxy')
# server.start()
# proxy = server.create_proxy()

option = webdriver.ChromeOptions()
# option.add_argument('--headless')
option.add_argument('--disable-gpu')  # 不需要GPU加速
option.add_argument('--no-sandbox')  # 无沙箱
option.add_argument('–disable-images')  # 禁用图像
option.add_experimental_option('useAutomationExtension', False)
option.add_argument("Sec-Ch-Ua-Platform=" + "'Windows'")
option.add_argument("disable-blink-features")
option.add_argument("disable-blink-features=AutomationControlled")
option.add_argument('user-agent=' + 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36')
# option.add_argument('--proxy-server={0}'.format(proxy.proxy))
res = requests.get(
    'http://api.tianqiip.com/getip?secret=3azei8uonu1y8246&type=json&num=1&time=3&yys=%E7%94%B5%E4%BF%A1&region=350000&ts=1&port=2').json()
if res['code'] == 1000:
    ip_port = f"{res['data'][0]['ip']}:{res['data'][0]['port']}"
    print(ip_port)
    print(res['expire'])
else:
    exit()
caps = webdriver.DesiredCapabilities.CHROME.copy()
# caps['goog:loggingPrefs'] = {'performance': 'INFO'}
caps['proxy'] = {
    'proxyType': 'MANUAL',
    'httpProxy': ip_port,
    'sslProxy': ip_port,
    'ftpProxy': ip_port
}
driver = webdriver.Chrome('/usr/local/bin/chromedriver', options=option, desired_capabilities=caps)

# proxy.new_har(options={
#         'captureContent': True,
#         'captureHeaders': True
#     })
driver.get('https://www.douyin.com/video/7013692017188343043')
# driver.get('https://httpbin.org/get?show_env=1')
arr = []
for request in driver.requests:
    if request.response:
        if 'https://www.douyin.com/aweme/v1/web/comment/list/' in request.url:
            if request.url not in arr:
                arr.append(request.url)
                print(
                    request.url,
                    request.response.status_code,
                    # request.response.headers,
                )
                data = brotli.decompress(request.response.body)
                data1 = data.decode('utf-8')
                print(data1)


# 设置页面加载和js加载超时时间，超时立即报错，如下设置超时时间为10秒
# browser.set_page_load_timeout(10)
# browser.set_script_timeout(10)
#
# # 设置动态代理ip端口，每次更换动态ip时修改httpProxy
# proxy = Proxy(
#     {
#         'proxyType': ProxyType.MANUAL,
#         'httpProxy': '125.123.71.7:26546'  # 代理ip和端口
#     }
# )
#
#
# desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
# proxy.add_to_capabilities(desired_capabilities)
#
# browser.start_session(desired_capabilities)
# browser.get("http://httpbin.org/ip")
#
# print(browser.page_source)
# browser.close()

# def process_browser_log_entry(entry):
#     response = json.loads(entry['message'])['message']
#     return response
#
# js="var q=document.documentElement.scrollTop=8000"
# driver.execute_script(js)
# time.sleep(10)
#
# browser_log = driver.get_log('performance')
# events = [process_browser_log_entry(entry) for entry in browser_log]
# events = [event for event in events if 'Network.response' in event['method']]
# print(1)
# print(events)
#
# result = proxy.har # 加载更多 就调用har获取（是否与之前重复）
# arr = []
# for entry in result['log']['entries']:
#     request = entry['request']
#     # 判断数据所在url并解析数据
#     if 'https://www.douyin.com/aweme/v1/web/comment/list/' in request['url']:
#         arr.append(request['url'])
# print(arr)
#
#
# server.stop()
# driver.close()


# -*- coding: utf-8 -*-
# @Time    : 2021/9/15 13:11
# @Author  : lx
# @IDE ：PyCharm

import os
import cv2
import requests
import numpy as np
from selenium import webdriver
from urllib.parse import urlparse
from selenium.webdriver import ActionChains

class Slide(object):

    def __init__(self, gap, bg, gap_size=None, bg_size=None, out=None):
        """
        :param bg: 带缺口的图片链接或者url
        :param gap: 缺口图片链接或者url
        """
        self.img_dir = os.path.join(os.getcwd(), 'img')
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)

        bg_resize = bg_size if bg_size else (340, 212)
        gap_size = gap_size if gap_size else (68, 68)
        self.bg = self.check_is_img_path(bg, 'bg', resize=bg_resize)
        self.gap = self.check_is_img_path(gap, 'gap', resize=gap_size)
        self.out = out if out else os.path.join(self.img_dir, 'out.jpg')

    @staticmethod
    def check_is_img_path(img, img_type, resize):
        if img.startswith('http'):
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;"
                          "q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,ja;q=0.6",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Host": urlparse(img).hostname,
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/91.0.4472.164 Safari/537.36",
            }
            img_res = requests.get(img, headers=headers)
            if img_res.status_code == 200:
                img_path = f'./img/{img_type}.jpg'
                image = np.asarray(bytearray(img_res.content), dtype="uint8")
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                if resize:
                    image = cv2.resize(image, dsize=resize)
                cv2.imwrite(img_path, image)
                return img_path
            else:
                raise Exception(f"保存{img_type}图片失败")
        else:
            return img

    @staticmethod
    def clear_white(img):
        """清除图片的空白区域，这里主要清除滑块的空白"""
        img = cv2.imread(img)
        rows, cols, channel = img.shape
        min_x = 255
        min_y = 255
        max_x = 0
        max_y = 0
        for x in range(1, rows):
            for y in range(1, cols):
                t = set(img[x, y])
                if len(t) >= 2:
                    if x <= min_x:
                        min_x = x
                    elif x >= max_x:
                        max_x = x

                    if y <= min_y:
                        min_y = y
                    elif y >= max_y:
                        max_y = y
        img1 = img[min_x:max_x, min_y: max_y]
        return img1

    def template_match(self, tpl, target):
        th, tw = tpl.shape[:2]
        result = cv2.matchTemplate(target, tpl, cv2.TM_CCOEFF_NORMED)
        # 寻找矩阵(一维数组当作向量,用Mat定义) 中最小值和最大值的位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        tl = max_loc
        br = (tl[0] + tw, tl[1] + th)
        # 绘制矩形边框，将匹配区域标注出来
        # target：目标图像
        # tl：矩形定点
        # br：矩形的宽高
        # (0,0,255)：矩形边框颜色
        # 1：矩形边框大小
        cv2.rectangle(target, tl, br, (0, 0, 255), 2)
        cv2.imwrite(self.out, target)
        return tl[0]

    @staticmethod
    def image_edge_detection(img):
        edges = cv2.Canny(img, 100, 200)
        return edges

    def discern(self):
        img1 = self.clear_white(self.gap)
        img1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
        slide = self.image_edge_detection(img1)

        back = cv2.imread(self.bg, 0)
        back = self.image_edge_detection(back)

        slide_pic = cv2.cvtColor(slide, cv2.COLOR_GRAY2RGB)
        back_pic = cv2.cvtColor(back, cv2.COLOR_GRAY2RGB)
        x = self.template_match(slide_pic, back_pic)
        # 输出横坐标, 即 滑块在图片上的位置
        return x

def get_tracks(distance, rate=0.6, t=0.2, v=0):
    tracks = []
    # 加速减速的临界值
    mid = rate * distance
    # 当前位移
    s = 0
    # 循环
    while s < distance:
        # 初始速度
        v0 = v
        if s < mid:
            a = 20
        else:
            a = -3
        # 计算当前t时间段走的距离
        s0 = v0 * t + 0.5 * a * t * t
        # 计算当前速度
        v = v0 + a * t
        # 四舍五入距离，因为像素没有小数
        tracks.append(round(s0))
        # 计算当前距离
        s += s0
    return tracks

def get_cookies():
    res = requests.get('http://api.tianqiip.com/getip?secret=3azei8uonu1y8246&type=json&num=1&time=3&yys=%E7%94%B5%E4%BF%A1&region=350000&ts=1&port=2').json()
    if res['code'] == 1000:
        ip_port = f"{res['data'][0]['ip']}:{res['data'][0]['port']}"
        print(ip_port)
    else:
        return

    check_url = 'https://www.douyin.com'
    driver_path=r'/usr/local/bin/chromedriver'
    option = webdriver.ChromeOptions()
    # option.add_argument('--headless')
    option.add_argument('--disable-gpu')  # 不需要GPU加速
    option.add_argument('--no-sandbox')   # 无沙箱
    option.add_experimental_option('useAutomationExtension', False)
    option.add_argument("disable-blink-features")
    option.add_argument("disable-blink-features=AutomationControlled")
    option.add_argument('--proxy-server=http://%s' % ip_port)
    driver = webdriver.Chrome(options=option,executable_path=driver_path)
    driver.get(check_url)
    import time
    time.sleep(12)

    FLAG = True
    try:
        driver.find_element_by_id('captcha-verify-image')
    except:
        FLAG = False
        print("没有滑块")

    while 1:
        if not FLAG:
            break
        try:
            p1 = driver.find_element_by_id('captcha-verify-image').get_attribute('src')
            p2 = driver.find_element_by_xpath('//*[@id="captcha_container"]/div/div[2]/img[2]').get_attribute('src')
            slide_app = Slide(gap=p2, bg=p1)
            distance = slide_app.discern()
            slider = driver.find_element_by_xpath('//*[@id="secsdk-captcha-drag-wrapper"]/div[2]')
            print("验证中...")
            ActionChains(driver).click_and_hold(slider).perform()
            _tracks = get_tracks(distance)
            new_1 = _tracks[-1] - (sum(_tracks) - distance)
            _tracks.pop()
            _tracks.append(new_1)
            print(_tracks)
            for mouse_x in _tracks:
                ActionChains(driver).move_by_offset(mouse_x, 0).perform()
            ActionChains(driver).release().perform()
            time.sleep(2)
        except:
            break


    cks = ''
    for ck in driver.get_cookies():
        k = ck['name']
        v = ck['value']
        cks +=f'{k}={v}; '
    cks = cks.replace(' =douyin.com; ',' ')
    # driver.close()
    # driver.quit()
    # return cks
    print(cks)

get_cookies()
