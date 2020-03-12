#!/usr/bin/env python3
# -*- coding:UTF-8-sig -*-

import os
from shutil import copyfile
import csv
from flask import Flask, flash, request, render_template, escape
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from datetime import datetime, timedelta, timezone


app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z$T4&*]c]/'

app.config['UPLOADED_PHOTOS_DEST'] = 'photos/'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # 文件大小限制，默认为16MB
timedict = {'am':'上午', 'pm':'下午'}

def seekgps(filepath, targetcol, offset, data):
    pass

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST' and 'photo' in request.files:

        username = request.form['username']
        temperature = request.form['temperature']
        f_temperature = '%.2f' % float(temperature)
        print(f_temperature)
        time = request.form['time']
        cntime = timedict[time]

        utc_t = datetime.utcnow().replace(tzinfo=timezone.utc)
        bjt = utc_t.astimezone(timezone(timedelta(hours=8)))
        bjt_date = bjt.strftime('%m%d')
        bjt_date_y = bjt.strftime('%Y-%m-%d')
        bjt_time = bjt.strftime('%H:%M%p')

        rename = username + '+五部+' + bjt_date + cntime
        subfolder = bjt_date + '/' + bjt_date + time + '/'
        
        listcsvpath = app.config['UPLOADED_PHOTOS_DEST'] + 'listcsv.csv'
        log_file = app.config['UPLOADED_PHOTOS_DEST'] + subfolder + bjt_date + time + '.csv'

        if os.path.exists(log_file) == False:
            os.makedirs(app.config['UPLOADED_PHOTOS_DEST'] + subfolder)
            copyfile(listcsvpath, log_file)
        with open(log_file, 'r+', encoding='utf-8-sig', newline='') as logcsv:
            usergps = logcsv.read().find(username)
            if usergps == -1:
                flash('【 ' + username + ' 】请输入正确的姓名', 'warning')
                return render_template('heat.html', message=bjt_date_y + ' ' + bjt_time)
            else:
                logcsv.seek(0)
                namecol = [row[0] for row in csv.reader(logcsv)]
                rownum = namecol.index(username)
                # 找到username在哪行

                logcsv.seek(0)
                # 把seek指针复位到开头，上一段代码执行后，指针到了最后

                for i in range(rownum):
                    logcsv.readline()
                # 读取username之前的几行，把指针移到username前

                cellseek = logcsv.tell() + len(username)*3 + 1
                logcsv.seek(cellseek)

                # logcsv.seek(cellseek)
                logcsv.write(f_temperature)

        filename = photos.save(request.files['photo'], folder=subfolder, name=rename + '.')  
        file_url = photos.url(filename)
        return render_template('show.html', username=username, cntime=cntime, temp=temperature, message=file_url)


    utc_t = datetime.utcnow().replace(tzinfo=timezone.utc)
    bjt = utc_t.astimezone(timezone(timedelta(hours=8)))
    bjt_date_y = bjt.strftime('%Y-%m-%d')
    bjt_time = bjt.strftime('%H:%M%p')
    return render_template('heat.html', message=bjt_date_y + ' ' + bjt_time)

@app.route('/listx')
def list_file():
    files_list = os.listdir(app.config['UPLOADED_PHOTOS_DEST'])
    file_url = '/listx'
    print(files_list)
    return render_template('listx.html', files_list=files_list, file_url=file_url)

@app.route('/listx/<path:path_name>')
def open_file(path_name):
    abs_path = app.config['UPLOADED_PHOTOS_DEST'] + escape(path_name)
    print('这是abs_path：' + str(abs_path))
    files_list = os.listdir(abs_path)
    url_list = []
    for file in files_list:
        file_path = abs_path + '/' + file
        print('这是file_path：' + str(file_path))
        if os.path.isfile(file_path):
            file_url = photos.url(escape(path_name)) + '/' + file
        else:
            file_url = '/listx/' + escape(path_name) + '/' + file
        print('这是file_url：' + str(file_url))
        url_list.append(file_url)
    print('这是url_list：' + str(url_list))
    # return render_template('listx.html', files_list=files_list, file_url=file_url, message='目录')
    return render_template('listx.html', url_list=url_list)

if __name__ == '__main__':
    app.run()