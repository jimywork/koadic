import core.stager

class RunDLL32JSStager(core.stager.Stager):

    NAME = "JScript rundll32.exe JavaScript Stager"
    DESCRIPTION = "Listens for new sessions, using JavaScript for payloads"
    AUTHORS = ['zerosum0x0']

    def load(self):
        #self.options.set("LPORT", 9997)
        self.port = 9997

        self.template = "~SCRIPT~"
        self.stagecmd = self.loader.load_script("data/stager/js/rundll32_js/rundll32_js.cmd")
        self.forkcmd = self.stagecmd
