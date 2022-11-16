#爬取图片
import os.path
import requests
import time
from bs4 import BeautifulSoup
#超时重试处理
from retrying import retry
#配置文件设置
import ruamel.yaml

#爬取图片
def img_crapper(url):
    #此处的url存放想要下载图片的网址
    #folder_name是下载的文件夹名字
    folder_name = get_folder_name(url)
    try:
        response = get_url_response(url)
    except:
        timeout_data = open(save_path + 'timeout_url.txt', 'a')
        timeout_data.write(url + '\n')
        timeout_data.close()
        return
    downloading_progress_write('url', url)

    #得到图集页数
    try:
        page_num = 1 + len(BeautifulSoup(response.text, 'lxml').select(selector = url_selector))
    except:
        page_num = 1 + len(BeautifulSoup(response.text, 'html.parser').select(selector = url_selector))

    #文件会下载在你运行程序所在的目录下
    #创建文件夹(日期文件夹(年月日),图集文件夹)
    data_folder_name = folder_name[0:10]
    year_folder_name = data_folder_name[0:4]
    month_folder_name = data_folder_name[0:7]
    folder_name = folder_name.lstrip(data_folder_name + '_')
    path = save_path + year_folder_name
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
    
    #开始爬取图片
    i = 1
    for n in range(page_num):
        extra_str = '/' + str(n + 1) if n else ''
        print('downloading: ' + url + extra_str)
        try:
            response = get_url_response(url + extra_str)
        except:
            timeout_data = open(save_path + 'timeout_url.txt', 'a')
            timeout_data.write(url + '\n')
            timeout_data.close()
            return

        #数据解析
        try:
            figure_list = BeautifulSoup(response.text, 'lxml').select(selector = img_selector)
        except:
            figure_list = BeautifulSoup(response.text, 'html.parser').select(selector = img_selector)
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
                timeout_data = open(save_path + 'timeout_url.txt', 'a')
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
    response = requests.get(url, headers = headers, timeout = 5)
    return response

#尝试爬取图片
@retry(stop_max_attempt_number = 10, wait_incrementing_start = 500,   wait_incrementing_increment = 500)
def get_img_data(url):
    response = requests.get(url, headers = headers, timeout = 5).content
    return response

#得到文件名
def get_folder_name(url):
    url = url.lstrip('https://www.4khd.com/')
    url = url.rstrip('.hmtl')
    url = url.replace('/', '_')
    return url

#爬取网页的主函数
def page_crapper(page_url):
    try:
        strhtml = get_url_response(page_url)
    except:
        timeout_data = open(save_path + 'timeout_page_url.txt', 'a')
        timeout_data.write(page_url + '\n')
        timeout_data.close()
        return 1

    #得到该页所有图集的链接
    try:
        soup = BeautifulSoup(strhtml.text, 'lxml')
    except:
        soup = BeautifulSoup(strhtml.text, 'html.parser')
    data = soup.select(selector = page_selector)
    if data == []:
        return 0
    for item in data:
        url = (item.get('href'))
        img_crapper(url)
    return 1

#记录下载进度（下载的主界面链接page_url和图集链接url）
def downloading_progress_write(type, item):
    if type == 'page':
        config_data['downloading_progress_page'] = int(item)
    elif type == 'url':
        config_data['downloading_progress_url'] = item
    f = open('./config.yml', 'w', encoding = 'utf-8')
    yaml.dump(config_data, f)
    f.close()

#超时链接的重爬取
def timeout_url_crapper():
    if os.path.exists(save_path + 'timeout_page_url.txt'):
        f = open(save_path + 'timeout_page_url.txt', 'r+')
        timeout_page = f.readlines()
        f.truncate(0)
        f.close()
        for page_url in timeout_page:
            page_url = page_url.rstrip('\n')
            print('正在爬取网页' + page_url)
            page_crapper(page_url)
    if os.path.exists(save_path + 'timeout_url.txt'):
        f = open(save_path + 'timeout_url.txt', 'r+')
        timeout_url = f.readlines()
        f.truncate(0)
        f.close()
        for url in timeout_url:
            url = url.rstrip('\n')
            img_crapper(url)
    empty_txt_delete()

