# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import

import argparse
import sys
import numpy as np
import os
import glob
import cv2
import imageio
from PIL import Image
from PIL import ImageDraw

#라벨_인덱스 

def save_png(saved_path, new_save_path, code_path):
#     saved_list= os.listdir(saved_path)
#     save_list = [file for file in saved_list if file.endswith(".png")]
#     save_list = save_list.sort()
#     print(save_list)
    save_list = sorted(glob.glob(os.path.join(saved_path, "*.png")))
    for p in save_list:
            odd , even = read_split_image(p)
            odd = np.where(odd < 127,0,225 ) #127보다 작으면 0 ,127보다 크면 255
            even = np.where(even < 127,0,225 ) #127보다 작으면 0 ,127보다 크면 255
            
            
            
            
            odd_label = 2 * int(os.path.basename(p).split("_")[1].split(".")[0])
            even_label = 2 * int(os.path.basename(p).split("_")[1].split(".")[0]) + 1 
            
            if code_path is None :                     
                    odd_name = new_save_path + "/inffered_"+str(odd_label)+'.png'
                    even_name = new_save_path + "/inffered_"+str(even_label)+'.png'
                    imageio.imwrite(odd_name, odd)
                    imageio.imwrite(even_name,even)
                    
            else :
                    unicode_list = open(code_path).read().splitlines()
                    odd_unicode_label = unicode_list[odd_label]
                    even_unicode_label = unicode_list[even_label]
                    odd_unicode_name = new_save_path + "/inffered_"+str(odd_unicode_label)+'.png'
                    even_unicode_name = new_save_path + "/inffered_"+str(even_unicode_label)+'.png'
                    imageio.imwrite(odd_unicode_name, odd)
                    imageio.imwrite(even_unicode_name,even)
                    


                        
def read_split_image(img):
    mat = imageio.imread(img).astype(np.uint8)
    side = int(mat.shape[0] / 2)
    print(mat.shape)
    img_A = mat[:side, :]  # 홀수번 label
    img_B = mat[side:, :]  # 짝수번 label

    return img_A, img_B



parser = argparse.ArgumentParser(description='generated hand crop image crop 1x1 and saved')
parser.add_argument('--saved_path', dest='saved_path', required=True, help='path of savede xamples')
parser.add_argument('--new_save_path', dest='new_save_path', required=True, help='path to save new files')
parser.add_argument('--code_path', dest='code_path', help='path to save unicode_txt')
args = parser.parse_args()

if __name__ == "__main__":
    save_png(args.saved_path,args.new_save_path,args.code_path)
    print("완료!")
 