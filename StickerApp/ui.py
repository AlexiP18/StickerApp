
import tkinter as tk
from tkinter import filedialog, messagebox
from excel_utils import cargar_excel
from pdf_templates import generar_pdf_caja, generar_pdf_etiquetado
from image_utils import asociar_imagen
from tabla_view import TablaView
from vista_previa import mostrar_vista_previa_pdf

class StickerApp:
    def vista_previa_pdf(self):
        from pdf_templates import generar_pdf_caja, generar_pdf_etiquetado
        mostrar_vista_previa_pdf(self.root, self.data, self.tipo_sticker, generar_pdf_caja, generar_pdf_etiquetado)

    def __init__(self, root):
        self.root = root
        self.root.title('StickerApp - Generador de Stickers para Zapatos')
        self.root.geometry('1000x600')
        self.data = None

        # Frame para los botones de carga y agregar
        frame_carga = tk.Frame(root)
        frame_carga.pack(pady=10)
        self.btn_cargar = tk.Button(frame_carga, text='Cargar archivo Excel', command=self.cargar_excel)
        self.btn_cargar.pack(side='left', padx=(0,5))
        self.btn_agregar = tk.Button(frame_carga, text='Agregar archivo Excel', command=self.agregar_excel)
        self.btn_agregar.pack(side='left')

        # Usar TablaView para la tabla principal
        self.tabla = TablaView(root)

        self.btn_asociar_img = tk.Button(root, text='Asociar imágenes a modelos', command=self.abrir_ventana_asociar_imagen)
        self.btn_asociar_img.pack(pady=5)

        self.tipo_sticker = tk.StringVar(value='etiquetado')
        frame_tipo = tk.Frame(root)
        frame_tipo.pack(pady=5)
        tk.Label(frame_tipo, text='Tipo de sticker:').pack(side='left')
        tk.Radiobutton(frame_tipo, text='Etiquetado (interior)', variable=self.tipo_sticker, value='etiquetado').pack(side='left')
        tk.Radiobutton(frame_tipo, text='Caja', variable=self.tipo_sticker, value='caja').pack(side='left')

        self.btn_generar_pdf = tk.Button(root, text='Generar stickers en PDF', command=self.generar_pdf)
        self.btn_generar_pdf.pack(pady=10)

        self.btn_previsualizar = tk.Button(root, text='Vista previa e imprimir', command=self.vista_previa_pdf)
        self.btn_previsualizar.pack(pady=5)

    def agregar_excel(self):
        file_path = filedialog.askopenfilename(
            title='Selecciona un archivo Excel para agregar',
            filetypes=[('Archivos Excel', '*.xlsx *.xls')]
        )
        if not file_path:
            return
        try:
            df_nuevo = cargar_excel(file_path)
            if self.data is not None:
                import pandas as pd
                self.data = pd.concat([self.data, df_nuevo], ignore_index=True)
            else:
                self.data = df_nuevo
            self.mostrar_datos(self.data)
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo agregar el archivo Excel.\n{e}')

    def cargar_excel(self):
        file_path = filedialog.askopenfilename(
            title='Selecciona un archivo Excel',
            filetypes=[('Archivos Excel', '*.xlsx *.xls')]
        )
        if not file_path:
            return
        try:
            df = cargar_excel(file_path)
            self.data = df
            self.mostrar_datos(df)
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo leer el archivo Excel.\n{e}')

    def generar_pdf(self):
        if self.data is None:
            messagebox.showwarning('Advertencia', 'Primero debes cargar un archivo Excel.')
            return
        tipo = self.tipo_sticker.get()
        if tipo == 'etiquetado':
            generar_pdf_etiquetado(self.data)
        else:
            generar_pdf_caja(self.data)

    def mostrar_datos(self, df):
        self.tabla.mostrar_datos(df)

    def abrir_ventana_asociar_imagen(self):
        if self.data is None:
            messagebox.showwarning('Advertencia', 'Primero debes cargar un archivo Excel.')
            return
        asociar_imagen(self.data, self.root)
