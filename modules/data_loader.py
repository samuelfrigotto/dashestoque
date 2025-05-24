# modules/data_loader.py
import pandas as pd

# Definindo os prefixos como constantes para facilitar a manutenção
PREFIXO_CATEGORIA = "* Total Categoria :"
PREFIXO_GRUPO = "* Total GRUPO :"

def _limpar_valor_estoque(serie_estoque):
    """Converte uma série de strings de estoque para numérico, tratando separadores."""
    if not pd.api.types.is_string_dtype(serie_estoque):
        serie_estoque = serie_estoque.astype(str)
    
    # Remove separador de milhar (ponto) e substitui vírgula decimal por ponto
    # Ex: "1.234,50" -> "1234,50" -> "1234.50"
    # Ex: "1.000" -> "1000" (se for inteiro)
    # Ex: "123,45" -> "123.45"
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
            usecols=[0, 1, 2, 7], # Colunas A, B, C, H
            header=None,
            low_memory=False,
            dtype=str  # Ler todas as colunas selecionadas como string inicialmente
        )
        df.columns = ['Código', 'Un', 'Produto', 'Estoque']

        # Filtrar produtos com código válido
        df.dropna(subset=['Código'], inplace=True) # Remove linhas onde o 'Código' original era NaN
        df['Código'] = df['Código'].str.strip()
        df = df[df['Código'] != ''] # Remove linhas onde 'Código' é string vazia após strip

        # Remover linhas de total de categoria e grupo explicitamente
        # Usar na=False para tratar possíveis NaNs na coluna Produto após strip como não começando com o prefixo
        df['Produto_strip'] = df['Produto'].str.strip()
        df = df[~df['Produto_strip'].str.startswith(PREFIXO_CATEGORIA, na=False)]
        df = df[~df['Produto_strip'].str.startswith(PREFIXO_GRUPO, na=False)]
        df.drop(columns=['Produto_strip'], inplace=True)
        
        # Converter 'Estoque' para numérico
        df['Estoque'] = _limpar_valor_estoque(df['Estoque'])
        # Opcional: df.dropna(subset=['Estoque'], inplace=True) # Remover produtos com estoque inválido/NaN

        if df.empty:
            print(f"Nenhum produto encontrado após a filtragem no arquivo: {caminho_arquivo}")
        else:
            print(f"Produtos carregados (apenas produtos): {len(df)} do arquivo: {caminho_arquivo}")
        return df

    except FileNotFoundError:
        print(f"Erro: O arquivo {caminho_arquivo} não foi encontrado.")
        return pd.DataFrame(columns=['Código', 'Un', 'Produto', 'Estoque']) # Retorna DataFrame vazio com colunas esperadas
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
            usecols=[0, 1, 2, 7], # Colunas A, B, C, H
            header=None,
            low_memory=False,
            dtype=str # Ler tudo como string para manipulação inicial
        )
        df_full.columns = ['Código', 'Un', 'Produto_Original', 'Estoque_Original']

        # Inicializar colunas para Categoria e Grupo extraídos
        df_full['CategoriaExtraida'] = pd.NA # Usar pd.NA para consistência
        df_full['GrupoExtraido'] = pd.NA

        for index, row in df_full.iterrows():
            produto_original_strip = row['Produto_Original'].strip() if pd.notna(row['Produto_Original']) else ''
            
            if produto_original_strip.startswith(PREFIXO_CATEGORIA):
                nome_categoria = produto_original_strip[len(PREFIXO_CATEGORIA):].strip()
                df_full.loc[index, 'CategoriaExtraida'] = nome_categoria
            
            if produto_original_strip.startswith(PREFIXO_GRUPO):
                nome_grupo = produto_original_strip[len(PREFIXO_GRUPO):].strip()
                df_full.loc[index, 'GrupoExtraido'] = nome_grupo
        
        # Propagar os valores de categoria e grupo para as linhas acima (produtos)
        df_full['Categoria'] = df_full['CategoriaExtraida'].bfill()
        df_full['Grupo'] = df_full['GrupoExtraido'].bfill()

        # Filtrar para manter apenas as linhas de produtos reais
        df_produtos = df_full.copy()

        # Condição 1: Código deve ser válido (não NaN, não vazio)
        df_produtos.dropna(subset=['Código'], inplace=True)
        df_produtos['Código'] = df_produtos['Código'].str.strip()
        df_produtos = df_produtos[df_produtos['Código'] != '']

        # Condição 2: Não deve ser uma linha de total (verificando Produto_Original)
        # Usar na=False para tratar possíveis NaNs na coluna Produto_Original após strip como não começando com o prefixo
        df_produtos['Produto_Original_strip'] = df_produtos['Produto_Original'].str.strip()
        df_produtos = df_produtos[~df_produtos['Produto_Original_strip'].str.startswith(PREFIXO_CATEGORIA, na=False)]
        df_produtos = df_produtos[~df_produtos['Produto_Original_strip'].str.startswith(PREFIXO_GRUPO, na=False)]
        
        # Selecionar e renomear colunas finais
        df_produtos = df_produtos[['Código', 'Un', 'Produto_Original', 'Estoque_Original', 'Categoria', 'Grupo']].copy() # Usar .copy() para evitar SettingWithCopyWarning
        df_produtos.rename(columns={'Produto_Original': 'Produto', 'Estoque_Original': 'Estoque'}, inplace=True)

        # Converter 'Estoque' para numérico
        df_produtos['Estoque'] = _limpar_valor_estoque(df_produtos['Estoque'])
        # Opcional: df_produtos.dropna(subset=['Estoque'], inplace=True)

        if df_produtos.empty:
            print(f"Nenhum produto encontrado após atribuição de hierarquia e filtragem no arquivo: {caminho_arquivo}")
        else:
            print(f"Produtos com hierarquia carregados: {len(df_produtos)} do arquivo: {caminho_arquivo}")
        
        return df_produtos

    except FileNotFoundError:
        print(f"Erro: O arquivo {caminho_arquivo} não foi encontrado.")
        return pd.DataFrame() # Retornar DataFrame vazio genérico
    except Exception as e:
        print(f"Erro ao carregar (com hierarquia) os dados de estoque: {e}")
        return pd.DataFrame(columns=['Código', 'Un', 'Produto', 'Estoque', 'Categoria', 'Grupo'])