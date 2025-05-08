import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageTk
import os
from gui.seleccion import registrar_imagen, eliminar_seleccionadas, imagenes_registradas, imagenes_seleccionadas
from gui.eventos import mostrar_nombre, agregar_imagen, actualizar_visibilidad_dpi, detectar_cantidad_y_aplicar_comportamiento, guardar_imagenes_redimensionadas



class RedimensionadorGUI:
    def __init__(self, master):
        def solo_numeros(valor):
            if valor == "":
                return True
            try:
                float(valor)
                return float(valor) > 0
            except ValueError:
                return False

        validacion = master.register(solo_numeros)

        from gui.scroll import activar_scroll
        self.master = master
        self.datos_imagenes = []

        self.frame_principal = tk.Frame(master)
        self.frame_principal.pack(fill="both", expand=True)

        self.frame_scrollable = tk.Frame(self.frame_principal)
        self.frame_scrollable.pack(side="left", padx=10, pady=10)

        self.canvas = tk.Canvas(self.frame_scrollable, bg="#e0e0e0", width=700, height=450)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.scroll_y = tk.Scrollbar(self.frame_scrollable, orient="vertical", command=self.canvas.yview)
        self.scroll_y.grid(row=0, column=1, sticky="ns")

        self.scroll_x = tk.Scrollbar(self.frame_scrollable, orient="horizontal", command=self.canvas.xview)
        self.scroll_x.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        self.frame_scrollable.grid_rowconfigure(0, weight=1)
        self.frame_scrollable.grid_columnconfigure(0, weight=1)

        self.frame_visualizador = tk.Frame(self.canvas, bg="#f8f8f8")
        self.canvas.create_window((0, 0), window=self.frame_visualizador, anchor="nw")

        self.frame_visualizador.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        activar_scroll(self.canvas, self.master)

        self.frame_lateral = tk.Frame(self.frame_principal, width=120)
        self.frame_lateral.pack(side="right", fill="y", padx=(0,10), pady=10)


        self.btn_agregar = tk.Button(self.frame_lateral, text="+", font=("Arial", 14), height=2, width=4, command=lambda: agregar_imagen(self))
        self.btn_agregar.pack(pady=10)

        self.btn_borrar = tk.Button(
            self.frame_lateral, text="🗑", font=("Arial", 12), height=2, width=4,
            command=lambda: eliminar_seleccionadas(self)
        )
        self.btn_borrar.pack(pady=10)

        from gui.eventos import redimensionar_lote  # al principio del archivo

        self.btn_redimensionar = tk.Button(
            self.frame_lateral,
            text="↔",
            font=("Arial", 12),
            height=2,
            width=4,
            command=lambda: redimensionar_lote(self)
        )
        self.btn_redimensionar.pack(pady=10)


        self.frame_inferior = tk.Frame(master, height=80)
        self.frame_inferior.pack(fill="x", side="bottom", padx=10, pady=5)

        tk.Label(self.frame_inferior, text="Alto:").pack(side="left", padx=5)

        self.entry_alto = tk.Entry(
        self.frame_inferior,
        width=6,
        validate="key",
        validatecommand=(validacion, "%P")
        )
        self.entry_alto.pack(side="left")

        tk.Label(self.frame_inferior, text="Ancho:").pack(side="left", padx=5)

        self.entry_ancho = tk.Entry(
        self.frame_inferior,
        width=6,
        validate="key",
        validatecommand=(validacion, "%P")
        )
        self.entry_ancho.pack(side="left")


        self.entry_alto.bind("<FocusIn>", lambda e: self.entry_alto.config(bg="white"))
        self.entry_ancho.bind("<FocusIn>", lambda e: self.entry_ancho.config(bg="white"))

        self.entry_alto.bind("<KeyRelease>", lambda e: detectar_cantidad_y_aplicar_comportamiento(self, "alto"))
        self.entry_ancho.bind("<KeyRelease>", lambda e: detectar_cantidad_y_aplicar_comportamiento(self, "ancho"))




        # Selector de unidad: pixeles o centímetros
        self.unidad = tk.StringVar(value="px")
        tk.Label(self.frame_inferior, text="Unidad:").pack(side="left", padx=(20, 5))

        unidad_px = tk.Radiobutton(self.frame_inferior, text="px", variable=self.unidad, value="px", command=lambda: actualizar_visibilidad_dpi(self))
        unidad_px.pack(side="left")

        unidad_cm = tk.Radiobutton(self.frame_inferior, text="cm", variable=self.unidad, value="cm", command=lambda: actualizar_visibilidad_dpi(self))
        unidad_cm.pack(side="left")

        # Campo para DPI (solo visible si se elige cm)
        self.label_dpi = tk.Label(self.frame_inferior, text="DPI:")
        self.entry_dpi = tk.Entry(self.frame_inferior, width=5)
        self.entry_dpi.insert(0, "150")
        self.label_dpi.pack_forget()
        self.entry_dpi.pack_forget()

        self.btn_guardar = tk.Button(
        self.frame_lateral,
            text="💾",
            font=("Arial", 12),
            height=2,
            width=4,
            command=lambda: guardar_imagenes_redimensionadas(self)
            )
        self.btn_guardar.pack(pady=10)

        

        self.bloquear_proporcion = tk.IntVar(value=1)
        self.check_proporcion = tk.Checkbutton(self.frame_inferior, text="Mantener proporciones", variable=self.bloquear_proporcion)
        self.check_proporcion.pack(side="left", padx=10)

        self.status_label = tk.Label(self.frame_inferior, text="0 imágenes cargadas", anchor="w", fg="gray")
        self.status_label.pack(side="right", padx=10)



    def redibujar_imagenes(self):
        import os
        from gui.seleccion import registrar_imagen

        imagenes_registradas.clear()
        imagenes_seleccionadas.clear()

        # Eliminar tarjetas anteriores
        for widget in self.frame_visualizador.winfo_children():
            widget.destroy()

        for idx, datos in enumerate(self.datos_imagenes):
            ruta = datos["ruta"]
            nombre_archivo = datos["nombre"]
            try:
                # Abrir imagen y crear thumbnail
                img = Image.open(ruta)
                img.thumbnail((150, 150))
                tk_img = ImageTk.PhotoImage(img)

                # Calcular posición en grilla
                fila = idx // 5
                columna = idx % 5

                # Crear contenedor de tarjeta
                frame_tarjeta = tk.Frame(self.frame_visualizador, bg="#ffffff", bd=2, relief="solid")
                frame_tarjeta.grid(row=fila, column=columna, padx=5, pady=5)

                # Imagen
                lbl_imagen = tk.Label(frame_tarjeta, image=tk_img, bg="#ffffff")
                lbl_imagen.image = tk_img  # mantener referencia
                lbl_imagen.pack()

                # Obtener nombre del archivo sin extensión
                nombre_archivo = os.path.splitext(os.path.basename(ruta))[0]

                # Mostrar nombre debajo de la imagen
                mostrar_nombre(frame_tarjeta, self.datos_imagenes[idx], idx)

                #   lbl_nombre = tk.Label(
                #   frame_tarjeta,
                #   text=nombre_archivo,
                #   wraplength=150,
                #   justify="center",
                #   bg="#ffffff",
                #   font=("Arial", 9)
                #   )
                #   lbl_nombre.pack(pady=(2, 0))

                # Registrar imagen (solo con el label de la imagen)
                registrar_imagen(lbl_imagen, ruta, self)

            except Exception as e:
                print(f"Error cargando imagen: {e}")

        self.actualizar_estado()




        

    def actualizar_estado(self):
       
        total = len(self.datos_imagenes)

        self.status_label.config(text=f"{total} imágenes cargadas")
