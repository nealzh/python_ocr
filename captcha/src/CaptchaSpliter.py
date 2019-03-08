import os
from PIL import Image
from CaptchaHandler import DAPCaptchaHandler

source_dir = 'C:\\workspace\\python\\captcha2\\image\\dap\\source\\'
target_dir = 'C:\\workspace\\python\\captcha2\\image\\dap\\split\\'

file_names = os.listdir(source_dir)

handler = DAPCaptchaHandler()

count = 0

for file_name in file_names:

    # if count > 500:
    #     break

    file_seq = file_name.split('.')[0]
    file_path = os.path.join(source_dir, file_name)
    print(file_path)
    source_image = Image.open(file_path)
    image_list = handler.handle(source_image)

    for i in range(len(image_list)):
        image_list[i].save(target_dir + file_seq + '_' + str(i) + '.png')
    source_image.close()

    count = count + 1

