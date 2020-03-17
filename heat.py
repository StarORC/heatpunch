#!/usr/bin/env python3
# -*- coding:UTF-8-sig -*-

import os
from shutil import copyfile
import csv
from flask import Flask, flash, request, render_template, escape
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class, UploadNotAllowed
from datetime import datetime, timedelta, timezone
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z$T4&*]c]/'

app.config['UPLOADED_PHOTOS_DEST'] = 'photos/'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # 文件大小限制，默认为16MB
timedict = {'am':'上午', 'pm':'下午'}

def seekgps(filepath, targetcol, offset, data):
    pass

def scale_tag(old_file, new_path, size, text):
    with Image.open(old_file) as im:
        (ow, oh) = im.size
        scale = size/max(ow, oh)
        out = im.resize((int(ow*scale), int(oh*scale)))

        # 给图片加标签
        fnt = ImageFont.truetype('static/fonts/SourceHanSansSC-Medium.otf', 36)
        d = ImageDraw.Draw(out)
        d.polygon([(30,60), (40,50), (460,50), (445,78), (460,105), (40,105), (30,95)], fill=(4,188,212))
        d.text((45,50), text, font=fnt, fill=(255,255,255))

        if os.path.exists(new_path) == False:
            os.makedirs(new_path)
        new_file = new_path + '/' + os.path.split(im.filename)[1]
        out.save(new_file)
    return(new_file)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST' and 'photo' in request.files:
        # 格式化时间
        utc_t = datetime.utcnow().replace(tzinfo=timezone.utc)
        bjt = utc_t.astimezone(timezone(timedelta(hours=8)))
        bjt_date = bjt.strftime('%m%d')
        bjt_date_y = bjt.strftime('%Y-%m-%d')
        bjt_time = bjt.strftime('%H:%M%p')
        bjt_time_s = bjt.strftime('%H:%M:%S')

        request_files = request.files['photo']
        username = request.form['username']
        temperature = request.form['temperature']
        temperature_f = '%.2f' % float(temperature)
        time = request.form['time']
        cntime = timedict[time]

        try:
            ext = request_files.filename.split('.')[1]
        except:
            ext = '无扩展名'
            user_info = [username, cntime, temperature, ext, bjt_time_s]
            print('可能是无扩展名错误：' + str(user_info))
            flash(['照片格式错误，请重新上传', '微信告诉刘静怡，您用什么软件编辑了照片？'], 'danger')
            return render_template('heat.html', time_message=bjt_date_y + ' ' + bjt_time)

        user_info = [username, cntime, temperature, ext, bjt_time_s]

        rename = username + '+五部+' + bjt_date + cntime
        subfolder = bjt_date + '/' + bjt_date + time + '/'
        
        # 开始写入csv文件
        listcsv_file = app.config['UPLOADED_PHOTOS_DEST'] + 'listcsv.csv'
        log_file = app.config['UPLOADED_PHOTOS_DEST'] + subfolder + bjt_date + time + '.csv'

        if os.path.exists(log_file) == False:
            os.makedirs(app.config['UPLOADED_PHOTOS_DEST'] + subfolder)
            copyfile(listcsv_file, log_file)
        with open(log_file, 'r+', encoding='utf-8-sig', newline='') as logcsv:
            usergps = logcsv.read().find(username)
            if usergps == -1:
                flash(['【 ' + username + ' 】请输入正确的姓名', ''], 'warning')
                return render_template('heat.html', time_message=bjt_date_y + ' ' + bjt_time)
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
                # 此处缺少功能：如果有记录体温数据，是否再次上报
                # logcsv.seek(cellseek)
                logcsv.write(temperature_f)

        #开始保存图片
        try:
            photo_path = photos.save(request_files, folder=subfolder, name=rename + '.')
        except UploadNotAllowed:
            print('可能是非图片扩展名：' + str(user_info))
            flash(['照片格式错误，请重新上传', '微信告诉刘静怡，您用什么软件编辑了照片？'], 'danger')
            return render_template('heat.html', time_message=bjt_date_y + ' ' + bjt_time)
        else:
            # 函数scale(old_file, new_path, size)修改图片尺寸
            old_file = app.config['UPLOADED_PHOTOS_DEST'] + photo_path
            new_path = os.path.split(old_file)[0] + '/' + bjt_date + time
            if os.path.getsize(old_file) <= 4096:
                status_message = ['danger', '照片上传失败', '照片被妖怪抓走啦', '再传一次吧']
                return render_template('show.html', user_info=user_info, status_message=status_message)
            # elif os.path.getsize(old_file) < 51200:
            #     if os.path.exists(new_path) == False:
            #         os.makedirs(new_path)
            #     new_file = new_path + '/' + os.path.split(old_file)[1]
            #     copyfile(old_file, new_file)
            else:
                tag = username + ' ' + bjt_date + cntime + ' ' + temperature + '℃'
                new_file = scale_tag(old_file, new_path, 1024, tag)

            file_url = '_uploads/' + new_file
            print(user_info)
            status_message = ['success', '上报成功', file_url, '']
            return render_template('show.html', user_info=user_info, status_message=status_message)


    utc_t = datetime.utcnow().replace(tzinfo=timezone.utc)
    bjt = utc_t.astimezone(timezone(timedelta(hours=8)))
    bjt_date_y = bjt.strftime('%Y-%m-%d')
    bjt_time = bjt.strftime('%H:%M%p')
    return render_template('heat.html', time_message=bjt_date_y + ' ' + bjt_time)

