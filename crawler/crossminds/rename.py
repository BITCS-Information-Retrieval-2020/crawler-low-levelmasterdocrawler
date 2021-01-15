import os
import re

# path = input('./test2/')
path = './test_video/'
dirs = os.listdir(path)


def delete_meeting(str):
    str = re.sub(
        '10minvideo|2020icra|cpp2020|crossdomain|[a-e][1-9][a-g]|oralsession[1-9][1-9][a-g]|emnlp2020talk'
        '|specialeventatecai2020|longversion|acl2020|bmvc2020|cikm2020|corl2020|cvpr2020|cvpr2019|ecai2020'
        '|eccv2020|emnlp2020|gotoconference|gtc2020|hotchips2020|icalp2020|iccv2019|icml2020|icra2020|miccai2020'
        '|neurips2019|neurips2020|podc2020|popl2020|recsys2020|sail2020|sigir2020|spaa2020|stoc2020|goto2020|goto2019'
        '|iccv19oralsession[0-9][0-9][a-c|iccv19oralsession[0-9][0-9]|bestpaperinautomation|bestpaperfinalist'
        '|bestpaperinunmannedaerialvehicles|bestpaperhonorablemention|bestdemoaward|koenderinkaward'
        '|bestpaperpresentationaward|orallongtalk|spotlightfull|bestsystempaper|bestthemepaper|amazon|beststudentpaper'
        '|honorablemention|awardnominee|oralpresentationin|oralsession[0-9]|oral|amazonscience|cikmtraining25aug2020'
        '|4k|paperhighlight|nominee|spotlightbrief|spotlighttalk[0-9][0-9][0-9]|spotlighttalk[0-9][0-9]|keynote[0-9]'
        '|keynote|spotlighttalk[0-9]|tutorial[0-9]|bestpaper|spotlight|workshop[0-9]|iccv19|longpresentation|longtalk'
        '|eccv20|10mtalk|longvideo|cvpr20|1minutetalk|10mintalk|1stplace|10minsvideo|[a-z][1-3][a-b]|presentation'
        '|session[1-9][a-c]|session[1-9][0-9][a-c]|3mintalk|icra20',
        '', str)
    return str


def get_new_name(str):
    str = str[:-4]
    # 去除特殊符号
    str = re.sub(
        u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", str)
    # 大写转小写
    str = str.lower()
    # 去除前面的会议
    str = delete_meeting(str)
    return str + '.mp4'


def get_new_name2(str):
    # str = str[:-4]
    # 去除特殊符号
    str = re.sub(
        u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", str)
    # 大写转小写
    str = str.lower()
    # 去除前面的会议
    str = delete_meeting(str)
    return str


if __name__ == '__main__':
    for file in dirs:
        # print(file[:-4])
        newname = get_new_name(file)
        print(newname)
        os.rename(os.path.join(path, file), os.path.join(path, newname))
