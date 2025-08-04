import tkinter as tk
from tkinter import ttk

class TablaView:
    def vaciar(self):
        self.tree.delete(*self.tree.get_children())
    def __init__(self, parent):
        # --- Definir columnas por defecto usando el header del CSV proporcionado, pero con números del 21 al 42 ---
        self.default_columns = [
            'N° ORDEN', 'CLIENTE', 'CÓDIGO', 'COLOR', 'MARCA', 'CAPELLADA', 'FORRO', 'SUELA'
        ] + [str(n) for n in range(21, 43)] + ['TOTAL']

        self.frame = tk.Frame(parent)
        self.frame.pack(expand=True, fill='both')

        self.tree = ttk.Treeview(self.frame, columns=self.default_columns, show='headings')

        # Scrollbars
        vsb = ttk.Scrollbar(self.frame, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(self.frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        # Asignar ancho menor y centrado a las columnas numéricas
        numeric_cols = {str(n) for n in range(21, 43)}
        small_width = 40
        normal_width = 80
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview.Heading', font=('Arial', 10, 'bold'), background='#e0e0e0', foreground='#222')

        for col in self.default_columns:
            if col in numeric_cols:
                self.tree.heading(col, text=col, anchor='center')
                self.tree.column(col, width=small_width, anchor='center')
            else:
                self.tree.heading(col, text=col, anchor='center')
                self.tree.column(col, width=normal_width, anchor='center')

    def mostrar_datos(self, df):
        import pandas as pd
        self.tree.delete(*self.tree.get_children())
        all_numeric_cols = [str(n) for n in range(21, 43)]
        numeric_cols = [col for col in all_numeric_cols if col in df.columns]
        small_width = 40
        normal_width = 80
        # Eliminar columna TOTAL si viene en el Excel
        cols = [col for col in df.columns if col != 'TOTAL']
        # Calcular TOTAL sumando solo las columnas numéricas que existan
        df = df.copy()
        if numeric_cols:
            df['TOTAL'] = df[numeric_cols].apply(lambda x: pd.to_numeric(x, errors='coerce').fillna(0).sum(), axis=1)
        else:
            df['TOTAL'] = 0
        # Reemplazar NaN por 0 en columnas numéricas
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(0)
        # Ordenar columnas como en default_columns
        ordered_cols = [col for col in self.default_columns if col in df.columns or col == 'TOTAL']
        self.tree['columns'] = ordered_cols
        self.tree['show'] = 'headings'
        for col in ordered_cols:
            if col in numeric_cols:
                self.tree.heading(col, text=col, anchor='center')
                self.tree.column(col, width=small_width, anchor='center')
            else:
                self.tree.heading(col, text=col, anchor='center')
                self.tree.column(col, width=normal_width, anchor='center')
        # Mostrar filas, formateando los valores numéricos
        for _, row in df[ordered_cols].iterrows():
            vals = []
            for col in ordered_cols:
                val = row[col]
                if col in numeric_cols:
                    # Si el valor es NaN o 0, mostrar vacío; si es entero, mostrar como int
                    if pd.isna(val) or val == 0:
                        vals.append('')
                    elif float(val).is_integer():
                        vals.append(str(int(val)))
                    else:
                        vals.append(str(val))
                elif col == 'TOTAL':
                    # Mostrar TOTAL como int si es entero
                    if pd.isna(val):
                        vals.append('')
                    elif float(val).is_integer():
                        vals.append(str(int(val)))
                    else:
                        vals.append(str(val))
                else:
                    vals.append(val)
            self.tree.insert('', 'end', values=vals)

        # --- Footer de sumas ---
        # Solo si hay filas
        if not df.empty:
            sumas = []
            for col in ordered_cols:
                if col in numeric_cols or col == 'TOTAL':
                    try:
                        suma = df[col].astype(float).sum()
                        suma = int(suma) if suma == int(suma) else round(suma, 2)
                        sumas.append(suma)
                    except Exception:
                        sumas.append('')
                else:
                    sumas.append('')
            # Insertar como última fila, con estilo diferente si se desea
            self.tree.insert('', 'end', values=sumas, tags=('footer',))
            self.tree.tag_configure(
                'footer',
                background='#b6d7a8',  # verde suave
                font=('Arial', 10, 'bold'),
                foreground='#222'
            )

    def get_frame(self):
        return self.frame
    
    def get_tree(self):
        return self.tree
