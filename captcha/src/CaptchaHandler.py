from PIL import Image

import random
import numpy as np

class CaptchaHandler(object):

    def __init__(self,
                 char_num=4,
                 standard_size=30,
                 binary_threshold=140,
                 noise_point_size=2,
                 noise_range_size=2):

        self.char_num = char_num
        self.standard_size = standard_size
        self.binary_threshold = binary_threshold
        self.noise_point_size = noise_point_size
        self.noise_range_size = noise_range_size

        self.point_table = self.gen_point_table(binary_threshold)

    def points_2_image(self, points, size):

        image_frame = Image.new('L', size, "white")

        image_frame_access = image_frame.load()
        for pix in points:
            # print(pix)
            image_frame_access[pix[0], pix[1]] = 0

        return image_frame

    def reduction_dim(self, point_image):

        effective_image = self.effective_range_image(point_image)
        width, high = effective_image.size
        image_access = effective_image.load()
        line = []
        for w in range(width):
            black_count = 0
            for h in range(high):
                if image_access[w, h] == 0:
                    black_count = black_count + 1
            line.append(black_count)
        return line

    def line_2_image(self, line, size):

        image_frame = Image.new('L', size, "white")
        image_frame_access = image_frame.load()

        for w in range(len(line)):
            for cursor in range(line[w]):
                image_frame_access[w, cursor] = 0
        return image_frame

    def reduce_dim_split(self, source_image):

        images = []
        point_image = source_image.convert('L').point(self.point_table, '1')
        line = self.reduction_dim(point_image)
        groups = self.reduction_dim_analysis(line)
        width, high = point_image.size

        if len(groups) >= self.char_num:
            while len(groups) > self.char_num:
                groups = self.merge_group(groups, line)
            for group in groups:
                images.append(self.effective_range_image(point_image.crop((group[0][0], 0, group[0][-1], high))))
        else:
            images = self.split(source_image)

        return images

    def merge_group(self, groups, line):

        merge_groups = []
        min_len = 65536
        min_len_index = 0

        for x in range(len(groups)):
            key_group = groups[x][0]
            if len(key_group) < min_len:
                min_len = len(key_group)
                min_len_index = x

        if min_len_index == 0:
            merge_groups.append(self.merge(groups[min_len_index], groups[min_len_index + 1], line))
            merge_groups.extend(groups[min_len_index + 2 : ])
        elif min_len_index == len(groups) - 1:
            merge_groups.extend(groups[ : min_len_index - 1])
            merge_groups.append(self.merge(groups[min_len_index - 1], groups[min_len_index], line))
        elif len(groups[min_len_index - 1]) < len(groups[min_len_index + 1]):
            merge_groups.extend(groups[ : min_len_index - 1])
            merge_groups.append(self.merge(groups[min_len_index - 1], groups[min_len_index], line))
            merge_groups.extend(groups[min_len_index + 1 : ])
        else:
            merge_groups.extend(groups[ : min_len_index])
            merge_groups.append(self.merge(groups[min_len_index], groups[min_len_index + 1], line))
            if min_len_index + 2 < len(groups):
                merge_groups.extend(groups[min_len_index + 2 : ])
        return merge_groups

    def merge(self, first, second, line):

        merge_key_group = []
        merge_value_group = []
        merge_key_group.extend(first[0])
        merge_value_group.extend(first[1])
        for key in range(first[0][-1] + 1, second[0][0]):
            merge_key_group.append(key)
            merge_value_group.append(line[key])
        merge_key_group.extend(second[0])
        merge_value_group.extend(second[1])

        return (merge_key_group, merge_value_group)

    def reduction_dim_analysis(self, line, min_mean=3):

        np_line = np.array(line)
        groups = self.scan_interval(np_line)

        while len(groups) < self.char_num or not self.group_mean_check(groups, min_mean):
            if np.max(np_line) == 0:
                break
            np_line = np_line - np.min(np_line[np_line > 0])
            np_line[np_line < 0] = 0
            groups = self.scan_interval(np_line)

        return groups

    def scan_interval(self, line):

        principal_component = []

        group = []
        index_group = []
        start_status = False

        for index in range(len(line)):
            if line[index] == 0 and not start_status:
                continue
            elif line[index] == 0 and start_status:
                principal_component.append((index_group, group))
                group = []
                index_group = []
                start_status = False
            elif line[index] != 0 and not start_status:
                start_status = True
                group.append(line[index])
                index_group.append(index)
            elif line[index] != 0 and start_status:
                group.append(line[index])
                index_group.append(index)

        return principal_component

    def group_mean_check(self, groups, min_mean):
        for index in range(len(groups)):
            value_group = groups[index][1]
            if sum(value_group) / len(value_group) < min_mean:
                return False
        return True

    def denoise(self, image):

        (width, high) = image.size
        black_points = []
        for w in range(width):
            for h in range(high):
                if(image.getpixel((w, h)) == 0):
                    black_points.append((w, h))

        groups = self.scan_black_group(black_points, image.size)
        noises_groups = []
        pixes_groups = []
        for group in groups:
            if(len(group) <= self.noise_point_size):
                noises_groups.append(group)
            else:
                pixes_groups.append(group)
        return (noises_groups, pixes_groups)

    def scan_black_group(self, black_points, pic_size):
        scanned = set()
        need_scan = []
        group = []
        groups = []
        bp = set(black_points)
        for black_point in black_points:
            #print "black_point: ",black_point
            if(black_point not in scanned):
                scanned.add(black_point)
                group.append(black_point)
                need_scan.extend((self.gen_around_points(black_point, pic_size) - scanned) & bp)
                #print "first scan around: ", group
                while(len(need_scan) > 0):
                    scan = need_scan.pop()
                    #print "scan: ",scan
                    group.append(scan)
                    scanned.add(scan)
                    need_scan.extend(((self.gen_around_points(scan, pic_size) - scanned) & bp) - set(need_scan))
                if(len(group) > 0):
                    groups.append(group)
                group = []
        return groups

    def gen_around_points(self, point, pic_size):
        #print "point: ",point
        (width, high) = pic_size
        points = set()
        for x in range(point[0] - self.noise_range_size, point[0] + self.noise_range_size + 1):
            for y in range(point[1] - self.noise_range_size, point[1] + self.noise_range_size + 1):

                #print "x,y: ",x,y

                if(x >= 0 and x < pic_size[0] and y >= 0 and y < pic_size[1]):
                    if(x == point[0] and y == point[1]):
                        continue
                    else:
                        points.add((x, y))
        #print "from point ",point,"genPoints: ",points
        return points

    def effective_range_image(self, image, margin=1):
        effective = self.effective_range(image, margin)
        effective_image = image.crop(effective)
        return effective_image

    def effective_range(self, image, margin=1):

        (width, high) = image.size

        lefter = (False, width - 1)
        righter = (False, 0)
        upper = (False, 0)
        lower = (False, high - 1)

        for i in range(width):
            for j in range(high):
                if(not lefter[0]):
                    #print "i: ",i,"j: ",j
                    if(image.getpixel((i, j)) == 0):
                        if(i >= 1):
                            lefter = (True, i - margin)
                        else:
                            lefter = (True, 0)
                if(not righter[0]):
                    #print "width - i - 1: ",width - i - 1,"j: ",j
                    if(image.getpixel((width - i - 1, j)) == 0):
                        if(i >= 1):
                            righter = (True, width - i + margin)
                        else:
                            righter = (True, width)
                if(lefter[0] and righter[0]):
                    break
            if(upper[0] and lower[0]):
                break

        for i in range(high):
            for j in range(width):
                if(not upper[0]):
                    #print "i: ",i,"j: ",j
                    if(image.getpixel((j, i)) == 0):
                        if(i >= 1):
                            upper = (True, i - margin)
                        else:
                            upper = (True, 0)
                if(not lower[0]):
                    #print "high - i - 1: ",high - i - 1,"j: ",j
                    if(image.getpixel((j, high - i - 1)) == 0):
                        if(i >= 1):
                            lower = (True, high - i + margin)
                        else:
                            lower = (True, high)
                if(upper[0] and lower[0]):
                    break
            if(upper[0] and lower[0]):
                break
        if(not lefter[0]):
            lefter = (False, -1)
        if(not righter[0]):
            righter = (False, -1)
        if(not upper[0]):
            upper = (False, -1)
        if(not lower[0]):
            lower = (False, -1)
        return (lefter[1], upper[1], righter[1], lower[1])

    def gen_point_table(self, threshold):
        table = []
        for i in range(256):
            if i < threshold:
                table.append(0)
            else:
                table.append(1)
        return table

    def split(self, source_image):

        point_image = source_image.convert('L').point(self.point_table, '1')
        noises_groups, pixes_groups = self.denoise(point_image)

        #if(len(pixes_groups) != self.char_num):
        #    effective_image = self.effective_range_image(point_image)
        #    images = self.avg_split(effective_image, self.char_num)
        #else:
        #    images = []
        #    for pixes_group in pixes_groups:
        #        images.append(self.effective_range_image(self.points_2_image(pixes_group, source_image.size)))
        images = []
        if (len(pixes_groups) == self.char_num):
            for pixes_group in pixes_groups:
                images.append(self.effective_range_image(self.points_2_image(pixes_group, source_image.size)))
        #source_image.close()
        return images

    def avg_split(self, image, target_num):
        (width, high) = image.size
        if(target_num < 1):
            return [image.crop((0, 0, width - 1, high - 1))]

        avg = width / target_num
        mod = width % target_num
        wheel = []
        splits = []
        for i in range(mod):
            wheel.append(1)
        for i in range(target_num - mod):
            wheel.append(0)

        start = 0
        #print "pic: ",pic
        for i in range(target_num):
            if(i == target_num - 1):
                #print "subPic", start, pic[1], pic[2], pic[3]
                splits.append(image.crop((start, 0, width - 1, high - 1)))
                #print (start, 0, width - 1, high - 1)
                break
            end = start + avg + random.choice(wheel) - 1
            #print "subPic", start, pic[1], end, pic[3]
            splits.append(image.crop((start, 0, end, high - 1)))
            #print (start, 0, end, high - 1)
            start = end + 1
        return splits

    def size(self, headLine, tanLine, length):
        maxWidth = 0
        minWidth = 1 << 32
        for i in range(length):
            if(maxWidth < tanLine[i][0]):
                maxWidth = tanLine[i][0]
            if(minWidth > headLine[i][0]):
                minWidth = headLine[i][0]
        return (minWidth, maxWidth - minWidth)

    def brush(self, imageArray, points, color):

        for (x, y) in points:
            for index in range(x):
                imageArray[y][index] = color

    def scan_clearance(self, imageArray, size, points, split_threshold):
        (width, high) = size
        clear = True
        for (x, y) in points:
            count = 0
            for index in range(x - split_threshold, x + split_threshold):
                if(index > 0 and index < width):
                    if(imageArray[y][index]):
                        count = count + 1
                    else:
                        count = 0
            if(count < split_threshold):
                clear = False
                break
        return clear

    def proportion_zoom(self, images, size):
        resize_images = []
        for image in images:
            w, h = image.size
            resize_prop = size / (w if w <= h else h)
            resize_images.append(image.resize((int(w * resize_prop), int(h * resize_prop)), Image.ANTIALIAS))
        return resize_images

    def zoom(self, images, size):
        resize_images = []
        for image in images:
            resize_image = image.resize((size, size), Image.ANTIALIAS)
            resize_images.append(resize_image)
        return resize_images

    def binarization(self, images):
        binary_images = []
        for image in images:
            point = image.copy().convert('L').point(self.point_table, '1')
            binary_images.append(point)
        return binary_images

    def standard(self, images, size):
        standard_images = []
        for image in images:
            (width, high) = image.size
            if(width == size and high == size):
                #image.show()
                standard_images.append(image)
            else:
                standard_images.append(self.zoom(image, size))
        return standard_images

    def copy_image(self, target_image, source_image):
        target_width, target_high = target_image.size
        source_width, source_high = source_image.size
        image = source_image.copy()
        if(source_width > target_width):
            image = self.zoom([image], target_width)[0]
            source_width, source_high = image.size
        if(source_high > target_high):
            image = self.zoom([image], target_high)[0]
            source_width, source_high = image.size

        deviation_width = abs((target_width - source_width) / 2)
        deviation_high = abs((target_high - source_high) / 2)

        target_access = target_image.load()
        source_access = image.load()

        for w in range(source_width):
            for h in range(source_high):
                target_access[w + deviation_width, h + deviation_high] = source_access[w, h]
        #target_image.show()
        return target_image

    def handle(self, image):
        images = self.zoom(self.split(image), self.standard_size)
        return images

