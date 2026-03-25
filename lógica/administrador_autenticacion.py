import json #Importamos json para manejar la base de datos de usuarios en formato JSON
import os   #Importamos os para verificar la existencia del archivo de usuarios y manejar rutas

DB_PATH = "usuarios.json" # Ruta del archivo JSON que actúa como base de datos para almacenar los usuarios.

def obtener_lista_usuarios(): #Función para obtener la lista de usuarios desde el archivo JSON. Si el archivo no existe, se crea uno con un usuario admin por defecto.
    if not os.path.exists(DB_PATH): # Si el archivo no existe, lo creamos con un usuario admin por defecto
        data = {"usuarios": [{"username": "admin", "password": "123", "role": "admin", "initials": "AD"}]}
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return data["usuarios"]
    
    with open(DB_PATH, "r", encoding="utf-8") as f: 
        try:
            return json.load(f)["usuarios"]
        except:
            return []


# Función para guardar un nuevo usuario en el archivo JSON. Recibe el nombre de usuario, la contraseña y el rol (admin o usuario).
def guardar_nuevo_usuario(username, password, role):
    usuarios = obtener_lista_usuarios()
    nuevo = {
        "username": username,
        "password": password,
        "role": role,
        "initials": username[:2].upper()
    }
    usuarios.append(nuevo)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump({"usuarios": usuarios}, f, indent=4)

# Función para eliminar un usuario del archivo JSON. Recibe el nombre de usuario a eliminar.
def eliminar_usuario(username):
    usuarios = obtener_lista_usuarios()
    nueva_lista = [u for u in usuarios if u['username'] != username]
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump({"usuarios": nueva_lista}, f, indent=4)