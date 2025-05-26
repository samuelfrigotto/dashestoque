import pandas as pd

PREFIXO_CATEGORIA = "* Total Categoria :"
PREFIXO_GRUPO = "* Total GRUPO :"

def _limpar_valor_estoque(serie_estoque):
    """Converte uma série de strings de estoque para numérico, tratando separadores."""
    if not pd.api.types.is_string_dtype(serie_estoque):
        serie_estoque = serie_estoque.astype(str)
    
    serie_limpa = serie_estoque.str.replace('.', '', regex=False) 
    serie_limpa = serie_limpa.str.replace(',', '.', regex=False)
    return pd.to_numeric(serie_limpa, errors='coerce')

def carregar_apenas_produtos(caminho_arquivo):
    """
    Carrega e prepara os dados de estoque, retornando apenas linhas de produtos.
    - Pula as primeiras 4 linhas.
    - Usa as colunas A, B, C, H.
    - Renomeia colunas: 'Código', 'Un', 'Produto', 'Estoque'.
    - Filtra para manter apenas produtos com 'Código' válido e remove linhas de total.
    """
    try:
        df = pd.read_csv(
            caminho_arquivo,
            delimiter=';',
            encoding='latin-1',
            skiprows=4,
            usecols=[0, 1, 2, 7],
            header=None,
            low_memory=False,
            dtype=str 
        )
        df.columns = ['Código', 'Un', 'Produto', 'Estoque']


        df.dropna(subset=['Código'], inplace=True) 
        df['Código'] = df['Código'].str.strip()
        df = df[df['Código'] != '']

        df['Produto_strip'] = df['Produto'].str.strip()
        df = df[~df['Produto_strip'].str.startswith(PREFIXO_CATEGORIA, na=False)]
        df = df[~df['Produto_strip'].str.startswith(PREFIXO_GRUPO, na=False)]
        df.drop(columns=['Produto_strip'], inplace=True)
        
        df['Estoque'] = _limpar_valor_estoque(df['Estoque'])

        if df.empty:
            print(f"Nenhum produto encontrado após a filtragem no arquivo: {caminho_arquivo}")
        else:
            print(f"Produtos carregados (apenas produtos): {len(df)} do arquivo: {caminho_arquivo}")
        return df

    except FileNotFoundError:
        print(f"Erro: O arquivo {caminho_arquivo} não foi encontrado.")
        return pd.DataFrame(columns=['Código', 'Un', 'Produto', 'Estoque'])
    except Exception as e:
        print(f"Erro ao carregar (apenas produtos) os dados de estoque: {e}")
        return pd.DataFrame(columns=['Código', 'Un', 'Produto', 'Estoque'])

def carregar_produtos_com_hierarquia(caminho_arquivo):
    """
    Carrega produtos e atribui Categoria e Grupo extraídos das linhas de totais.
    A categoria/grupo é atribuída aos produtos listados ANTES da linha de total correspondente.
    """
    try:
        df_full = pd.read_csv(
            caminho_arquivo,
            delimiter=';',
            encoding='latin-1',
            skiprows=4,
            usecols=[0, 1, 2, 7], 
            header=None,
            low_memory=False,
            dtype=str 
        )
        df_full.columns = ['Código', 'Un', 'Produto_Original', 'Estoque_Original']
        df_full['CategoriaExtraida'] = pd.NA 
        df_full['GrupoExtraido'] = pd.NA

        for index, row in df_full.iterrows():
            produto_original_strip = row['Produto_Original'].strip() if pd.notna(row['Produto_Original']) else ''
            
            if produto_original_strip.startswith(PREFIXO_CATEGORIA):
                nome_categoria = produto_original_strip[len(PREFIXO_CATEGORIA):].strip()
                df_full.loc[index, 'CategoriaExtraida'] = nome_categoria
            
            if produto_original_strip.startswith(PREFIXO_GRUPO):
                nome_grupo = produto_original_strip[len(PREFIXO_GRUPO):].strip()
                df_full.loc[index, 'GrupoExtraido'] = nome_grupo
        
        df_full['Categoria'] = df_full['CategoriaExtraida'].bfill()
        df_full['Grupo'] = df_full['GrupoExtraido'].bfill()
        df_produtos = df_full.copy()
        df_produtos.dropna(subset=['Código'], inplace=True)
        df_produtos['Código'] = df_produtos['Código'].str.strip()
        df_produtos = df_produtos[df_produtos['Código'] != '']

        df_produtos['Produto_Original_strip'] = df_produtos['Produto_Original'].str.strip()
        df_produtos = df_produtos[~df_produtos['Produto_Original_strip'].str.startswith(PREFIXO_CATEGORIA, na=False)]
        df_produtos = df_produtos[~df_produtos['Produto_Original_strip'].str.startswith(PREFIXO_GRUPO, na=False)]

        df_produtos = df_produtos[['Código', 'Un', 'Produto_Original', 'Estoque_Original', 'Categoria', 'Grupo']].copy() # Usar .copy() para evitar SettingWithCopyWarning
        df_produtos.rename(columns={'Produto_Original': 'Produto', 'Estoque_Original': 'Estoque'}, inplace=True)

        df_produtos['Estoque'] = _limpar_valor_estoque(df_produtos['Estoque'])

        if df_produtos.empty:
            print(f"Nenhum produto encontrado após atribuição de hierarquia e filtragem no arquivo: {caminho_arquivo}")
        else:
            print(f"Produtos com hierarquia carregados: {len(df_produtos)} do arquivo: {caminho_arquivo}")
        
        return df_produtos

    except FileNotFoundError:
        print(f"Erro: O arquivo {caminho_arquivo} não foi encontrado.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Erro ao carregar (com hierarquia) os dados de estoque: {e}")
        return pd.DataFrame(columns=['Código', 'Un', 'Produto', 'Estoque', 'Categoria', 'Grupo'])