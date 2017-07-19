import os
import sys
import inspect
import core.plugin

def load_plugins(dir, instantiate = False, shell = None):
    plugins = {}

    for root, dirs, files in os.walk(dir):
        sys.path.append(root)

        # make forward slashes on windows
        module_root = root.replace(dir, "").replace("\\", "/")

        #if (module_root.startswith("/")):
            #module_root = module_root[1:]

        #print root
        for file in files:
            if not file.endswith(".py"):
                continue

            if file in ["__init__.py"]:
                continue

            file = file.rsplit(".py", 1)[0]
            pname = module_root + "/" + file
            if (pname.startswith("/")):
                pname = pname[1:]

            if instantiate:
                if pname in sys.modules:
                    del sys.modules[pname]
                env = __import__(file, )
                for name, obj in inspect.getmembers(env):
                    if inspect.isclass(obj) and issubclass(obj, core.plugin.Plugin):
                        plugins[pname] = obj(shell)
                        break
            else:
                plugins[pname] = __import__(file)

        sys.path.remove(root)

    return plugins

def load_script(path, options = None, minimize = True):
    with open(path, "rb") as f:
        script = f.read().strip()

    #script = self.linter.prepend_stdlib(script)

    #if minimize:
        #script = self.linter.minimize_script(script)

    script = apply_options(script, options)

    return script

def apply_options(script, options = None):
    if options is not None:
        for option in options.options:
            name = "~%s~" % option.name
            val = str(option.value).encode()

            script = script.replace(name.encode(), val)
            script = script.replace(name.lower().encode(), val)

    return script
