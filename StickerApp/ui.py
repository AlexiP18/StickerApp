
import tkinter as tk
from tkinter import filedialog, messagebox
from excel_utils import cargar_excel
from pdf_templates import generar_pdf_caja, generar_pdf_etiquetado
from image_utils import asociar_imagen
from tabla_view import TablaView
from vista_previa import mostrar_vista_previa_pdf

class StickerApp:
    def vaciar_tabla(self):
        self.data = None
        self.tabla.vaciar()
    def vista_previa_pdf(self):
        from pdf_templates import generar_pdf_caja, generar_pdf_etiquetado
        mostrar_vista_previa_pdf(self.root, self.data, self.tipo_sticker, generar_pdf_caja, generar_pdf_etiquetado)

    def __init__(self, root):
        self.root = root
        self.root.title('StickerApp - Generador de Stickers para Zapatos')
        self.root.geometry('1000x600')
        self.data = None

        # HEADER: Botones de Excel (arriba)
        frame_header = tk.Frame(self.root)
        frame_header.pack(side='top', fill='x', pady=10)
        header_inner = tk.Frame(frame_header)
        header_inner.pack(expand=True, fill='both')
        # Centrar horizontal y vertical
        header_inner.grid_rowconfigure(0, weight=1)
        header_inner.grid_columnconfigure(0, weight=1)
        header_buttons = tk.Frame(header_inner)
        header_buttons.grid(row=0, column=0, sticky='nsew')
        # Usar grid para centrar los botones
        self.btn_agregar = tk.Button(header_buttons, text='Agregar archivo Excel', command=self.agregar_excel)
        self.btn_vaciar = tk.Button(header_buttons, text='Vaciar tabla', command=self.vaciar_tabla)
        self.btn_descargar = tk.Button(header_buttons, text='Descargar Excel', command=self.descargar_excel)
        self.btn_agregar.grid(row=0, column=0, padx=(0,5), pady=2)
        self.btn_vaciar.grid(row=0, column=1, padx=(0,5), pady=2)
        self.btn_descargar.grid(row=0, column=2, padx=(0,5), pady=2)
        header_buttons.grid_columnconfigure((0,1,2), weight=1)
        header_buttons.grid_rowconfigure(0, weight=1)

        # BODY: Tabla principal (centro)
        frame_body = tk.Frame(self.root)
        frame_body.pack(side='top', fill='both', expand=True)
        self.tabla = TablaView(frame_body)

        # FOOTER: Asociar imágenes, radios y vista previa
        frame_footer = tk.Frame(self.root)
        frame_footer.pack(side='bottom', fill='x', pady=10)
        footer_inner = tk.Frame(frame_footer)
        footer_inner.pack(expand=True, fill='both')
        # Centrar horizontal y vertical
        footer_inner.grid_rowconfigure(0, weight=1)
        footer_inner.grid_columnconfigure(0, weight=1)
        footer_buttons = tk.Frame(footer_inner)
        footer_buttons.grid(row=0, column=0, sticky='nsew')
        # Usar grid para centrar los controles
        self.btn_asociar_img = tk.Button(footer_buttons, text='Asociar imágenes a modelos', command=self.abrir_ventana_asociar_imagen)
        self.btn_asociar_img.grid(row=0, column=0, padx=(0,10), pady=2)

        self.tipo_sticker = tk.StringVar(value='etiquetado')
        frame_tipo = tk.Frame(footer_buttons)
        frame_tipo.grid(row=0, column=1, padx=(0,10), pady=2)
        tk.Label(frame_tipo, text='Tipo de sticker:').pack(side='left')
        tk.Radiobutton(frame_tipo, text='Etiquetado (interior)', variable=self.tipo_sticker, value='etiquetado').pack(side='left')
        tk.Radiobutton(frame_tipo, text='Caja', variable=self.tipo_sticker, value='caja').pack(side='left')

        self.btn_previsualizar = tk.Button(footer_buttons, text='Vista previa e imprimir', command=self.vista_previa_pdf)
        self.btn_previsualizar.grid(row=0, column=2, padx=(0,10), pady=2)
        footer_buttons.grid_columnconfigure((0,1,2), weight=1)
        footer_buttons.grid_rowconfigure(0, weight=1)

    def descargar_excel(self):
        import datetime
        if self.data is None or self.data.empty:
            messagebox.showwarning('Advertencia', 'No hay datos para exportar.')
            return
        nombre_sugerido = f"datos_stickers_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = filedialog.asksaveasfilename(
            defaultextension='.xlsx',
            filetypes=[('Archivos Excel', '*.xlsx')],
            title='Guardar datos como Excel',
            initialfile=nombre_sugerido
        )
        if not file_path:
            return
        try:
            self.data.to_excel(file_path, index=False)
            messagebox.showinfo('Éxito', f'Datos exportados correctamente a:\n{file_path}')
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo exportar el archivo Excel.\n{e}')

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
