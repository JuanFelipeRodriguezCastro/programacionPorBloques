import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np

class Bloque:
    """Representa un bloque visual de la red neuronal en el Canvas."""

    def __init__(self, aplicacion, tipo, x, y, neuronas=1, activacion="Sigmoid"):
        self.aplicacion = aplicacion
        self.tipo = tipo
        self.neuronas = neuronas
        self.activacion = activacion
        self.x = x
        self.y = y
        self.nombre = {
            "entrada": "Entrada",
            "oculta": "Capa Oculta",
            "salida": "Salida",
        }[tipo]
        self.descripcion = {
            "entrada": "Recibe los datos de entrada y define la cantidad de características.",
            "oculta": "Aplica pesos, sesgo y una función de activación para crear nuevas representaciones.",
            "salida": "Genera la predicción final de la red neuronal.",
        }[tipo]

        self.canvas = aplicacion.canvas
        self.ancho = 165
        self.alto = 90

        self.rect = self.canvas.create_rectangle(
            x - self.ancho // 2,
            y - self.alto // 2,
            x + self.ancho // 2,
            y + self.alto // 2,
            fill="#dbeafe",
            outline="#1d4ed8",
            width=2,
            tags=("bloque", tipo),
        )

        self.lbl_tipo = self.canvas.create_text(
            x,
            y - 20,
            text=self.nombre,
            font=("Arial", 10, "bold"),
            fill="#111827",
            tags=("bloque", tipo),
        )

        self.lbl_desc = self.canvas.create_text(
            x,
            y + 4,
            text=self.descripcion,
            font=("Arial", 8),
            fill="#374151",
            width=150,
            tags=("bloque", tipo),
            justify="center",
        )

        self.btn_configurar = tk.Button(
            self.canvas,
            text="Config",
            font=("Arial", 8),
            width=8,
            command=lambda: self.abrir_configuracion(),
        )
        self.btn_codigo = tk.Button(
            self.canvas,
            text="Código",
            font=("Arial", 8),
            width=8,
            command=lambda: self.mostrar_codigo(),
        )
        self.btn_eliminar = tk.Button(
            self.canvas,
            text="X",
            font=("Arial", 8, "bold"),
            width=3,
            command=lambda: self.eliminar(),
        )

        self._id_btn_config = self.canvas.create_window(
            x + 55,
            y + 35,
            anchor="nw",
            window=self.btn_configurar,
        )
        self._id_btn_codigo = self.canvas.create_window(
            x - 65,
            y + 35,
            anchor="nw",
            window=self.btn_codigo,
        )
        self._id_btn_eliminar = self.canvas.create_window(
            x - 20,
            y - 45,
            anchor="nw",
            window=self.btn_eliminar,
        )

        self.canvas.tag_bind(self.rect, "<ButtonPress-1>", self._on_press)
        self.canvas.tag_bind(self.lbl_tipo, "<ButtonPress-1>", self._on_press)
        self.canvas.tag_bind(self.lbl_desc, "<ButtonPress-1>", self._on_press)

    def _on_press(self, event):
        self.aplicacion.iniciar_arrastre_bloque(self, event.x, event.y)

    def actualizar_posicion(self, dx, dy):
        self.x += dx
        self.y += dy
        self.canvas.coords(
            self.rect,
            self.x - self.ancho // 2,
            self.y - self.alto // 2,
            self.x + self.ancho // 2,
            self.y + self.alto // 2,
        )
        self.canvas.coords(self.lbl_tipo, self.x, self.y - 20)
        self.canvas.coords(self.lbl_desc, self.x, self.y + 4)
        self.canvas.coords(self._id_btn_config, self.x + 55, self.y + 35)
        self.canvas.coords(self._id_btn_codigo, self.x - 65, self.y + 35)
        self.canvas.coords(self._id_btn_eliminar, self.x - 20, self.y - 45)
        self.aplicacion.dibujar_conexiones()

    def abrir_configuracion(self):
        """Abre una pequeña ventana para configurar neuronas y activación."""
        ventana = tk.Toplevel(self.aplicacion.ventana)
        ventana.title(f"Configurar {self.nombre}")
        ventana.geometry("280x180")
        ventana.transient(self.aplicacion.ventana)
        ventana.grab_set()

        tk.Label(ventana, text="Número de neuronas:").pack(pady=(10, 2))
        entrada_neuronas = tk.Entry(ventana)
        entrada_neuronas.insert(0, str(self.neuronas))
        entrada_neuronas.pack(padx=10, pady=2, fill="x")

        tk.Label(ventana, text="Función de activación:").pack(pady=(10, 2))
        combo = ttk.Combobox(
            ventana,
            values=["Sigmoid", "ReLU", "Tanh"],
            state="readonly",
        )
        combo.set(self.activacion)
        combo.pack(padx=10, pady=2, fill="x")

        def guardar():
            try:
                nuevas_neuronas = int(entrada_neuronas.get())
                if nuevas_neuronas < 1:
                    raise ValueError
                self.neuronas = nuevas_neuronas
                self.activacion = combo.get()
                self.actualizar_texto_bloque()
                self.aplicacion.actualizar_panel_entrada()
                self.aplicacion.dibujar_conexiones()
                ventana.destroy()
            except ValueError:
                messagebox.showerror("Error", "Introduce un número entero válido de neuronas.")

        ttk.Button(ventana, text="Guardar", command=guardar).pack(pady=(12, 10))

    def actualizar_texto_bloque(self):
        texto = f"{self.nombre}\nNeur: {self.neuronas}\nAct: {self.activacion}"
        if self.tipo == "entrada":
            texto = f"{self.nombre}\nNeur: {self.neuronas}\nRecibe datos"
        self.canvas.itemconfig(self.lbl_tipo, text=texto.split("\n")[0])
        self.canvas.itemconfig(self.lbl_desc, text=("\n".join(texto.split("\n")[1:]))[:80])

    def mostrar_codigo(self):
        """Muestra el fragmento de Python que ejecuta ese bloque."""
        ventana = tk.Toplevel(self.aplicacion.ventana)
        ventana.title(f"Código del bloque {self.nombre}")
        ventana.geometry("560x280")
        ventana.transient(self.aplicacion.ventana)
        ventana.grab_set()

        texto = tk.Text(ventana, wrap="word", font=("Consolas", 10))
        texto.insert("1.0", self.obtener_codigo_python())
        texto.config(state="disabled")
        texto.pack(fill="both", expand=True, padx=10, pady=10)

    def obtener_codigo_python(self):
        if self.tipo == "entrada":
            return (
                "# Bloque de Entrada\n"
                "# Define la cantidad de variables de entrada que llega a la red.\n"
                "x = np.array(entrada_usuario, dtype=float)\n"
                "# El vector es la primera capa visible para la red."
            )
        if self.tipo == "oculta":
            return (
                "# Bloque de Capa Oculta\n"
                "# z = x @ W + b\n"
                "# a = activacion(z)\n"
                f"z = x @ pesos + sesgo\n"
                f"a = {self.activacion.lower()}(z)\n"
                "# Esta salida se usa como entrada de la siguiente capa."
            )
        return (
            "# Bloque de Salida\n"
            "# Esta capa produce la predicción final de la red.\n"
            "z = x @ pesos + sesgo\n"
            f"a = {self.activacion.lower()}(z)\n"
            "# a contiene el resultado final de la red."
        )

    def eliminar(self):
        self.canvas.delete(self.rect, self.lbl_tipo, self.lbl_desc, self._id_btn_config, self._id_btn_codigo, self._id_btn_eliminar)
        self.btn_configurar.destroy()
        self.btn_codigo.destroy()
        self.btn_eliminar.destroy()
        self.aplicacion.bloques = [b for b in self.aplicacion.bloques if b is not self]
        self.aplicacion.actualizar_panel_entrada()
        self.aplicacion.dibujar_conexiones()

    def centro_x(self):
        return self.x


