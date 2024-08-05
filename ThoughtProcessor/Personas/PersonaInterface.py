class PersonaInterface:
    def __init__(self, name):
        self.name = name

    def work(self, task):
        raise NotImplementedError("This method should be overridden by subclasses")
