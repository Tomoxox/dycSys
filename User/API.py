import requests
import execjs
import os
import redis
import time

_proxyUrl = 'http://api.tianqiip.com/getip?secret=3azei8uonu1y8246&type=json&num=1&time=5&ts=1&port=2'
# _proxyUrl = 'http://api.tianqiip.com/getip?secret=3azei8uonu1y8246&type=json&num=1&time=10&port=2'


def dy_sign(method,kw=None,page=1):
    red = redis.Redis(host='localhost', port=6379, decode_responses=True)
    cookie = red.get('cookie')
    # print(cookie)
    current_work_dir = os.path.dirname(__file__)
    js_path = os.path.join(current_work_dir, 'signature.js')
    with open(js_path,'r',encoding='utf-8') as f:
        b = f.read()
    c = execjs.compile(b)
    d = c.call(method,kw,page)
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.douyin.com/",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "cookie":cookie
    }
    e = requests.get(d, headers=headers)
    try:
        data = e.json()
        return data
    except:
        cookie = get_cookies()
        red.set('cookie',cookie)
        dy_sign(method,kw,page)


def scrawl(method,taskId,kw=None,page=1):
    cookie_task = 'cookie'+str(taskId)
    red = redis.Redis(host='localhost', port=6379, decode_responses=True)
    cookie = red.get(cookie_task)
    if not cookie:
        cookie = get_cookies()
        red.set(cookie_task, cookie)

    # print(cookie)
    current_work_dir = os.path.dirname(__file__)
    js_path = os.path.join(current_work_dir, 'signature.js')
    with open(js_path,'r',encoding='utf-8') as f:
        b = f.read()
    c = execjs.compile(b)
    d = c.call(method,kw,page)
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
        "Referer": "https://www.douyin.com/",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "cookie":cookie
    }

    proxy = getProxy(taskId)
    if not proxy:
        return
    proxies = {
        "http": "http://%(proxy)s/" % {'proxy': proxy},
        "https": "http://%(proxy)s/" % {'proxy': proxy}
    }
    e = requests.get(d, headers=headers,proxies=proxies)
    try:
        data = e.json()
        return data
    except:
        cookie = get_cookies()
        red.set(cookie_task,cookie)
        scrawl(method,taskId,kw,page)


def getProxy(taskId):
    ip_task = 'ip_task' + str(taskId)
    expire_task = 'expire_task' + str(taskId)
    red = redis.Redis(host='localhost', port=6379, decode_responses=True)
    ip = red.get(ip_task)
    if not ip:
        ip,exp = req()
        red.set(ip_task,ip)
        red.set(expire_task,exp)
    else:
        # 是否失效
        now = time.time()
        exp = time.strptime(red.get(expire_task), '%Y-%m-%d %H:%M:%S')
        exp = int(time.mktime(exp))

        if now >= exp:
            ip, exp = req()
            red.set(ip_task, ip)
            red.set(expire_task, exp)

    return ip

def req():
    res = requests.get(_proxyUrl).json()
    if res['code'] == 1000:
        ip_port = f"{res['data'][0]['ip']}:{res['data'][0]['port']}"
        return ip_port, res['data'][0]['expire']
    else:
        return

# if __name__ == '__main__':
    # 首页推荐视频
    # print(dy_sign(method='feed'))
    # 搜索视频
    # print(dy_sign(method='search_video',kw='哈哈哈'))
    # 搜索达人
    # print(dy_sign(method='search_expert',kw='鼻炎'))
    # 搜索推荐词
    # print(dy_sign(method='search_sug',kw='鼻炎'))
    # 评论
    # print(dy_sign(method='comment',kw='6989198974582263070'))
    # 作品
    # print(dy_sign(method='aweme_post',kw='MS4wLjABAAAAIWFmTfNJmRajbViR_rK6iGgQMIq0lAWdFmQ5z6iU9Vd4uo9KXOgcJE0o5Dn0JAmW'))
    # TODO 其他的自行补充吧
    ...


# import os
import cv2
# import requests
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
    """
    将distance分割成小段的距离
    :param distance: 总距离
    :param rate: 加速减速的临界比例
    :param a1: 加速度
    :param a2: 减速度
    :param t: 单位时间
    :param t: 初始速度
    :return: 小段的距离集合
    """
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
    check_url = 'https://www.douyin.com'
    driver_path=r'/usr/local/bin/chromedriver'
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    option.add_argument('--disable-gpu')  # 不需要GPU加速
    option.add_argument('--no-sandbox')   # 无沙箱
    option.add_experimental_option('useAutomationExtension', False)
    option.add_argument("disable-blink-features")
    option.add_argument("disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=option,executable_path=driver_path)
    driver.get(check_url)
    import time
    time.sleep(2)
    try:
        p1 = driver.find_element_by_id('captcha-verify-image').get_attribute('src')
        p2 = driver.find_element_by_xpath('//*[@id="captcha_container"]/div/div[2]/img[2]').get_attribute('src')
        slide_app = Slide(gap=p2,bg=p1)
        distance = slide_app.discern()

        while 1:
            try:
                slider = driver.find_element_by_xpath('//*[@id="secsdk-captcha-drag-wrapper"]/div[2]')
                print("验证中...")
                ActionChains(driver).click_and_hold(slider).perform()
                _tracks = get_tracks(distance)
                new_1 = _tracks[-1]-(sum(_tracks) - distance)
                _tracks.pop()
                _tracks.append(new_1)
                print(_tracks)
                for mouse_x in _tracks:
                    ActionChains(driver).move_by_offset(mouse_x,0).perform()
                ActionChains(driver).release().perform()
                time.sleep(2)
            except:
                break

    except:
        ...

    cks = ''
    for ck in driver.get_cookies():
        k = ck['name']
        v = ck['value']
        cks +=f'{k}={v}; '
    cks = cks.replace(' =douyin.com; ',' ')
    driver.close()
    driver.quit()
    # print(cks)
    return cks