class NTSMSCaptchaHandler(CaptchaHandler):

    def __init__(self, char_num=4,
                 standard_size=30,
                 binary_threshold=240,
                 noise_point_size=2,
                 noise_range_size=2):
        super(NTSMSCaptchaHandler, self).__init__(char_num,
                                                  standard_size,
                                                  binary_threshold,
                                                  noise_point_size,
                                                  noise_range_size)

    def handle(self, image):
        images = self.split(image)
        #if len(images) != self.char_num:
         #   images = self.reduce_dim_split(image)

        return self.zoom(images, self.standard_size)

#mobile communication
class MCCaptchaHandler(CaptchaHandler):

    def __init__(self, char_num=4,
                 standard_size=30,
                 binary_threshold=135,
                 noise_point_size=2,
                 noise_range_size=2):
        super(MCCaptchaHandler, self).__init__(char_num,
                                               standard_size,
                                               binary_threshold,
                                               noise_point_size,
                                               noise_range_size)

    def handle(self, image):
        images = self.split(image)
        # if len(images) != self.char_num:
        #   images = self.reduce_dim_split(image)

        return self.zoom(images, self.standard_size)

# DispatchAdminPlatform
class DAPCaptchaHandler(CaptchaHandler):
    def __init__(self, char_num=4,
                 standard_size=30,
                 binary_threshold=140,
                 noise_point_size=2,
                 noise_range_size=2):
        super(DAPCaptchaHandler, self).__init__(char_num,
                                               standard_size,
                                               binary_threshold,
                                               noise_point_size,
                                               noise_range_size)

    def handle(self, image):
        images = self.split(image)
        # if len(images) != self.char_num:
        #   images = self.reduce_dim_split(image)

        return self.proportion_zoom(images, self.standard_size)

#douban
class DouBanCaptchaHandler(CaptchaHandler):

    def __init__(self):
        super(DouBanCaptchaHandler, self).__init__()

    def color_filter(self, image):
        pass

