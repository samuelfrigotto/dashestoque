# main.py
import pandas as pd
import dash
from dash import html, dash_table
import dash_bootstrap_components as dbc

# --- 1. Carregamento e Preparação dos Dados de Estoque ---
def carregar_dados_estoque(caminho_arquivo):
    """
    Carrega e prepara os dados de estoque do arquivo CSV especificado.
    - Pula as primeiras 4 linhas.
    - Usa as colunas A, B, C, H.
    - Renomeia as colunas para 'Código', 'Un', 'Produto', 'Estoque'.
    - Filtra linhas onde 'Código' está presente.
    """
    try:
        # Ler o CSV, pulando as primeiras 4 linhas, usando apenas as colunas especificadas (A=0, B=1, C=2, H=7)
        # e sem linha de cabeçalho, pois vamos nomeá-las.
        df = pd.read_csv(
            caminho_arquivo,
            delimiter=';',
            encoding='latin-1', # Mantendo latin-1, ajuste se necessário para o novo arquivo
            skiprows=4,        # Pula as primeiras 4 linhas
            usecols=[0, 1, 2, 7], # Seleciona colunas A, B, C, H
            header=None,       # Indica que não há linha de cabeçalho nos dados lidos (após skiprows)
            low_memory=False   # Para evitar DtypeWarning, se aplicável
        )

        # Renomear as colunas
        df.columns = ['Código', 'Un', 'Produto', 'Estoque']

        # Filtrar linhas: manter apenas aquelas onde a coluna 'Código' não é vazia/NaN
        # Convertemos para string para o caso de códigos serem numéricos e para facilitar a verificação de não vazio
        df = df[df['Código'].astype(str).notna() & (df['Código'].astype(str).str.strip() != '')]
        
        # Opcional: Converter a coluna 'Estoque' para numérico, se apropriado.
        # Se houver erros na conversão (ex: texto inesperado), eles se tornarão NaN.
        # df['Estoque'] = pd.to_numeric(df['Estoque'], errors='coerce')
        # df.dropna(subset=['Estoque'], inplace=True) # Opcional: remover linhas onde o estoque não pôde ser convertido

        print(f"Arquivo '{caminho_arquivo}' lido e preparado com sucesso.")
        return df
    except FileNotFoundError:
        print(f"Erro: O arquivo {caminho_arquivo} não foi encontrado.")
        return pd.DataFrame()
    except Exception as e:
        print(f"Erro ao carregar ou processar os dados de estoque: {e}")
        return pd.DataFrame()

# ATUALIZE O CAMINHO DO ARQUIVO E A CHAMADA DA FUNÇÃO:
caminho_novo_arquivo_csv = "data/16-05.CSV" # Ou "data/16-05/16-05.CSV" se estiver numa subpasta 16-05
df_estoque = carregar_dados_estoque(caminho_novo_arquivo_csv) # Nome da variável mudado para clareza

# --- 2. Inicialização do Aplicativo Dash ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard de Estoque"

# --- 3. Layout do Dashboard ---
# ATUALIZE AS COLUNAS DA TABELA AQUI:
colunas_tabela = []
if not df_estoque.empty:
    colunas_tabela = [{"name": i, "id": i} for i in df_estoque.columns]

app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(html.H1("Dashboard de Controle de Estoque - Bebidas", className="text-center my-4"), width=12)
    ),
    dbc.Row(
        dbc.Col(html.P(f"Exibindo dados do arquivo: {caminho_novo_arquivo_csv}"), width=12) # Mostra o nome do arquivo
    ),
    dbc.Row(
        dbc.Col(html.P(f"Total de produtos com código listados: {len(df_estoque)}"), width=12) if not df_estoque.empty else html.Div("")
    ),
    dbc.Row(
        dbc.Col(
            (dash_table.DataTable(
                id='tabela-estoque', # ID da tabela
                columns=colunas_tabela, # Colunas atualizadas
                data=df_estoque.head(1000).to_dict('records'), # Mostra as primeiras 20 linhas
                page_size=1000, # Adiciona paginação se quiser mostrar mais, mas manter o head(20) para data
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'left',
                    'minWidth': '100px', 'width': '150px', 'maxWidth': '300px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'padding': '5px'
                },
                style_header={
                    'backgroundColor': 'lightgrey',
                    'fontWeight': 'bold'
                }
            ) if not df_estoque.empty else html.Div("Dados de estoque não carregados ou arquivo vazio. Verifique o console.", className="text-center text-danger")),
            width=12
        )
    )
], fluid=True)


# --- 4. Execução do Servidor ---
if __name__ == '__main__':
    if not df_estoque.empty: # Verifique a variável df_estoque
        print("Dados de estoque carregados com sucesso. Iniciando o servidor Dash...")
        app.run(debug=True, host='127.0.0.1', port=8050)
    else:
        print("Não foi possível iniciar o servidor pois os dados de estoque não foram carregados ou o DataFrame está vazio. Verifique as mensagens acima.")