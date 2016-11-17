class MemoryOverFlowException(Exception):
    pass

class Memory:
    def __init__(self, size, default):
        self.cells = [default for i in range(size)]

    def load_program(self, program):
        self.cells = program + self.cells

    def __getitem__(self, key):
        if len(self.cells) < key:
            raise MemoryOverFlowException("SEGFAULT: Attemt to access memory",
                            " location outside of physical capacity (Address: {})".format(key))
        else:
            return self.cells[key]

    def __setitem__(self, key, value):
        if len(self.cells) < key:
            raise MemoryOverFlowException("SEGFAULT: Attemt to set memory",
                        " location outside of physical capacity (Address: {})".format(key))
        else:
            self.cells[key] = value

    def __delitem__(self, key):
        if len(self.cells) < key:
            raise MemoryOverFlowException("SEGFAULT: Attemt to set memory",
                        " location outside of physical capacity (Address: {})".format(key))
        else:
            self.cells[key] = 0