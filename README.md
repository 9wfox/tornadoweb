# tornadoweb

## How to install tornadoweb
```
pip install tornadoweb
```

## How to create tornado project

```
tornadoweb_init project
```

## How to run web application
```
cd project
python apprun.py
```
## How to run web application with options
```
cd project
python apprun.py -h

Usage: run.py [options]

Options:
  -h, --help       show this help message and exit
  --port=PORT      Listen port.
  --config=CONFIG  config

python apprun.py --port=80 --config=settings.py
```

## How to use buildins settings
```
USE __conf__.PORT ...
```

## How to write a http resful api
```
vim action/test.py

from tornadoweb import *
from logic.utility import LoginedRequestHandler

@url(r"/hello")
class GetHandler(BaseHandler):
    def get(self):
        to = self.get_argument("to", "World")
	self.write(dict(status = True, msg = "Hello {}".format(to)))
:wq

python run.py
curl http://localhost:9999/hello?to=World

```



