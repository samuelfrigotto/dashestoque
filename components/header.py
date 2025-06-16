import dash_bootstrap_components as dbc
from dash import html

def criar_cabecalho(df_completo):

    if df_completo.empty:
        total_skus, qtd_total_estoque, num_categorias, num_grupos = 0, 0, 0, 0
    else:
        total_skus = df_completo['Código'].nunique()
        qtd_total_estoque = df_completo['Estoque'].sum()
        num_categorias = df_completo['Categoria'].nunique()
        num_grupos = df_completo['Grupo'].nunique()

    card_style = {"display": "flex", "alignItems": "center", "justifyContent": "center", "height": "100%"}
    icon_style = {"fontSize": "2.5rem"}

    cabecalho = html.Header(
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.H2("Dashboard de Controle de Estoque", className="text-white fw-bold"),
                            width=12, lg=4,
                            className="d-flex align-items-center mb-3 mb-lg-0"
                        ),
                        dbc.Col(
                            dbc.Row(
                                [
                                    # Card 1: Total de SKUs -> Ícone de código de barras
                                    dbc.Col(html.Div([
                                        html.I(className="bi bi-upc-scan text-white me-3", style=icon_style),
                                        html.Div([
                                            html.H5(f"{total_skus:,}", className="text-white fw-bold mb-0"),
                                            html.Span("Total de SKUs", className="text-white-50")
                                        ])
                                    ], style=card_style)),
                                    
                                    # Card 2: Estoque Total -> Ícone de arquivo/depósito
                                    dbc.Col(html.Div([
                                        html.I(className="bi bi-archive-fill text-white me-3", style=icon_style),
                                        html.Div([
                                            html.H5(f"{int(qtd_total_estoque):,}", className="text-white fw-bold mb-0"),
                                            html.Span("Estoque Total", className="text-white-50")
                                        ])
                                    ], style=card_style)),

                                    # Card 3: Categorias Ativas -> Ícone de etiquetas (tags)
                                    dbc.Col(html.Div([
                                        html.I(className="bi bi-tags-fill text-white me-3", style=icon_style),
                                        html.Div([
                                            html.H5(f"{num_categorias:,}", className="text-white fw-bold mb-0"),
                                            html.Span("Categorias Ativas", className="text-white-50")
                                        ])
                                    ], style=card_style)),

                                    # Card 4: Grupos Ativos -> Ícone de diagrama/estrutura
                                    dbc.Col(html.Div([
                                        html.I(className="bi bi-diagram-3-fill text-white me-3", style=icon_style),
                                        html.Div([
                                            html.H5(f"{num_grupos:,}", className="text-white fw-bold mb-0"),
                                            html.Span("Grupos Ativos", className="text-white-50")
                                        ])
                                    ], style=card_style)),
                                ],
                                className="g-2"
                            ),
                            width=12, lg=8
                        ),
                    ],
                    align="center",
                    className="p-3"
                )
            ],
            fluid=True
        ),
        className="bg-dark shadow-sm mb-4"
    )
    
    return cabecalho