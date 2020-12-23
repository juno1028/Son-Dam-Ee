# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import

import argparse
import sys
import numpy as np
import os
import glob
import cv2
import collections
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

    
def draw_single_char(ch, font, canvas_size, x_offset, y_offset ):
    img = Image.new("RGB", (canvas_size, canvas_size), (255, 255, 255)).convert('L')
    draw = ImageDraw.Draw(img)
    draw.text((x_offset, y_offset), ch, (0), font=font)

# 전처리과정
#     if ch not in special_list : 
#         img_array = np.array(img)
#         centered_img_array = centering_image(img_array, canvas_size=128, char_size = 90 , pad_value=None)
#         img = Image.fromarray(centered_img_array).convert('L')
    
#     if is_monochromatic_image(img): 
#         return None   
    
    return img


def draw_example(ch, src_font, dst_font, canvas_size, x_offset, y_offset, filter_hashes):
    dst_img = draw_single_char(ch, dst_font, canvas_size, x_offset, y_offset) 
    # check the filter example in the hashes or not
    
    
    dst_hash = hash(dst_img.tobytes())
    if dst_hash in filter_hashes:
        return None
 
    src_img = draw_single_char(ch, src_font, canvas_size, x_offset, y_offset)
    example_img = Image.new("RGB", (canvas_size * 2, canvas_size), (255, 255, 255)).convert('L')
    example_img.paste(dst_img, (0, 0))
    example_img.paste(src_img, (canvas_size, 0))
    return example_img




def filter_recurring_hash(charset, font, canvas_size, x_offset, y_offset):
    """ Some characters are missing in a given font, filter them
    by checking the recurring hashes
    """
    _charset = charset[:]
    np.random.shuffle(_charset)
    sample = _charset[:]
    hash_count = collections.defaultdict(int)
    for c in sample:
        img = draw_single_char(c, font, canvas_size, x_offset, y_offset)
        hash_count[hash(img.tobytes())] += 1
    recurring_hashes = filter(lambda d: d[1] > 2, hash_count.items())
    return [rh[0] for rh in recurring_hashes]




def font2img(src, dst, charset, char_size, canvas_size,
             x_offset, y_offset,sample_dir, filter_by_hash=True, label=0 ):
    
    src_font = ImageFont.truetype(src, size=char_size)
    
    filter_hashes = set()
    
    if filter_by_hash:
        filter_hashes = set(filter_recurring_hash(charset, dst_font, canvas_size, x_offset, y_offset))
        print("filter hashes -> %s" % (",".join([str(h) for h in filter_hashes])))

    if not os.path.exists(sample_dir):
        os.makedirs(sample_dir)
        print("create font2img directory")
    
    count = 0
    
    for c in charset:
        e = draw_example(c, src_font, dst_font, canvas_size, x_offset, y_offset, filter_hashes)
        
        if e:
            e.save(os.path.join(sample_dir, "%d_%04d.png" % (label, count))) ##작명 순서 : 폰트별 label __ 폰트내에서의 순서 
            count += 1
            
        if count == 2434:
            print("processed %d chars" % count)
                

                
                


#### 전처리 과정 #####
def tight_crop_image(img, char_size = 90 ):
    col_sum = np.where( np.sum(img,axis=0) <  255 * 128) # 글씨가 존재하는 행
    row_sum = np.where( np.sum(img, axis=1) < 255 * 128) # 글씨가 존재하는 열
#     row_sum = np.where(full_white - np.sum(img, axis=1) > 1) # 글씨가 존재하는 행 
    y1, y2 = row_sum[0][0], row_sum[0][-1]
    x1, x2 = col_sum[0][0], col_sum[0][-1]
    cropped_image = img[y1-2:y2+2, x1-2:x2+2] #글씨가 존재하는 부분만 여유롭게 ㅜㅜ 네모낳게 자름 
    cropped_image_size = cropped_image.shape 
    
    
    #char_size가 인수형인 경우
    if type(char_size) == int:
        origin_h, origin_w = cropped_image.shape
        if origin_h > origin_w: #crop된 사진의 높이>너비인 경우
            resize_w = int(origin_w * (char_size / origin_h))
            resize_h = char_size
            
        else:
            resize_h = int(origin_h * (char_size / origin_w))
            resize_w = char_size
            
        
        cropped_image = cv2.resize(cropped_image, (resize_h, resize_w)) #,resize크기에 맞춰 재조정
        cropped_image_size = cropped_image.shape

        
    elif type(char_size) == float:     #resize_fix가 실수형인 경우 
        origin_h, origin_w = cropped_image.shape
        resize_h, resize_w = int(origin_h * char_size), int(origin_w * char_size)
        # 왜 120인데요 ㅜㅅ ㅜ
        if resize_h > 120:
            resize_h = 120
            resize_w = int(resize_w * 120 / resize_h)
        if resize_w > 120:
            resize_w = 120
            resize_h = int(resize_h * 120 / resize_w)

        # resize
