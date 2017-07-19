DESCRIPTION = "shows info about jobs"

def autocomplete(shell, line, text, state):
    pass

def help(shell):
    pass

def print_job(shell, id):
    for stager in shell.stagers:
        for session in stager.sessions:
            for job in session.jobs:
                if job.id == int(id):
                    job.display()

def print_all_jobs(shell):
    formats = "\t{0:<5}{1:<10}{2:<20}{3:<40}"

    shell.print_plain("")

    shell.print_plain(formats.format("ID", "STATUS", "ZOMBIE", "NAME"))
    shell.print_plain(formats.format("-"*4,  "-"*9, "-"*10, "-"*20))
    for stager in shell.stagers:
        for session in stager.sessions:
            for job in session.jobs:
                zombie = "%s (%d)" % (session.ip, session.id)
                shell.print_plain(formats.format(job.id, job.status_string(), zombie, job.name))


    shell.print_plain("")



def execute(shell, cmd):

    splitted = cmd.strip().split(" ")

    if len(splitted) > 1:
        id = splitted[1]
        print_job(shell, id)
        return

    print_all_jobs(shell)
