# Learning

## Contents

Crawler 爬虫学习

## Crawler

视频来自网站Bilibili: 小北不熬夜啊啊/2022自学爬虫全套，学完可接项目（无私分享）

https://www.bilibili.com/video/BV1iu411C79S

## 4khd_crapper

爬取网站为https://4khd.com/

### 4khd_single_url_crapper.py

`4khd_single_url_crapper.py`的运行需要非官方库有requests, lxml

需要手动输入url和folder_name来进行爬取，图片保存在与运行文件同路径的名为folder_name的文件夹中

### 4khd_crapper.py

#### 运行依赖的库

`requirements.txt`记录运行需要的库，可通过`pip`功能安装：

```
pip install -r requirements.txt
```

#### 爬取功能介绍

可以从主页和cosplay界面进行图片的爬取（默认从主页进行爬取，主页内容包括cosplay中的内容，需要修改的请自行在代码中更改注释）

自动获取url进行爬取，图片以图集文件夹的形式分类保存在运行文件同路径下，以年、月、日进行分类

每次运行从主页第一页开始，直到最后一页停止，过程中会对图集完整性进行检查，下载缺失的图片

#### 连接超时的链接重爬取功能

如果有连接超时的链接，链接会被记录在运行文件同路径下的txt文件中，分别记录在`timeout_page_url.txt`（记录连接超时的页链接）和`timeout_url.txt`（记录连接超时的图连接）

在开始爬取时和完成所有图集的爬取后，会尝试一次对记录的超时链接爬取的重试，并记录依然连接超时的链接

#### 图片保存的路径设置

第一次运行文件是，会询问图片保存的路径，输入为空则默认选择运行文件所在的路径作为图片保存的路径

输入图片保存的路径后，会在运行文件所在的路径生成名为`config.yml`的配置文件

`config.yml`的默认设置为：

```
save_path: .\
save_path_request: true
```

在运行一次`4khd_crapper.py`后，`config.yml`中的`save_path_request`设置会变为`false`
