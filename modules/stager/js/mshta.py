import core.stager

class MSHTAStager(core.stager.Stager):

    NAME = "JScript MSHTA Stager"
    DESCRIPTION = "Listens for new sessions, using JScript MSHTA for payloads"
    AUTHORS = ['zerosum0x0']

    WORKLOAD = "js"

    def load(self):
        #self.options.set("LPORT", 9999)
        self.port = 9999

        self.template = self.loader.load_script("data/stager/js/mshta/template.hta")
        self.stagecmd = self.loader.load_script("data/stager/js/mshta/mshta.cmd")
        self.forkcmd = self.loader.load_script("data/stager/js/rundll32/rundll32.cmd")
