#爬取图片
import os.path
import requests
import time
from bs4 import BeautifulSoup
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
    
    #得到图集页数
    selector = 'body > div > div > main > div.is-layout-flex.wp-container-36.wp-block-columns > div > div > div:nth-child(1) > div.is-layout-flow.wp-block-group.is-style-default > div > figure > div.page-link-box > ul > li> a'
    try:
        page_num = 1 + len(BeautifulSoup(response.text, 'lxml').select(selector = selector))
    except:
        page_num = 1 + len(BeautifulSoup(response.text, 'html.parser').select(selector = selector))

    #文件会下载在你运行程序所在的目录下
    #创建文件夹(日期文件夹(年月日),图集文件夹)
    data_folder_name = folder_name[0:10]
    year_folder_name = data_folder_name[0:4]
    month_folder_name = data_folder_name[0:7]
    folder_name = folder_name.lstrip(data_folder_name + '_')
    path = './' + year_folder_name
    if not os.path.exists(path):
        os.mkdir(path)
    path += '/' + month_folder_name
    if not os.path.exists(path):
        os.mkdir(path)
    path += '/' + data_folder_name
    if not os.path.exists(path):
        os.mkdir(path)
    path += '/' + folder_name
    if not os.path.exists(path):
        os.mkdir(path)
    
    
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

        #数据解析
        selector = 'body > div > div > main > div > div > div > div:nth-child(1) > div.is-layout-flow.wp-block-group.is-style-default > div > figure > figure > a'
        try:
            figure_list = BeautifulSoup(response.text, 'lxml').select(selector = selector)
        except:
            figure_list = BeautifulSoup(response.text, 'html.parser').select(selector = selector)
        for item in figure_list:
            img_name = str(i) + '.jpg'
            i += 1
            #防止重复下载
            if os.path.exists(path + '/' + str(i - 1) + '.jpg'):
                continue

            figure = item.get('href')
            try:
                img_data = get_img_data(figure)
            except:
                #记录连接超时的链接
                timeout_data = open('timeout_url.txt', 'a')
                timeout_data.write(url + '\n')
                timeout_data.close()
                continue

            img_path = path + '/' + img_name
            with open(img_path,'wb')as fp:
                fp.write(img_data)
                print(img_name,'下载成功！')

    print(url, '爬取完成!')

#尝试爬取网页
@retry(stop_max_attempt_number = 10, wait_incrementing_start = 500,   wait_incrementing_increment = 500)
def get_url_response(url):
    if __name__ == '__main__':
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
    response = requests.get(url, headers = headers, timeout = 5)
    return response

#尝试爬取图片
@retry(stop_max_attempt_number = 10, wait_incrementing_start = 500,   wait_incrementing_increment = 500)
def get_img_data(url):
    if __name__ == '__main__':
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }
    response = requests.get(url, headers = headers, timeout = 5).content
    return response

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
    try:
        soup = BeautifulSoup(strhtml.text, 'lxml')
    except:
        soup = BeautifulSoup(strhtml.text, 'html.parser')
    # 爬取主页的selector
    selector = 'body > div > div > div > div.is-layout-flow.wp-block-query > ul > li > div > div.is-layout-flow.wp-block-group.is-style-no-margin > figure > a'
    # 爬取cosplay的selector
    # selector = 'body > div > div > main > div.is-layout-constrained.entry-content.wp-block-post-content > div.is-layout-constrained.wp-container-62.wp-block-group.is-style-no-margin > div > ul > li > div > div.is-layout-flow.wp-block-group.is-style-no-margin > figure > a'
    data = soup.select(selector = selector)
    if data == []:
        return 0
    for item in data:
        url = (item.get('href'))
        img_crapper(url, get_folder_name(url))
    return 1

#超时链接的重爬取
def timeout_url_crapper():
    if os.path.exists('./timeout_page_url.txt'):
        f = open('./timeout_page_url.txt', 'r+')
        timeout_page = f.readlines()
        f.truncate(0)
        f.close()
        for page_url in timeout_page:
            page_url = page_url.rstrip('\n')
            print('正在爬取网页' + page_url)
            page_crapper(page_url)
    if os.path.exists('./timeout_url.txt'):
        f = open('./timeout_url.txt', 'r+')
        timeout_url = f.readlines()
        f.truncate(0)
        f.close()
        for url in timeout_url:
            url = url.rstrip('\n')
            img_crapper(url, get_folder_name(url))
    empty_txt_delete()

#删除空的timeout_url文件
def empty_txt_delete():
    txt_list = ['./timeout_page_url.txt', './timeout_url.txt', './timeout_img_url.txt']
    for txt_name in txt_list:
        if os.path.exists(txt_name):
            if not os.path.getsize(txt_name):
                os.remove(txt_name)

### 开始主程序 ###

#先对已储存的tiomeout的page和url的爬取
print('对已记录的超时网页进行再爬取')
timeout_url_crapper()

#设置原始网页链接
# cosplay原始网页
# origin_url = 'https://www.4khd.com/pages/cosplay?query-3-page='
# 主页原始网页
# 吐槽：这个网页的页面管理实在是太垃圾了！一个网页可以有多种链接...
# origin_url = 'https://www.4khd.com/page/2?query-3-page='
# origin_url = 'https://www.4khd.com/?cst&query-3-page='
origin_url = 'https://www.4khd.com/?query-3-page='

#爬取所有页的网页
#爬取最近更新的内容，因为有时origin_url里的内容不一定是最新的
print('正在爬取网页https://www.4khd.com/')
page_crapper('https://www.4khd.com/')

#爬取剩余的内容
i = 1
print('正在爬取网页' + origin_url + str(i))
while page_crapper(origin_url + str(i)) != 0: #判断是否到最后一页
    i += 1
    print('正在爬取网页' + origin_url + str(i))
print('所有网页爬取完成！')

#再次尝试之前tiomeout的page和url的爬取
print('尝试连接超时网页的再爬取')
timeout_url_crapper()