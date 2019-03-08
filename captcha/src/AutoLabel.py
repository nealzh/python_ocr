#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Required
- pillow (必须)
Info
- author : "zhangli"
- email  : "2005.zl@163.com"
- date   : "2017.5.24"
Update
- name   : ""
- email  : ""
- date   : ""
'''

import os
import nanotime

from PIL import Image as PILImage
from CaptchaHandler import NTSMSCaptchaHandler
from CaptchaDownloader import NTSMSCaptchaDownloader
from CaptchaHandler import MCCaptchaHandler
from CaptchaDownloader import MCCaptchaDownloader
from CaptchaRecognitioner import SVMCaptchaRecognitioner

class AutoLabel(object):

    def download_image(self):
        images = self.downloader.download()
        while len(images) < 1:
            images = self.downloader.download()
        return images[0]

    def save_image(self, image, binary_sub_images, char_code):

        seq = str(int(nanotime.now()))

        image_name = self.named_dir + '_'.join([str(ord(char)) for char in char_code]) + '.' + seq + '.png'
        image.save(image_name)

        for i in range(len(char_code)):
            train_dir = self.label_dir + str(ord(char_code[i])) + '//'
            if(not os.path.exists(train_dir)):
                os.makedirs(train_dir)
            binary_sub_images[i].save(train_dir + seq + '.png')

class NTSMSAutoLabel(AutoLabel):

    def __init__(self, named_dir, label_dir, downloader, handler, recognitioner):
        self.named_dir = named_dir
        self.label_dir = label_dir
        self.downloader = downloader
        self.handler = handler
        self.recognitioner = recognitioner

    def label(self, label_num=10000):

        for num in range(label_num):
            image = self.download_image()
            binary_sub_images = self.handler.handle(image)

            while len(binary_sub_images) < 1:
                image = self.download_image()
                binary_sub_images = self.handler.handle(image)

            labelies = self.recognitioner.predict(binary_sub_images)

            self.save_image(image, binary_sub_images, labelies)

            image.close()
            for binary_image in binary_sub_images:
                binary_image.close()
            print('第', num + 1, '个图片已打标。')


class MCAutoLabel(AutoLabel):

    def __init__(self, named_dir, label_dir, downloader, handler, recognitioner):
        self.named_dir = named_dir
        self.label_dir = label_dir
        self.downloader = downloader
        self.handler = handler
        self.recognitioner = recognitioner

    def label(self, label_num=10000):

        for num in range(label_num):
            image = self.download_image()
            binary_sub_images = self.handler.handle(image)

            while len(binary_sub_images) < 1:
                image = self.download_image()
                binary_sub_images = self.handler.handle(image)

            labelies = self.recognitioner.predict(binary_sub_images)

            self.save_image(image, binary_sub_images, labelies)

            image.close()
            for binary_image in binary_sub_images:
                binary_image.close()
            print('第', num + 1, '个图片已打标。')


if __name__ == '__main__':

    #source_dir = '..//image//ntsms//source//'
    #named_dir = '..//image//ntsms//name//'
    #label_dir = '..//image//ntsms//train//'
    #model_dir = '..//model//ntsms//1495605689_model.bin'
    #index_label_dir = '..//model//ntsms//1495605689_index_label.bin'

    source_dir = '..//image//mc//source//'
    named_dir = '..//image//mc//name//'
    label_dir = '..//image//mc//train//'
    model_dir = '..//model//mc//1514462292_model.bin'
    index_label_dir = '..//model//mc//1514462292_index_label.bin'

    #downloader = NTSMSCaptchaDownloader(image_dir=source_dir)
    #handler = NTSMSCaptchaHandler()

    downloader = MCCaptchaDownloader(image_dir=source_dir)
    handler = MCCaptchaHandler()
    recognitioner = SVMCaptchaRecognitioner(model_dir, index_label_dir)

    if (not os.path.exists(source_dir)):
        os.makedirs(source_dir)
    if (not os.path.exists(named_dir)):
        os.makedirs(named_dir)
    if (not os.path.exists(label_dir)):
        os.makedirs(label_dir)

    auto_label = MCAutoLabel(named_dir, label_dir, downloader, handler, recognitioner)
    auto_label.label()
