from core.linter import Linter
from core.options import Options
import core.loader
import copy
import string
import random

class Plugin(object):

    NAME = ""
    DESCRIPTION = ""
    AUTHORS = []

    def __init__(self, shell):
        self.options = Options()
        self.shell = shell

        self.loader = core.loader

        self.load()

    ''' called when the framework starts '''
    def load(self):
        pass

    ''' called when the plugin is invoked '''
    def run(self):
        pass

    def dispatch(self, workloads, job):
        target = self.options.get("ZOMBIE")
        splitted = [x.strip() for x in target.split(",")]

        for server in self.shell.stagers:
            for session in server.sessions:
                if target == "ALL" or str(session.id) in splitted:
                    if server.stager.WORKLOAD in workloads.keys():
                        workload = workloads[server.stager.WORKLOAD]
                        options = copy.deepcopy(self.options)
                        j = job(self.shell, session, self.shell.state, workload, options)
                        session.jobs.append(j)

    def load_payload(self, id):
        try:
            for server in self.shell.stagers:
                if int(server.payload_id) == int(id):
                    return server.get_payload().decode()
        except:
            pass

        return None

    def parse_ips(self, ips):
        import core.cidr
        return core.cidr.get_ips(ips)

    def parse_ports(self, ports):
        import core.cidr
        return core.cidr.get_ports(ports)

    def make_vb_array(self, name, array):
        ret = "dim %s(%d)\n" % (name, len(array) - 1)

        count = 0
        for el in array:
            x = '%s(%d) = "%s"\n' % (name, count, str(el))
            ret += x
            count += 1

        return ret

    def make_js_array(self, name, array):
        array = ['"%s"' % item for item in array]
        ret = "var %s = [%s];" % (name, ", ".join(array))
        return ret

    def random_string(self, length):
        return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for n in range(length))

    def validate_shellcode(self, shellcode):
        if len(shellcode) % 2 != 0:
            return False

        return all(c in string.hexdigits for c in shellcode)

    def convert_shellcode(self, shellcode):
        decis = []
        count = 0
        for i in range(0, len(shellcode), 2):
            count += 1
            hexa = shellcode[i:i+2]
            deci = int(hexa, 16)

            if count % 25 == 0:
                decis.append(" _\\n" + str(deci))
            else:
                decis.append(str(deci))

        return ",".join(decis)
