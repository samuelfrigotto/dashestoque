# components/tabs/tab_estoque_geral.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc
# Ajuste o caminho da importação para subir um nível e depois entrar em 'tables'
from ..tables.table1 import criar_tabela_estoque 

def criar_conteudo_aba_estoque_geral(df_completo, page_size_tabela=20):
    """
    Cria o conteúdo para a aba de visão geral do estoque (cards, filtros, tabela).
    """
    if not df_completo.empty:
        total_skus_inicial = df_completo['Código'].nunique()
        qtd_total_estoque_inicial = pd.to_numeric(df_completo['Estoque'], errors='coerce').fillna(0).sum()
        num_categorias_inicial = df_completo['Categoria'].nunique()
        num_grupos_inicial = df_completo['Grupo'].nunique()
        
        opcoes_categoria = [{'label': str(cat), 'value': str(cat)} for cat in sorted(df_completo['Categoria'].dropna().unique())]
        opcoes_grupo = [{'label': str(grp), 'value': str(grp)} for grp in sorted(df_completo['Grupo'].dropna().unique())]
    else:
        total_skus_inicial = 0
        qtd_total_estoque_inicial = 0
        num_categorias_inicial = 0
        num_grupos_inicial = 0
        opcoes_categoria = []
        opcoes_grupo = []

    cards_estatisticas = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Total de Produtos (SKUs)"),
            dbc.CardBody([html.H4(f"{total_skus_inicial:,}", className="card-title", id="card-total-skus")])
        ]), width=6, lg=3, className="mb-2"),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Quantidade Total em Estoque"),
            dbc.CardBody([html.H4(f"{qtd_total_estoque_inicial:,.0f}", className="card-title", id="card-qtd-total-estoque")])
        ]), width=6, lg=3, className="mb-2"),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Categorias (Visão Atual)"),
            dbc.CardBody([html.H4(f"{num_categorias_inicial:,}", className="card-title", id="card-num-categorias")])
        ]), width=6, lg=3, className="mb-2"),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Grupos (Visão Atual)"),
            dbc.CardBody([html.H4(f"{num_grupos_inicial:,}", className="card-title", id="card-num-grupos")])
        ]), width=6, lg=3, className="mb-2"),
    ], className="mb-4")

    filtros_componente = dbc.Row([
        dbc.Col([
            html.Label("Filtrar por Grupo:"),
            dcc.Dropdown(id='dropdown-grupo-filtro', options=opcoes_grupo, value=None, multi=False, placeholder="Selecione um Grupo")
        ], width=12, md=5, className="mb-2"),
        dbc.Col([
            html.Label("Filtrar por Categoria:"),
            dcc.Dropdown(id='dropdown-categoria-filtro', options=opcoes_categoria, value=None, multi=False, placeholder="Selecione uma Categoria")
        ], width=12, md=5, className="mb-2"),
        dbc.Col([
            html.Label("Limpar Filtros", style={'visibility': 'hidden'}), 
            dbc.Button("Resetar Filtros", id="btn-resetar-filtros", color="secondary", className="w-100")
        ], width=12, md=2, className="d-flex align-items-end mb-2")
    ], className="mb-4 align-items-center")
    
    df_para_tabela_dash = df_completo if not df_completo.empty else pd.DataFrame()
    # O ID 'tabela-estoque' é definido aqui, dentro da função criar_tabela_estoque
    tabela_estoque_componente = criar_tabela_estoque(df_para_tabela_dash, page_size=page_size_tabela) 

    return html.Div([
        html.Hr(),
        cards_estatisticas,
        html.Hr(),
        filtros_componente,
        dbc.Row(dbc.Col(tabela_estoque_componente, width=12))
    ])