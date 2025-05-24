# components/tabs/tab_produtos_em_falta.py
from dash import html

def criar_conteudo_aba_produtos_em_falta():
    return html.Div([
        html.H4("Produtos em Falta", className="mt-3"), 
        html.P("Esta seção mostrará os produtos com estoque zerado ou abaixo de um limite crítico.")
    ])