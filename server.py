import asyncio
import websockets
import mysql.connector
import json

# --- CONFIGURACIÓN DE LA BASE DE DATOS ---
DB_CONFIG = {
    'host': 'localhost',      # ¡Asegúrese de cambiar esto!
    'user': 'root',           # ¡Asegúrese de cambiar esto!
    'password': '',# ¡Asegúrese de cambiar esto!
    'database': 'miguelhogar' 
}

# --- FUNCIÓN PARA CONECTAR Y ACTUALIZAR STOCK (SIN CAMBIOS) ---
async def update_stock_in_db(id_articulo, nuevo_stock):
    """Conecta a la BD y actualiza el campo Stock del artículo."""
    try:
        db = mysql.connector.connect(**DB_CONFIG)
        cursor = db.cursor()
        
        # SQL para actualizar la tabla 'articulos'
        sql = "UPDATE articulos SET Stock = %s WHERE Id_articulo = %s"
        val = (nuevo_stock, id_articulo)
        
        cursor.execute(sql, val)
        db.commit()
        
        if cursor.rowcount > 0:
            return True, f"Stock actualizado para Id_articulo {id_articulo}. Nuevo Stock: {nuevo_stock}"
        else:
            return False, f"Error: No se encontró el artículo con Id_articulo {id_articulo}."

    except mysql.connector.Error as err:
        print(f"Error de base de datos: {err}")
        return False, f"Error de BD: {err}"
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

# --- HANDLER DEL SERVIDOR WEBSOCKET (CORRECCIÓN CLAVE) ---
# Se elimina el argumento 'path' para resolver el TypeError.
async def handler(websocket): 
    """Maneja las conexiones y mensajes entrantes del cliente."""
    print(f"Cliente conectado desde {websocket.remote_address}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                
                if 'id_articulo' in data and 'nuevo_stock' in data:
                    id_articulo = int(data['id_articulo'])
                    nuevo_stock = int(data['nuevo_stock'])

                    print(f"Recibida solicitud: Articulo={id_articulo}, Stock={nuevo_stock}")

                    success, message_result = await update_stock_in_db(id_articulo, nuevo_stock)

                    response = json.dumps({
                        "status": "success" if success else "error",
                        "message": message_result
                    })
                    await websocket.send(response)
                else:
                    response = json.dumps({"status": "error", "message": "Faltan campos id_articulo o nuevo_stock."})
                    await websocket.send(response)

            except json.JSONDecodeError:
                await websocket.send(json.dumps({"status": "error", "message": "Formato de mensaje JSON inválido."}))
            except ValueError:
                await websocket.send(json.dumps({"status": "error", "message": "Los valores de ID y Stock deben ser números enteros."}))

    except websockets.exceptions.ConnectionClosedOK:
        print(f"Cliente desconectado correctamente.")
    except Exception as e:
        print(f"Ocurrió un error general en el handler: {e}")


# --- INICIO DEL SERVIDOR (SIN CAMBIOS) ---
async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Servidor WebSocket iniciado en ws://0.0.0.0:8765. Esperando conexiones...")
        await asyncio.Future() # Corre indefinidamente

if __name__ == "__main__":
    asyncio.run(main())