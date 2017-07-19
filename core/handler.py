try:
    from SocketServer import ThreadingMixIn
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from urlparse import parse_qs
except:
    # why is python3 so terrible for backward compatibility?
    from socketserver import ThreadingMixIn
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import parse_qs

import cgi
import socket
import random
import threading
import os
import ssl
import io
import time
import copy
import core.job
import core.session
import core.loader


class Handler(BaseHTTPRequestHandler):

    def reply(self, status, data=b"", headers={}):

        self.send_response(status)

        for key, value in headers.items():
            self.send_header(key, value)

        self.end_headers()

        # python is so utterly incapable that we have to write CS 101 socket
        # code
        if data != b"":
            total = len(data)
            written = 0
            while written < total:
                a = self.wfile.write(data[written:])
                self.wfile.flush()

                if a is None:
                    break

                written += a

    def send_file(self, fname):
        with open(fname, "rb") as f:
            fdata = f.read()

        headers = {}
        headers['Content-Type'] = 'application/octet-stream'
        headers['Content-Length'] = len(fdata)
        self.reply(200, fdata, headers)

    def get_header(self, header, default=None):
        if header in self.headers:
            return self.headers[header]

        return default

    # ignore log messages
    def log_message(*arg):
        pass

    def setup(self):
        self.timeout = 90000
        BaseHTTPRequestHandler.setup(self)
        self.request.settimeout(90000)

    #BaseHTTPServer.server_version = 'Apache'
    #BaseHTTPServer.sys_version = ''
    def version_string(self):
        return 'Apache'

    def handle(self):
        """Handles a request ignoring dropped connections."""
        try:
            self.stager = self.server.stager
            self.shell = self.stager.shell
            self.options = copy.deepcopy(self.server.server.options)
            self.loader = core.loader

            return BaseHTTPRequestHandler.handle(self)
        except (socket.error, socket.timeout) as e:
            pass
        # except:
            # pass

    def init_session(self, stage=True):
        if stage:
            ip = self.client_address
            agent = self.get_header('user-agent', '')

            self.session = core.session.Session(
                self.server.server, ip[0], agent)
            self.server.server.sessions.append(self.session)

        self.session.update_active()
        self.options.set("SESSIONKEY", self.session.key)
        self.options.set("SESSIONPATH", "%s=%s;" %
                         (self.options.get("SESSIONNAME"), self.session.key))

    def parse_params(self):
        splitted = self.path.split("?")
        self.endpoint = splitted[0]

        endpoint = self.options.get("ENDPOINT").strip()

        if len(endpoint) > 0:
            if self.endpoint[1:] != endpoint:
                return False

        self.get_params = parse_qs(splitted[1]) if len(splitted) > 1 else {}
        self.session = None
        self.job = None

        sesskey = self.options.get("SESSIONNAME")
        if sesskey in self.get_params:
            self.session = self.find_session(self.get_params[sesskey][0])

            if not self.session:
                return False

            jobkey = self.options.get("JOBNAME")
            if jobkey in self.get_params:
                self.job = self.session.get_job(self.get_params[jobkey][0])

                if self.job:
                    self.options.set("JOBKEY", self.job.key)
                    self.options.set("JOBPATH", "%s=%s;" % (jobkey, self.job.key))

            self.init_session(False)

        return True

    # the initial stage is a GET request
    def do_GET(self):
        if self.parse_params():
            if not self.session:
                return self.handle_new_session()

            if self.job:
                return self.handle_job()

            return self.handle_stage()

        self.reply(404)

    def do_POST(self):
        if self.parse_params():
            if not self.session:
                return self.reply(403)

            if not self.job:
                return self.handle_work()

            return self.handle_report()

        return self.reply(404)

    def handle_stage(self):
        self.options.set("JOBKEY", "stage")
        data = self.post_process_script(self.options.get("_STAGE_"))
        self.reply(200, data)

    def handle_new_session(self):
        self.init_session()
        data = self.post_process_script(self.options.get("_STAGE_"))
        self.reply(200, data)

    def handle_job(self):
        script = self.job.payload()
        script = self.post_process_script(script)
        self.reply(200, script)

    def handle_work(self):
        while True:
            if self.session.killed:
                return self.reply(500, "");

            job = self.session.get_created_job()
            if job is not None:
                break

            time.sleep(1)
            self.session.update_active()

        job.receive()

        # hack to tell us to fork 32 bit
        status = 202 if job.fork32Bit else 201

        self.reply(status, job.key.encode())

    def handle_report(self):
        content_len = int(self.get_header('content-length', 0))
        data = self.rfile.read(content_len)

        errno = self.get_header('errno', False)
        if errno:
            errdesc = self.get_header('errdesc', 'No Description')
            errname = self.get_header('errname', 'Error')
            self.job.error(errno, errdesc, errname, data)
            self.reply(200)
            return

        self.job.report(self, data)

    def find_session(self, key):
        #key = key[0].decode()
        for session in self.server.server.sessions:
            if session.key == key:
                return session
        return None

    def do_post(self):
        self.do_POST()

    def do_get(self):
        self.do_GET()

    def parse_post_vars(self):
        ctype, pdict = cgi.parse_header(self.headers['content-type'])
        if ctype == 'multipart/form-data':
            postvars = cgi.parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(self.rfile.read(length), keep_blank_values=1)
        else:
            postvars = {}
        return postvars

    # ugly dragons, turn back
    def post_process_script(self, script, stdlib=True):
        if stdlib:
            script = self.options.get("_STDLIB_") + script

            # crappy hack for forkcmd
            forkopt = copy.deepcopy(self.options)
            forkopt.set("URL", "***K***")
            forkopt.set("_JOBPATH_", "")
            forkopt.set("_SESSIONPATH_", "")
            forkcmd = self.options.get("_FORKCMD_")
            forkcmd = self.loader.apply_options(forkcmd, forkopt)

            self.options.set("_FORKCMD_", forkcmd.decode())

        template = self.options.get("_TEMPLATE_")

        script = self.loader.apply_options(script, self.options)
        script = template.replace(b"~SCRIPT~", script)
        return script
