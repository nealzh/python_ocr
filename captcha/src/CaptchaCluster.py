import os
import time
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

source_dir = 'C:\\workspace\\python\\captcha2\\image\\dap\\split\\'
target_dir = 'C:\\workspace\\python\\captcha2\\image\\dap\\cluster\\'

def image_vector(file_list, normalization=255):

    vectors = []
    for file_path in file_list:
        image = Image.open(file_path)
        vectors.append(np.array([pix // normalization for pix in image.getdata()]))
        image.close()
    return np.array(vectors)

file_names = os.listdir(source_dir)

vector_list = []
file_list = []

for file_name in file_names:

    file_path = os.path.join(source_dir, file_name)
    file_list.append(file_path)

print('file list length:', len(file_list))

vector_list = image_vector(file_list)

print('vector list length:', len(vector_list))

km = KMeans(n_clusters=60)
km.fit(vector_list)

print('cluster_centers_', km.cluster_centers_)
print('labels_ ', km.labels_)

labels = km.predict(vector_list)

for index in range(len(labels)):
    #print(labels[index])
    file_dir = target_dir + str(labels[index]) + '\\'
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    file_name = file_dir + str(int(time.time() * 1000)) + '.png'

    file_path = file_list[index]
    image = Image.open(file_path)
    image.save(file_name)
    image.close()
    print('save as:', file_name)