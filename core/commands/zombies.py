import datetime

DESCRIPTION = "lists hooked targets"

def autocomplete(shell, line, text, state):
    return None

def help(shell):
    pass

def execute(shell, cmd):
    splitted = cmd.strip().split(" ")
    if len(splitted) == 1:
        print_all_sessions(shell)
        return

    for stager in shell.stagers:
        for session in stager.sessions:
            if session.id == int(splitted[1]):
                print_session(shell, session)
                return

    shell.print_error("Unable to find that session.")

def print_data(shell, title, data):
    formats = "\t{0:<32}{1:<32}"
    shell.print_plain(formats.format(shell.colors.colorize(title + ":", [shell.colors.BOLD]), data))

def print_jobs(shell, session):

    formats = "\t{0:<5}{1:<32}{2:<8}{3:<8}"
    shell.print_plain(formats.format("JOB", "NAME", "STATUS", "ERRNO"))
    shell.print_plain(formats.format("----", "---------", "-------", "-------"))

    for job in session.jobs:
        shell.print_plain(formats.format(job.id, job.name, job.status_string(), job.errno))


def print_session(shell, session):
    shell.print_plain("")
    print_data(shell, "ID", session.id)
    print_data(shell, "Status", "Alive" if session.status == session.ALIVE else "Dead")
    print_data(shell, "Last Seen", datetime.datetime.fromtimestamp(session.last_active).strftime('%Y-%m-%d %H:%M:%S'))
    shell.print_plain("")
    print_data(shell, "IP", session.ip)
    print_data(shell, "User Agent", session.user_agent)
    print_data(shell, "Session Key", session.key)
    shell.print_plain("")
    print_jobs(shell, session)
    shell.print_plain("")

def print_all_sessions(shell):
    formats = "\t{0:<5}{1:<16}{2:<8}{3:16}"

    shell.print_plain("")

    shell.print_plain(formats.format("ID", "IP", "STATUS", "LAST SEEN"))
    shell.print_plain(formats.format("---", "---------", "-------", "------------"))
    for stager in shell.stagers:
        for session in stager.sessions:
            alive = "Alive" if session.status == 1 else "Dead"
            seen = datetime.datetime.fromtimestamp(session.last_active).strftime('%Y-%m-%d %H:%M:%S')
            shell.print_plain(formats.format(session.id, session.ip, alive, seen))

    shell.print_plain("")
    shell.print_plain('Use "zombies %s" for detailed information about a session.' % shell.colors.colorize("ID", [shell.colors.BOLD]))
    shell.print_plain("")
