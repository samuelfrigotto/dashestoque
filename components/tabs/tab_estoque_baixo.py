# components/tabs/tab_estoque_baixo.py
from dash import html, dcc # dcc pode ser útil para futuros filtros nesta aba
import dash_bootstrap_components as dbc

def criar_conteudo_aba_estoque_baixo():
    """
    Cria o contêiner para o conteúdo dinâmico da aba de Estoque Baixo.
    O conteúdo real (gráfico e tabela) será carregado por um callback.
    """
    layout = html.Div([
        html.H4("Produtos com Estoque Baixo", className="mt-4 mb-3"),
        # Este Div será o alvo do callback para injetar o gráfico e a tabela
        html.Div(id="conteudo-dinamico-aba-estoque-baixo") 
    ])
    return layout