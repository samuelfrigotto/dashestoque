from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from modules.config_manager import (
    carregar_definicoes_niveis_estoque, 
    VALORES_PADRAO_NIVEIS,
    carregar_configuracoes_exclusao
)

def criar_conteudo_aba_configuracoes(df_completo_para_opcoes):
    """
    Cria o layout para a aba de Configurações, com seções distintas
    lado a lado para definições de níveis de estoque e exclusão de itens.
    """
    config_niveis_atuais = carregar_definicoes_niveis_estoque()
    valor_inicial_baixo = config_niveis_atuais.get("limite_estoque_baixo")
    valor_inicial_medio = config_niveis_atuais.get("limite_estoque_medio")

    config_exclusao_atuais = carregar_configuracoes_exclusao()
    grupos_excluidos_atuais = config_exclusao_atuais.get("excluir_grupos", [])
    categorias_excluidas_atuais = config_exclusao_atuais.get("excluir_categorias", [])
    produtos_excluidos_atuais_codigos = config_exclusao_atuais.get("excluir_produtos_codigos", [])

    opcoes_grupos_excluir, opcoes_categorias_excluir, opcoes_produtos_excluir = [], [], []
    if df_completo_para_opcoes is not None and not df_completo_para_opcoes.empty:
        opcoes_grupos_excluir = [{'label': str(grp), 'value': str(grp)} for grp in sorted(df_completo_para_opcoes['Grupo'].dropna().unique())]
        opcoes_categorias_excluir = [{'label': str(cat), 'value': str(cat)} for cat in sorted(df_completo_para_opcoes['Categoria'].dropna().unique())]
        produtos_unicos = df_completo_para_opcoes.drop_duplicates(subset=['Código'])
        opcoes_produtos_excluir = sorted([
            {'label': f"{row['Produto']} (Cód: {row['Código']})", 'value': str(row['Código'])} 
            for index, row in produtos_unicos.iterrows() if pd.notna(row['Código']) and str(row['Código']).strip() != ''
        ], key=lambda x: x['label'])

    card_definicoes_niveis = dbc.Card([
        dbc.CardHeader(html.H5("Definições de Níveis de Estoque", className="my-2")),
        dbc.CardBody([
            html.P(
                "Defina os valores para as faixas de Estoque Baixo, Médio e Alto, "
                "usados no gráfico 'Produtos por Nível de Estoque'."
            ),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Estoque Baixo é: Estoque ≤", html_for="input-limite-config-baixo", className="fw-bold"),
                    dcc.Input(
                        id="input-limite-config-baixo", type="number",
                        placeholder=f"Padrão: {VALORES_PADRAO_NIVEIS['limite_estoque_baixo']}",
                        min=0, step=1, value=valor_inicial_baixo,
                        className="form-control mb-2", style={'maxWidth': '150px'}
                    ),
                ], md=6),
                dbc.Col([
                    dbc.Label("Estoque Médio é: > Baixo e ≤", html_for="input-limite-config-medio", className="fw-bold"),
                    dcc.Input(
                        id="input-limite-config-medio", type="number",
                        placeholder=f"Padrão: {VALORES_PADRAO_NIVEIS['limite_estoque_medio']}",
                        min=0, step=1, value=valor_inicial_medio,
                        className="form-control mb-2", style={'maxWidth': '150px'}
                    ),
                ], md=6)
            ], className="mb-3"),
            html.P(html.Small(["Estoque Alto será: Estoque > Limite Médio"]), className="text-muted mt-1"),
            dbc.Button("Salvar Definições de Níveis", id="btn-salvar-config-niveis", color="primary", className="mt-2 mb-3"),
            html.Div(id="div-status-config-niveis", className="mt-2"),
            html.Div([
                html.H6("Definições de Níveis Atuais:", className="mt-3"),
                dbc.Row([
                    dbc.Col(html.Strong("Limite Estoque Baixo (≤):"), width="auto", className="pe-0"),
                    dbc.Col(html.Span(id="span-config-atual-limite-baixo", children=str(valor_inicial_baixo)))
                ]),
                dbc.Row([
                    dbc.Col(html.Strong("Limite Estoque Médio (> Baixo e ≤):"), width="auto", className="pe-0"),
                    dbc.Col(html.Span(id="span-config-atual-limite-medio", children=str(valor_inicial_medio)))
                ]),
            ], className="mt-3 p-3 border rounded bg-light")
        ])
    ], className="h-100 shadow-sm")

    card_excluir_itens = dbc.Card([
        dbc.CardHeader(html.H5("Excluir Itens da Visualização Principal", className="my-2")),
        dbc.CardBody([
            html.P("Selecione Grupos, Categorias ou Produtos para não exibir na aba 'Visão Geral do Estoque'."),
            dbc.Label("Grupos a Excluir:", className="fw-bold"),
            dcc.Dropdown(
                id='dropdown-excluir-grupos', options=opcoes_grupos_excluir,
                value=grupos_excluidos_atuais, multi=True, placeholder="Selecione Grupos"
            ),
            html.Br(),
            dbc.Label("Categorias a Excluir:", className="fw-bold"),
            dcc.Dropdown(
                id='dropdown-excluir-categorias', options=opcoes_categorias_excluir,
                value=categorias_excluidas_atuais, multi=True, placeholder="Selecione Categorias"
            ),
            html.Br(),
            dbc.Label("Produtos (por Código) a Excluir:", className="fw-bold"),
            dcc.Dropdown(
                id='dropdown-excluir-produtos-codigos', options=opcoes_produtos_excluir,
                value=produtos_excluidos_atuais_codigos, multi=True, searchable=True,
                placeholder="Busque e selecione Produtos"
            ),
            dbc.Button("Salvar Exclusões", id="btn-salvar-exclusoes", color="danger", className="mt-3 mb-3"),
            html.Div(id="div-status-salvar-exclusoes", className="mt-2"),
            html.Div([
                html.H6("Itens Atualmente Excluídos:", className="mt-3"),
                dbc.Row([
                    dbc.Col(html.Strong("Grupos:"), width="auto", className="pe-0"),
                    dbc.Col(html.Span(id="span-excluidos-grupos", children=", ".join(grupos_excluidos_atuais) if grupos_excluidos_atuais else "Nenhum"))
                ]),
                dbc.Row([
                    dbc.Col(html.Strong("Categorias:"), width="auto", className="pe-0"),
                    dbc.Col(html.Span(id="span-excluidos-categorias", children=", ".join(categorias_excluidas_atuais) if categorias_excluidas_atuais else "Nenhuma"))
                ]),
                dbc.Row([
                    dbc.Col(html.Strong("Produtos (Códigos):"), width="auto", className="pe-0"),
                    dbc.Col(html.Span(id="span-excluidos-produtos-codigos", children=", ".join(produtos_excluidos_atuais_codigos) if produtos_excluidos_atuais_codigos else "Nenhum"))
                ]),
            ], className="mt-3 p-3 border rounded bg-light")
        ])
    ], className="h-100 shadow-sm")

    layout_aba = html.Div([
        html.H4("Configurações Gerais do Dashboard", className="mt-4 mb-4 text-center"),
        dbc.Row([ 
            dbc.Col(card_definicoes_niveis, width=12, md=6, className="mb-4"), 
            dbc.Col(card_excluir_itens, width=12, md=6, className="mb-4")    
        ], className="g-3") 
    ])

    return layout_aba