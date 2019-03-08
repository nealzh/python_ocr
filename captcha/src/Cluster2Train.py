import os
import shutil

source_dir = 'C:\\workspace\\python\\captcha2\\image\\dap\\cluster01\\'
target_dir = 'C:\\workspace\\python\\captcha2\\image\\dap\\train\\'

source_dir_names = os.listdir(source_dir)

for source_dir_name in source_dir_names:

    target_dir_name = str(ord(source_dir_name[0]))

    source_dir_path = os.path.join(source_dir, source_dir_name)
    target_dir_path = os.path.join(target_dir, target_dir_name)

    print('move image from', source_dir_path, target_dir_path)

    shutil.copytree(source_dir_path, target_dir_path)