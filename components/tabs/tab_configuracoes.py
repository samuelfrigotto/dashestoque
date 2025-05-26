# components/tabs/tab_configuracoes.py
from dash import html, dcc
import dash_bootstrap_components as dbc
from modules.config_manager import carregar_definicoes_niveis_estoque, VALORES_PADRAO_NIVEIS

def criar_conteudo_aba_configuracoes():
    config_atuais = carregar_definicoes_niveis_estoque()
    valor_inicial_baixo = config_atuais.get("limite_estoque_baixo")
    valor_inicial_medio = config_atuais.get("limite_estoque_medio")

    layout = html.Div([
        dbc.Row(
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(html.H4("Definições de Níveis de Estoque", className="my-2")), # my-2 para padding vertical no header
                    dbc.CardBody([
                        html.P(
                            "Defina os valores que determinam as faixas de Estoque Baixo, Médio e Alto. "
                            "Estes valores serão usados para classificar os produtos no gráfico 'Produtos por Nível de Estoque'."
                        ),
                        html.Hr(),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Estoque Baixo é: Estoque <= (menor ou igual a)", html_for="input-limite-config-baixo", className="fw-bold"),
                                dcc.Input(
                                    id="input-limite-config-baixo", type="number",
                                    placeholder=f"Padrão: {VALORES_PADRAO_NIVEIS['limite_estoque_baixo']}",
                                    min=0, step=1, value=valor_inicial_baixo,
                                    className="form-control mb-2", style={'maxWidth': '200px'}
                                ),
                            ], md=6),
                            dbc.Col([
                                dbc.Label("Estoque Médio é: Limite Baixo < Estoque <= (menor ou igual a)", html_for="input-limite-config-medio", className="fw-bold"),
                                dcc.Input(
                                    id="input-limite-config-medio", type="number",
                                    placeholder=f"Padrão: {VALORES_PADRAO_NIVEIS['limite_estoque_medio']}",
                                    min=0, step=1, value=valor_inicial_medio,
                                    className="form-control mb-2", style={'maxWidth': '200px'}
                                ),
                            ], md=6)
                        ], className="mb-3"), # Margem abaixo da linha dos inputs
                        html.P(html.Small([
                            "Baixo: Estoque ", html.I("≤"), " [Limite Baixo]", html.Br(),
                            "Médio: [Limite Baixo] ", html.I("<"), " Estoque ", html.I("≤"), " [Limite Médio]", html.Br(),
                            "Alto: Estoque ", html.I(">"), " [Limite Médio]"
                        ]), className="text-muted mt-1 border p-2 rounded bg-light mb-3"), # Adicionado bg-light e mb-3

                        dbc.Button(
                            "Salvar Definições", 
                            id="btn-salvar-config-niveis", 
                            color="primary", 
                            className="mt-2 mb-3" # Adicionado mb-3
                        ),
                        html.Div(id="div-status-config-niveis", className="mt-2"), # Status abaixo do botão
                        
                        html.Div([
                            html.H5("Definições Atuais em Uso:", className="mt-4"),
                            dbc.Row([
                                dbc.Col(html.Strong("Limite Estoque Baixo (≤):"), width="auto", className="pe-0"),
                                dbc.Col(html.Span(id="span-config-atual-limite-baixo", children=str(valor_inicial_baixo)))
                            ]),
                            dbc.Row([
                                dbc.Col(html.Strong("Limite Estoque Médio (> Baixo e ≤):"), width="auto", className="pe-0"),
                                dbc.Col(html.Span(id="span-config-atual-limite-medio", children=str(valor_inicial_medio)))
                            ]),
                            dbc.Row([
                                dbc.Col(html.Strong("Estoque Alto (> Limite Médio)"), width="auto")
                            ])
                        ], className="mt-3 p-3 border rounded bg-lightest") # Usar bg-lightest ou outra cor suave

                    ]) # Fim CardBody
                ], className="shadow-sm"), # Adicionado shadow-sm ao Card
            width=12, lg=10, xl=8, className="mx-auto mt-4") # Centralizar o card e limitar largura em telas grandes
        )
    ])
    return layout