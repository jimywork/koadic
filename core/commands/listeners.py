DESCRIPTION = "shows info about stagers"

def autocomplete(shell, line, text, state):
    pass

def help(shell):
    pass

def print_all_payloads(shell):
    if len(shell.stagers) == 0:
        shell.print_error("No payloads yet.")
        return

    shell.print_plain("")

    formats = "\t{0:<5}{1:<16}{2:<8}{3:<20}"

    shell.print_plain(formats.format("ID", "IP", "PORT", "TYPE"))
    shell.print_plain(formats.format("----", "---------", "-----", "-------"))

    for stager in shell.stagers:
        #shell.print_plain("")
        payload = stager.get_payload().decode()
        shell.print_plain(formats.format(stager.payload_id, stager.hostname, stager.port, stager.module))

    shell.print_plain("")
    shell.print_plain('Use "listeners %s" to print a payload' % shell.colors.colorize("ID", [shell.colors.BOLD]))
    shell.print_plain("")

def print_payload(shell, id):
    for stager in shell.stagers:
        if str(stager.payload_id) == id:
            payload = stager.get_payload().decode()

            #shell.print_good("%s" % stager.options.get("URL"))
            shell.print_command("%s" % payload)

            #shell.print_plain("")
            return

    shell.print_error("No payload %s." % id)


def execute(shell, cmd):

    splitted = cmd.strip().split(" ")

    if len(splitted) > 1:
        id = splitted[1]
        print_payload(shell, id)
        return

    print_all_payloads(shell)