#删除空的timeout_url文件
def empty_txt_delete():
    txt_list = [save_path + 'timeout_page_url.txt', save_path + 'timeout_url.txt', save_path + 'timeout_img_url.txt']
    for txt_name in txt_list:
        if os.path.exists(txt_name):
            if not os.path.getsize(txt_name):
                os.remove(txt_name)

#配置文件全部读取
def read_yml_all(yml_path):
    try:
        f = open(yml_path, 'r', encoding = 'utf-8')
        yml_config = yaml.load(f)
        f.close()
        return yml_config
    except:
        return None

#配置文件初始设置
def set_config_default():
    config_data_str = """\
#图片保存的路径，（默认为.\，即与运行文件同一路径）
save_path: .\\
#爬取界面选择，默认为主页main
#其余选项有cosplay，album
page_choice: main

#是否请求图片保存路径的设置（true为是，默认为true）
request_save_path: true
#是否请求爬取界面的选择（true为是，默认为true）
request_page_choice: true

#记录爬取进度
#爬取的界面页数，默认为1，即第一页
downloading_progress_page: 1
#爬取的图集链接，默认为none，即没有正在爬取的图集
downloading_progress_url: none
#记录是否已经全部爬取完成
download_success: false
"""
    config_data = yaml.load(config_data_str)
    f = open('./config.yml', 'w', encoding = 'utf-8')
    yaml.dump(config_data, f)
    f.close()

#保存config文件
def save_config():
    f = open('./config.yml', 'w', encoding = 'utf-8')
    yaml.dump(config_data, f)
    f.close()

### 开始主程序 ###

## 全局变量设置 ##

#page_url的字典（主页和分类子页）
page_dict = {
    'main': {
        # 吐槽：这个网页的页面管理实在是太垃圾了！一个网页可以有多种链接...
        'choice1': 'https://www.4khd.com/?query-3-page=',
        'choice2': 'https://www.4khd.com/page/2?query-3-page=',
        'choice3': 'https://www.4khd.com/?cst&query-3-page='
    },
    'cosplay': 'https://www.4khd.com/pages/cosplay?query-3-page=',
    'album': 'https://www.4khd.com/pages/album?query-3-page='
}

#selector的字典
selector_dict = {
    'page_selector': {
        'main': 'body > div > div > div > div.is-layout-flow.wp-block-query > ul > li > div > div.is-layout-flow.wp-block-group.is-style-no-margin > figure > a',
        'cosplay': 'body > div > div > main > div.is-layout-constrained.entry-content.wp-block-post-content > div.is-layout-constrained.wp-container-62.wp-block-group.is-style-no-margin > div > ul > li > div > div.is-layout-flow.wp-block-group.is-style-no-margin > figure > a',
        'album': 'body > div > div > main > div.is-layout-constrained.entry-content.wp-block-post-content > div.is-layout-constrained.wp-container-62.wp-block-group.is-style-no-margin > div > ul > li > div > div.is-layout-flow.wp-block-group.is-style-no-margin > figure > a'
    },
    #the old url_selector isn't the best though it's usable
    # 'url_selector': 'body > div > div > main > div.is-layout-flex.wp-container-36.wp-block-columns > div > div > div:nth-child(1) > div.is-layout-flow.wp-block-group.is-style-default > div > figure > div.page-link-box > ul > li> a',
    #new url_selector
    'url_selector': 'body > div > div > main > div > div > div > div:nth-child(1) > div.is-layout-flow.wp-block-group.is-style-default > div > figure > div.page-link-box > ul > li> a',
    'img_selector': 'body > div > div > main > div > div > div > div:nth-child(1) > div.is-layout-flow.wp-block-group.is-style-default > div > figure > figure > a'
}

#请求头伪装
if __name__ == '__main__':
        headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
        }

#配置文件的导入
yaml = ruamel.yaml.YAML()
try:
    config_data = read_yml_all('./config.yml')
except:
    set_config_default()
    config_data = read_yml_all('./config.yml')

#载入保存图片的路径和所要爬取界面的设置
try:
    save_path = config_data['save_path']
    page_choice = config_data['page_choice']
    request_save_path = config_data['request_save_path']
    request_page_choice = config_data['request_page_choice']
