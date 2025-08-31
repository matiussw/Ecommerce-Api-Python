#!/usr/bin/env python3
"""
Script para hashear contraseñas en texto plano en la base de datos SQLite
usando PBKDF2-SHA256 para mantener consistencia.
"""

import sqlite3
import hashlib
import secrets
from werkzeug.security import generate_password_hash, check_password_hash

def connect_database(db_path):
    """Conectar a la base de datos SQLite"""
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

def is_password_hashed(password):
    """Verificar si la contraseña ya está hasheada"""
    return password.startswith('pbkdf2:sha256:')

def hash_password(password):
    """Hashear contraseña usando PBKDF2-SHA256"""
    # Usar el mismo método que Werkzeug con 600000 iteraciones
    return generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

def update_passwords(db_path, dry_run=True):
    """
    Actualizar contraseñas en texto plano a formato hasheado
    
    Args:
        db_path (str): Ruta a la base de datos
        dry_run (bool): Si es True, solo muestra qué haría sin modificar la DB
    """
    
    conn = connect_database(db_path)
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Obtener todos los usuarios
        cursor.execute("SELECT ID_User, UserName, PasswordKey FROM Users")
        users = cursor.fetchall()
        
        updates_needed = []
        
        print(f"Analizando {len(users)} usuarios...\n")
        
        for user_id, username, password in users:
            if not is_password_hashed(password):
                hashed_password = hash_password(password)
                updates_needed.append((user_id, username, password, hashed_password))
                print(f"Usuario: {username}")
                print(f"  Contraseña actual: {password}")
                print(f"  Nueva contraseña hasheada: {hashed_password[:50]}...")
                print()
            else:
                print(f"Usuario {username}: contraseña ya hasheada ✓")
        
        print(f"\nResumen: {len(updates_needed)} contraseñas necesitan ser actualizadas")
        
        if updates_needed and not dry_run:
            print("\nActualizando contraseñas en la base de datos...")
            
            for user_id, username, old_password, new_password in updates_needed:
                cursor.execute(
                    "UPDATE Users SET PasswordKey = ? WHERE ID_User = ?",
                    (new_password, user_id)
                )
                print(f"✓ Actualizado usuario: {username}")
            
            conn.commit()
            print(f"\n¡Éxito! {len(updates_needed)} contraseñas actualizadas.")
        
        elif updates_needed and dry_run:
            print("\n[MODO SIMULACIÓN] - No se realizaron cambios.")
            print("Ejecuta con dry_run=False para aplicar los cambios.")
        
        else:
            print("\nTodas las contraseñas ya están hasheadas. No se necesitan cambios.")
            
    except sqlite3.Error as e:
        print(f"Error ejecutando consulta: {e}")
        return False
    
    finally:
        conn.close()
    
    return True

def verify_password_update(db_path, username, original_password):
    """
    Verificar que una contraseña hasheada funcione correctamente
    
    Args:
        db_path (str): Ruta a la base de datos
        username (str): Nombre del usuario a verificar
        original_password (str): Contraseña original en texto plano
    """
    conn = connect_database(db_path)
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT PasswordKey FROM Users WHERE UserName = ?", (username,))
        result = cursor.fetchone()
        
        if result:
            hashed_password = result[0]
            is_valid = check_password_hash(hashed_password, original_password)
            print(f"Verificación para {username}: {'✓ VÁLIDA' if is_valid else '✗ INVÁLIDA'}")
            return is_valid
        else:
            print(f"Usuario {username} no encontrado")
            return False
            
    except sqlite3.Error as e:
        print(f"Error en verificación: {e}")
        return False
    
    finally:
        conn.close()

def main():
    # Ruta a tu base de datos
    DB_PATH = "/Users/teo/Documents/Ecommerce-Api-Python/database/ecommerce.db"
    
    print("=== SCRIPT DE ACTUALIZACIÓN DE CONTRASEÑAS ===\n")
    
    # Paso 1: Ejecutar en modo simulación
    print("PASO 1: Simulación (no modifica la base de datos)")
    print("-" * 50)
    update_passwords(DB_PATH, dry_run=True)
    
    # Solicitar confirmación
    print("\n" + "="*60)
    response = input("¿Quieres proceder con la actualización? (y/N): ").lower()
    
    if response in ['y', 'yes', 'sí', 's']:
        print("\nPASO 2: Aplicando cambios")
        print("-" * 30)
        update_passwords(DB_PATH, dry_run=False)
        
        # Verificar algunas contraseñas (opcional)
        print("\nPASO 3: Verificación de muestra")
        print("-" * 35)
        # Aquí puedes verificar contraseñas específicas si sabes cuáles eran
        # verify_password_update(DB_PATH, "admin", "admin123")
        # verify_password_update(DB_PATH, "juan_perez", "password123")
        
    else:
        print("Operación cancelada.")

if __name__ == "__main__":
    main()

    