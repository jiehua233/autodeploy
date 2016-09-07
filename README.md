# GitLab Auto Deploy

Auto deploy your code to your servers using web hook when you push to Gitlab.
Besides, it can be configed to mirror your project on Github.

## Usage

Build up a new virtual env:
    
    $ virtualenv ~/virtualenvs/autodeploy 
    $ source ~/virtualenvs/autodeploy/bin/activate
    (autodeploy)$ pip install -r requirements.txt

Config is quite simple:

    (autodeploy)$ cp config.py.sample config.py
    (autodeploy)$ vim config.py

* `project_root`: your project root directory, all repos will be searched here;
* `backend["broker"]`: you need to specific a broker for `celery`, `redis` is simple enough;
* `bind`: the server's bind address and port;

Run server and backend:
    
    (autodeploy)$ python server.py
    # or start server using gunicorn
    (autodeploy)$ gunicorn server:app -c config.py
    (autodeploy)$ python backend.py worker -l info

## Deploy 

`Supervisord` is recommended, take a look at `supervisor.conf`.

## Github Mirror

Just add git remote `github` to that repo:

    $ git remote add --mirror=push github git@github.com:your-name/your-project.git 

when you push to your gitlab, it'll also push to github.
