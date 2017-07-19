DESCRIPTION = "switch to a different module"

def autocomplete(shell, line, text, state):
    # todo: make this show shorter paths at a time
    # should never go this big...
    if len(line.split(" ")) >= 3:
        return None

    options = [x + " " for x in shell.plugins.keys() if x.startswith(text)]

    try:
        return options[state]
    except:
        return None

def help(shell):
    pass

def execute(shell, cmd):
    splitted = cmd.split(" ")

    if len(splitted) >= 2:
        module = splitted[1]
        if module not in shell.plugins:
            shell.print_error("No module named %s" % (module))
            return

        shell.state = module
