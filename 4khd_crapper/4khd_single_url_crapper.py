#爬取图片
import os.path
import requests
import time
from lxml import etree

if __name__ == '__main__':
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
i = 1
#此处的url存放想要下载图片的网址
#folder_name是下载的文件夹名字
url = 'https://www.4khd.com/2022/10/13/coseryuuhui-yuhui-no013-chinese-girl.html'
folder_name = 'yuhui_chinese_girl_original'
response = requests.get(url = url, headers = headers)
page_text = response.text
tree = etree.HTML(page_text)
page_nums = tree.xpath('//ul[@class="page-links"]/li')
page_num = len(page_nums)
if page_num == 0:
    page_num = 1
#文件会下载在你运行程序所在的目录下
#每一次下载新的图包都要修改文件夹名称不然之前的图片会被覆盖
#创建一个文件夹
if not os.path.exists('./' + folder_name):
    os.mkdir('./' + folder_name)
for n in range(page_num):
    extra_str = '/' + str(n + 1) if n else ''
    print('downloading: ' + url + extra_str)
    response = requests.get(url=url + extra_str, headers=headers)
    page_text = response.text
    #数据解析
    tree = etree.HTML(page_text)
    figure_list = tree.xpath('//figure[@class="wp-block-image size-large"]')
    src_str1 = '@src'
    src_str2 = '@data-lazy-src'
    for figure in figure_list:
        img_name = str(i) + '.jpg'
        
        i = i + 1
        try:
            time.sleep(1)
            img_data = requests.get(url = figure.xpath('./a/img/' + src_str1)[0], headers=headers).content
        except:
            print("swaping sources...")
            time.sleep(1)
            src_str1, src_str2 = src_str2, src_str1
            img_data = requests.get(url = figure.xpath('./a/img/' + src_str1)[0], headers=headers).content
        img_path = folder_name + '/' + img_name
        with open(img_path,'wb')as fp:
            fp.write(img_data)
            print(img_name,'下载成功！')