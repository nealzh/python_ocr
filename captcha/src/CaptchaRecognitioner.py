#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Required
- numpy (必须)
- sklearn (必须)
Info
- author : "zhangli"
- email  : "2005.zl@163.com"
- date   : "2017.5.24"
Update
- name   : ""
- email  : ""
- date   : ""
'''

import numpy as np

from sklearn.externals import joblib

class CaptchaRecognitioner(object):

    def image_vector(self, images, normalization=255):

        vectors = []
        for image in images:
            vectors.append(np.array([pix // normalization for pix in image.getdata()]))
        return np.array(vectors)

class SVMCaptchaRecognitioner(CaptchaRecognitioner):

    def __init__(self, model_file_dir, index_label_file_dir):
        self.model_file_dir = model_file_dir
        self.index_label_file_dir = index_label_file_dir

        self.model = joblib.load(self.model_file_dir)
        self.index_label = joblib.load(self.index_label_file_dir)

    def predict(self, images, ascii=False):

        vectors = self.image_vector(images)
        if ascii:
            return [self.index_label[index] for index in self.model.predict(vectors)]
        else:
            return [chr(self.index_label[index]) for index in self.model.predict(vectors)]
