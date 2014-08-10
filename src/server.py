#!/usr/bin/env python
# -*- coding: utf-8 -*-

# uredirect-py
#   by Naoki Rinmous <sukareki@gmail.com>
#   published under WTFPL


# HTTP Frontend Server
#   simply place it behind nginx

import os.path
import re
from tornado.ioloop import IOLoop
from tornado.web import Application, HTTPError, RequestHandler, StaticFileHandler, url
import utils

class Server:
    class LookupHandler(RequestHandler):
        def initialize(self, db):
            self.db = db
        def get(self, id):
            url = self.db.lookupId(id)
            if url:
                self.redirect(url)
            else:
                raise HTTPError(500)

    class CommitHandler(RequestHandler):
        def initialize(self, db, prefix):
            self.db = db
            self.urlpartten = re.compile('^((([A-Za-z]{3,9}:(?:\/\/)?)(?:[\-;:&=\+\$,\w]+@)?[A-Za-z0-9\.\-]+|(?:www\.|[\-;:&=\+\$,\w]+@)[A-Za-z0-9\.\-]+)((?:\/[\+~%\/\.\w\-_]*)?\??(?:[\-\+=&;%@\.\w_]*)#?(?:[\.\!\/\\\w]*))?)$')
            self.urlprefix = prefix
        def get(self):
            self.render('commit.html')
        def post(self):
            url = self.get_argument('url', '')
            if not url:
                raise HTTPError(400)
            if len(url) > 255:
                raise HTTPError(400)
            if not self.urlpartten.match(url):
                raise HTTPError(400)
            self.write(self.urlprefix + self.db.createRecord(url))

    class StaticHandler(StaticFileHandler):
        def initialize(self, path):
            self.dirname, self.filename = os.path.split(path)
            super(Server.StaticHandler, self).initialize(self.dirname)

        def get(self, path=None, include_body=True):
            # Ignore 'path'.
            super(Server.StaticHandler, self).get(self.filename, include_body)

    def __init__(self, config, db):
        self.app = self.createApplication(db, config['prefix'])
        self.app.listen(config['http_port'])
        IOLoop.current().start()

    def createApplication(self, db, prefix):
        return Application([
            url(r"/", self.StaticHandler, {'path': './static/index.html'}),
            url(r"/new", self.CommitHandler, dict(db = db, prefix = prefix)),
            url(r"/([A-Z,a-z,0-9]{6})", self.LookupHandler, dict(db = db))
        ])
