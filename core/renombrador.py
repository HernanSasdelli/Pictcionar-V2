import tkinter as tk
from tkinter import Label



def mostrar_nombre(frame, datos_imagen, idx):
    lbl_nombre = tk.Label(
    frame,
    text=datos_imagen["nombre"],
    wraplength=150,
    justify="center",
    bg="#ffffff",
    font=("Arial", 9)
)
    lbl_nombre.pack(pady=(2, 0))
    from gui.eventos import activar_edicion_nombre  # para evitar import circular al definir todo junto
    lbl_nombre.bind("<Button-1>", lambda e: activar_edicion_nombre(e, frame, datos_imagen, idx))

def guardar_nombre(entry, frame, datos_imagen, idx):
    nuevo_nombre = entry.get().strip()
    if nuevo_nombre:
        datos_imagen["nombre"] = nuevo_nombre
    entry.destroy()
    mostrar_nombre(frame, datos_imagen, idx)

