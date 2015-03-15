使用方法
---

##安装

####安装Flask和插件

```
sudo pip install -r requirements.txt
```

####题目
题目是xml格式的，为了方便数据查看，我把它们换成了文件的格式
运行

```python
python create_database.py
```

就可以得到相应的题目集合

####其他

使用了mysql和redis，所以必须保证她们都能跑起来，配置文件在config里面，需要修改

发email的程序是用tornado写的，不喜欢可以自己换

##运行

主文件夹下的`restart.sh`和`stop.sh`是用来跑web端程序的，`acmjudger`文件夹下的`restart.sh`和`stop.sh`是用来跑评测程序的