from core.mappings import mappings
import string
import threading
import uuid


class Job(object):
    CREATED = 0
    RECEIVED = 2
    RUNNING = 3
    COMPLETE = 4
    FAILED = 5

    JOB_ID = 0
    JOB_ID_LOCK = threading.Lock()

    def __init__(self, shell, session, name, script, options):
        self.fork32Bit = False
        self.completed = Job.CREATED
        self.script = script
        self.shell = shell
        self.options = options
        self.session = session
        self.name = name
        self.errno = ""
        self.data = b""
        self.unsafe_data = b""
        self.key = uuid.uuid4().hex

        with Job.JOB_ID_LOCK:
            self.id = Job.JOB_ID
            Job.JOB_ID += 1

        self.create()

        self.shell.print_status("Zombie %d: Job %d (%s) created." % (
            self.session.id, self.id, self.name))

    def create(self):
        pass

    def receive(self):
        #self.shell.print_status("Zombie %d: Job %d (%s) received." % (self.session.id, self.id, self.name))
        self.completed = Job.RECEIVED

    def payload(self):
        #self.shell.print_status("Zombie %d: Job %d (%s) running." % (self.session.id, self.id, self.name))
        self.completed = Job.RUNNING
        return self.script

    def error(self, errno, errdesc, errname, data):
        self.errno = str(errno)
        self.errdesc = errdesc
        self.errname = errname
        self.status = Job.FAILED
        self.sanitize_data(data)

        self.print_error()

    def print_error(self):
        self.shell.print_error("Zombie %d: Job %d (%s) failed!" % (
            self.session.id, self.id, self.name))
        self.shell.print_error("%s (%08x): %s " % (
            self.errname, int(self.errno) + 2**32, self.errdesc))

    def sanitize_data(self, data):
        # clean up unprintable characters from data
        self.data = b""
        for i in range(0, len(data)):
            try:
                if data[i:i + 1].decode() in string.printable:
                    self.data += data[i:i + 1]
            except:
                pass
        self.data = self.data.decode()

        #self.data = "".join(i for i in data.decode() if i in string.printable)

    def report(self, handler, data, sanitize=True):
        #self.errno = str(errno)
        self.completed = Job.COMPLETE

        self.unsafe_data = data

        if (sanitize):
            self.sanitize_data(data)
        else:
            self.data = ""

        if handler:
            handler.reply(202)

        self.shell.print_good("Zombie %d: Job %d (%s) completed." % (
            self.session.id, self.id, self.name))

        self.done()

    def status_string(self):
        if self.completed == Job.COMPLETE:
            return "Complete"
        if self.completed == Job.CREATED:
            return "Created"
        if self.completed == Job.RECEIVED:
            return "Received"
        if self.completed == Job.RUNNING:
            return "Running"
        if self.completed == Job.FAILED:
            return "Failed"

    def done(self):
        pass

    def display(self):
        pass

    def print_status(self, message):
        self.shell.print_status("Zombie %d: Job %d (%s) %s" % (
            self.session.id, self.id, self.name, message))

    def print_good(self, message):
        self.shell.print_good("Zombie %d: Job %d (%s) %s" % (
            self.session.id, self.id, self.name, message))


    def decode_downloaded_data(self, data):
        slash_char = chr(92).encode()
        zero_char = chr(0x30).encode()
        null_char = chr(0).encode()
        mapping = mappings

        b_list = []
        escape_flag = False
        special_char = {
            '0': null_char,
            '\\': slash_char
        }

        for i in data.decode('utf-8'):
            # Decide on slash char
            if escape_flag:
                escape_flag = False
                b_list.append(special_char[i])
                continue

            if ord(i) in mapping.keys():
                b_list.append(mapping[ord(i)])
            else:
                escape_flag = True
                # EAT the slash
                continue

        return b"".join(b_list)
