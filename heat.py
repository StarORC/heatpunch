#!/usr/bin/env python3
# -*- coding:UTF-8-sig -*-

import os
import csv
from flask import Flask, request, render_template
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from datetime import datetime, timedelta, timezone


app = Flask(__name__)
app.config['UPLOADED_PHOTOS_DEST'] = 'photos/'
logpath = 'data/today.csv'

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)  # 文件大小限制，默认为16MB
timedict = {'am':'上午', 'pm':'下午'}


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST' and 'photo' in request.files:

        username = request.form['username']
        temperature = request.form['temperature']
        time = request.form['time']
        cntime = timedict[time]

        utc_t = datetime.utcnow().replace(tzinfo=timezone.utc)
        bjt = utc_t.astimezone(timezone(timedelta(hours=8)))
        bjt_date = bjt.strftime('%m%d')

        rename = username + '+五部+' + bjt_date + cntime
        folder = bjt_date + time + '/'
        filename = photos.save(request.files['photo'], folder=folder, name=rename + '.')
        
        logpath = app.config['UPLOADED_PHOTOS_DEST'] + folder + bjt_date + time + '.csv'

        if os.path.exists(logpath):
            with open(logpath, 'a', encoding='utf-8-sig', newline='') as logcsv:
                headernames = ['Name','Temp']
                row = {'Name':username,'Temp':temperature}
                writer = csv.DictWriter(logcsv,fieldnames=headernames)
                writer.writerow(row)
        else:
            with open(logpath, 'a', encoding='utf-8-sig', newline='') as logcsv:
                headernames = ['Name','Temp']
                row = {'Name':username,'Temp':temperature}
                writer = csv.DictWriter(logcsv,fieldnames=headernames)
                writer.writeheader()
                writer.writerow(row)

        file_url = photos.url(filename)

        return render_template('show.html', message=file_url)

    utc_t = datetime.utcnow().replace(tzinfo=timezone.utc)
    bjt = utc_t.astimezone(timezone(timedelta(hours=8)))
    bjt_date_y = bjt.strftime('%Y-%m-%d')
    bjt_time = bjt.strftime('%H:%M%p')
    return render_template('heat.html', message=bjt_date_y + ' ' + bjt_time)

@app.route('/listx')
def list_file():
    files_list = os.listdir(app.config['UPLOADED_PHOTOS_DEST'])
    file_url = '/listx'
    return render_template('listx.html', files_list=files_list, file_url=file_url)

@app.route('/listx/<filename>')
def open_file(filename):
    files_list = os.listdir(app.config['UPLOADED_PHOTOS_DEST'] + filename)
    file_url = photos.url(filename)
    return render_template('listx.html', files_list=files_list, file_url=file_url)

if __name__ == '__main__':
    app.run()