#爬取图片
import os.path
import requests
import time
from bs4 import BeautifulSoup
from lxml import etree
#超时重试处理
from retrying import retry

#爬取图片
def img_crapper(url, folder_name):
    #此处的url存放想要下载图片的网址
    #folder_name是下载的文件夹名字
    try:
        response = get_url_response(url)
    except:
        timeout_data = open('timeout_url.txt', 'a')
        timeout_data.write(url + '\n')
        timeout_data.close()
        return
    
    page_text = response.text
    tree = etree.HTML(page_text)
    page_nums = tree.xpath('//ul[@class="page-links"]/li')
    page_num = len(page_nums)
    if page_num == 0:
        page_num = 1
    #文件会下载在你运行程序所在的目录下
    #创建文件夹(日期文件夹(年月日),图集文件夹)
    data_folder_name = folder_name[0:10]
    year_folder_name = data_folder_name[0:4]
    month_folder_name = data_folder_name[0:7]
    folder_name = folder_name.lstrip(data_folder_name + '_')
    if not os.path.exists('./' + year_folder_name):
        os.mkdir('./' + year_folder_name)
    if not os.path.exists('./' + year_folder_name + '/' + month_folder_name):
        os.mkdir('./' + year_folder_name + '/' + month_folder_name)
    if not os.path.exists('./' + year_folder_name + '/' + month_folder_name + '/' + data_folder_name):
        os.mkdir('./' + year_folder_name + '/' + month_folder_name + '/' + data_folder_name)
    if not os.path.exists('./' + year_folder_name + '/' + month_folder_name + '/' + data_folder_name + '/' + folder_name):
        os.mkdir('./' + year_folder_name + '/' + month_folder_name + '/' + data_folder_name + '/' + folder_name)
    
    
    i = 1
    for n in range(page_num):
        extra_str = '/' + str(n + 1) if n else ''
        print('downloading: ' + url + extra_str)
        try:
            response = get_url_response(url + extra_str)
        except:
            timeout_data = open('timeout_url.txt', 'a')
            timeout_data.write(url + '\n')
            timeout_data.close()
            return
        
        page_text = response.text
        #数据解析
        tree = etree.HTML(page_text)
        figure_list = tree.xpath('//figure[@class="wp-block-image size-large"]')
        src_str1 = '@data-lazy-src'
        src_str2 = '@src'
        for figure in figure_list:
            img_name = str(i) + '.jpg'
            i += 1
            #防止重复下载
            if os.path.exists('./' + year_folder_name + '/' + month_folder_name + '/' + data_folder_name + '/' + folder_name + '/' + str(i - 1) + '.jpg'):
                continue
            
            try:
                img_data, src_str1, src_str2 = get_img_data(figure, src_str1, src_str2)
            except:
                #记录连接超时的链接
                timeout_data = open('timeout_url.txt', 'a')
                timeout_data.write(url + '\n')
                timeout_data.close()
                return

            img_path = year_folder_name + '/' + month_folder_name + '/' + data_folder_name + '/' + folder_name + '/' + img_name
            with open(img_path,'wb')as fp:
                fp.write(img_data)
                print(img_name,'下载成功！')
    print(url, '爬取完成!')

#尝试爬取网页
@retry(stop_max_attempt_number = 5, wait_fixed = 1000)
def get_url_response(url):
    if __name__ == '__main__':
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
    response = requests.get(url, headers = headers, timeout = 5)
    return response

#尝试爬取图片
@retry(stop_max_attempt_number = 5, wait_fixed = 1000)
def get_img_data(figure, src_str1, src_str2):
    if __name__ == '__main__':
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
    try:
        img_data = requests.get(url = figure.xpath('./a/img/' + src_str1)[0], headers=headers, timeout = 5).content
        return img_data, src_str1, src_str2
    except:
        print("swaping sources...")
        time.sleep(1)
        try:
            img_data = requests.get(url = figure.xpath('./a/img/' + src_str2)[0], headers=headers, timeout = 5).content
            return img_data, src_str2, src_str1
        except:
            raise

#得到文件名
def get_folder_name(url):
    url = url.lstrip('https://www.4khd.com/')
    url = url.rstrip('.hmtl')
    url = url.replace('/','_')
    return url

#爬取网页的主函数
def page_crapper(page_url):
    try:
        strhtml = get_url_response(page_url)
    except:
        timeout_data = open('timeout_page_url.txt', 'a')
        timeout_data.write(page_url + '\n')
        timeout_data.close()
        return 1

    #得到该页所有图集的链接
    soup=BeautifulSoup(strhtml.text,'lxml')
    # 爬取主页的selector
    # data = soup.select('body > div > div > div > div.is-layout-flow.wp-block-query > ul > li > div > div.is-layout-flow.wp-block-group.is-style-no-margin > figure > a')
    # 爬取cosplay的selector
    data = soup.select('body > div > div > main > div.is-layout-constrained.entry-content.wp-block-post-content > div.is-layout-constrained.wp-container-62.wp-block-group.is-style-no-margin > div > ul > li > div > div.is-layout-flow.wp-block-group.is-style-no-margin > figure > a')
    if data == []:
        return 0
    for item in data:
        url = (item.get('href'))
        img_crapper(url, get_folder_name(url))
    return 1

### 开始主程序 ###

#设置原始网页链接
# cosplay原始网页
origin_url = 'https://www.4khd.com/pages/cosplay?query-3-page='
# 主页原始网页
# origin_url = 'https://www.4khd.com/page/2?query-3-page='

#爬取所有页的网页
i = 1
print('正在爬取网页' + origin_url + str(i))
while page_crapper(origin_url + str(i)) != 0: #判断是否到最后一页
    i += 1
    print('正在爬取网页' + origin_url + str(i))
print('所有网页爬取完成！')

#再次尝试之前tiomeout的page和url的爬取
print('尝试连接超时网页的再爬取')
f = open('./timeout_page_url.txt', 'r+')
timeout_page = f.readlines()
f.truncate(0)
f.close()
for page_url in timeout_page:
    page_crapper(page_url.rstrip('\n'))
f = open('./timeout_url.txt', 'r+')
timeout_url = f.readlines()
f.truncate(0)
f.close()
for url in timeout_url:
    url = url.rstrip('\n')
    img_crapper(url, get_folder_name(url))