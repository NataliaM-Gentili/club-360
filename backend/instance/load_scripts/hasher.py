from os import name
import sys
from werkzeug.security import generate_password_hash, check_password_hash


def usar_desde_terminal():
    # Esto nos ayudará a ver qué está recibiendo realmente Python
    argumentos = sys.argv[1:]
    total_argumentos = len(argumentos)

    # Caso 1: Generar hash (Se pasa 1 argumento)
    if total_argumentos == 1:
        password = argumentos[0]
        hash_resultado = generate_password_hash(password, method="scrypt")
        print("\n[Hash Generado]:")
        print(hash_resultado)

    elif total_argumentos == 2:
        hash_guardado = argumentos[0]
        password_intento = argumentos[1]

        print(f"\nVerificando contraseña contra el hash...")

        if check_password_hash(hash_guardado, password_intento):
            print("\033[92m[✓] ¡COINCIDE! La contraseña es correcta.\033[0m")
        else:
            print(
                "\033[91m[X] NO COINCIDE. El hash o la contraseña son incorrectos.\033[0m"
            )
            sys.exit(1)


usar_desde_terminal()
