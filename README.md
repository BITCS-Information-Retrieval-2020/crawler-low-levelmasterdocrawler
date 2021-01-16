# crawler-low-levelmasterdocrawler

## 项目介绍

总项目为实现一个学术网站综合搜索引擎，用户可以检索到一篇论文的综合信息，不仅有pdf文件，还有oral视频，数据集，源代码等多模态信息。本项目为总项目下的爬虫模块，实现对crossmind、acl、paper with code、arxiv和paperweekly的爬取，实现了爬取学术论文相关的元信息、pdf文件、讲解视频和数据集等信息。

## 目录

[toc]

## 小组分工

| 姓名                                    | 学号       | 分工                           |
| --------------------------------------- | ---------- | ------------------------------ |
| [雷云霖](https://github.com/Lylist)     | 3120201035 | 系统架构搭建，scrapy健壮性优化 |
| [魏博](https://github.com/Web985)       | 3120201080 | 数据库，scrapy速度优化         |
| [李家伟](https://github.com/Captainr22) | 3120201036 | crossmind网站爬取              |
| [马放](https://github.com/BD-MF)        |3120201055  | acl网站爬取                    |
| [宦紫仪](https://github.com/hsnowsunny) |3220200891  | paperwithcode网站爬取          |
| [蔡建](https://github.com/MrdotCai)     |            | arxiv网站爬取，IP池开发        |
| [吴为伦](https://github.com/PoolSon)    |3120201082  | paperweekly网站爬取            |

## 功能特色

#### 1、支持分布式爬取

- 充分利用每个人的设备，一定程度上平摊成本，增加系统的性能及可扩展性

#### 2、支持增量式爬取

- 聚合多个网站上爬取结果，可设置定时任务定时启动爬取，持续搜集

#### 3、IP池爬取

- 部署了一个爬虫服务爬取免费可用的代理IP，向proxy服务发送请求即可获得一个随机可用的IP，增加爬虫的健壮性

#### 4、线程池爬取

- 多线程爬取数据，快人一步

#### 5、使用简单，全平台支持

- 支持Windows、Linux和MacOS平台运行，各组件积木式使用，修改配置文件后运行脚本即可快速使用

## 系统架构

#### 1、系统总体

![系统架构](./extra/system_ach.jpg)

本系统为分布式的，在远程端部署文件存储服务、数据库服务、IP池proxy服务和master节点。本地节点可以从master节点获取任务，之后爬取，将爬取的数据再传输到远程相关服务中。

这些服务都是可解耦合的，增加系统的稳定性。但资源与成本有限，这四个服务部署在一个服务器上了。

#### 2、爬虫服务

![爬虫架构](./extra/spider_ach.jpg)

本地爬虫先获取配置文件，这个可以本地修改也可以部署服务从master节点自动获取，然后通过中间件获取IP池服务提供的proxy，用这个proxy去请求网站，获得回复后解析页面，提取相关信息。然后送入下载组件，下载PDF、视频等数据。下载完成后上传到文件服务和数据库服务。然后处理下一个页面，直到所有任务完成。

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

Crossminds网站包括**论文的基本信息**（包括论文的名称、会议名称、作者信息、论文描述等），论文的**视频url信息**，**部分论文的pdf与code信息等**。我们按Conference分类爬取所有会议中的视频以及论文信息，共3100条视频数据。

#### 1.1\. 整体流程

Crossminds视频爬取流程主要分为两步：第一，在网页把所有视频的url信息爬取下来保存到本地。第二、通过不同方式访问不同类型的url进行视频爬取。

#### 1.2\. 论文信息爬取
Crossminds视频页是动态加载页面，我们分析了三种处理动态加载页面的方式：直接通过构造requests请求访问数据、通过selenium爬取数据以及通过splash爬取数据。由于直接通过requests访问数据的爬取速度比其他两种方式快得多，所以采用这种方式来爬取。具体过程如下：

   - 找到浏览器向服务器请求数据的url：https://api.crossminds.io/web/content/bycategory
   - 分析请求数据的url，浏览器像服务器发送的是POST请求，请求参数为Request Payload(json)格式。
   - 分析请求参数的规律：请求参数中**limit**表示每次返回的视频个数；**offset**为偏移量，初始值为0，**category**表示当前正在爬取什么会议的信息。
   - 分析返回数据：返回数据中，有用的信息包括**results**和**next_request**。其中，**results**中包含我们第一步需要的论文的所有信息。**next_rquest**为下一次浏览器要发送的请求参数，也就是说我们只需要找到浏览器的初始请求参数，不需要为POST请求的参数再找规律。
   - 使用代码模拟浏览器向数据库发送请求，动态构造请求参数得到所有数据。(先通过前一个页面得到目前所有会议的名称信息，请求参数中初始化的**offset**为0，接下来的请求参数从**next_request**中获取，当返回数据为**null**时，将**category**设置成下一个会议，直至所有数据爬取结束)。
   - 将数据以csv格式保存到本地。

#### 1.3\. 视频爬取
Crossminds中的视频包含三种格式：youtube_video,m3u8_video和Vimeo_video(3100条数据中仅有一条)。我们主要对前两种格式的video视频进行爬取。
1. youtube_video使用第三方工具pytube对youtube视频进行下载。

2. m3u8_video视频爬取：
   * 首先通过url解析m3u8文件，得到一个视频信息的文本文件。
   * 分析文本文件是否经过加密（Crossminds中的m3u8视频均未加密）
   * 通过视频文本文件中的url下载ts视频文件，这个ts文件为整个视频的子文件，每个ts视频为整个视频文件中的某几秒信息。
   * 合并所有ts视频为一个完整的m3u8视频文件。

3. 构造线程池快速下载视频
由于视频文件下载速度过慢，所以我们希望通过多线程的方式在同一时间一次性下载多个视频，提高视频的爬取速度。
我们在爬取视频文件的过程中，通过threadpool构造线程池，同时下载一个会议中的所有视频信息（例如CVPR2020中共有1645条视频，那么会同时启动1645个线程，使这1645条视频同时下载）。事实上，考虑到网络带宽的限制以及同时大量访问会使得ip地址被封的问题，在实际操作中我们使用没10秒启动一个线程，大大增加了视频的爬取速度。最终爬取3100条视频用时不超过12小时。

4. 构造ip池下载视频
虽然每10秒启动一个线程，对线程池进行了一定的限制，但这种快速访问仍然会造成封ip的现象，所以我们使用了ip代理池，访问每一个视频url的ip都是不同的，不会造成ip被封的问题。

#### 1.4\. pdf以及code的爬取
通过**正则表达式**解析**description**内容可以得到**300条**左右的pdf和code信息。然而由于视频数量远远大于pdf和code的数量，所以我们主要的pdf来源于小组其他成员爬取的**arxiv**和**paperwithcode**中的数据。我们以paper的title作为标识符对论文及pdf和code进行匹配，最终能为1686条视频匹配到其对应的pdf和code。

#### 1.5\. 具体运行
爬取Crossminds论文信息
```
python crawl_data.py
```
多线程下载视频:
```
python download_video.py
```
上传到mongoDB中，并于arxiv和paperwithcode中的数据匹配:
```
python rename.py
python dataManager.py
```

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
  │   └── rename.py
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

马放的两个移动硬盘以及他逝去的VPN。感谢学校网络中心这个月给我们每个人赠送的80G流量，没有让我们本就不富裕的家庭雪上加霜><!
