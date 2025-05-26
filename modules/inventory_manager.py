# modules/inventory_manager.py
import pandas as pd

def identificar_produtos_em_falta(df_estoque, limite_falta=0):
    """
    Identifica produtos que estão em falta com base em um limite.
    Por padrão, considera produtos com estoque <= 0.
    """
    if df_estoque is None or df_estoque.empty or 'Estoque' not in df_estoque.columns:
        return pd.DataFrame(columns=df_estoque.columns if df_estoque is not None else [])

    df_estoque_copia = df_estoque.copy()
    df_estoque_copia['Estoque'] = pd.to_numeric(df_estoque_copia['Estoque'], errors='coerce')
    
    df_em_falta = df_estoque_copia[df_estoque_copia['Estoque'] <= limite_falta].copy()
    return df_em_falta

def identificar_produtos_estoque_baixo(df_estoque, limite_estoque_baixo):
    """
    Identifica produtos com estoque baixo (Estoque <= limite_estoque_baixo).
    Não inclui produtos com estoque NaN após conversão.

    Args:
        df_estoque (pd.DataFrame): DataFrame contendo os dados de estoque.
                                   Deve incluir uma coluna 'Estoque'.
        limite_estoque_baixo (int/float): O limite para considerar estoque como baixo.

    Returns:
        pd.DataFrame: DataFrame contendo apenas os produtos com estoque baixo.
    """
    if df_estoque is None or df_estoque.empty or 'Estoque' not in df_estoque.columns:
        return pd.DataFrame(columns=df_estoque.columns if df_estoque is not None else [])

    try:
        limite = float(limite_estoque_baixo)
    except (ValueError, TypeError):
        print(f"Limite de estoque baixo inválido: {limite_estoque_baixo}. Nenhum produto será classificado como baixo.")
        return pd.DataFrame(columns=df_estoque.columns)


    df_copia = df_estoque.copy()
    df_copia['EstoqueNum'] = pd.to_numeric(df_copia['Estoque'], errors='coerce')
    
    # Filtrar produtos com estoque baixo, excluindo NaNs resultantes da conversão de 'EstoqueNum'
    df_baixo = df_copia[
        (df_copia['EstoqueNum'].notna()) & 
        (df_copia['EstoqueNum'] <= limite)
    ].copy()
    
    return df_baixo.drop(columns=['EstoqueNum'], errors='ignore') # Remove coluna auxiliar se existir