# 通过listx.html筛选csv、img文件用open.html打开，其他文件下载，目录进入
@app.route('/listx')
def list_file():
    files_list = os.listdir(app.config['UPLOADED_PHOTOS_DEST'])
    url_list = []
    for file in files_list:
        file_path = app.config['UPLOADED_PHOTOS_DEST'] + file
        if os.path.isfile(file_path):
            if file.split('.')[1] == 'csv':
                url_filter = 'file_csv'
                file_url = file_path
            elif file.split('.')[1] in IMAGES:
                url_filter = 'file_img'
                file_url = photos.url('') + file
            else:
                url_filter = 'file_other'
                file_url = photos.url('') + file
        else:
            url_filter = 'folder'
            file_url = '/listx/' + file
        url_list.append([url_filter, file_url, file])
    url_list.sort(reverse = True)
    return render_template('listx.html', url_list=url_list)

@app.route('/listx/<path:path_name>')
def subpath_file(path_name):
    abs_path = app.config['UPLOADED_PHOTOS_DEST'] + escape(path_name)
    files_list = os.listdir(abs_path)
    url_list = []
    for file in files_list:
        file_path = abs_path + '/' + file
        if os.path.isfile(file_path):
            if file.split('.')[1] == 'csv':
                url_filter = 'file_csv'
                file_url = file_path
            elif file.split('.')[1] in IMAGES:
                url_filter = 'file_img'
                file_url = photos.url(escape(path_name)) + '/' + file
            else:
                url_filter = 'file_other'
                file_url = photos.url(escape(path_name)) + '/' + file
        else:
            url_filter = 'folder'
            file_url = '/listx/' + escape(path_name) + '/' + file
        url_list.append([url_filter, file_url, file])
    url_list.sort(reverse = True)
    return render_template('listx.html', url_list=url_list)

# 在浏览器页面展示csv和图片文件。
@app.route('/open/<path:file_path>?url_filter=<url_filter>')
def open_file(file_path, url_filter):
    file_name = os.path.split(file_path)[1]
    if url_filter == 'file_csv':
        download_link = '/_uploads/' + file_path
        dict_row = []
        with open(file_path, 'r', encoding='utf-8-sig', newline='') as logcsv:
            for row in csv.DictReader(logcsv):
                dict_row.append(row)    
        file_content = [download_link, dict_row]
    else:
        file_content = file_path
    file = [url_filter, file_name, file_content]
    return render_template('open.html', file=file)

if __name__ == '__main__':
    app.run()