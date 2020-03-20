# 图片体温签到 Heat Punch
上传体温计照片，登记姓名体温，记录在csv文件中

Upload thermometer photo,Register name and temperature, record in csv file

```
/heat_punch/
├─photos/
│  ├─0318/ # 此目录按日子自动生成
│  │  ├─0318am/
│  │  ├─0318pm/
│  │  ├─20200318上午/
│  │  ├─20200318下午/
│  │  ├─0318am.csv
│  │  └─0318pm.csv
│  ├─listcsv.csv
│  └─PHOTOS.md
├─static/
│  ├─css/
│  │  ├─bootstrap.min.css
│  │  └─bootstrap.min.css.map
│  ├─js/
│  │  ├─bootstrap.bundle.min.js
│  │  └─bootstrap.bundle.min.js.map
│  └─fonts/
│     └─SourceHanSansSC-Medium.otf
├─templates/
│  ├─base.html
│  ├─heat.html
│  ├─listx.html
│  ├─open.html
│  └─show.html
├─venv/
└─heat.py
```