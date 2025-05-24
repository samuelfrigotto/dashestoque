# components/tabs/tab_estoque_baixo.py
from dash import html

def criar_conteudo_aba_estoque_baixo():
    return html.Div([
        html.H4("Produtos com Estoque Baixo", className="mt-3"), 
        html.P("Aqui serão listados os produtos que estão abaixo do limite de estoque configurado.")
    ])