class RedNeuronal:
    """Modelo matemático de la red neuronal MLP a ejecutar."""

    def __init__(self, arquitectura):
        self.arquitectura = arquitectura

    def activacion(self, nombre, z):
        if nombre == "Sigmoid":
            return 1 / (1 + np.exp(-z))
        if nombre == "ReLU":
            return np.maximum(0, z)
        if nombre == "Tanh":
            return np.tanh(z)
        raise ValueError("Función de activación no soportada")

    def forward(self, entrada_usuario):
        """Ejecuta el forward pass real de la red con NumPy."""
        entrada = np.array(entrada_usuario, dtype=float).reshape(1, -1)
        valores_capa = [entrada]
        pesos = []
        sesgos = []
        activaciones = []
        capas = []

        for i in range(len(self.arquitectura) - 1):
            capa_actual = self.arquitectura[i]
            capa_siguiente = self.arquitectura[i + 1]

            w = np.random.default_rng().normal(0, 1, size=(capa_actual.neuronas, capa_siguiente.neuronas))
            b = np.random.default_rng().normal(0, 1, size=(1, capa_siguiente.neuronas))

            pesos.append(w)
            sesgos.append(b)

            z = valores_capa[-1] @ w + b
            a = self.activacion(capa_siguiente.activacion, z)

            valores_capa.append(a)
            activaciones.append(a)
            capas.append(capa_siguiente)

        return {
            "salida": valores_capa[-1],
            "intermedios": valores_capa[1:],
            "pesos": pesos,
            "sesgos": sesgos,
            "capas": capas,
        }


