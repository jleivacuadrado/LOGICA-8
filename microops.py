
def fetch_operand(cpu):
    cpu.operand = cpu.bus.read(cpu.PC)
    cpu.PC += 1
    cpu.add_log(f"uOP: FETCH operand {cpu.operand:02X}")

def load_A(cpu):
    cpu.A = cpu.operand
    cpu.zero = (cpu.A == 0)
    cpu.add_log(f"uOP: LOAD A <. {cpu.A:02X}")