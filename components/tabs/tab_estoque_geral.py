# components/tabs/tab_estoque_geral.py
import pandas as pd
import dash_bootstrap_components as dbc
from dash import html, dcc
from ..tables.table1 import criar_tabela_estoque 

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

    filtro_grupo_component = html.Div([
        dbc.Label("Grupo:", className="fw-bold"),
        dcc.Dropdown(id='dropdown-grupo-filtro', options=opcoes_grupo, value=None, multi=False, placeholder="Todos os Grupos")
    ], className="mb-3")
    
    filtro_categoria_component = html.Div([
        dbc.Label("Categoria:", className="fw-bold"),
        dcc.Dropdown(id='dropdown-categoria-filtro', options=opcoes_categoria, value=None, multi=False, placeholder="Todas as Categorias")
    ], className="mb-3")

    filtro_nome_produto_component = html.Div([
        dbc.Label("Nome do Produto:", className="fw-bold"),
        dcc.Input(id='input-nome-produto-filtro', type='text', placeholder='Buscar por nome...', debounce=True, className="form-control")
    ], className="mb-3")

    botao_resetar_component = dbc.Button("Resetar Todos os Filtros", id="btn-resetar-filtros", color="secondary", className="w-100 mb-4")

    card_total_skus = dbc.Card([dbc.CardHeader("Total SKUs"), dbc.CardBody(html.H5(f"{total_skus_inicial:,}", id="card-total-skus", className="text-center"))], className="shadow-sm mb-3")
    card_qtd_total_estoque = dbc.Card([dbc.CardHeader("Qtde. Total Estoque"), dbc.CardBody(html.H5(f"{qtd_total_estoque_inicial:,.0f}", id="card-qtd-total-estoque", className="text-center"))], className="shadow-sm mb-3")
    card_num_categorias = dbc.Card([dbc.CardHeader("Categorias Ativas"), dbc.CardBody(html.H5(f"{num_categorias_inicial:,}", id="card-num-categorias", className="text-center"))], className="shadow-sm mb-3")
    card_num_grupos = dbc.Card([dbc.CardHeader("Grupos Ativos"), dbc.CardBody(html.H5(f"{num_grupos_inicial:,}", id="card-num-grupos", className="text-center"))], className="shadow-sm mb-3")

    # Card que agora contém o gráfico de Volume por Grupo e o gráfico de Estoque dos Populares
    card_graficos_principais = dbc.Card([
        dbc.CardBody([
            # Título para o primeiro gráfico (Volume de Estoque por Grupo)
            # O título interno do gráfico Plotly também existe
            html.H5("Volume de Estoque por Grupo", className="card-title text-center mb-2"),
            dcc.Graph(id='grafico-estoque-grupo', config={'displayModeBar': False}),
            html.Hr(className="my-3"),
            # Título para o segundo gráfico (Estoque dos Produtos Mais Populares)
            # O título interno do gráfico Plotly também existe
            html.H5("Estoque dos Produtos Mais Populares", className="card-title text-center mb-2"),
            dcc.Graph(id='grafico-estoque-populares', config={'displayModeBar': False}) # Movido para cá
        ])
    ], className="shadow-sm h-100") # h-100 para tentar preencher altura

    # Cards para os gráficos secundários restantes
    grafico_sec_top_n_card = dbc.Card([
        dbc.CardHeader("Top 7 Produtos com Maior Estoque"), 
        dbc.CardBody(dcc.Graph(id='grafico-top-n-produtos', config={'displayModeBar': False}))
    ], className="shadow-sm h-100")

    grafico_sec_niveis_card = dbc.Card([
        dbc.CardHeader("Produtos por Nível de Estoque"), 
        dbc.CardBody(dcc.Graph(id='grafico-niveis-estoque', config={'displayModeBar': False}))
    ], className="shadow-sm h-100")

    # Placeholder para a tabela de estoque baixo, agora na linha dos gráficos secundários
    # Envolvido em um Card para consistência visual. O título virá do callback.
    tabela_estoque_baixo_card = dbc.Card([
        # O CardHeader será o título da tabela, definido no callback via criar_tabela_produtos_criticos
        dbc.CardBody(html.Div(id='container-tabela-alerta-estoque-baixo-geral')) 
    ], className="shadow-sm h-100")


    df_para_tabela_dash = df_completo if not df_completo.empty else pd.DataFrame()
    tabela_estoque_principal_componente = criar_tabela_estoque(df_para_tabela_dash, page_size=page_size_tabela)

    botao_exportar_excel = dbc.Button(
        [html.I(className="bi bi-file-earmark-excel-fill me-2"), "Exportar para Excel"], # Adiciona ícone (requer Bootstrap Icons)
        id="btn-exportar-tabela-geral", 
        color="success", 
        className="mb-3 mt-2", # Margem para separá-lo da tabela
        size="sm" # Botão um pouco menor
    )
    
    # Componente Download (invisível, usado pelo callback de exportação)
    download_component = dcc.Download(id="download-tabela-geral-excel")


    layout_aba = html.Div([
        dbc.Row([ 
            dbc.Col([ 
                html.H5("Filtros", className="mb-3"),
                filtro_grupo_component,
                filtro_categoria_component,
                filtro_nome_produto_component,
                botao_resetar_component,
                html.Hr(),
                html.H5("Resumo do Estoque", className="mb-3 mt-4"),
                card_total_skus,
                card_qtd_total_estoque,
                card_num_categorias,
                card_num_grupos,
            ], width=12, lg=3, className="p-3 bg-light border-end"),
            
            dbc.Col([ 
                card_graficos_principais 
            ], width=12, lg=9, className="p-3")
        ], className="g-0"),

        html.Hr(className="my-4"),

        dbc.Row([ 
            dbc.Col(grafico_sec_top_n_card, width=12, lg=4, className="mb-3"),
            dbc.Col(grafico_sec_niveis_card, width=12, lg=4, className="mb-3"),
            dbc.Col(tabela_estoque_baixo_card, width=12, lg=4, className="mb-3"),
        ], className="g-3", align="stretch"),

        html.Hr(className="my-4"),
        
        dbc.Row([ 
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader("Análise de Categorias com Estoque Baixo"), 
                    dbc.CardBody(dcc.Graph(id='grafico-categorias-estoque-baixo-visao-geral', config={'displayModeBar': False}))
                ]), width=12, className="mb-4 shadow-sm"
            )
        ]),
        dbc.Row([
            dbc.Col(tabela_estoque_principal_componente, width=12)
        ]),
        dbc.Row([ 
            dbc.Col(botao_exportar_excel, width="auto") 
        ], className="mt-3 justify-content-start"),
        
        download_component
        
    ], className="py-3")
    
    return layout_aba