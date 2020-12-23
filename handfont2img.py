# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import

import argparse
import sys
import numpy as np
import os
import glob
import cv2
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps
from PIL import ImageFilter
from PIL import ImageEnhance
from cv2 import bilateralFilter
from pdf2image import convert_from_path



def draw_single_char(ch, font, canvas_size, x_offset, y_offset ):
    img = Image.new("RGB", (canvas_size, canvas_size), (255, 255, 255)).convert('L')
    draw = ImageDraw.Draw(img)
    draw.text((x_offset, y_offset), ch, (0), font=font)    
    return img



def crop_image_uniform(src , src_dir, dst_dir ,idx_path ,label,charset , char_size , canvas_size, x_offset, y_offset):
    f = open(idx_path, "r")
    charset = open(charset).read().splitlines()
    
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    pages = convert_from_path(src_dir)
    
    for page in pages:
        page = page.convert('L')
        np_page = np.array(page)

        
        
        
        ## 외곽선 따기 
#         row_col = np.where(np_page < 127)
#         if len(row_col[0]) == 0 :
#             y1, y2 = row_col[0][0], row_col[0][-1] 
#         else:
#             y1 , y2 = 0 , np_page.shape[0]
        
#         if len(row_col[1])== 0:
#             x1, x2 = row_col[1][0], row_col[1][-1]
#         else :
#             x1 , x2 = 0 , np_page.shape[1]

#         row_col = np.where(np_page < 127)
#         y1, y2 = row_col[0][0], row_col[0][-1] 
#         x1, x2 = row_col[1][0], row_col[1][-1]

#         cropped_img = np_page[y1:y2, x1:x2]

### pdf 외곽선 따는 거 마저 python으로 하면 좋을텐데 스캔작업 과정에서 수직,수평이 기울어지는 일이 많습니다.
### 그럴 경우 외곽선 따기가 불편하므로 pdf 점편집을 통해서 템플릿만! pdf로 만들어서 올리는 것을 추천드립니다 ㅜㅠ
        
    
   
        #전처리
        prc_cropped_img = np.where(np_page < 127,0,255 ) #127보다 작으면 0 ,127보다 크면 255
        prc_cropped_img = np.where(np.sum(prc_cropped_img , axis=0) == 0 , 255 , prc_cropped_img)
        prc_cropped_img = np.where(np.sum(prc_cropped_img , axis=1) == 0 , 255 , prc_cropped_img)
        img = Image.fromarray(prc_cropped_img.astype(np.uint8) )

        
        width, height = img.size
        cell_width = width/float(cols)
        cell_height = height/float(rows)
        header_offset = height/float(rows) * header_ratio
        width_margin = cell_width * 0.005
        height_margin = cell_height * 0.005

        
        for j in range(0,rows):
            for i in range(0,cols):
                left = i * cell_width - 2 
                upper = j * cell_height + header_offset
                right = left + cell_width
                lower = (j+1) * cell_height

                center_x = (left + right) / 2
                center_y = (upper + lower) / 2

                crop_width = right - left - 2*width_margin
                crop_height = lower - upper - 2*height_margin

                size = 0
                if crop_width > crop_height:
                    size = crop_height/2
                else:
                    size = crop_width/2

                left = center_x - size;
                right = center_x + size;
                upper = center_y - size;
                lower = center_y + size;

                code = f.readline()
                
                if not code:
                    break
                    
                else:
                    name = dst_dir + '/'+str(label)+'_'+ code.strip() + ".png"
                    cropped_image = img.crop((left, upper, right, lower))
                    resized_cropped_image = cropped_image.resize((128,128), Image.LANCZOS)
                    np_resized_cropped_image = np.array(resized_cropped_image)
                    centered = centering_image(np_resized_cropped_image, image_size=128, verbose=False, resize_fix=90, pad_value=None)
                    centenred_image = Image.fromarray(centered).convert('L')
                    # 아웃풋 이미지 

                    # Increase constrast
                    enhancer = ImageEnhance.Contrast(centenred_image)
                    cropped_image = enhancer.enhance(2)
                    opencv_image = np.array(cropped_image)
                    opencv_image = bilateralFilter(opencv_image, 9, 30, 30)
                    dst_img = Image.fromarray(opencv_image).convert('L')
#                     dst_img.save(dst_dir +str(label)+'_'+ code.strip() + ".png")
                    
                         
                    src_font = ImageFont.truetype(src, size = char_size)
                    idx = int(code.strip())
                    ch = charset[idx]
                    src_img = draw_single_char(ch, src_font, canvas_size, x_offset, y_offset)
                    example_img = Image.new("RGB", (canvas_size * 2, canvas_size), (255, 255, 255)).convert('L')
                    example_img.paste(dst_img, (0, 0))
                    example_img.paste(src_img, (canvas_size, 0))
                    example_img.save(name)
                    
                    
