
class Bus:
    def __init__(self):
        self.memory = None

    def attach_memory(self, memory):
        self.memory = memory

    def read(self, addr):
        return self.memory.read(addr)

    def write(self, addr, value):
        self.memory.write(addr, value)