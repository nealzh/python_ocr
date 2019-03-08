#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Required
- tkinter (必须)
- pillow (必须)
Info
- author : "zhangli"
- email  : "2005.zl@163.com"
- date   : "2017.2.7"
Update
- name   : "zhangli"
- email  : "2005.zl@163.com"
- date   : "2017.5.8"
'''

import os
import io
import sys
import time
import random
import shutil
import CaptchaHandler
#import tkinter

import numpy as np

from PIL import Image as PILImage
from PIL import ImageTk

from tkinter import font
from tkinter import ttk
from tkinter.messagebox import *
from tkinter.filedialog import *

import xlrd
import xlwt
from xlutils.copy import copy as xlcopy

#from sklearn import svm
#from sklearn.externals import joblib

class CaptchaWindow(Tk):
    
    def __init__(self, source, target, train, model, length):
        
        super().__init__()
        
        self.source = source
        self.target = target
        self.train = train
        self.model = model
        self.model_file = model + '/model'
        self.length = length
        self.captcha_files = []
        self.logs = []

        fileNames = os.listdir(self.source)

        for fileName in fileNames:
            filePath = os.path.join(self.source, fileName)
            if(os.path.isfile(filePath)):
                self.captcha_files.append((fileName.split('.')[0], filePath))

        self.title("Graph Train")
        self.geometry("600x400")
        self.resizable(width=False, height=False)

        ims, tkImage = self.get_image()

        self.source_label = Label(self, image=tkImage)
        self.source_label.grid(row = 0, column=0, columnspan=4, sticky=E+W)

        self.ims_lable = []
        self.columnconfigure(2, minsize = 30)
        for i in range(length):
            label = Label(self, image=ims[i])
            #label.grid(row = 2 + i, sticky=N)
            label.grid(row=2, column=i)
            self.ims_lable.append(label)
        
        self.entry_text = Variable()
        self.entry_text.set('')
        self.entry = Entry(self, textvariable=self.entry_text)
        self.entry.bind('<Key-Return>', self.enter_next)
        self.entry.grid(row = 4, column=0, columnspan=4)

        self.label_info = Label(self, text='提示：\n      1.在输入框中输入验证码字符。\n      2.验证码字符必须区分大小写。\n      3.输入字符数量必须是4个。\n      4.输入完成后按回车键切换下一张验证码图案。', fg='red', justify='left')
        self.label_info.grid(row = 6, column=0, columnspan=4)

        self.label_blank_1 = Label(self)
        self.label_blank_2 = Label(self)
        self.label_blank_3 = Label(self)

        self.label_blank_1.grid(row = 1, column=0, columnspan=4)
        self.label_blank_2.grid(row = 3, column=0, columnspan=4)
        self.label_blank_3.grid(row = 5, column=0, columnspan=4)

        self.protocol("WM_DELETE_WINDOW", self.close)

        #model_predict = self.predict([np.array(b_s_i.getdata()) for b_s_i in self.binary_sub_images])
        #self.entry_text.set(str([chr(num) for num in model_predict]))
        
        #if os.path.exists(self.model_file):
        #    self.svc_model = joblib.load(self.model_file)
        #else:
        #    self.svc_model = svm.SVC()
        #    self.train_model_from_image(self.train, 10000)
            
        self.mainloop()

    def enter_next(self, event):

        ascii_code = [ord(char) for char in self.entry_text.get()]
        if len(ascii_code) != 4:
            return
        chars = [char for char in self.entry_text.get()]
        log = [self.file_name]
        log.extend(chars)
        log.extend(ascii_code)
        self.logs.append(log)

        self.move_file(ascii_code)
        
        #self.train_model([np.array(b_s_i.getdata()) for b_s_i in self.binary_sub_images], ascii_code)
        
        ims, tkImage = self.get_image()
        self.source_label.configure(image = tkImage)
        self.source_label.image = tkImage
        for i in range(length):
            self.ims_lable[i].configure(image = ims[i])
            self.ims_lable[i].image = ims[i]
            
        #model_predict = self.predict([np.array(b_s_i.getdata()) for b_s_i in self.binary_sub_images])
        
        #self.entry_text.set(''.join([chr(num) for num in model_predict]))
        self.entry_text.set('')
        self.update_idletasks()
        self.update()
    
    def get_image(self):
        
        if(len(self.captcha_files) > 0):
            self.file_name, self.file_path = self.captcha_files.pop()
        #print(self.file_path)    
        im = PILImage.open(self.file_path)
        (width, high) = im.size
        tkImage = ImageTk.PhotoImage(im.resize((width * 4, high * 4), PILImage.ANTIALIAS))
        
        #ims = CaptchaHandler.handle(im, binaryThreshold=220)
        #np.array(image.getdata())
        self.sub_images = CaptchaHandler.handle(im, binaryThreshold=220)
        tk_sub_images = []
        for sub_image in self.sub_images:
            tk_sub_images.append(ImageTk.PhotoImage(sub_image))
        
        self.binary_sub_images = CaptchaHandler.binarization(self.sub_images, pointThreshold=220)
        
        #print(ims)
        im.close
        return (tk_sub_images, tkImage)

    def move_file(self, ascii_code):
        #print(code)
        if(len(ascii_code) > 0):

            rename = self.target + '_'.join([str(char) for char in ascii_code]) + '.png'
            #print(rename)
            shutil.move(self.file_path, rename)
            for i in range(self.length):
                train_dir = self.train + str(ascii_code[i]) + '//'
                if(not os.path.exists(train_dir)):
                    os.makedirs(train_dir)
                self.binary_sub_images[i].save(train_dir + str(int(time.time() * 1000)) + '.png')

    def train_model(self, sample, label):
        self.svc_model.fit(sample, label)

    def train_model_from_image(self, train_image_dir, train_count, train_batch_size=10):

        self.lable_samples = self.load_train_sample_from_image(train_image_dir)
        lables = self.lable_samples.keys()

        for i in range(train_count):

            #print('generation: ', i, ' in all ', train_count)
            
            batch_lables = random.sample(lables, train_batch_size)
            batch_samples = []
            
            for lable in batch_lables:
                
                batch_samples.append(self.lable_samples[lable][random.randint(0, len(self.lable_samples[lable]) - 1)])

            self.train_model(batch_samples, batch_lables)

    def load_train_sample_from_image(self, train_image_dir):
        
        lable_names = os.listdir(train_image_dir)
        lable_samples = {}

        table = CaptchaHandler.pointTable(220)
        
        for lable_name in lable_names:
            
            lable_dir = os.path.join(train_image_dir, lable_name)
            lable = int(lable_name)

            lable_samples[lable] = []
            
            lable_file_names = os.listdir(lable_dir)
            for lable_file_name in lable_file_names:
                lable_file_path = os.path.join(lable_dir, lable_file_name)

                im = PILImage.open(lable_file_path)
                point = im.copy().convert('L').point(table, '1')
                lable_samples[lable].append(np.array(point.getdata()))
                im.close()
                point.close()
                                
        return lable_samples
        

    def predict(self, sample):
        return self.svc_model.predict(sample)
    
    def save_model(self):
        print('正在输出模型文件...')
        joblib.dump(self.svc_model, self.model_file)
        print('模型已保存完成!')
        
    def close(self):
        #self.save_model()
        self.write_log()
        self.destroy()

    def write_log(self):

        if len(self.logs) < 1:
            return
        if(not os.path.exists(log)):
            os.makedirs(log)
        if(not os.path.exists(log_file)):
            wb = xlwt.Workbook()
            wb.add_sheet('日志')
            wb.save(log_file)
        
        try:
            log_excel = xlrd.open_workbook(log_file) 
            log_sheet = log_excel.sheet_by_index(0) 
            rows = log_sheet.nrows
        
            new_log_excel = xlcopy(log_excel) 
            sheet_write = new_log_excel.get_sheet(0) 

            for i in range(len(self.logs)):
                for j in range(len(self.logs[i])): 
                    sheet_write.write(rows + i, j, self.logs[i][j]) 
 
            new_log_excel.save(log_file)
        except PermissionError as e:
            messagebox.showinfo('写入文件错误', '请确认日志文件是否已被其他程序打开！')
            raise e

if __name__ == '__main__':

    #source = input('请输入验证码源目录\n> ')
    #target = input('请输入验证码保存目录\n> ')
    #length = input('请输入验证码长度\n> ')
    source = '..//image//ntsms//source//'
    target = '..//image//ntsms//name//'
    train = '..//image//ntsms//train//'
    model = '..//model//ntsms//'
    log = '..//log//'
    log_file = log + 'result.xls'
    length = 4
    
    if(not os.path.exists(source)):
        os.makedirs(source)
    if(not os.path.exists(target)):
        os.makedirs(target)
    if(not os.path.exists(train)):
        os.makedirs(train)
    if(not os.path.exists(model)):
        os.makedirs(model)
    if(not os.path.exists(log)):
        os.makedirs(log)
    if(not os.path.exists(log_file)):
        wb = xlwt.Workbook()
        wb.add_sheet('日志')
        wb.save(log_file)
    

    captchaWindow = CaptchaWindow(source, target, train, model, length)
