import core.plugin

class Implant(core.plugin.Plugin):
    def __init__(self, shell):
        super(Implant, self).__init__(shell)
        self.options.register("ZOMBIE", "ALL", "the zombie to target")
