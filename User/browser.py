from seleniumwire import webdriver
from .useragent import randomUA
import requests
import execjs
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from utils.browserTools import Slide, get_tracks
from selenium.webdriver import ActionChains
import brotli
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import urllib.parse


class Browser:
    # _proxyUrl = 'http://api.tianqiip.com/getip?secret=3azei8uonu1y8246&type=json&num=1&time=3&yys=%E7%94%B5%E4%BF%A1&region=350000&ts=1&port=2'
    _proxyUrl = 'http://api.tianqiip.com/getip?secret=3azei8uonu1y8246&type=json&num=1&time=5&ts=1&port=2'
    _input_search_xpath = "//header/div[2]/div[1]/div[1]/div[2]/div[1]/form[1]/input[1]"  # 搜索页
    _input_hot_xpath = "//header/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/form[1]/input[1]"  # hot页
    _select_video_xpath = "//body/div[@id='root']/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/span[1]"
    _select_expert_xpath = "//body/div[@id='root']/div[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/span[2]"
    _header_xpath = "//head"


    _single_video = "https://www.douyin.com/video/"
    _user_page = "https://www.douyin.com/user/"

    _video_url = "v26-web.douyinvod.com"

    _request_urls = {
        'hot_words': 'https://www.douyin.com/aweme/v1/web/search/sug/',
        'hot_trending_list': 'https://www.douyin.com/aweme/v1/web/hot/search/list/',
        'hot_videos': 'https://www.douyin.com/aweme/v1/web/search/item/',
        'hot_experts': 'https://www.douyin.com/aweme/v1/web/discover/search/',
        'commentPage': 'https://www.douyin.com/aweme/v1/web/comment/list/',
        # 'userPage': 'https://www.douyin.com/aweme/v1/web/comment/list/',
    }

    # 实时搜索有四个窗口： hot search video user
    def __init__(self, user_agent=''):
        if user_agent == '':
            user_agent = randomUA()
        print(user_agent)
        option = webdriver.ChromeOptions()
        # option.add_argument('--headless')
        # No_Image_loading = {"profile.managed_default_content_settings.images": 2}
        # option.add_experimental_option("prefs", No_Image_loading)
        option.add_argument('--disable-gpu')  # 不需要GPU加速
        option.add_argument('--no-sandbox')  # 无沙箱
        option.add_argument('–disable-images')  # 禁用图像
        option.add_experimental_option('useAutomationExtension', False)
        option.add_argument(f'--host-resolver-rules=MAP {self._video_url} 127.0.0.1')
        option.add_argument("Sec-Ch-Ua-Platform=" + "'Windows'")
        option.add_argument("disable-blink-features")
        option.add_argument("disable-blink-features=AutomationControlled")
        option.add_argument('user-agent=' + user_agent)
        res = requests.get(self._proxyUrl).json()
        if res['code'] == 1000:
            ip_port = f"{res['data'][0]['ip']}:{res['data'][0]['port']}"
            print(ip_port)
            print(res['data'][0]['expire'])
            self.proxyExpireTime = res['data'][0]['expire']
            self.ip_port = ip_port
            options = {
                'proxy': {
                    'http': 'http://' + ip_port,
                    'https': 'https://' + ip_port,
                    'no_proxy': 'localhost,127.0.0.1'
                }
            }
            driver = webdriver.Chrome('/usr/local/bin/chromedriver', options=option, seleniumwire_options=options)
            self.driver = driver
            self.original_window = driver.current_window_handle
            self.window_handle_arr = {
                'hot': driver.current_window_handle,
            }
            self.driver.get('https://www.douyin.com/hot')
        else:
            print('NO PROXY!!!')

    def __del__(self):
        self.driver.close()

    def search(self, operation, keyword):
        print(f'--------------------------{operation}----------------------------')
        if self.checkProxy():
            # self.driver.get('https://httpbin.org/get?show_env=1')
            self.trySlide()
            self.tryCloseDYAccount()
            # 输入关键词
            waittingSec = 2
            if operation == 'hot_words':
                self.tryEnter(keyword)
                # 等待网络请求
                time.sleep(waittingSec)
            else:
                # 当前窗口是否有搜索页面
                if self.window_handle_arr.get('search'):
                    self.switchToWindow('search')
                    self.tryEnter(keyword + Keys.ENTER)
                # 否则回车搜索 窗口为2
                else:
                    self.switchToWindow('hot')
                    self.tryEnter(keyword + Keys.ENTER)
                    wait = WebDriverWait(self.driver, 10)
                    wait.until(EC.number_of_windows_to_be(len(self.window_handle_arr.values()) + 1))  # 前期窗口数+1
                    # 切换窗口
                    self.switchToNewWindow()
                    self.addNewWindow('search')

                try:
                    if operation == 'hot_videos':
                        videoSpan = self.driver.find_element_by_xpath(self._select_video_xpath)
                        videoSpan.click()
                    if operation == 'hot_experts':
                        expertSpan = self.driver.find_element_by_xpath(self._select_expert_xpath)
                        expertSpan.click()
                    self.driver.wait_for_request(self._request_urls.get(operation))
                except:
                    return {
                        'code': 0,
                        'msg': '服务器访问量大，请重试',
                    }
            self.trySlide()

            data = self.requestFilter(operation)
            return {
                'code': 1,
                'msg': '获取成功',
                'scene': operation,
                'data': data
            }
        else:
            return {
                'code': 0,
                'msg': '服务器访问量大，请重试',
            }

    def haveALook(self, operation, id, page=1):
        print(f'--------------------------{operation}----------------------------')

        print('self.window_handle_arr')
        print(self.window_handle_arr)

        if self.checkProxy():
            self.trySlide()
            is_new_page = False
            window = 'video'
            if operation == 'userPage':
                window = 'user'
            # 是否已存在页面
            if self.window_handle_arr.get(window):
                # 是  切换窗口，打开链接
                self.switchToWindow(window)

            else:
                # 否  切到热门，随便点击一个视频，改url，切换窗口，增加窗口
                self.switchToWindow('hot')
                self.trySlide()
                self.tryCloseDYAccount()

                try:
                    self.tryEnter('哈哈' + Keys.ENTER)
                    # WebDriverWait(self.driver, 2).until(
                    #     EC.number_of_windows_to_be(len(self.window_handle_arr.values()) + 1))  # 前期窗口数+1
                    # 设置一下加载时间，2秒就停止加载
                    # 新地址再设置回来
                    # 切换窗口
                    self.switchToNewWindow()
                    self.driver.execute_script('window.stop ? window.stop() : document.execCommand("Stop");')
                    is_new_page = True

                except Exception as e:
                    print(e.__str__())
                    return {
                        'code': 0,
                        'msg': '系统访问量大，请稍后重试',
                        'scene': operation,
                    }

            if operation == 'commentPage':
                if is_new_page:
                    self.addNewWindow('video')

                print('self.window_handle_arr')
                print(self.window_handle_arr)

                if page == 1:
                    self.driver.get(self._single_video + str(id))
                    print('-------------new window---------------')
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, self._header_xpath)))

                        data = self.driver.find_element_by_id('RENDER_DATA').get_attribute('innerHTML')
                        data = urllib.parse.unquote(data)
                        return {
                            'code': 1,
                            'msg': '获取成功',
                            'scene': operation,
                            'data': data,
                        }
                    except Exception as e:
                        print(e.__str__())
                        return {
                            'code': 0,
                            'msg': '服务器访问量大，请重试',
                        }
                else:
                    self.driver.execute_script('window.stop ? window.stop() : document.execCommand("Stop");')
                    js = f"var q=document.documentElement.scrollTop={page * 5000}"
                    self.driver.execute_script(js)
                    print('-------------scrollTop---------------')

            if operation == 'userPage':
                if is_new_page:
                    self.addNewWindow('user')

                print('self.window_handle_arr')
                print(self.window_handle_arr)

                if page == 1:
                    self.driver.get(self._user_page + str(id))
                    print('-------------new window---------------')
                try:
                    # header里面有个 RENDER_DATA 的script 有数据
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, self._header_xpath)))

                    data = self.driver.find_element_by_id('RENDER_DATA').get_attribute('innerHTML')
                    data = urllib.parse.unquote(data)
                    return {
                        'code': 1,
                        'msg': '获取成功',
                        'scene': operation,
                        'data': data,
                    }

                except Exception as e:
                    print(e.__str__())
                    return {
                        'code': 0,
                        'msg': '服务器访问量大，请重试',
                    }

            self.driver.wait_for_request(self._request_urls.get(operation))

            self.trySlide()

            data = self.requestFilter(operation)
            return {
                'code': 1,
                'msg': '获取成功',
                'scene': operation,
                'data': data
            }
        else:
            return {
                'code': 0,
                'msg': '服务器访问量大，请重试',
            }


    #
    # ------------------------------------------------------------------------------------------
    #

    def checkProxy(self):
        now = time.time()
        exp = time.strptime(self.proxyExpireTime, '%Y-%m-%d %H:%M:%S')
        exp = int(time.mktime(exp))
        # print('--------exp-------' + str(exp))
        # print('--------now-------' + str(now))
        if now >= exp:
            res = requests.get(self._proxyUrl).json()
            if res['code'] == 1000:
                ip_port = f"{res['data'][0]['ip']}:{res['data'][0]['port']}"
                self.proxyExpireTime = res['data'][0]['expire']
                self.ip_port = ip_port
                options = {
                    'https': 'https://' + ip_port,
                    'no_proxy': 'localhost,127.0.0.1'
                }
                self.driver.proxy = options
                return True
            else:
                return
        return True

    def tryEnter(self, keyword):
        try:
            self.enterKeyword(keyword)
            return True
        except Exception as e:
            print('输入关键词error')
            print(e.__str__())
            return False

    def trySlide(self):
        try:
            self.slide()
            return True
        except Exception as e:
            print('滑动后输入关键词error')
            print(e.__str__())
            return False

    def slide(self):
        p1 = self.driver.find_element_by_id('captcha-verify-image').get_attribute('src')
        p2 = self.driver.find_element_by_xpath(
            '//*[@id="captcha_container"]/div/div[2]/img[2]').get_attribute('src')
        slide_app = Slide(gap=p2, bg=p1)
        distance = slide_app.discern()
        slider = self.driver.find_element_by_xpath('//*[@id="secsdk-captcha-drag-wrapper"]/div[2]')
        print("验证中...")
        ActionChains(self.driver).click_and_hold(slider).perform()
        _tracks = get_tracks(distance)
        new_1 = _tracks[-1] - (sum(_tracks) - distance)
        _tracks.pop()
        _tracks.append(new_1)
        print(_tracks)
        for mouse_x in _tracks:
            ActionChains(self.driver).move_by_offset(mouse_x, 0).perform()
        ActionChains(self.driver).release().perform()
        time.sleep(2)

    def tryCloseDYAccount(self):
        try:
            # 登录窗口 dy-account-close
            dyAccountClose = self.driver.find_element_by_class_name('dy-account-close')
            dyAccountClose.click()
            return True
        except Exception as e:
            print(e.__str__())
            return False

    #
    # ------------------------------------------------------------------------------------------
    #

    def enterKeyword(self, kw):
        inputPath = self._input_hot_xpath if self.driver.current_window_handle == self.original_window else self._input_search_xpath
        searchInput = self.driver.find_element_by_xpath(inputPath)
        searchInput.send_keys(Keys.CONTROL, 'a')
        searchInput.send_keys(Keys.CONTROL, 'a')
        searchInput.send_keys(Keys.CONTROL, 'a')
        self.driver.execute_script("arguments[0].value = '';", searchInput)
        searchInput.send_keys(kw)

    def requestFilter(self, operation):
        data = ''
        for request in self.driver.requests:
            if request.response:
                if self._request_urls.get(operation) in request.url:
                    print('-----------------dataRes-----------------')
                    if len(request.response.body):
                        dataRes = brotli.decompress(request.response.body)
                        data = dataRes.decode('utf-8')
                        if operation != 'hot_words':
                            break
        self.driver.backend.storage.clear_requests()
        return data

    #
    # ------------------------------------------------------------------------------------------
    #

    def switchToNewWindow(self):
        for window_handle in self.driver.window_handles:
            if not window_handle in self.window_handle_arr.values():
                self.driver.switch_to.window(window_handle)
                break

    def addNewWindow(self, key):
        self.window_handle_arr[key] = self.driver.current_window_handle

    def switchToWindow(self, key):
        self.driver.switch_to.window(self.window_handle_arr[key])
