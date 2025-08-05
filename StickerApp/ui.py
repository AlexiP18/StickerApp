
import tkinter as tk
from tkinter import filedialog, messagebox
from excel_utils import cargar_excel
from pdf_templates import generar_pdf_caja, generar_pdf_etiquetado
from image_utils import asociar_imagen
from tabla_view import TablaView
from vista_previa import mostrar_vista_previa_pdf

class StickerApp:
    def abrir_gestor_logos(self):
        from logos_manager import LogosManagerWindow
        import os
        logos_dir = os.path.join(os.path.dirname(__file__), 'assets', 'logos')
        if not os.path.exists(logos_dir):
            os.makedirs(logos_dir)
        LogosManagerWindow(self.root, logos_dir)
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
        # Icono de ventana principal
        try:
            import os
            icon_path = os.path.join(os.path.dirname(__file__), 'favicon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception:
            pass
        # Centrar ventana principal
        try:
            from definir_colores_window import centrar_ventana
            centrar_ventana(self.root)
        except Exception:
            # Fallback si no existe la función
            self.root.update_idletasks()
            w = self.root.winfo_width()
            h = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (w // 2)
            y = (self.root.winfo_screenheight() // 2) - (h // 2)
            self.root.geometry(f'+{x}+{y}')
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
        # Cargar iconos
        import os
        from PIL import Image, ImageTk
        icon_dir = os.path.join(os.path.dirname(__file__), 'assets', 'icons')
        def load_icon(filename, size=(22,22)):
            path = os.path.join(icon_dir, filename)
            if os.path.exists(path):
                img = Image.open(path)
                img = img.resize(size, Image.LANCZOS)
                return ImageTk.PhotoImage(img)
            return None
        self._icon_refs = {}
        icon_excel = load_icon('excel.png')
        icon_vaciar = load_icon('vaciar.png')
        icon_descargar = load_icon('descargar.png')
        icon_cadena = load_icon('cadena.png')
        icon_paleta = load_icon('paleta.png')
        icon_vista = load_icon('vista.png')
        icon_logos = load_icon('logos.png')
        icon_plantilla = load_icon('plantilla.png')
        self._icon_refs.update({
            'excel': icon_excel,
            'vaciar': icon_vaciar,
            'descargar': icon_descargar,
            'cadena': icon_cadena,
            'paleta': icon_paleta,
            'vista': icon_vista,
            'logos': icon_logos,
            'plantilla': icon_plantilla
        })

        # Función para descargar plantilla
        def descargar_plantilla_excel():
            import shutil
            import pandas as pd
            from tkinter import filedialog, messagebox
            from tabla_view import TablaView
            plantilla_path = os.path.join(os.path.dirname(__file__), 'excel_samples', 'plantilla_stickers.xlsx')
            # Usar las columnas por defecto de TablaView, quitando 'TOTAL' (que es calculada)
            columnas = [col for col in TablaView.__init__.__globals__['TablaView'].default_columns if col != 'TOTAL'] if hasattr(TablaView, 'default_columns') else [
                'N° ORDEN', 'CLIENTE', 'CÓDIGO', 'COLOR', 'MARCA', 'CAPELLADA', 'FORRO', 'SUELA'] + [str(n) for n in range(21, 43)]
            if not os.path.exists(plantilla_path):
                # Crear plantilla si no existe
                os.makedirs(os.path.dirname(plantilla_path), exist_ok=True)
                df = pd.DataFrame(columns=columnas)
                df.to_excel(plantilla_path, index=False)
            file_path = filedialog.asksaveasfilename(
                defaultextension='.xlsx',
                filetypes=[('Archivos Excel', '*.xlsx')],
                title='Guardar plantilla Excel',
                initialfile='plantilla_stickers.xlsx'
            )
            if file_path:
                try:
                    shutil.copyfile(plantilla_path, file_path)
                    messagebox.showinfo('Éxito', f'Plantilla guardada en:\n{file_path}')
                except Exception as e:
                    messagebox.showerror('Error', f'No se pudo guardar la plantilla.\n{e}')

        # Usar grid para centrar los botones con iconos
        self.btn_agregar = tk.Button(header_buttons, text='Agregar Excel', image=icon_excel, compound='left', command=self.agregar_excel, padx=8)
        self.btn_vaciar = tk.Button(header_buttons, text='Vaciar tabla', image=icon_vaciar, compound='left', command=self.vaciar_tabla, padx=8)
        self.btn_descargar = tk.Button(header_buttons, text='Descargar Excel', image=icon_descargar, compound='left', command=self.descargar_excel, padx=8)
        self.btn_plantilla = tk.Button(header_buttons, text='Descargar plantilla', image=icon_plantilla, compound='left', command=descargar_plantilla_excel, padx=8)
        self.btn_agregar.grid(row=0, column=0, padx=(0,5), pady=2)
        self.btn_vaciar.grid(row=0, column=1, padx=(0,5), pady=2)
        self.btn_descargar.grid(row=0, column=2, padx=(0,5), pady=2)
        self.btn_plantilla.grid(row=0, column=3, padx=(0,5), pady=2)
        header_buttons.grid_columnconfigure((0,1,2,3), weight=1)
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
        # Usar grid para centrar los controles con iconos
        self.btn_asociar_img = tk.Button(footer_buttons, text='Imagenes-Modelos', image=icon_cadena, compound='left', command=self.abrir_ventana_asociar_imagen, padx=8)
        self.btn_asociar_img.grid(row=0, column=0, padx=(0,10), pady=2)

        # Botón para abrir la ventana de gestión de logos
        self.btn_logos = tk.Button(footer_buttons, text='Gestionar LOGOS', image=icon_logos, compound='left', padx=8, command=self.abrir_gestor_logos)
        self.btn_logos.grid(row=0, column=1, padx=(0,10), pady=2)

        self.tipo_sticker = tk.StringVar(value='etiquetado')
        frame_tipo = tk.Frame(footer_buttons)
        frame_tipo.grid(row=0, column=2, padx=(0,10), pady=2)
        tk.Label(frame_tipo, text='Tipo de sticker:').pack(side='left')
        tk.Radiobutton(frame_tipo, text='Etiquetado (interior)', variable=self.tipo_sticker, value='etiquetado').pack(side='left')
        tk.Radiobutton(frame_tipo, text='Caja', variable=self.tipo_sticker, value='caja').pack(side='left')

        self.btn_colores = tk.Button(footer_buttons, text='Paleta de colores', image=icon_paleta, compound='left', command=self.abrir_paleta_colores, padx=8)
        self.btn_colores.grid(row=0, column=3, padx=(0,10), pady=2)
        self.btn_previsualizar = tk.Button(footer_buttons, text='Vista previa', image=icon_vista, compound='left', command=self.vista_previa_pdf, padx=8)
        self.btn_previsualizar.grid(row=0, column=4, padx=(0,10), pady=2)
        footer_buttons.grid_columnconfigure((0,1,2,3,4), weight=1)
        footer_buttons.grid_rowconfigure(0, weight=1)

    def abrir_paleta_colores(self):
        import os
        import json
        import tkinter as tk
        from definir_colores_window import DefinirColoresWindow
        RUTA_PALETA = os.path.join(os.path.dirname(__file__), 'colores.json')
        if not os.path.exists(RUTA_PALETA):
            paleta = {}
        else:
            with open(RUTA_PALETA, 'r', encoding='utf-8') as f:
                paleta = json.load(f)
        colores_existentes = list(paleta.keys())
        def guardar_nueva_paleta(nueva_paleta):
            with open(RUTA_PALETA, 'w', encoding='utf-8') as f:
                json.dump(nueva_paleta, f, indent=2, ensure_ascii=False)
        root = self.root
        def on_guardar(res):
            guardar_nueva_paleta(res)
        win = DefinirColoresWindow(root, colores_existentes, on_guardar)
        # Prellenar los previews con los colores actuales
        for color in colores_existentes:
            hexcol = paleta.get(color)
            if hexcol:
                win.entries[color]['hex'] = hexcol
                win.entries[color]['preview'].config(bg=hexcol)
        win.verificar_completos()
        # Ya no es necesario centrar ni hacer modal aquí, lo hace DefinirColoresWindow

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
        asociar_imagen(self.data, self.root)
