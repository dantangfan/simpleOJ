User Guide
---

##Install

####Install Flask and requirements

```
sudo pip install -r requirements.txt
```

####About the problems
problems are download from code.google, and the are xml style. To use this system, we make the problems into files. Run the command below, and you can get a set of problems in your database

```python
python create_database.py
```

####Others

We use mysql, SQLAchemy and redis. So, make sure they running before you run this system.

You also should change all the configures in `./config.py` and `acmjudger/config.py`

##Run