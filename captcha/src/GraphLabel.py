#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Required
- tkinter (必须)
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
import time

from PIL import ImageTk
from PIL import Image as PILImage
from tkinter.filedialog import *
from CaptchaHandler import NTSMSCaptchaHandler
from CaptchaDownloader import NTSMSCaptchaDownloader
from CaptchaHandler import MCCaptchaHandler
from CaptchaDownloader import MCCaptchaDownloader
from CaptchaRecognitioner import SVMCaptchaRecognitioner

class CaptchaWindow(Tk):
    
    def __init__(self, named_dir, label_dir, downloader, handler, recognitioner):
        
        super().__init__()

        self.named_dir = named_dir
        self.label_dir = label_dir
        self.downloader = downloader
        self.handler = handler
        self.recognitioner = recognitioner

        self.title("Graph Label")
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
        self.entry_text.set(''.join(self.recognitioner.predict(self.binary_sub_images)))
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
            
        self.mainloop()

    def enter_next(self, event):

        ascii_code = [ord(char) for char in self.entry_text.get()]
        if len(ascii_code) != 4:
            return

        self.save_image(ascii_code)

        ims, tkImage = self.get_image()
        self.source_label.configure(image = tkImage)
        self.source_label.image = tkImage
        for i in range(length):
            self.ims_lable[i].configure(image = ims[i])
            self.ims_lable[i].image = ims[i]

        self.entry_text.set(''.join(self.recognitioner.predict(self.binary_sub_images)))
        self.update_idletasks()
        self.update()

    def download_image(self):
        images = self.downloader.download()
        while len(images) < 1:
            images = self.downloader.download()
        return images[0]

    def get_image(self):

        self.image = self.download_image()
        self.binary_sub_images = self.handler.handle(self.image)

        while len(self.binary_sub_images) < 1:
            self.image = self.download_image()
            self.binary_sub_images = self.handler.handle(self.image)

        (width, high) = self.image.size
        tkImage = ImageTk.PhotoImage(self.image.resize((width * 4, high * 4), PILImage.ANTIALIAS))

        tk_sub_images = []
        for sub_image in self.binary_sub_images:
            tk_sub_images.append(ImageTk.PhotoImage(sub_image))

        return (tk_sub_images, tkImage)

    def save_image(self, ascii_code):
        #print(code)
        if(len(ascii_code) > 0):

            image_name = self.named_dir + '_'.join([str(char) for char in ascii_code]) + '.png'
            self.image.save(image_name)

            for i in range(len(ascii_code)):
                train_dir = self.label_dir + str(ascii_code[i]) + '//'
                if(not os.path.exists(train_dir)):
                    os.makedirs(train_dir)
                self.binary_sub_images[i].save(train_dir + str(int(time.time() * 1000)) + '.png')

        self.image.close()
        for binary_image in self.binary_sub_images:
            binary_image.close()
        
    def close(self):
        self.destroy()

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

    length = 4
    
    if(not os.path.exists(source_dir)):
        os.makedirs(source_dir)
    if(not os.path.exists(named_dir)):
        os.makedirs(named_dir)
    if(not os.path.exists(label_dir)):
        os.makedirs(label_dir)

    captchaWindow = CaptchaWindow(named_dir, label_dir, downloader, handler, recognitioner)
