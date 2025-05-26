# components/tabs/tab_produtos_em_falta.py
from dash import html, dcc # dcc pode ser necessário para futuros componentes aqui
import dash_bootstrap_components as dbc
import pandas as pd
from modules.inventory_manager import identificar_produtos_em_falta
# Importar a função de criação de tabela do local correto
from ..tables.table1 import criar_tabela_estoque 

def criar_conteudo_aba_produtos_em_falta(df_completo, page_size_tabela=10):
    """
    Cria o conteúdo para a aba de Produtos em Falta.
    """
    if df_completo is None or df_completo.empty:
        return html.Div([
            html.H4("Produtos em Falta", className="mt-3"),
            dbc.Alert("Não há dados de estoque para processar.", color="warning")
        ])

    df_em_falta = identificar_produtos_em_falta(df_completo) # Usando limite padrão de <= 0

    if df_em_falta.empty:
        conteudo = dbc.Alert("Nenhum produto encontrado em falta!", color="success")
    else:
        # Reutilizar a função de criação de tabela
        # Passamos o DataFrame de produtos em falta
        # Pode ser necessário ajustar as colunas se quisermos uma visualização diferente para esta tabela
        tabela_produtos_em_falta = criar_tabela_estoque(
            df_em_falta, 
            id_tabela='tabela-produtos-em-falta', 
            page_size=page_size_tabela
        )
        conteudo = html.Div([
            html.P(f"Encontrados {len(df_em_falta)} produto(s) em falta (Estoque <= 0)."),
            tabela_produtos_em_falta
        ])
        
    layout = html.Div([
        html.H4("Produtos em Falta", className="mt-4 mb-3"),
        conteudo
    ])
    
    return layout