def tight_crop_image(img, verbose=False, resize_fix=False):
    #input : numpy 
    img_size = img.shape[0]
    full_white = img_size
    col_sum = np.where(np.sum(img, axis=0) < 255 * 128)
    row_sum = np.where(np.sum(img, axis=1) < 255 * 128)
    y1, y2 = row_sum[0][0], row_sum[0][-1]
    x1, x2 = col_sum[0][0], col_sum[0][-1]
    cropped_image = img[y1:y2, x1:x2]
    cropped_image_size = cropped_image.shape
    
    if verbose:
        print('(left x1, top y1):', (x1, y1))
        print('(right x2, bottom y2):', (x2, y2))
        print('cropped_image size:', cropped_image_size)
        
    if type(resize_fix) == int:
        origin_h, origin_w = cropped_image.shape
        if origin_h > origin_w:
            resize_w = int(origin_w * (resize_fix / origin_h))
            resize_h = resize_fix
        else:
            resize_h = int(origin_h * (resize_fix / origin_w))
            resize_w = resize_fix
        if verbose:
            print('resize_h:', resize_h)
            print('resize_w:', resize_w, \
                  '[origin_w %d / origin_h %d * target_h %d]' % (origin_w, origin_h, target_h))

        cropped_image = cv2.resize(cropped_image, (resize_h, resize_w), Image.LANCZOS)
        
#         cropped_image = cropped_image.resize((128,128))
        
#         cropped_image = normalize_image(cropped_image)
        cropped_image_size = cropped_image.shape
        if verbose:
            print('resized_image size:', cropped_image_size)
        
    elif type(resize_fix) == float:
        origin_h, origin_w = cropped_image.shape
        resize_h, resize_w = int(origin_h * resize_fix), int(origin_w * resize_fix)
        if resize_h > 120:
            resize_h = 120
            resize_w = int(resize_w * 120 / resize_h)
        if resize_w > 120:
            resize_w = 120
            resize_h = int(resize_h * 120 / resize_w)
        if verbose:
            print('resize_h:', resize_h)
            print('resize_w:', resize_w)
        
        # resize
        cropped_image = cv2.resize(cropped_image, (resize_h, resize_w))
        cropped_image_size = cropped_image.shape
        if verbose:
            print('resized_image size:', cropped_image_size)
    
    return cropped_image


def add_padding(img, image_size=128, verbose=False, pad_value=None):
    #인풋 넘파이 
    height, width = img.shape
    if not pad_value:
        pad_value = 255
    if verbose:
        print('original cropped image size:', img.shape)
    
    # Adding padding of x axis - left, right
    pad_x_width = (image_size - width) // 2
    pad_x = np.full((height, pad_x_width), pad_value, dtype=np.float32)
    img = np.concatenate((pad_x, img), axis=1)
    img = np.concatenate((img, pad_x), axis=1)
    
    width = img.shape[1]

    # Adding padding of y axis - top, bottom
    pad_y_height = (image_size - height) // 2
    pad_y = np.full((pad_y_height, width), pad_value, dtype=np.float32)
    img = np.concatenate((pad_y, img), axis=0)
    img = np.concatenate((img, pad_y), axis=0)
    
    # Match to original image size
    width = img.shape[1]
    if img.shape[0] % 2:
        pad = np.full((1, width), pad_value, dtype=np.float32)
        img = np.concatenate((pad, img), axis=0)
    height = img.shape[0]
    if img.shape[1] % 2:
        pad = np.full((height, 1), pad_value, dtype=np.float32)
        img = np.concatenate((pad, img), axis=1)

    if verbose:
        print('final image size:', img.shape)
    
    return img


def centering_image(img, image_size=128, verbose=False, resize_fix=False, pad_value=None):
    #인풋 , 아웃풋 넘파이 
    if not pad_value:
        pad_value = 255
    cropped_image = tight_crop_image(img, verbose=verbose, resize_fix=resize_fix)
    centered_image = add_padding(cropped_image, image_size=image_size, verbose=verbose, pad_value=pad_value)
    
    return centered_image
                    
    
parser = argparse.ArgumentParser(description='Crop scanned images to character images')
parser.add_argument('--src', dest='src', required=True, help='source font
parser.add_argument('--src_dir', dest='src_dir', required=True, help='directory to read scanned pdf')
parser.add_argument('--dst_dir', dest='dst_dir', required=True, help='directory to save character images')
parser.add_argument('--idx_path', dest='idx_path', required=True, help='directory to saved 210 character index')
parser.add_argument('--label', dest='label', type =int, help='font category label')
parser.add_argument('--charset', dest='charset', type=str, required=True , help='path of the charset')
parser.add_argument('--char_size', dest='char_size', type=int, default=90, help='character size')
parser.add_argument('--canvas_size', dest='canvas_size', type=int, default=128, help='canvas size')
parser.add_argument('--x_offset', dest='x_offset', type=int, default=10, help='x offset')
parser.add_argument('--y_offset', dest='y_offset', type=int, default=10, help='y_offset')

args = parser.parse_args()

if __name__ == "__main__":
    rows = 10
    cols = 7
    header_ratio = 18/50
    crop_image_uniform(args.src , args.src_dir, args.dst_dir, args.idx_path , args.label, args.charset,args.char_size , args.canvas_size , 
                       args.x_offset , args.y_offset)
    print("done")

    
    # src -- 고딕체 저장 경로 src_dir --pdf가 저장된 경로 , dst_dir --이미지 두개 저장되는 경로 , idx_path : character idx가 저장되어 있는 경로 
    # label = 29, charset=230.txt  char_size , 

# python handfont2img.py --src='/home/pirl/font_generation/font/source/NanumGothic.ttf' --src_dir='/home/pirl/font_generation/210_template_sh.pdf' --dst_dir='/home/pirl/font_generation/crop' --idx_path='/home/pirl/zi2zi-pytorch1/dataset/random210_idx.txt' --label=29 --charset='/home/pirl/zi2zi-pytorch1/2350-common-hangul.txt'


