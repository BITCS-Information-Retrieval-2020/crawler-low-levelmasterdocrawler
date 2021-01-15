import pymongo
import pandas as pd
import paramiko
from scp import SCPClient
# import yaml
import os


class MongoManager:
    # basic interaction with mongodb
    def __init__(self, ip="10.4.20.69", port="27017"):
        # self.myclient = pymongo.MongoClient("mongodb://" + ip + ":" + port + "/")
        self.myclient = pymongo.MongoClient("mongodb://10.4.20.69:27017/")
        self.dblist = self.myclient.list_database_names()
        self.mydb = None
        self.collist = None
        self.mycol = None

    def get_dblist(self):
        return self.dblist

    def get_collist(self):
        return self.collist

    def create_db(self, dbname):
        if dbname not in self.dblist:
            self.mydb = self.myclient[dbname]

    def select_db(self, dbname):
        if dbname in self.dblist:
            self.mydb = self.myclient[dbname]
            self.collist = self.mydb.list_collection_names()
            print("database:%s" % (dbname))
        else:
            print("ERROR: database %s not found" % (dbname))

    def create_col(self, colname):
        if colname not in self.collist:
            self.mycol = self.mydb[colname]

    def delete_col(self, colname):
        mycol = self.mydb[colname]
        mycol.drop()

    def select_col(self, colname):
        if colname in self.collist:
            self.mycol = self.mydb[colname]
            print("collection:%s" % (colname))
        else:
            print("ERROR: collection %s not found" % (colname))

    def get_amount(self, myquery=None):
        if myquery is None:
            res = self.mycol.estimated_document_count()
        else:
            res = self.mycol.count_documents(myquery)
        return res

    def find(self, myquery=None, show_list=None, hide_list=None):
        # myquery字典类型, show_list 和 hide_list 为列表类型
        if show_list is not None:
            show_dict = {key: 1 for key in show_list}
        elif hide_list is not None:
            show_dict = {key: 0 for key in hide_list}
        else:
            show_dict = None

        # show_dict["_id"] = 0
        if myquery is not None:
            # TODO
            pass
        else:
            myquery = None

        docs = self.mycol.find(myquery, show_dict)
        docs_list = [doc for doc in docs]
        return docs_list

    def insert_one(self, newdoc):
        # 插入一条文档, newdoc为字典
        rts = self.mycol.insert_one(newdoc)
        print("1 records have been inserted")
        return rts.inserted_id

    def insert_many(self, newdocs):
        # 插入多条文档, newdocs为列表, 元素为字典
        rts = self.mycol.insert_many(newdocs)
        print("%d records have been inserted" % len(rts.inserted_ids))
        return rts.inserted_ids

    def update_records(self, myquery, newvalues):
        # 更新多条文档, myquery 为字典, newvalues 为字典
        newvalues = {"$set": newvalues}
        rts = self.mycol.update_many(myquery, newvalues)
        print("%d records have been updated" % rts.modified_count)
        return rts.modified_count

    def delete_records(self, myquery):
        # 删除多条文档, myquery 为字典, newvalues 为字典
        rts = self.mycol.delete_many(myquery)
        print("%d records have been deleted" % rts.deleted_count)
        return rts.deleted_count

    def push_one(self, newdoc, mainkey="_id"):
        # 若重复, 则将以新文档为主，添加旧文档中的缺失信息更新至数据库, 否则直接插入数据库
        # newdoc 为字典, mainkey 为字符串, 用于查重匹配
        myquery = {mainkey: newdoc[mainkey]}
        docs = self.find(myquery)
        print("found %d similar records of %s:%s" %
              (len(docs), mainkey, newdoc[mainkey]))
        # if len(docs) == 0:
        #     self.insert_one(newdoc)
        # else:
        #     for doc in docs:
        #         newvalues = newdoc
        #         for key in doc.keys():
        #             if key not in newdoc.keys() or newdoc[key] is None:
        #                 newvalues[key] = doc[key]
        #         if len(newvalues) != 0:
        #             self.update_records(doc, newvalues)

    def push_many(self, newdocs, mainkey="_id"):
        # 用法同 push_one, 输入为列表
        for newdoc in newdocs:
            self.push_one(newdoc, mainkey)


class FileManager:
    def __init__(self, host="10.4.20.69", port=22, user_name, passwd):
        self.host = host
        self.port = port
        self.user = user_name
        self.passwd = passwd
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self.ssh_client.connect(host, port, user_name, passwd)
        self.scpclient = SCPClient(
            self.ssh_client.get_transport(), socket_timeout=15.0)

    def upload_file(self, local_path, remote_path):
        try:
            self.scpclient.put(local_path, remote_path)
        except FileNotFoundError as e:
            print("ERROR: Can't find local file at: " + local_path)
            print(e)
        else:
            print("Successful upload 1 file! ")

    def get_file(self, remote_path, local_path):
        try:
            self.scpclient.get(remote_path, local_path)
        except FileNotFoundError as e:
            print("ERROR: Can't find remote file at: " + remote_path)
            print(e)
        else:
            print("Successful download 1 file! ")

    def close(self):
        self.ssh_client.close()


if __name__ == "__main__":
    mm = MongoManager('10.4.20.96', "27017")
    # print(mm.get_dblist())
    mm.select_db("lowermaster")
    mm.select_col("crawler")
    fm = FileManager(host='10.4.20.69', port=22,
                     user_name='***', passwd='***')
    # videos_dir = './test_video/'
    # video_paths = os.listdir(videos_dir)
    # print(video_paths)
    # exit()
    # for video in video_paths:
    #     item = {}
    #     item['_id'] = video[0:-4]
    #     item['videoPath'] = "/home/work/crawler/crossmind/" + video
    #     item['videoUrl'] = "https://"
    #     item['title'] = ""
    #     fm.upload_file(videos_dir + video, "/home/work/crawler/crossmind/" + video)
    #     mm.push_one(item)
    # fm.close()
    csv_list = os.listdir('./outputfinal/')
    video_dir = os.listdir('./crossmind/')
    for filename in csv_list:
        # print(f'filename={filename.format()}')
        df = pd.read_csv(f'./outputfinal/{filename}', encoding='utf-8')
        # print(len(video_dir))
        for index, row in df.iterrows():
            video = str(row['_id']) + '.mp4'
            if video in video_dir:
                item = {}
                item['_id'] = row['_id']
                item['videoPath'] = "/home/work/crawler/crossmind/" + video
                item['videoUrl'] = row['videoUrl']
                item['title'] = row['title']
                item['abstract'] = row['abstract']
                item['subjects'] = row['subjects']
                # fm.upload_file("./test_video2/" + video, "/home/work/crawler/crossmind/" + video)
                mm.push_one(item)
            # fm.close()

    # mm.push_many([{"likes": 81, "name": "test"}, {"likes": 97, "name": "lalala"}], "likes")
    # # mm.update_records({"likes": 100}, {"unlink": 20})
    # # mm.delete_records({"likes": 88})
    # res = mm.find(hide_list=["_id"])
    # for i in res:
    #     print(i)
    #
    # file_manager = FileManager()
    # file_manager.get_file("/home/lyl/output.json", "./output.json")
