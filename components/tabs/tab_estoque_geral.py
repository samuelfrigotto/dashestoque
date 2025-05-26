# components/tabs/tab_estoque_geral.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc
from ..tables.table1 import criar_tabela_estoque

def criar_conteudo_aba_estoque_geral(df_completo, page_size_tabela=20):
    """
    Cria o conteúdo para a aba de visão geral do estoque (cards, filtros, gráficos, tabela).
    """
    if not df_completo.empty:
        total_skus_inicial = df_completo['Código'].nunique()
        qtd_total_estoque_inicial = pd.to_numeric(df_completo['Estoque'], errors='coerce').fillna(0).sum()
        num_categorias_inicial = df_completo['Categoria'].nunique()
        num_grupos_inicial = df_completo['Grupo'].nunique()
        opcoes_categoria = [{'label': str(cat), 'value': str(cat)} for cat in sorted(df_completo['Categoria'].dropna().unique())]
        opcoes_grupo = [{'label': str(grp), 'value': str(grp)} for grp in sorted(df_completo['Grupo'].dropna().unique())]
    else:
        total_skus_inicial, qtd_total_estoque_inicial, num_categorias_inicial, num_grupos_inicial = 0, 0, 0, 0
        opcoes_categoria, opcoes_grupo = [], []

    cards_estatisticas = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardHeader("Total de Produtos (SKUs)"),
            dbc.CardBody([html.H4(f"{total_skus_inicial:,}", className="card-title", id="card-total-skus")])
        ], className="shadow-sm h-100"), width=6, lg=3, className="mb-4"), # Adicionado shadow-sm e h-100, mb-4
        dbc.Col(dbc.Card([
            dbc.CardHeader("Quantidade Total em Estoque"),
            dbc.CardBody([html.H4(f"{qtd_total_estoque_inicial:,.0f}", className="card-title", id="card-qtd-total-estoque")])
        ], className="shadow-sm h-100"), width=6, lg=3, className="mb-4"),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Categorias (Visão Atual)"),
            dbc.CardBody([html.H4(f"{num_categorias_inicial:,}", className="card-title", id="card-num-categorias")])
        ], className="shadow-sm h-100"), width=6, lg=3, className="mb-4"),
        dbc.Col(dbc.Card([
            dbc.CardHeader("Grupos (Visão Atual)"),
            dbc.CardBody([html.H4(f"{num_grupos_inicial:,}", className="card-title", id="card-num-grupos")])
        ], className="shadow-sm h-100"), width=6, lg=3, className="mb-4"),
    ], className="mb-3") # Reduzida margem inferior da linha de cards

    filtros_dropdown_componente = dbc.Row([
        dbc.Col([
            dbc.Label("Filtrar por Grupo:", className="fw-bold"), # Adicionado fw-bold
            dcc.Dropdown(id='dropdown-grupo-filtro', options=opcoes_grupo, value=None, multi=False, placeholder="Selecione um Grupo")
        ], width=12, md=6, className="mb-3"), # Aumentado mb
        dbc.Col([
            dbc.Label("Filtrar por Categoria:", className="fw-bold"),
            dcc.Dropdown(id='dropdown-categoria-filtro', options=opcoes_categoria, value=None, multi=False, placeholder="Selecione uma Categoria")
        ], width=12, md=6, className="mb-3")
    ], className="mt-2") # Adicionado mt-2

    filtro_texto_e_reset_componente = dbc.Row([
        dbc.Col([
            dbc.Label("Filtrar por Nome do Produto:", className="fw-bold"),
            dcc.Input(
                id='input-nome-produto-filtro', type='text',
                placeholder='Digite parte do nome...', debounce=True,
                className="form-control"
            )
        ], width=12, md=10, className="mb-3"),
        dbc.Col([
            dbc.Label("Ações:", className="fw-bold", style={'visibility': 'visible'}), # Label visível para alinhar
            dbc.Button("Resetar Todos", id="btn-resetar-filtros", color="secondary", className="w-100")
        ], width=12, md=2, className="d-flex align-items-end mb-3")
    ], className="align-items-center")
    
    area_graficos = dbc.Container([
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Volume de Estoque por Grupo"), # Adicionado CardHeader
                dbc.CardBody(dcc.Graph(id='grafico-estoque-grupo', config={'displayModeBar': False})) # config para remover a barra de modo Plotly
            ]), width=12, className="mb-4 shadow-sm"), # Adicionado shadow-sm e mb-4
        ]),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Top 7 Produtos com Maior Estoque"),
                dbc.CardBody(dcc.Graph(id='grafico-top-n-produtos', config={'displayModeBar': False}))
            ]), md=6, className="mb-4 shadow-sm"),
            dbc.Col(dbc.Card([
                dbc.CardHeader("Produtos por Nível de Estoque"),
                dbc.CardBody(dcc.Graph(id='grafico-niveis-estoque', config={'displayModeBar': False}))
            ]), md=6, className="mb-4 shadow-sm"),
        ])
    ], fluid=True, className="mt-4") # Removido mb-4 daqui, adicionado aos cards individuais
        
    df_para_tabela_dash = df_completo if not df_completo.empty else pd.DataFrame()
    tabela_estoque_componente = criar_tabela_estoque(df_para_tabela_dash, page_size=page_size_tabela) 

    return html.Div([
        # Removido o primeiro Hr(), o espaçamento dos cards já cria separação
        cards_estatisticas,
        # Removido o Hr() aqui também
        filtros_dropdown_componente,
        filtro_texto_e_reset_componente,
        # Removido o Hr() aqui
        area_graficos,
        # Removido o Hr() antes da tabela
        dbc.Row(dbc.Col(tabela_estoque_componente, width=12), className="mt-4") # Adicionado mt-4 para espaço acima da tabela
    ])