class AplicacionGUI:
    """Interfaz principal del constructor visual de redes MLP."""

    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Constructor visual de redes MLP")
        self.ventana.geometry("1200x760")

        self.bloques = []
        self.arrastre = None
        self.ultimo_tipo_drag = None
        self.entrada_usuario_campos = []

        self.panel_lateral = tk.Frame(self.ventana, bg="#f3f4f6", padx=10, pady=10)
        self.panel_lateral.pack(side="left", fill="y")

        tk.Label(self.panel_lateral, text="Bloques disponibles", font=("Arial", 12, "bold")).pack(pady=(0, 10))

        self.bloques_sidebar = {
            "entrada": tk.Button(self.panel_lateral, text="Bloque de Entrada", width=22, command=lambda: self.crear_copia_de_bloque("entrada")),
            "oculta": tk.Button(self.panel_lateral, text="Bloque de Capa Oculta", width=22, command=lambda: self.crear_copia_de_bloque("oculta")),
            "salida": tk.Button(self.panel_lateral, text="Bloque de Salida", width=22, command=lambda: self.crear_copia_de_bloque("salida")),
        }

        for boton in self.bloques_sidebar.values():
            boton.pack(pady=6)

        self.canvas = tk.Canvas(self.ventana, width=760, height=600, bg="#ffffff", highlightthickness=1, highlightbackground="#94a3b8")
        self.canvas.pack(side="left", padx=(10, 10), pady=10)
        self.canvas.bind("<ButtonRelease-1>", self.fin_arrastre)
        self.canvas.bind("<B1-Motion>", self.mover_drag)

        self.panel_derecha = tk.Frame(self.ventana, bg="#f8fafc")
        self.panel_derecha.pack(side="right", fill="y", padx=(0, 10), pady=10)

        tk.Label(self.panel_derecha, text="Configuración de entrada", font=("Arial", 11, "bold")).pack(pady=(5, 8))
        self.frame_entrada = tk.Frame(self.panel_derecha)
        self.frame_entrada.pack(fill="x", pady=(0, 12))

        self.boton_validar = tk.Button(self.panel_derecha, text="Validar estructura", command=self.validar_estructura)
        self.boton_validar.pack(fill="x", pady=4)

        self.boton_ejecutar = tk.Button(self.panel_derecha, text="Ejecutar red", command=self.ejecutar_red)
        self.boton_ejecutar.pack(fill="x", pady=4)

        self.boton_limpiar = tk.Button(self.panel_derecha, text="Limpiar lienzo", command=self.limpiar_lienzo)
        self.boton_limpiar.pack(fill="x", pady=4)

        tk.Label(self.panel_derecha, text="Salida de la red", font=("Arial", 11, "bold")).pack(pady=(10, 4))
        self.texto_resultados = tk.Text(self.panel_derecha, width=34, height=20, wrap="word")
        self.texto_resultados.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>", self.click_referencia_canvas)
        self.actualizar_panel_entrada()
        self.dibujar_conexiones()

    def click_referencia_canvas(self, event):
        """Permite iniciar un arrastre simple cuando el usuario hace click sobre el lienzo."""
        self.arrastre = {"x": event.x, "y": event.y, "bloque": None}

    def iniciar_arrastre_bloque(self, bloque, x, y):
        self.arrastre = {"x": x, "y": y, "bloque": bloque}

    def mover_drag(self, event):
        if self.arrastre and self.arrastre["bloque"] is not None:
            dx = event.x - self.arrastre["x"]
            dy = event.y - self.arrastre["y"]
            self.arrastre["bloque"].actualizar_posicion(dx, dy)
            self.arrastre["x"] = event.x
            self.arrastre["y"] = event.y

    def fin_arrastre(self, event):
        if self.arrastre and self.arrastre["bloque"] is not None:
            self.arrastre = None

    def crear_copia_de_bloque(self, tipo):
        """Crea un bloque de manera visual sobre el canvas en la posición del cursor."""
        x = 130 + len(self.bloques) * 20
        y = 110 + len(self.bloques) * 20
        bloque = Bloque(self, tipo, x, y, neuronas=(3 if tipo != "entrada" else 2), activacion="Sigmoid")
        self.bloques.append(bloque)
        self.actualizar_panel_entrada()
        self.dibujar_conexiones()

    def limpiar_lienzo(self):
        for bloque in list(self.bloques):
            bloque.eliminar()
        self.bloques = []
        self.texto_resultados.delete("1.0", tk.END)
        self.actualizar_panel_entrada()
        self.dibujar_conexiones()

    def actualizar_panel_entrada(self):
        """Actualiza los campos donde el usuario escribe el vector de entrada."""
        for hijo in self.frame_entrada.winfo_children():
            hijo.destroy()
        self.entrada_usuario_campos = []

        bloque_entrada = next((b for b in self.bloques if b.tipo == "entrada"), None)
        if bloque_entrada is None:
            tk.Label(self.frame_entrada, text="Aún no hay bloque de entrada.").pack(anchor="w")
            return

        for i in range(1, bloque_entrada.neuronas + 1):
            fila = tk.Frame(self.frame_entrada)
            fila.pack(fill="x", pady=3)
            tk.Label(fila, text=f"x{i}:").pack(side="left")
            entrada = tk.Entry(fila, width=12)
            entrada.pack(side="left", padx=5)
            entrada.insert(0, "0")
            self.entrada_usuario_campos.append(entrada)

    def obtener_bloques_ordenados(self):
        """Ordena los bloques según su posición horizontal en el canvas."""
        return sorted(self.bloques, key=lambda b: (b.centro_x(), b.y))

    def validar_estructura(self):
        """Valida que la red visual tenga una arquitectura correcta."""
        bloques = self.obtener_bloques_ordenados()

        if not bloques:
            messagebox.showerror("Error", "Debes agregar al menos un bloque para construir la red.")
            return False

        entradas = [b for b in bloques if b.tipo == "entrada"]
        salidas = [b for b in bloques if b.tipo == "salida"]

        if len(entradas) != 1:
            messagebox.showerror("Error", "Debe existir exactamente un bloque de Entrada.")
            return False

        if len(salidas) != 1:
            messagebox.showerror("Error", "Debe existir exactamente un bloque de Salida.")
            return False

        if bloques[0].tipo != "entrada":
            messagebox.showerror("Error", "El bloque de Entrada debe ir primero.")
            return False

        if bloques[-1].tipo != "salida":
            messagebox.showerror("Error", "El bloque de Salida debe ir de último.")
            return False

        tipos = [b.tipo for b in bloques]
        if any(t == "entrada" for t in tipos[1:]) or any(t == "salida" for t in tipos[:-1]):
            messagebox.showerror("Error", "La arquitectura debe seguir el orden: Entrada -> Capas ocultas -> Salida.")
            return False

        return True

    def dibujar_conexiones(self):
        """Dibuja flechas conectando las capas en el orden visual del canvas."""
        self.canvas.delete("conexion")
        bloques = self.obtener_bloques_ordenados()
        for i in range(len(bloques) - 1):
            actual = bloques[i]
            siguiente = bloques[i + 1]
            x1 = actual.x + actual.ancho // 2
            y1 = actual.y
            x2 = siguiente.x - siguiente.ancho // 2
            y2 = siguiente.y
            self.canvas.create_line(x1, y1, x2, y2, fill="#2563eb", width=2, arrow=tk.LAST, tags="conexion")

    def obtener_vector_entrada(self):
        """Lee el vector de entrada escrito por el usuario en el panel derecho."""
        valores = []
        for campo in self.entrada_usuario_campos:
            try:
                valores.append(float(campo.get()))
            except ValueError:
                raise ValueError("Todos los valores de entrada deben ser números.")
        return valores

    def ejecutar_red(self):
        """Ejecuta la red construida y muestra las salidas intermedias."""
        if not self.validar_estructura():
            return

        bloques = self.obtener_bloques_ordenados()
        bloque_entrada = bloques[0]
        if len(self.entrada_usuario_campos) != bloque_entrada.neuronas:
            messagebox.showerror("Error", "El número de campos de entrada no coincide con las neuronas del bloque de Entrada.")
            return

        try:
            vector_entrada = self.obtener_vector_entrada()
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        if len(vector_entrada) != bloque_entrada.neuronas:
            messagebox.showerror("Error", "La longitud del vector de entrada no coincide con el número de neuronas de entrada.")
            return

        red = RedNeuronal(bloques)
        resultado = red.forward(vector_entrada)

        salida = resultado["salida"]
        self.texto_resultados.delete("1.0", tk.END)
        self.texto_resultados.insert("1.0", "Resultados de la red neuronal\n\n")
        self.texto_resultados.insert(tk.END, "Vector de entrada:\n")
        self.texto_resultados.insert(tk.END, f"{vector_entrada}\n\n")

        for idx, capa in enumerate(resultado["intermedios"], start=1):
            self.texto_resultados.insert(tk.END, f"Capa intermedia {idx}:\n")
            self.texto_resultados.insert(tk.END, f"{np.array2string(capa, precision=4)}\n\n")

        self.texto_resultados.insert(tk.END, "Salida final:\n")
        self.texto_resultados.insert(tk.END, f"{np.array2string(salida, precision=4)}\n")

        messagebox.showinfo("Éxito", "La red se ejecutó correctamente.")

    def iniciar(self):
        self.ventana.mainloop()


if __name__ == "__main__":
    app = AplicacionGUI()
    app.iniciar()
