
def fetch_operand(cpu):
    cpu.operand = cpu.bus.read(cpu.PC)
    cpu.PC += 1
    cpu.add_log(f"uOP: BUS READ  -> Op:{cpu.operand:02X} (PC incrementado)")

def load_A(cpu):
    cpu.A = cpu.operand
    update_flags(cpu, cpu.A)
    cpu.add_log(f"uOP: REG LOAD  -> A = {cpu.A:02X}")

def update_flags(cpu, value):
    cpu.zero = (value == 0)
    z_stat = "ON" if cpu.zero else "OFF"
    c_stat = "ON" if cpu.carry else "OFF"
    cpu.add_log(f"uOP: FLAGS     -> Z:{z_stat} C:{c_stat}")