
import os
import time

from cpu import *
from assembler import *
from system_tests import *
from sample_programs import *


# --- SISTEMA DE MENÚS (Interfaz) ---

HELP_TEXT = """
LOGICA-8 - AYUDA
----------------------------------
01 [val] : LDA #val - Carga el valor en el Acumulador (A).
02 [val] : ADD #val - Suma el valor al Acumulador.
03 [dir] : STA $dir - Guarda el Acumulador en la dirección RAM.
04 [dir] : JMP $dir - Salta la ejecución a la dirección indicada.
05 [val] : SUB #val - Resta el valor al Acumulador.
06 [dir] : BEQ $dir - Salta a $dir si el Flag ZERO está ON.
07 [val] : AND #val - Operación lógica AND bit a bit.
08 [val] : OR  #val - Operación lógica OR bit a bit.
09 [val] : XOR #val - Operación lógica XOR (OR exclusiva).
0A       : NOT      - Invierte todos los bits del Acumulador.
0B [val] : LDX #val - Carga el valor en el Registro X.
0C       : INX      - Incrementa el Registro X en 1.
0D       : DEX      - Decrementa el Registro X en 1.
FF       : HALT     - Detiene la CPU.

REGLAS Y FLAGS:
- Memoria: 256 celdas ($00 a $FF).
- Registros: A y X son de 8 bits (0-255).
- CARRY: Se activa (ON) si una operación excede los 8 bits.
- ZERO : Se activa (ON) si el resultado de la operación es 0.
"""


def run_emulator(cpu):
    while cpu.running:
        cpu.render()
        cmd = input("\n[ENTER: Paso | Q: Menú] > ").upper()
        if cmd == "Q": break
        cpu.step()
    cpu.render()
    if not cpu.running: input("\nHALT alcanzado. ENTER para volver...")


def main():
    cpu = Logica8()
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("      █▒▒▒▒▒▒▒▒▒ LOGICA-8: CONTROL PANEL ▒▒▒▒▒▒▒▒▒█")
        print("      1. Ver Ayuda")
        print("      2. Cargar Programa de Ejemplo")
        print("      3. Introducir Programa en código hexadecimal")
        print("      4. Introducir Programa en lenguaje ensamblador")
        print("      5. Ejecutar Tests de Sistema")
        print("      6. Salir")
        print("      " + "─"*43)
        
        opcion = input(" Selecciona una opción > ")
        
        if opcion == "1":
            os.system('cls' if os.name == 'nt' else 'clear')
            print(HELP_TEXT)
            input("Presiona ENTER para volver...")
        
        elif opcion == "2":
            print("\nPROGRAMAS DISPONIBLES:")
            for k, v in PROGRAMS.items():
                print(f"{k}. {v[0]}")
            p_op = input("Seleccionar > ")
            if p_op in PROGRAMS:
                nombre, bytecode, offset = PROGRAMS[p_op]
                cpu.load_program(bytecode, offset)
                cpu.add_log(f"SISTEMA: Cargado '{nombre}'")
                run_emulator(cpu)

        elif opcion == "3":
            print("\nEscribe los bytes separados por espacios.")
            print("Formatos aceptados: 10 (Dec), 0x0A (Hex), %00001010 (Bin)")
            entrada = input("INPUT > ")
            
            partes = entrada.split()
            bytecode = []
            error = False
            
            for p in partes:
                valor = parse_value(p)
                if valor is not None and 0 <= valor <= 255:
                    bytecode.append(valor)
                else:
                    print(f"Error: '{p}' no es un valor de 8 bits válido.")
                    error = True
                    break
            
            if not error and bytecode:
                cpu.load_program(bytecode, 0x00)
                cpu.add_log("SISTEMA: Código manual cargado en $00")
                run_emulator(cpu)
            elif not error:
                print("Error: El programa está vacío.")
                time.sleep(2)
            else:
                time.sleep(2)

        elif opcion == "4":
            nuevo_programa = assembler()
            if nuevo_programa:
                cpu.load_program(nuevo_programa, 0x00)
                cpu.add_log("SISTEMA: Programa ensamblado y cargado en $00")
                run_emulator(cpu)

        elif opcion == "5":
            run_tests()

        elif opcion == "6":
            print("Apagando LOGICA-8...")
            break

if __name__ == "__main__":
    main()