except:
    print('config.yml数据错误，已重置文件')
    set_config_default()
    config_data = read_yml_all('./config.yml')
    save_path = config_data['save_path']
    page_choice = config_data['page_choice']
    request_save_path = config_data['request_save_path']
    request_page_choice = config_data['request_page_choice']
#查询是否要请求修改图片保存路径，默认是
#询问一次之后，之后就不再询问（可以到config.yml将request_save_path改为true来再开启一次询问）
if request_save_path:
    config_data['request_save_path'] = False
    print('请输入图片要保存到的路径（空着为保存到该运行文件所在的路径）')
    save_path = input()
    if save_path == '':
        save_path = '.\\'
    else:
        config_data['save_path'] = save_path
    save_config()
save_path += '/'

#查询是否要选择爬取的界面，默认是
#询问一次之后，之后就不再询问（可以到config.yml将request_page_choice改为true来再开启一次询问）
if request_page_choice:
    config_data['request_page_choice'] = False
    print('请选择要爬取的界面[main, cosplay, album]（默认为main，即主页；输入空为默认）：')
    page_choice = input()
    while not page_choice in ['', 'main', 'cosplay', 'album']:
        print('输入有误，请重新输入[main, cosplay, album]：')
        page_choice = input()
    if page_choice == '':
        page_choice = 'main'
    if config_data['page_choice'] != page_choice:
        config_data['page_choice'] = page_choice
        config_data['downloading_progress_page'] = 1  #改变爬取界面的设定，将从第一页开始爬取
        config_data['download_success'] = False #改变爬取为未完成
        save_config()
if page_choice == 'main':
    origin_url = page_dict[page_choice]['choice1']
else:
    origin_url = page_dict[page_choice]

#selector的导入
#page_selector为界面选择器，url_selector为图集选择器，img_selector图片选择器
page_selector = selector_dict['page_selector'][page_choice]
url_selector = selector_dict['url_selector']
img_selector = selector_dict['img_selector']

## 爬取程序 ##

#载入爬取进度
print('正在载入爬取进度...')
try:
    downloading_progress_page = config_data['downloading_progress_page']
    downloading_progress_url = config_data['downloading_progress_url']
    download_success = config_data['download_success']
except:
    print('config.yml数据错误，已重置文件')
    set_config_default()
    config_data = read_yml_all('./config.yml')
    downloading_progress_page = config_data['downloading_progress_page']
    downloading_progress_url = config_data['downloading_progress_url']
    download_success = config_data['download_success']
print('载入完成！')
#如果已经爬取完成，则询问是否重新开始一轮爬取
if download_success:
    print('爬取已经完成，是否开始新一轮爬取？[y/n]')
    crapper_request = input()
    if crapper_request == 'y':
        config_data['download_success'] = False
        config_data['downloading_progress_page'] = 1
        config_data['downloading_progress_url'] = 'none'
        download_success = False
        downloading_progress_page = 1
        downloading_progress_url = 'none'
        save_config()
#对之前没有爬取完的图集完成爬取
if downloading_progress_url != 'none':
    print('对之前没有爬取完的图集完成爬取')
    img_crapper(downloading_progress_url)
    config_data['downloading_progress_url'] = 'none'
    save_config()

#先对已储存的tiomeout的page和url的爬取
print('对已记录的超时网页进行再爬取')
timeout_url_crapper()
print('再爬取完成！')

#爬取最近更新的内容，因为有时origin_url里的内容不一定是最新的
#只会在爬取主页的时候运行
if page_choice == 'main':
    print('正在爬取最新内容')
    page_crapper('https://www.4khd.com/')
    print('最新内容爬取完成！')

#爬取page_choice界面下所有页的网页
#页数载入到还未爬取的页码
if not download_success:
    i = downloading_progress_page
    print('正在爬取网页' + origin_url + str(i))
    downloading_progress_write('page', i)
    while page_crapper(origin_url + str(i)) != 0: #判断是否到最后一页
        i += 1
        print('正在爬取网页' + origin_url + str(i))
        downloading_progress_write('page', i)
    config_data['download_success'] = True
    save_config()
print('所有网页爬取完成！')

#再次尝试之前tiomeout的page和url的爬取
print('尝试对连接超时网页的再爬取')
timeout_url_crapper()
print('再爬取完成！')