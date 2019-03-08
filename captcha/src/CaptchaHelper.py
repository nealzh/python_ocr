#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Required
- CaptchaHandler (必须)
- CaptchaRecognitioner (必须)
Info
- author : "zhangli"
- email  : "2005.zl@163.com"
- date   : "2017.5.24"
Update
- name   : ""
- email  : ""
- date   : ""
'''
from CaptchaHandler import *
from CaptchaRecognitioner import *

def captcha_init(captcha_config):
    
    captcha_config_str = eval(captcha_config)

    captcha_config_obj = {}
    
    for captcha_type, (handler, recog, model_dir, model_index_label_dir) in captcha_config_str.items():
        captcha_config_obj[captcha_type] = (eval(handler + '()'), eval(recog + '("' + model_dir + '","' + model_index_label_dir + '")'))

    return captcha_config_obj
        
