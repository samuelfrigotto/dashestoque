from dash import html, dcc 
import dash_bootstrap_components as dbc

def criar_conteudo_aba_estoque_baixo():
    """
    Cria o contêiner para o conteúdo dinâmico da aba de Estoque Baixo.
    O conteúdo real (gráfico e tabela) será carregado por um callback.
    """
    layout = html.Div([
        html.H4("Produtos com Estoque Baixo", className="mt-4 mb-3"),
        html.Div(id="conteudo-dinamico-aba-estoque-baixo") 
    ])
    return layout