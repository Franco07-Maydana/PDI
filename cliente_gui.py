import ttkbootstrap as ttk 
from tkinter import messagebox
import asyncio
import websockets
import json
import sys

# --- CONFIGURACIÓN DEL SERVIDOR ---
# Asegúrese que esta URI coincida con donde está corriendo server.py
URI = "ws://localhost:8765" 

class StockApp(ttk.Window): 
    def __init__(self, loop):
        # Usamos un tema moderno de Bootstrap
        super().__init__(themename="superhero") 
        self.loop = loop
        
        # Configuración básica de la ventana
        self.title("Sistema de Gestión de Stock Remota")
        self.geometry("650x600")
        self.resizable(False, False) # Evitamos que el usuario cambie el tamaño
        
        # Variables de entrada
        self.id_articulo_var = ttk.StringVar()
        self.nuevo_stock_var = ttk.StringVar()
        self.status_var = ttk.StringVar(value="Esperando acción del usuario...")

        # Configurar la interfaz gráfica
        self._setup_ui()

    def _setup_ui(self):
        # Contenedor principal con padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill='both', expand=True)

        # Título
        ttk.Label(main_frame, text="Inventario Remoto: Actualizar Stock", font=('Helvetica', 20, 'bold'), bootstyle="primary").pack(pady=(0, 20))
        
        # Frame para las entradas
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill='x', pady=5)
        
        # --- Campo ID Artículo ---
        ttk.Label(input_frame, text="ID Artículo:").grid(row=0, column=0, sticky='w', padx=10, pady=10)
        self.id_entry = ttk.Entry(input_frame, textvariable=self.id_articulo_var, width=20)
        self.id_entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        
        # --- Campo Nuevo Stock ---
        ttk.Label(input_frame, text="Nuevo Stock:").grid(row=1, column=0, sticky='w', padx=10, pady=10)
        self.stock_entry = ttk.Entry(input_frame, textvariable=self.nuevo_stock_var, width=20)
        self.stock_entry.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        
        # Configurar la columna para que se expanda
        input_frame.columnconfigure(1, weight=1)

        # Botón de Acción con estilo "success"
        self.send_button = ttk.Button(main_frame, text="Actualizar Stock", 
                                      command=self.on_send_click, bootstyle="success")
        self.send_button.pack(pady=15, fill='x')

        # Etiqueta de Estado
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                      wraplength=400, bootstyle="info")
        self.status_label.pack(pady=5)
        
    def on_send_click(self):
        """Manejador del click. Valida los datos e inicia la tarea asíncrona."""
        id_articulo = self.id_articulo_var.get()
        nuevo_stock = self.nuevo_stock_var.get()

        try:
            id_articulo = int(id_articulo)
            nuevo_stock = int(nuevo_stock)
        except ValueError:
            self.status_var.set("❌ ERROR: ID y Stock deben ser números enteros válidos.")
            self.status_label.config(bootstyle="danger")
            return

        # CORRECCIÓN AQUÍ: Usamos la cadena "disabled" en lugar de ttk.DISABLED
        self.send_button.config(state="disabled") 
        self.status_var.set("Conectando y enviando datos al servidor...")
        self.status_label.config(bootstyle="warning") 
        
        # Programar la tarea asíncrona
        task = self.loop.create_task(self.connect_and_send(id_articulo, nuevo_stock))
        task.add_done_callback(self.handle_task_result)

    def handle_task_result(self, task):
        """Maneja el resultado de la tarea asíncrona una vez que se completa."""
        
        # CORRECCIÓN AQUÍ: Usamos la cadena "normal" en lugar de ttk.NORMAL
        self.send_button.config(state="normal") 
        
        try:
            result = task.result()
            
            if result['status'] == 'success':
                self.status_var.set(f"✅ ÉXITO: {result['message']}")
                self.status_label.config(bootstyle="success")
            else:
                self.status_var.set(f"❌ ERROR de BD: {result['message']}")
                self.status_label.config(bootstyle="danger")
                
        except ConnectionRefusedError:
            self.status_var.set(f"🛑 ERROR de Conexión: Servidor no disponible en {URI}. Verifique que 'server.py' esté corriendo.")
            self.status_label.config(bootstyle="danger")
        except Exception as e:
            self.status_var.set(f"⚠️ ERROR Inesperado: {type(e).__name__} - {e}")
            self.status_label.config(bootstyle="danger")

    async def connect_and_send(self, id_articulo, nuevo_stock):
        """Establece conexión y envía el mensaje de actualización."""
        # Se usa 'async with' para asegurar que la conexión se cierre correctamente.
        async with websockets.connect(URI) as websocket:
            message = json.dumps({
                "id_articulo": id_articulo,
                "nuevo_stock": nuevo_stock
            })
            
            await websocket.send(message)
            response = await websocket.recv()
            
            return json.loads(response)

# --- INTEGRACIÓN ASYNCIO CON TKINTER ---
def tk_after_callback(app, loop):
    """Ejecuta tareas pendientes de asyncio para evitar que la GUI se bloquee."""
    loop.call_soon(loop.stop)
    loop.run_forever()
    
    # Programa la próxima ejecución para mantener la responsividad
    app.after(50, tk_after_callback, app, loop)

if __name__ == '__main__':
    # 1. Configurar el loop de asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    # 2. Crear la aplicación ttkbootstrap
    app = StockApp(loop)

    # 3. Iniciar la integración asíncrona
    app.after(50, tk_after_callback, app, loop)
    
    # 4. Iniciar la GUI
    app.mainloop()

    # 5. Limpieza al cerrar la aplicación
    pending = asyncio.all_tasks(loop)
    for task in pending:
        task.cancel()
    
    if pending:
        loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        
    loop.close()