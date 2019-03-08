#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Required
- PIL (必须)
- numpy (必须)
- pandas (必须)
- sklearn (必须)
Info
- author : "zhangli"
- email  : "2005.zl@163.com"
- date   : "2017.5.23"
Update
- name   : ""
- email  : ""
- date   : ""
'''

import os
import time
import random
import numpy as np
import pandas as pd

from PIL  import Image
from sklearn import svm
from sklearn.externals import joblib
from sklearn.svm import SVC
from sklearn.svm import LinearSVC

class ModelTrainer(object):

    def __init__(self, data_dir, model_dir, iteration=10, batch_size=500, training_set_proportion=0.8):

        self.data_dir = data_dir
        self.model_dir = model_dir
        self.iteration = iteration
        self.batch_size = batch_size
        self.training_set_proportion = training_set_proportion

    def run(self):

        print('begin load data.')
        start_time = time.time()
        self.load_data()
        end_time = time.time()
        print('load data done.')
        print('spend:', end_time - start_time, 'seconds.')
        
        print()
        
        print('begin split data.')
        self.split_data()
        print('split data done.')

        print()

        print('begin train model.')
        start_time = time.time()
        self.train()
        end_time = time.time()
        print('train model done.')
        print('spend:', end_time - start_time, 'seconds.')

        print()

        print('begin save model.')
        model_file, index_label_file = self.save_model()
        print('save model at: ', model_file, 'done.')
        print('save index_label at: ', index_label_file, 'done.')


    def save_model(self):

        seq = str(int(time.time()))
        model_file = os.path.join(self.model_dir, seq + '_model.bin')
        index_label_file = os.path.join(self.model_dir, seq + '_index_label.bin')
        
        joblib.dump(self.model, model_file)
        joblib.dump(self.index_label, index_label_file)
        
        return (model_file, index_label_file)

    def train(self):

        test_data, test_label = self.format_data(self.test_data)
        for epho in range(self.iteration):
            for batch_num, batch_data, batch_label in self.get_train_batch():
            
                self.model.fit(batch_data, batch_label)

                pred_label = pd.DataFrame([self.model.predict(test_data), test_label]).T
                pred_label.columns = ['pred', 'lab']

                correct = pred_label[pred_label['pred'] == pred_label['lab']]
                error = pred_label[pred_label['pred'] != pred_label['lab']]

                print('epho:', epho, ' batch:', (batch_num + 1) * self.batch_size, ' correct:', len(correct), ' error:', len(error), ' accuracy:', str((len(correct) / len(test_label)) * 100) + '%')

    def get_train_batch(self):

        batch_num = 0

        while batch_num * self.batch_size < len(self.train_data):

            batch = self.train_data[batch_num * self.batch_size : (batch_num + 1) * self.batch_size]

            batch_data, batch_label = self.format_data(batch)

            yield (batch_num, batch_data, batch_label)
            batch_num = batch_num + 1

    def format_data(self, batch):

        batch_data = []
        batch_labers = []

        for data in batch:
            batch_data.append(data[0 : -1])
            batch_labers.append(data[-1])

        return (np.array(batch_data), np.array(batch_labers))

    def split_data(self):

        self.train_data = []
        self.test_data = []

        for data in self.data:
            if random.random() < self.training_set_proportion:
                self.train_data.append(data)
            else:
                self.test_data.append(data)

    def load_image_data(self, normalization=255):

        self.labers, label_files = self.load_classify_files()

        self.index_label = dict(zip([i for i in range(len(self.labers))], self.labers))
        self.label_index = {v : k for k, v in self.index_label.items()}

        self.data = []

        for label, files in label_files.items():
            for file in files:
                image = Image.open(file)
                data_list = [pix // normalization for pix in image.getdata()]
                image.close()
                data_list.append(self.label_index[label])
                self.data.append(np.array(data_list, dtype='uint8'))
        
        random.shuffle(self.data)
    
    def load_classify_files(self):

        label_files = {}
        labers = []

        for dir in os.listdir(self.data_dir):
            label = int(dir)
            file_dir = os.path.join(self.data_dir, dir)
            files = [file_dir + '/' + file_name for file_name in os.listdir(file_dir)]
            label_files[label] = files
            labers.append(label)

        return (sorted(labers), label_files)


class SVMModelTrainer(ModelTrainer):

    def __init__(self, data_dir, model_dir, training_set_proportion=0.8):

        self.data_dir = data_dir
        self.model_dir = model_dir
        self.training_set_proportion = training_set_proportion
        self.model = svm.SVC()

    def train(self):

        train_data, train_label = self.format_data(self.train_data)
        test_data, test_label = self.format_data(self.test_data)
            
        self.model.fit(train_data, train_label)

        pred_label = pd.DataFrame([self.model.predict(test_data), test_label]).T
        pred_label.columns = ['pred', 'lab']

        correct = pred_label[pred_label['pred'] == pred_label['lab']]
        error = pred_label[pred_label['pred'] != pred_label['lab']]
        print(error)

        print('correct:', len(correct), ' error:', len(error), ' accuracy:', str((len(correct) / len(test_label)) * 100) + '%')

    def load_data(self):
        self.load_image_data()

class LinearSVCModelTrainer(ModelTrainer):

    def __init__(self, data_dir, model_dir, training_set_proportion=0.8):
        self.data_dir = data_dir
        self.model_dir = model_dir
        self.training_set_proportion = training_set_proportion
        self.model = LinearSVC()

    def train(self):
        train_data, train_label = self.format_data(self.train_data)
        test_data, test_label = self.format_data(self.test_data)

        self.model.fit(train_data, train_label)

        pred_label = pd.DataFrame([self.model.predict(test_data), test_label]).T
        pred_label.columns = ['pred', 'lab']

        correct = pred_label[pred_label['pred'] == pred_label['lab']]
        error = pred_label[pred_label['pred'] != pred_label['lab']]
        print(error)

        print('correct:', len(correct), ' error:', len(error), ' accuracy:',
                  str((len(correct) / len(test_label)) * 100) + '%')

    def load_data(self):
        self.load_image_data()

if __name__ == '__main__':

    data_dir = 'C:\\workspace\\python\\captcha\\image\\mc\\train\\'
    model_dir = 'C:\\workspace\\python\\captcha\\model\\mc\\'

    trainer = SVMModelTrainer(data_dir, model_dir)
    trainer.run()

#if __name__ == '__main__':
#
#    data_dir = 'C:\\workspace\\python\\captcha2\\image\\dap\\train\\'
#    model_dir = 'C:\\workspace\\python\\captcha2\\model\\dap\\'
#
#    trainer = LinearSVCModelTrainer(data_dir, model_dir)
#    trainer.run()
