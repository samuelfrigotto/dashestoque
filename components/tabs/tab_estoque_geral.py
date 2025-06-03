# components/tabs/tab_estoque_geral.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc
from ..tables.table1 import criar_tabela_estoque # Ajuste o caminho se necessário

def criar_conteudo_aba_estoque_geral(df_completo, page_size_tabela=20):
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

    # Conteúdo do painel esquerdo (filtros e resumo) - permanece o mesmo
    painel_esquerdo_conteudo = html.Div([
        html.H5("Filtros", className="mb-3"),
        html.Div([dbc.Label("Grupo:", className="fw-bold"), dcc.Dropdown(id='dropdown-grupo-filtro', options=opcoes_grupo, value=None, multi=False, placeholder="Todos os Grupos")], className="mb-3"),
        html.Div([dbc.Label("Categoria:", className="fw-bold"), dcc.Dropdown(id='dropdown-categoria-filtro', options=opcoes_categoria, value=None, multi=False, placeholder="Todas as Categorias")], className="mb-3"),
        html.Div([dbc.Label("Nome do Produto:", className="fw-bold"), dcc.Input(id='input-nome-produto-filtro', type='text', placeholder='Buscar por nome...', debounce=True, className="form-control")], className="mb-3"),
        dbc.Button("Resetar Todos os Filtros", id="btn-resetar-filtros", color="secondary", className="w-100 mb-4"),
        html.Hr(),
        html.H5("Resumo do Estoque", className="mb-3 mt-4"),
        dbc.Card([dbc.CardHeader("Total SKUs"), dbc.CardBody(html.H5(f"{total_skus_inicial:,}", id="card-total-skus", className="text-center"))], className="shadow-sm mb-3"),
        dbc.Card([dbc.CardHeader("Qtde. Total Estoque"), dbc.CardBody(html.H5(f"{qtd_total_estoque_inicial:,.0f}", id="card-qtd-total-estoque", className="text-center"))], className="shadow-sm mb-3"),
        dbc.Card([dbc.CardHeader("Categorias Ativas"), dbc.CardBody(html.H5(f"{num_categorias_inicial:,}", id="card-num-categorias", className="text-center"))], className="shadow-sm mb-3"),
        dbc.Card([dbc.CardHeader("Grupos Ativos"), dbc.CardBody(html.H5(f"{num_grupos_inicial:,}", id="card-num-grupos", className="text-center"))], className="shadow-sm mb-3"),
    ])

    # Botão para abrir/fechar o Offcanvas de filtros
    # Vamos reutilizar o ID 'btn-toggle-painel-esquerdo' para a callback, mas ajustar o texto.
    # Ou criar um novo botão se preferir manter o antigo para outra finalidade.
    botao_toggle_filtros_offcanvas = dbc.Button(
        "Filtros", id="btn-toggle-painel-esquerdo", n_clicks=0, className="mb-3 me-2", color="primary"
    )

    # Definição do Offcanvas para os filtros
    offcanvas_filtros = dbc.Offcanvas(
        painel_esquerdo_conteudo,
        id="offcanvas-filtros-estoque-geral", # ID único para este offcanvas
        title="Filtros e Resumo",
        is_open=False, # Começa fechado
        placement="start", # 'start' (esquerda), 'end' (direita), 'top', 'bottom'
        backdrop=True, # Permite fechar clicando fora
        scrollable=True, # Adiciona scroll se o conteúdo for maior que a tela
        style={'width': '380px'} # Ajuste a largura conforme necessário
    )

    card_graficos_principais = dbc.Card([
        dbc.CardBody([
            dcc.Graph(id='grafico-estoque-grupo', config={'displayModeBar': False}),
            html.Hr(className="my-3"),
            dcc.Graph(id='grafico-estoque-populares', config={'displayModeBar': False})
        ])
    ], className="shadow-sm h-100")

    nova_coluna_conteudo = dbc.Card([
        dbc.CardHeader("Análises Adicionais"),
        dbc.CardBody([
            html.P("Espaço para insights rápidos ou KPIs."),
            html.Div(id='conteudo-dinamico-nova-coluna')
        ])
    ], className="shadow-sm h-100")

    # ... (definições de outros cards, modais, etc. permanecem as mesmas) ...
    grafico_sec_top_n_card_clicavel = html.Div(
        dbc.Card([dbc.CardBody(dcc.Graph(id='grafico-top-n-produtos', config={'displayModeBar': True}, style={'height': '360px'}))], className="shadow-sm h-100 clickable-card"),
        id="card-clicavel-grafico-donut", style={'cursor': 'pointer'}
    )
    grafico_sec_niveis_card_clicavel = html.Div(
        dbc.Card([dbc.CardBody(dcc.Graph(id='grafico-niveis-estoque', config={'displayModeBar': True}, style={'height': '400px'}))], className="shadow-sm h-100 clickable-card"),
        id="card-clicavel-grafico-niveis", style={'cursor': 'pointer'}
    )
    tabela_estoque_baixo_card = dbc.Card([dbc.CardBody(html.Div(id='container-tabela-alerta-estoque-baixo-geral'))], className="shadow-sm h-100", style={'height': '400px'})
    grafico_cat_estoque_baixo_card = dbc.Card([dbc.CardBody(dcc.Graph(id='grafico-categorias-estoque-baixo-visao-geral', config={'displayModeBar': False}))], className="shadow-sm")
    df_para_tabela_dash = df_completo if not df_completo.empty else pd.DataFrame()
    tabela_estoque_principal_componente = criar_tabela_estoque(df_para_tabela_dash, page_size=page_size_tabela)
    botao_exportar_excel = dbc.Button([html.I(className="bi bi-file-earmark-excel-fill me-2"), "Exportar para Excel"],id="btn-exportar-tabela-geral", color="success", className="mb-3 mt-2",size="sm")
    download_component = dcc.Download(id="download-tabela-geral-excel")
    modal_grafico_donut = dbc.Modal([dbc.ModalHeader(dbc.ModalTitle("Participação dos Top 7 Produtos no Estoque")), dbc.ModalBody(dcc.Graph(id='grafico-donut-modal', style={'height': '65vh'})), dbc.ModalFooter(dbc.Button("Fechar", id="btn-fechar-modal-donut", className="ms-auto", n_clicks=0))], id="modal-grafico-donut-popup", size="xl", is_open=False, centered=True)
    modal_grafico_niveis = dbc.Modal([dbc.ModalHeader(dbc.ModalTitle("Clique na Coluna para ver Detalhes")), dbc.ModalBody([dcc.Graph(id='grafico-niveis-modal', style={'height': '50vh'}), html.Hr(), html.H5("Produtos no Nível Selecionado:", className="mt-3"), html.Div(id='tabela-detalhes-nivel-estoque-modal-container')]), dbc.ModalFooter(dbc.Button("Fechar", id="btn-fechar-modal-niveis", className="ms-auto", n_clicks=0))], id="modal-grafico-niveis-popup", size="xl", is_open=False, centered=True)
    store_dados_filtrados_modais = dcc.Store(id='store-dados-filtrados-para-modais')


    layout_aba = html.Div([
        dbc.Row([ # Linha para o botão de toggle dos filtros
            dbc.Col(botao_toggle_filtros_offcanvas)
        ]),
        dbc.Row([
            dbc.Col([ # Coluna dos Gráficos Principais
                card_graficos_principais
            ],
            id="coluna-conteudo-principal",
            width=12, lg=8, # Largura fixa em lg=8
            className="p-3"
            ),
            dbc.Col([ # Nova Coluna Adicionada
                nova_coluna_conteudo
            ],
            id="coluna-nova-customizada",
            width=12, lg=4, # Largura fixa em lg=4
            className="p-3"
            )
        ], className="g-0"), # g-0 remove gutters entre as colunas principais

        offcanvas_filtros, # Adiciona o componente Offcanvas ao layout da aba

        html.Hr(className="my-4"),
        dbc.Row([
            dbc.Col(grafico_sec_top_n_card_clicavel, width=12, lg=4),
            dbc.Col(grafico_sec_niveis_card_clicavel, width=12, lg=4),
            dbc.Col(tabela_estoque_baixo_card, width=12, lg=4),
        ], className="g-3", align="stretch"),
        html.Hr(className="my-4"),
        dbc.Row([
            dbc.Col(grafico_cat_estoque_baixo_card, width=12, className="mb-4")
        ]),
        dbc.Row([
            dbc.Col(tabela_estoque_principal_componente, width=12)
        ]),
        dbc.Row([
            dbc.Col(botao_exportar_excel, width="auto")
        ], className="mt-3 justify-content-start"),
        download_component,
        modal_grafico_donut,
        modal_grafico_niveis,
        store_dados_filtrados_modais
    ], className="py-3")

    return layout_aba