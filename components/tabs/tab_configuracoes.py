# components/tabs/tab_configuracoes.py
from dash import html

def criar_conteudo_aba_configuracoes():
    return html.Div([
        html.H4("Configurações de Alerta de Estoque", className="mt-3"), 
        html.P("Esta seção permitirá definir os limites para alertas de estoque baixo.")
    ])