# GitLab Auto Deploy

Auto deploy your code to your servers using web hook when you push to Gitlab.
Besides, it can be configed to mirror your project on Github.

## Setup

    $ pip install sh
    $ python autodeploy.sh

Now it's working, just visit localhost:27001. But if you want to run it as daemon,
it's a better idea to use supervisor.

## Config

Edit `repository.josn`, add your project on the format:

```json
    {
        "path": "/path/to/your/project/",
        "git": "git@your-git-server:namespace/your-project.git",
        "sync": true
    },
```

## Github Mirror

Set `sync` to `true`, and add `github` repo:

    $ cd /path/to/your/project 
    $ git remote add --mirror=push github git@github.com:your-name/your-project.git 

when you push to your gitLab, it'll also push to github.
