import os

file = open('2434_unicode.txt', 'r')
char_unicodes = file.read()

char_unicode_list = char_unicodes.split()

print(len(char_unicode_list))

count = 0

for char_unicode in char_unicode_list:
    os.rename('./extracted_dir/extracted_'+(str(count).zfill(4))+'.png','./extracted_dir/'+char_unicode+'.png')
    count += 1