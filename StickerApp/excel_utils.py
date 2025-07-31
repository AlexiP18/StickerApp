import pandas as pd

def cargar_excel(file_path):
    df = pd.read_excel(file_path, engine='openpyxl')
    df.columns = [str(col).strip() for col in df.columns]
    return df
