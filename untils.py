# -*- coding:utf-8 -*-
__author__ = 'young'

import json
import urllib
import urllib2
import string
import threading
import time
import os

import Entity

task_count = 0;


def getAblums(qq, url):
    ablums = list()
    print url + qq + "&outstyle=2"
    request = urllib2.Request(url + qq + "&outstyle=2")
    f = urllib2.urlopen(request, timeout=10)
    response = f.read().decode('gbk')
    f.close()
    response = response.replace('_Callback(', '')
    response = response.replace(');', '')
    # print response
    if 'album' in json.loads(response):
        for i in json.loads(response)['album']:
            ablums.append(Entity.Album(i['id'], i['name'], i['total']))
    return ablums


def getPhotosByAlum(album, qq, url):
    photos = list()
    print url + qq + "&albumid=" + album.ID + "&outstyle=json"
    request = urllib2.Request(url + qq + "&albumid=" + album.ID + "&outstyle=json")
    f = urllib2.urlopen(request, timeout=10)
    response = f.read().decode('gbk')
    f.close()
    response = response.replace('_Callback(', '')
    response = response.replace(');', '')
    # print response
    if 'pic' in json.loads(response):
        for i in json.loads(response)['pic']:
            photos.append(Entity.Photo(i['url'], i['name'], album))
    return photos


maxThreadCount = 50
threadCount = 0
errorCount = 0
usebadImage = 0


def saveImage(path, photo, qq, alum_index, image_index):
    global threadCount
    global task_count
    global errorCount
    global usebadImage

    threadCount = threadCount + 1

    url = photo.URL.replace('\\', '')
    head = 'http://r'
    url = head + url[11:]
    url = url[0:-35] + '/r/' + url[-32:-20]

    print url

    qq_dir_path = path + os.path.sep + qq
    alum_path = qq_dir_path + os.path.sep + alum_index + '_' + photo.Album.Name
    image_file_path = alum_path + os.path.sep + photo.Name + '_' + image_index + '.jpeg'

    if not os.path.exists(image_file_path):

        try:
            f = urllib2.urlopen(url, timeout=30000)
            data = f.read()
            f.close()

            if not os.path.exists(qq_dir_path):
                os.mkdir(qq_dir_path)
            if not os.path.exists(alum_path):
                os.mkdir(alum_path)

            with open(alum_path + os.path.sep + photo.Name + '_' + image_index + '.jpeg', "wb") as code:
                code.write(data)
                code.close()
        except Exception, ex:
            print 'ERROR ', url, Exception, ex
            errorCount = errorCount + 1
            print 'errorCount = %s' % errorCount

            f = urllib2.urlopen(photo.URL.replace('\\', ''), timeout=30000)
            data = f.read()
            f.close()

            if not os.path.exists(qq_dir_path):
                os.mkdir(qq_dir_path)
            if not os.path.exists(alum_path):
                os.mkdir(alum_path)

            with open(alum_path + os.path.sep + photo.Name + '_' + image_index + '.jpeg', "wb") as code:
                code.write(data)
                code.close()
            usebadImage = usebadImage + 1
            print 'usebadImage = %s' % usebadImage

    task_count = task_count + 1
    print 'task finish: alum=' + photo.Album.Name, photo.Name + '_' + image_index + '.jpeg'
    print 'task_count = %s' % task_count
    threadCount = threadCount - 1


def save_photos(qq, path=Entity.savepath):
    print u'获取：' + qq + u'的相册信息'
    ablums = getAblums(qq, Entity.albumbase1)
    if len(ablums) > 0:
        for i, a in enumerate(ablums):
            if a.Count > 0:
                print u'开始下载第' + str(i + 1) + u'个相册'
                photos = getPhotosByAlum(a, qq, Entity.photobase1)
                for index, p in enumerate(photos):

                    while threadCount > maxThreadCount:
                        time.sleep(1)

                    t = threading.Thread(target=saveImage, args=(path, p, qq, str(i), str(index),))
                    t.start()
                    # saveImage(path, p, qq, str(i) + '_' + str(index))
    else:
        print u'读取到得相册个数为0'
