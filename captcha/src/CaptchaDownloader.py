#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Required
- requests (必须)
- pillow (可选)
Info
- author : "zhangli"
- email  : "2005.zl@163.com"
- date   : "2017.2.7"
Update
- name   : ""
- email  : ""
- date   : ""
'''

import io
import os
import time
import requests
from PIL import Image
try:
    import cookielib
except:
    import http.cookiejar as cookielib

class CaptchaDownloader(object):

    host = ''
    referer = ''
    image_dir = './'
    urlgenerator = lambda:''
    sleep = 1

    def __init__(self):
        
        # 构造 Request headers
        self.headers = {
            'Host': self.host,
            'Referer': self.referer,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, sdch, br',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Upgrade-Insecure-Requests':'1'
        }
        
        # 使用cookie信息
        self.session = requests.session()
        self.session.cookies = cookielib.LWPCookieJar(filename='cookies')

    # 下载验证码
    def get_captcha(self, url):
        
        response = self.session.get(url, headers=self.headers)
        stream = io.BytesIO(response.content)
        image = Image.open(stream)
        
        return image

    #保存验证码
    def save_captcha(self, image, name):
        try:
            if not os.path.exists(self.image_dir):
                os.mkdir(self.image_dir)
            image.save(self.image_dir + name + '.png')
        except Exception as e:
            print(e)
        finally:
            image.close()

    def download(self, image_num=1):
        images = []
        for i in range(image_num):
            try:
                (name, url) = self.urlgenerator()
                image = self.get_captcha(url)
                images.append(image.copy())
                self.save_captcha(image, name)
                print('第', i, '个图片', name, ' 已下载。')
                if image_num > 1:
                    time.sleep(self.sleep)
            except Exception as e:
                print(e)
                print('will sleep 30 seconds.')
                time.sleep(30)
        return images
    
class NTSMSCaptchaDownloader(CaptchaDownloader):
    
    def __init__(self, image_dir='..//image//ntsms//source//'):
        self.host = 'bigdata.palmyou.com'
        self.referer = 'http://bigdata.palmyou.com/ntsms/'
        self.image_dir = image_dir
        self.urlgenerator = lambda: (str(int(time.time() * 1000)), 'http://bigdata.palmyou.com/ntsms/captcha.jsp?d=' + str(int(time.time() * 1000)))
        super().__init__()

#mobile communication
class MCCaptchaDownloader(CaptchaDownloader):
    def __init__(self, image_dir='..//image//mc//source//'):
        self.host = 'ha.10086.cn'
        self.referer = 'http://ha.10086.cn/adc/euap/doLogin.action'
        self.image_dir = image_dir
        self.urlgenerator = lambda: (str(int(time.time() * 1000)), 'http://ha.10086.cn/adc/confirmCodeServlet')
        super().__init__()

#Dispatch Administration platform
class DispatchAdminPlatformCaptchaDownloader(CaptchaDownloader):
    def __init__(self, image_dir='..//image//dap//source//'):
        self.host = '112.33.0.176:4480'
        self.referer = 'http://112.33.0.176:4480/station/logoutAction_logout.action'
        self.image_dir = image_dir
        self.urlgenerator = lambda: (str(int(time.time() * 1000)), 'http://112.33.0.176:4480/station/logoutAction_image.action?k=0.11705784971009048')
        super().__init__()

#douban
import json
class DouBanCaptchaDownloader(CaptchaDownloader):
    def __init__(self, image_dir='..//image//douban//source//'):
        self.host = 'www.douban.com'
        self.referer = 'https://www.douban.com/'
        self.image_dir = image_dir
        self.sleep = 3
        super().__init__()

    def urlgenerator(self):
        resp = self.session.get('https://www.douban.com/j/misc/captcha')
        arg_dict = json.loads(resp.text)
        return (str(int(time.time() * 1000)), 'https:' + arg_dict['url'])

class HRNSCaptchaDownloader(CaptchaDownloader):
    def __init__(self, image_dir='..//image//hrns//source//'):
        self.host = 'sc.hrnewspaper.com'
        self.referer = 'view-source:http://sc.hrnewspaper.com/show.asp?id=122'
        self.image_dir = image_dir
        self.sleep = 1
        self.urlgenerator = lambda: (str(int(time.time() * 1000)), 'http://sc.hrnewspaper.com/checkcode_add.asp')
        super().__init__()

if __name__ == '__main__':

    downloader = NTSMSCaptchaDownloader()
#    downloader = MCCaptchaDownloader()
#    downloader = DouBanCaptchaDownloader()
#    downloader = DispatchAdminPlatformCaptchaDownloader()
#    downloader.download(image_num=3000)
#    downloader = HRNSCaptchaDownloader()
    downloader.download(image_num=300)

