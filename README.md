SCPC Training System V2
=======

http://mrchenyi.com:5000/


####需要插件
  
plugin				|   version	| 
:----------------:	|	:-----------:	|	
flask               |   0.10.1          |
Flask-Login			|	0.2.9			|	
Flask-SQLAlchemy	|	1.0				|	
Flask-WTF			|	0.9.4			|	
flask-cache			|	0.12			|	
MySQL-python		|	1.2.5			|
Flask-Admin			|	1.07			|
Gevent              |   1.0             |




#### Debian
	add "deb http://mirror.cse.iitk.ac.in/debian/ testing main contrib" 
		to /etc/api.source.list
	aptitude update
	aptitude install python2.7


    apt-get update
    apt-get upgrade
    apt-get install python-pip
    pip install flask==0.10.1
    pip install Flask-Admin==1.0.7
    pip install Flask-Cache==0.12
    pip install Flask-Login==0.2.9
    pip install Flask-SQLAlchemy==1.0
    pip install Flask-WTF==0.9.4
    pip install MySQL-python==1.2.5

    apt-get install python-mysqldb

