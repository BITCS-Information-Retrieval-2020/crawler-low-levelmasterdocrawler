# crawler-low-levelmasterdocrawler

## 项目介绍

总项目为实现一个学术网站综合搜索引擎，用户可以检索到一篇论文的综合信息，不仅有pdf文件，还有oral视频，数据集，源代码等多模态信息。本项目为总项目下的爬虫模块，实现对crossmind、acl、paper with code、arxiv和paperweekly的爬取，实现了爬取学术论文相关的元信息、pdf文件、讲解视频和数据集等信息。

## 目录

pass

## 小组分工

| 姓名                                    | 学号       | 分工                           |
| --------------------------------------- | ---------- | ------------------------------ |
| [雷云霖](https://github.com/Lylist)     | 3120201035 | 系统架构搭建，scrapy健壮性优化 |
| [魏博](https://github.com/Web985)       |            | 数据库，scrapy速度优化         |
| [李家伟](https://github.com/Captainr22) |            | crossmind网站爬取              |
| [马放](https://github.com/BD-MF)        |3120201055  | acl网站爬取                    |
| [宦紫仪]()                              |            | paperwithcode网站爬取          |
| [蔡建](https://github.com/MrdotCai)     |            | arxiv网站爬取，IP池开发        |
| [吴为伦]()                              |            | paperweekly网站爬取            |

## 功能特色

#### 1、支持分布式爬取

- 充分利用每个人的设备，一定程度上平摊成本，增加系统的性能及可扩展性

#### 2、支持增量式爬取

- 聚合多个网站上爬取结果，可设置定时任务定时启动爬取，持续搜集

#### 3、IP池爬取

- 部署了一个爬虫服务爬取免费可用的代理IP，向`http://10.4.20.69:5010/get/`发送请求即可获得一个随机可用的IP，增加爬虫的健壮性

#### 4、线程池爬取

- 多线程爬取数据，快人一步

#### 5、使用简单，全平台支持

- 支持Windows、Linux和MacOS平台运行，各组件积木式使用，修改配置文件后运行脚本即可快速使用

## 系统架构

#### 1、系统总体

![系统架构](./extra/system_ach.jpg)

本系统为分布式的，在远程端部署文件存储服务、数据库服务、IP池proxy服务和master节点。本地节点可以从master节点获取任务，之后爬取，将爬取的数据再传输到远程相关服务中。

这些服务都是可解耦合的，增加系统的稳定性。但资源与成本有限，这四个服务部署在一个服务器上了。



## 执行方法及原理

### 一、 执行方法

#### 1、运行环境

系统：Windows、Linux、MacOS

软件：python3

#### 2、安装依赖

```
pip install -r requirements.txt
```

#### 3、运行

- 将仓库克隆至本地

- 修改`config.yaml`和`start_urls.txt`(如果需要)

- Windows系统执行`start.bat`文件，Linux、MacOS执行`start.sh`即可快速运行

### 二、各模块执行原理

#### 1、Crossmind

@ljw

#### 2、ACL

@mf

#### 3、arxiv

@cj

#### 4、Paper with code

@hzy

#### 5、paperweekly

@wwl

#### 6、IP池服务

@cj

#### 7、数据库

@wb

## 整体效果

pass

## 代码及文件结构

- #### 代码结构

  ```
  .
  ├── conf
  │   ├── config.yaml  //运行配置文件
  │   └── logging_config.yaml //log配置文件(无需修改)
  ├── crawler
  │   ├── __init__.py
  │   ├── dataManager.py //数据库与服务器交互组件
  │   ├── items.py //爬取信息定义
  │   ├── middlewares.py //IP池中间件
  │   ├── pdfToJson //抽取PDF内容组件，检索组提供
  │   │   ├── __init_.py
  │   │   ├── client.py
  │   │   ├── config.json
  │   │   ├── pdfClient.py
  │   │   ├── requirements.txt
  │   │   ├── run.py
  │   │   └── xmlToJson.py
  │   ├── pipelines.py //各网站下载组件
  │   ├── settings.py
  │   └── spiders
  │       ├── __init__.py
  │       ├── acl_crawler.py //acl解析
  │       ├── arxiv_crawler.py //arxiv解析
  │       ├── papersWithCode_crawler.py //paperwithcode解析
  │       └── paperweekly_crawler.py //paperweekly解析
  ├── crossminds
  │   ├── crawl_data.py
  │   ├── dataManager.py
  │   ├── download_m3u8_video.py
  │   ├── download_video.py
  │   ├── download_youtube_video.py
  │   ├── log.py
  │   ├── m3u8
  │   ├── m3u8_video
  │   ├── outputfinal
  │   ├── rename.py
  │   └── youtube_video
  ├── download //下载本地存储文件夹
  ├── logs //log日志存储文件夹
  ├── output.json //爬取结果本地备份文件
  ├── run_crawler.py //执行主体
  ├── scrapy.cfg
  ├── start.bat //windows运行脚本
  ├── start.sh //Unix运行脚本
  └── start_urls.txt //爬取的站点
  ```

- #### 文件结构

  ```
  .
  ├── crossmind //crossmind下载视频存储
  ├── video //acl下载视频存储
  └── paper //所有pdf存储
  ```

  

## 特别鸣谢
