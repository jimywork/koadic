import random
import threading
import uuid
import time
from core.job import Job

class Session(object):
    SESSION_ID = 0
    SESSION_ID_LOCK = threading.Lock()

    DEAD = 0
    ALIVE = 1

    def __init__(self, stager, ip, user_agent):
        with Session.SESSION_ID_LOCK:
            self.id = Session.SESSION_ID
            Session.SESSION_ID += 1

        self.key = uuid.uuid4().hex
        self.jobs = []
        self.killed = False

        self.ip = ip
        self.user_agent = user_agent

        self.stager = stager
        self.shell = stager.shell
        self.status = Session.ALIVE
        self.update_active()

        self.whoami = ""
        self.hostname = ""
        self.win_ver = ""

        self.shell.print_good(
            "Zombie %d: Staging new connection (%s)" % (self.id, self.ip))

    def kill(self):
        self.killed = True
        self.set_dead()

    def set_dead(self):
        if self.status != self.DEAD:
            self.status = self.DEAD
            self.shell.print_warning("Zombie %d: Timed out." % self.id)

    def set_reconnect(self):
        if not self.killed:
            self.shell.print_good("Zombie %d: Re-connected." % self.id)
            self.status = self.ALIVE

    def update_active(self):
        self.last_active = time.time()

    def get_job(self, job_key):
        for job in self.jobs:
            if job.key == job_key:
                return job

        return None

    def get_created_job(self):
        shell = self.stager.shell

        for job in self.jobs:
            #if job.completed != Job.COMPLETE:
            if job.completed == Job.CREATED:
                return job

        return None
