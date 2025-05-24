# components/layout.py
import dash_bootstrap_components as dbc
from dash import html

# Importar as funções de criação de conteúdo de cada aba
from .tabs.tab_estoque_geral import criar_conteudo_aba_estoque_geral
from .tabs.tab_configuracoes import criar_conteudo_aba_configuracoes
from .tabs.tab_estoque_baixo import criar_conteudo_aba_estoque_baixo
from .tabs.tab_produtos_em_falta import criar_conteudo_aba_produtos_em_falta

def criar_layout_principal(df_completo, nome_arquivo, page_size_tabela=20):
    """
    Cria o layout principal do dashboard com sistema de abas,
    onde cada aba carrega seu conteúdo de um módulo separado.
    """
    titulo_app = dbc.Row(
        dbc.Col(html.H1("Dashboard de Controle de Estoque - Bebidas", className="text-center my-4"), width=12)
    )
    
    info_arquivo_componente = dbc.Row(
        dbc.Col(html.P(f"Dados do arquivo: {nome_arquivo}"), width=12)
    )

    abas_componente = dbc.Tabs(
        [
            dbc.Tab(
                label="Visão Geral do Estoque", 
                # Chama a função do módulo específico da aba
                children=criar_conteudo_aba_estoque_geral(df_completo, page_size_tabela),
                tab_id="tab-estoque-geral",
                className="pt-3" 
            ),
            dbc.Tab(
                label="Configurações de Alerta", 
                children=criar_conteudo_aba_configuracoes(),
                tab_id="tab-configuracoes",
                className="pt-3"
            ),
            dbc.Tab(
                label="Estoque Baixo", 
                children=criar_conteudo_aba_estoque_baixo(),
                tab_id="tab-estoque-baixo",
                className="pt-3"
            ),
            dbc.Tab(
                label="Produtos em Falta", 
                children=criar_conteudo_aba_produtos_em_falta(),
                tab_id="tab-produtos-em-falta",
                className="pt-3"
            ),
        ],
        id="abas-principais", # ID para o conjunto de abas
        active_tab="tab-estoque-geral", # Aba ativa por padrão
    )

    layout = dbc.Container([
        titulo_app,
        info_arquivo_componente,
        abas_componente 
    ], fluid=True, style={'padding-bottom': '100px'})
    
    return layout