#         cropped_image = imresize(cropped_image, (resize_h, resize_w))
        cropped_image = cv2.resize(cropped_image, (resize_h, resize_w))
        cropped_image_size = cropped_image.shape

    
    return cropped_image

# 글자 제외 나머지 부분 padding 간격 맞추기 
def add_padding(img, canvas_size=128,  pad_value=None):
    height, width = img.shape
    if not pad_value:
        pad_value = img[0][0]

    
    # Adding padding of x axis - left, right
    pad_x_width = (canvas_size - width) // 2
    pad_x = np.full((height, pad_x_width), pad_value, dtype=np.float32)
    #(height, pad_x_width)만큼 pad_value로 채움 
    img = np.concatenate((pad_x, img), axis=1)
    img = np.concatenate((img, pad_x), axis=1)
    # 빈칸 - 글자 - 빈칸 이 되도록 axis에 대해 concat해줌
    width = img.shape[1]

    # Adding padding of y axis - top, bottom
    pad_y_height = (canvas_size - height) // 2
    pad_y = np.full((pad_y_height, width), pad_value, dtype=np.float32)
    img = np.concatenate((pad_y, img), axis=0)
    img = np.concatenate((img, pad_y), axis=0)
    # Match to original image size
    
    
    #w,h가 홀수면 
    width = img.shape[1]
    if img.shape[0] % 2:
        pad = np.full((1, width), pad_value, dtype=np.float32)
        img = np.concatenate((pad, img), axis=0)
        
    height = img.shape[0]
    if img.shape[1] % 2:
        pad = np.full((height, 1), pad_value, dtype=np.float32)
        img = np.concatenate((pad, img), axis=1)
    
    return img


def centering_image(img, canvas_size=128,  char_size = 90 ,  pad_value=None ):
    if not pad_value:
        pad_value = img[0][0]
    cropped_image = tight_crop_image(img, char_size=char_size)
    centered_image = add_padding(cropped_image, canvas_size=canvas_size,  pad_value=pad_value)
    
    return centered_image



parser = argparse.ArgumentParser(description='Convert font to images')
parser.add_argument('--src_font', dest='src_font', required=True, help='path of the source font')
parser.add_argument('--dst_font', dest='dst_font', required=True, help='path of the target font folder')
parser.add_argument('--filter', dest='filter', type=int, default=0, help='filter recurring characters')
parser.add_argument('--charset', dest='charset', type=str, required=True , help='path of the charset')
parser.add_argument('--shuffle', dest='shuffle', type=int, default=0, help='shuffle a charset before processings')
parser.add_argument('--char_size', dest='char_size', type=int, default=90, help='character size')
parser.add_argument('--canvas_size', dest='canvas_size', type=int, default=128, help='canvas size')
parser.add_argument('--x_offset', dest='x_offset', type=int, default=10, help='x offset')
parser.add_argument('--y_offset', dest='y_offset', type=int, default=10, help='y_offset')
parser.add_argument('--sample_count', dest='sample_count', type=int, default=1000, help='number of characters to draw')
parser.add_argument('--sample_dir', dest='sample_dir', help='directory to save examples')


args = parser.parse_args()

if __name__ == "__main__":
#     charset = open(args.charset).read().splitlines()
    charset = open(args.charset,'rt',encoding='UTF-8').read().splitlines()

    if args.shuffle:
        np.random.shuffle(charset)
    
    dst_dir = args.dst_font
    dst_list = os.listdir(dst_dir)
    dst_list = [file for file in dst_list if file.endswith(".ttf")] 
    ## dst 폴더 내에 있는 target 폰트들의 리스트
    
    label=0
    
    for name in dst_list:
        font_paths = glob.glob(os.path.join(args.dst_font, name))[0] #폰트명
        dst_font = ImageFont.truetype(font_paths, args.char_size) #폰트를 불러옴 
        font2img(args.src_font, dst_font, charset, args.char_size,
             args.canvas_size, args.x_offset, args.y_offset,
              args.sample_dir, args.filter , label = label )
        print("%d fonts"%label)
        label += 1

