import pandas as pd

def cargar_excel(file_path):
    df = pd.read_excel(file_path, engine='openpyxl')
    df.columns = [str(col).strip() for col in df.columns]
    # Rellenar NaN con ceros
    df.fillna(0, inplace=True)
    # Convertir todas las columnas numéricas a enteros si no hay decimales
    for col in df.select_dtypes(include=['float', 'int']).columns:
        # Solo convertir si todos los valores son enteros
        if (df[col] % 1 == 0).all():
            df[col] = df[col].astype(int)
    return df
