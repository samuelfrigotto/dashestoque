import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc
from ..tables.table1 import criar_tabela_estoque # Mantenha o seu import correto

def criar_conteudo_aba_estoque_geral(df_completo, page_size_tabela=20):
    '''
    Cria o layout da aba de Estoque Geral, otimizado para reduzir espaços em branco.
    As classes de espaçamento do Bootstrap (como p-*, m-*, g-*) foram ajustadas
    para criar um layout mais compacto.
    '''
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

    painel_esquerdo_conteudo = html.Div([
        html.H5("Filtros", className="mb-3"),
        html.Div([dbc.Label("Grupo:", className="fw-bold"), dcc.Dropdown(id='dropdown-grupo-filtro', options=opcoes_grupo, value=None, multi=False, placeholder="Todos os Grupos")], className="mb-3"),
        html.Div([dbc.Label("Categoria:", className="fw-bold"), dcc.Dropdown(id='dropdown-categoria-filtro', options=opcoes_categoria, value=None, multi=False, placeholder="Todas as Categorias")], className="mb-3"),
        html.Div([dbc.Label("Nome do Produto:", className="fw-bold"), dcc.Input(id='input-nome-produto-filtro', type='text', placeholder='Buscar por nome...', debounce=True, className="form-control")], className="mb-3"),
        dbc.Button("Resetar Todos os Filtros", id="btn-resetar-filtros", color="warning", outline=True, className="w-100 mb-4"),
    ])

    botao_toggle_filtros_offcanvas = dbc.Button(
        "Filtros", id="btn-toggle-painel-esquerdo", n_clicks=0, className="mb-2 me-2", color="warning", size="sm"
    )

    offcanvas_filtros = dbc.Offcanvas(
        painel_esquerdo_conteudo,
        id="offcanvas-filtros-estoque-geral",
        title="Filtros e Resumo",
        is_open=False,
        placement="start",
        backdrop=False,
        scrollable=True,
        style={'width': '350px'},
        className="custom-offcanvas-filtros"
    )

    # --- CARDs de Resumo com margem inferior reduzida (mb-2) ---
    card_total_skus_comp = dbc.Card([dbc.CardHeader("Total de Produtos Diferentes"), dbc.CardBody(html.H5(f"{total_skus_inicial:,}", id="card-total-skus", className="text-center"))], className="shadow-sm mb-2")
    card_qtd_total_estoque_comp = dbc.Card([dbc.CardHeader("Qtde. Total Estoque"), dbc.CardBody(html.H5(f"{qtd_total_estoque_inicial:,.0f}", id="card-qtd-total-estoque", className="text-center"))], className="shadow-sm mb-2")
    card_num_categorias_comp = dbc.Card([dbc.CardHeader("Categorias Ativas"), dbc.CardBody(html.H5(f"{num_categorias_inicial:,}", id="card-num-categorias", className="text-center"))], className="shadow-sm mb-2")
    card_num_grupos_comp = dbc.Card([dbc.CardHeader("Grupos Ativos"), dbc.CardBody(html.H5(f"{num_grupos_inicial:,}", id="card-num-grupos", className="text-center"))], className="shadow-sm") # Último card sem margem inferior

    bloco_cards_resumo = dbc.Card(dbc.CardBody([
        html.H5("Resumo do Estoque", className="mb-3 text-center fw-bold"),
        card_total_skus_comp,
        card_qtd_total_estoque_comp,
        card_num_categorias_comp,
        card_num_grupos_comp
    ]), className="shadow-sm h-100")

    # --- Gráficos e Tabelas ---
    altura_graficos_padrao = '410px'
    grafico_estoque_grupo_card = dbc.Card(dbc.CardBody(dcc.Graph(id='grafico-estoque-grupo', config={'displayModeBar': False}, style={'height': '530px'})), className="shadow-sm h-100")
    grafico_estoque_populares_card = dbc.Card(dbc.CardBody(dcc.Graph(id='grafico-estoque-populares', config={'displayModeBar': False}, style={'height': altura_graficos_padrao})), className="shadow-sm h-100")
    grafico_colunas_resumo_treemap_card = dbc.Card(dbc.CardBody(dcc.Graph(id='grafico-colunas-resumo-estoque', config={'displayModeBar': False})), className="shadow-sm h-100")
    grafico_sec_top_n_card_clicavel = html.Div(dbc.Card([dbc.CardBody(dcc.Graph(id='grafico-top-n-produtos', config={'displayModeBar': True}, style={'height': '360px'}))], className="shadow-sm h-100 clickable-card"), id="card-clicavel-grafico-donut", style={'cursor': 'pointer'})
    grafico_sec_niveis_card_clicavel = html.Div(dbc.Card([dbc.CardBody(dcc.Graph(id='grafico-niveis-estoque', config={'displayModeBar': True}, style={'height': '400px'}))], className="shadow-sm h-100 clickable-card"), id="card-clicavel-grafico-niveis", style={'cursor': 'pointer'})
    tabela_estoque_baixo_card = dbc.Card([dbc.CardBody(html.Div(id='container-tabela-alerta-estoque-baixo-geral'))], className="shadow-sm h-100", style={'height': '400px'})
    grafico_cat_estoque_baixo_card = dbc.Card([dbc.CardBody(dcc.Graph(id='grafico-categorias-estoque-baixo-visao-geral', config={'displayModeBar': False}))], className="shadow-sm")

    df_para_tabela_dash = df_completo if not df_completo.empty else pd.DataFrame()
    tabela_estoque_principal_componente = criar_tabela_estoque(df_para_tabela_dash, page_size=page_size_tabela)

    botao_exportar_excel = dbc.Button([html.I(className="bi bi-file-earmark-excel-fill me-2"), "Exportar para Excel"], id="btn-exportar-tabela-geral", color="warning", className="mb-2 mt-2", size="sm")
    download_component = dcc.Download(id="download-tabela-geral-excel")

    # --- Modais (sem alterações no layout) ---
    modal_grafico_donut = dbc.Modal([dbc.ModalHeader(dbc.ModalTitle("Participação dos Top 7 Produtos no Estoque")), dbc.ModalBody(dcc.Graph(id='grafico-donut-modal', style={'height': '65vh'})), dbc.ModalFooter(dbc.Button("Fechar", id="btn-fechar-modal-donut", className="ms-auto", n_clicks=0, color="warning"))], id="modal-grafico-donut-popup", size="xl", is_open=False, centered=True)
    modal_grafico_niveis = dbc.Modal([dbc.ModalHeader(dbc.ModalTitle("Clique na Coluna para ver Detalhes")), dbc.ModalBody([dcc.Graph(id='grafico-niveis-modal', style={'height': '50vh'}), html.Hr(), html.H5("Produtos no Nível Selecionado:", className="mt-3"), html.Div(id='tabela-detalhes-nivel-estoque-modal-container')]), dbc.ModalFooter(dbc.Button("Fechar", id="btn-fechar-modal-niveis", className="ms-auto", n_clicks=0, color="warning"))], id="modal-grafico-niveis-popup", size="xl", is_open=False, centered=True)
    store_dados_filtrados_modais = dcc.Store(id='store-dados-filtrados-para-modais')

    # --- LAYOUT PRINCIPAL com espaçamentos ajustados ---
    layout_aba = html.Div([
        dbc.Row([
            dbc.Col(botao_toggle_filtros_offcanvas)
        ]),

        # --- Linha 1: Gráficos Populares e Treemap ---
        # g-2: Adiciona um pequeno espaçamento (gutter) entre as colunas
        # mb-2: Margem inferior pequena
        dbc.Row([
            dbc.Col(grafico_estoque_grupo_card, width=12, lg=7),
            dbc.Col(grafico_sec_niveis_card_clicavel, width=12, lg=5),
        ], className="g-2 mb-2", align="stretch"),

        offcanvas_filtros,

        html.Hr(className="my-2"), # Margem vertical do Hr reduzida

        # --- Linha 2: Gráficos de Donut, Níveis e Tabela de Estoque Baixo ---
        dbc.Row([
            dbc.Col(grafico_estoque_populares_card, width=12, lg=6),
            dbc.Col(grafico_sec_top_n_card_clicavel, width=12, lg=6),
        ], className="g-2 mb-2", align="stretch"), # g-2 para espaçamento, mb-2 para margem

        html.Hr(className="my-2"),

        # --- Linha 3: Resumo e Gráfico de Grupo ---
        dbc.Row([
            dbc.Col(bloco_cards_resumo, width=12, lg=3),
            dbc.Col(grafico_colunas_resumo_treemap_card, width=12, lg=9),
        ], className="g-2 mb-2", align="stretch"),

        html.Hr(className="my-2"),

        # --- Linha 4: Gráfico de Categorias com Estoque Baixo ---
        dbc.Row([
            dbc.Col(grafico_cat_estoque_baixo_card, width=12, lg=8),
            dbc.Col(tabela_estoque_baixo_card, width=12, lg=4)
        ], className="mb-2"), # Apenas margem inferior

        html.Hr(className="my-2"),

        # --- Linha 5: Tabela Principal ---
        #dbc.Row([
        #    dbc.Col(tabela_estoque_principal_componente, width=12)
        #]),

        # --- Linha 6: Botão de Exportar ---
        #dbc.Row([
        #    dbc.Col(botao_exportar_excel, width="auto")
        #], className="mt-2 justify-content-start"), # mt-2 para uma pequena margem superior

        download_component,
        modal_grafico_donut,
        modal_grafico_niveis,
        store_dados_filtrados_modais

    ], className="p-2") # Padding geral pequeno para não colar nas bordas da tela

    return layout_aba