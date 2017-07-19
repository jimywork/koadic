import core.plugin
import core.server
import random
import string

class Stager(core.plugin.Plugin):
    WORKLOAD = "NONE"

    def __init__(self, shell):
        self.port = 9999
        super(Stager, self).__init__(shell)

        # general, non-hidden, non-advanced options
        self.options.register('LHOST', '0.0.0.0', 'Where the stager should call home')
        self.options.register('LPORT', self.port, 'The port to listen for stagers on')
        self.options.register('EXPIRES', '', 'MM/DD/YYYY to stop calling home', required = False)
        #self.options.register('DIRECTORY', '%TEMP%', 'A writeable directory on the target', advanced = True)
        self.options.register('KEYPATH', '',  'Private key for TLS communications', required = False)
        self.options.register('CERTPATH', '', 'Certificate for TLS communications', required = False)
        self.options.register('ENDPOINT', self.random_string(5), 'URL path for callhome operations', required = False, advanced = True)

        # names of query string properties
        self.options.register("JOBNAME", "csrf", "name for jobkey cookie", advanced = True)
        self.options.register("SESSIONNAME", "sid", "name for session cookie", advanced = True)

        # query strings
        self.options.register("_JOBPATH_", "", "the job path", hidden = True)
        self.options.register("_SESSIONPATH_", "", "the session path", hidden = True)

        # script payload file paths
        self.options.register("_STDLIB_", "", "path to stdlib file", hidden = True)
        self.options.register("_TEMPLATE_", "", "path to template file", hidden = True)
        self.options.register("_STAGE_", "", "stage worker", hidden = True)
        self.options.register("_STAGECMD_", "", "path to stage file", hidden = True)
        self.options.register("_FORKCMD_", "", "path to fork file", hidden = True)

        # is this one needed, hmm, I dunno
        #fname = self.random_string(5)
        #self.options.register('FILE', fname, 'unique file name', advanced=True)

        # standard scripts
        self.stdlib = self.loader.load_script("data/stager/js/stdlib.js")
        self.stage = self.loader.load_script("data/stager/js/stage.js")

    def run(self):
        self.options.set("_STDLIB_", self.stdlib)
        self.options.set("_TEMPLATE_", self.template)
        self.options.set("_STAGECMD_", self.stagecmd)
        self.options.set("_FORKCMD_", self.forkcmd)
        self.options.set("_STAGE_", self.stage)

        self.start_server(core.handler.Handler)



    def start_server(self, handler):
        try:
            server = core.server.Server(self, handler)
            self.shell.stagers.append(server)
            server.start()

            self.shell.print_good("Spawned a stager at %s" % (server.options.get("URL")))
            server.print_payload()
        except OSError as e:
            port = str(self.options.get("LPORT"))
            if e.errno == 98:
                self.shell.print_error("Port %s is already bound!" % (port))
            elif e.errno == 13:
                self.shell.print_error("Port %s bind permission denied!" % (port))
            else:
                raise
            return
        except Exception as ex:
            template = "An exception of type {0} occured. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            self.shell.print_error(message)
        except:
            self.shell.print_error("Failed to spawn stager")
            raise
