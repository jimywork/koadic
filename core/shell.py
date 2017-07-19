import os
import sys
import traceback
import threading

import core.loader
import core.colors
import core.job
import core.extant

''' Cmd is just a bad wrapper around readline with buggy input '''
class Shell(object):

    def __init__(self, banner, version):
        self.banner = banner
        self.version = version
        self.actions = core.loader.load_plugins("core/commands")
        self.plugins = core.loader.load_plugins("modules", True, self)
        self.stagers = []
        self.state = "stager/js/mshta"
        self.colors = core.colors.Colors()
        self.extant = core.extant.Extant(self)

    def run(self):
        self.main_thread_id = threading.current_thread().ident

        self.print_banner()


        while True:
            try:
                self.prompt = self.colors.get_prompt(self.state, True)
                self.clean_prompt = self.colors.get_prompt(self.state, False)
                cmd = self.get_command(self.prompt, self.autocomplete)
                self.run_command(cmd)

            except KeyboardInterrupt:
                self.confirm_exit()
            except EOFError:
                self.run_command("exit")
            except Exception:
                self.print_plain(traceback.format_exc())

    def confirm_exit(self):
        sys.stdout.write(os.linesep)
        try:
            res = "n"
            res = self.get_command("Exit? y/N: ")
        except:
            sys.stdout.write(os.linesep)

        if res.strip().lower() == "y":
            self.run_command("exit")

    def run_command(self, cmd):
        action = cmd.split(" ")[0].lower()

        if action in self.actions:
            self.actions[action].execute(self, cmd)
        else:
            try:
                os.system(cmd)
            except:
                pass

    def get_command(self, prompt, auto_complete_fn=None):
        try:
            if auto_complete_fn != None:
                import readline
                readline.set_completer_delims(' \t\n;')
                readline.parse_and_bind("tab: complete")
                readline.set_completer(auto_complete_fn)
        except:
            pass

        # python3 changes raw input name
        if sys.version_info[0] == 3:
            raw_input = input
        else:
            raw_input = __builtins__['raw_input']

        cmd = raw_input("%s" % prompt)
        return cmd.strip()

    def autocomplete(self, text, state):
        import readline
        line = readline.get_line_buffer()
        splitted = line.split(" ")

        # if there is a space, delegate to the commands autocompleter
        if len(splitted) > 1:
            if splitted[0] in self.actions:
                return self.actions[splitted[0]].autocomplete(self, line, text, state)
            else:
                return None

        # no space, autocomplete will be the basic commands:
        options = [x + " " for x in self.actions.keys() if x.startswith(text)]
        try:
            return options[state]
        except:
            return None

    def print_banner(self):
        os.system("clear")

        implant_len = len([a for a in self.plugins.keys()
                           if a.startswith("implant")])
        stager_len = len([a for a in self.plugins.keys()
                          if a.startswith("stager")])
        print(self.banner % (self.version, stager_len, implant_len))

    def print_plain(self, text, redraw = False):
        sys.stdout.write("\033[1K\r" + text + os.linesep)
        sys.stdout.flush()

        if redraw or threading.current_thread().ident != self.main_thread_id:
            import readline
            #sys.stdout.write("\033[s")
            sys.stdout.write(self.clean_prompt + readline.get_line_buffer())
            #sys.stdout.write("\033[u\033[B")
            sys.stdout.flush()

    def print_text(self, sig, text, redraw = False):
        self.print_plain(sig + " " + text, redraw)

    def print_good(self, text, redraw = False):
        self.print_text(self.colors.good("[+]"), text, redraw)

    def print_warning(self, text, redraw = False):
        self.print_text(self.colors.warning("[!]"), text, redraw)

    def print_error(self, text, redraw = False):
        self.print_text(self.colors.error("[-]"), text, redraw)

    def print_status(self, text, redraw = False):
        self.print_text(self.colors.status("[*]"), text, redraw)

    def print_help(self, text, redraw = False):
        self.print_text(self.colors.colorize("[?]", [self.colors.BOLD]), text, redraw)

    def print_command(self, text, redraw = False):
        self.print_text(self.colors.colorize("[>]", [self.colors.BOLD]), text, redraw)

    def print_hash(self, text, redraw = False):
        self.print_text(self.colors.colorize("[#]", [self.colors.BOLD]), text, redraw)
