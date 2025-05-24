# components/layout.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html
from .tables.table1 import criar_tabela_estoque # <--- IMPORTAÇÃO ATUALIZADA

def criar_layout_principal(df_completo, nome_arquivo, num_linhas_para_exibir=1000, page_size_tabela=1000):
    """
    Cria o layout principal do dashboard.
    df_completo: O DataFrame completo carregado.
    num_linhas_para_exibir: Número de linhas do df_completo a serem passadas para a tabela.
    page_size_tabela: O page_size a ser usado na DataTable.
    """
    titulo_app = dbc.Row(
        dbc.Col(html.H1("Dashboard de Controle de Estoque - Bebidas", className="text-center my-4"), width=12)
    )

    info_arquivo_componente = dbc.Row(
        dbc.Col(html.P(f"Exibindo dados do arquivo: {nome_arquivo}"), width=12)
    )

    total_itens_componente = html.Div() 
    if not df_completo.empty:
        total_itens_componente = dbc.Row(
            dbc.Col(html.P(f"Total de itens no DataFrame completo: {len(df_completo)} (mostrando os primeiros {num_linhas_para_exibir} na tabela)"), width=12)
        )
    
    if not df_completo.empty:
        df_para_tabela_dash = df_completo.head(num_linhas_para_exibir)
    else:
        df_para_tabela_dash = pd.DataFrame()

    tabela_estoque_componente = criar_tabela_estoque(df_para_tabela_dash, page_size=page_size_tabela)

    layout = dbc.Container([
        titulo_app,
        info_arquivo_componente,
        total_itens_componente,
        dbc.Row(
            dbc.Col(tabela_estoque_componente, width=12)
        )
    ], fluid=True)
    
    return layout