# Raspberry Pi 4 

This device runs the webserver and hosts the website where users can upload their messages


## Delpoy


Using node v20.x:

```
npm install
```

and then: 

```
npm run build
```

after this, we create a virtualenv:

```
virtualenv env --python=python3.10
```

```
source env/bin/activate
```

```
pip install -r requirements.txt
```

```
python3 app.py
```