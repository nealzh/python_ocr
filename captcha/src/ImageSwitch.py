import os
import shutil
import nanotime

from PIL import Image
from CaptchaHandler import NTSMSCaptchaHandler

class ImageSwitch(object):

    def __init__(self, source_dir, target_dir, captcha_handler, size=30):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.captcha_handler = captcha_handler
        self.size = size

    def split_named_image(self):
        file_names = os.listdir(self.source_dir)
        for file_name in file_names:
            file_path = os.path.join(self.source_dir, file_name)
            print(file_path)
            file_dirs = file_name.split('.')[0].split('_')
            source_image = Image.open(file_path)
            images = self.captcha_handler.handle(source_image)

            if len(file_dirs) != len(images):
                print(file_path, 'handle failed.')
            else:
                for index in range(len(images)):
                    sub_dir_path = os.path.join(self.target_dir, file_dirs[index])
                    if not os.path.exists(sub_dir_path):
                        os.mkdir(sub_dir_path)
                    images[index].save(os.path.join(sub_dir_path, str(int(nanotime.now())) + '.png'))
            source_image.close()

    def format_named_image(source_dir, target_dir, size):
        file_names = os.listdir(source_dir)

        for file_name in file_names:
            file_path = os.path.join(source_dir, file_name)

            if(os.path.isdir(file_path)):

                ascii_name = str(ord(file_name[0]))
                sub_file_names = os.listdir(file_path)

                if(len(sub_file_names) > 0):

                    print('handling dir: ', file_path)

                    target_file_path = os.path.join(target_dir, ascii_name)

                    if(not os.path.exists(target_file_path)):
                        os.makedirs(target_file_path)

                    for sub_file in sub_file_names:

                        sub_file_path = os.path.join(file_path, sub_file)
                        target_sub_file_path = os.path.join(target_file_path, sub_file)

                        im = Image.open(sub_file_path)
                        resizeImage = im.resize((size, size), Image.ANTIALIAS)
                        resizeImage.save(sub_file_path)
                        im.close()
                        resizeImage.close()
                        shutil.move(sub_file_path, target_sub_file_path)

#source_dir = 'C://workspace//python//VerificationCode//img2//train//'
#target_dir = 'C://workspace//python//VerificationCode//imgn//train//'
#size = 30
#scan_file(source_dir, target_dir, size)

source_dir = 'C:\\Users\\15637\\Desktop\\回收\\name'
target_dir = 'C:\\workspace\\python\\captcha2\\image\\ntsms\\train2'
handler = NTSMSCaptchaHandler()

switcher = ImageSwitch(source_dir, target_dir, handler)
switcher.split_named_image()
