import dash_bootstrap_components as dbc
from dash import html
from .tabs.tab_estoque_geral import criar_conteudo_aba_estoque_geral
from .tabs.tab_configuracoes import criar_conteudo_aba_configuracoes
from .tabs.tab_estoque_baixo import criar_conteudo_aba_estoque_baixo
from .tabs.tab_produtos_em_falta import criar_conteudo_aba_produtos_em_falta
from components.header import criar_cabecalho

def criar_layout_principal(df_completo, nome_arquivo, page_size_tabela=20):
    """
    Cria o layout principal do dashboard com sistema de abas,
    onde cada aba carrega seu conteúdo de um módulo separado,
    com melhorias de estilização e espaçamento.
    """

    titulo_app = dbc.Row(
        dbc.Col(html.H1("Dashboard de Controle de Estoque", 
                        className="text-center my-4 display-5 fw-bold"), width=12) 
    )

    abas_componente = dbc.Tabs(
        [
            dbc.Tab(
                label="Visão Geral do Estoque", 
                children=criar_conteudo_aba_estoque_geral(df_completo, page_size_tabela),
                tab_id="tab-estoque-geral",
                className="py-3"
            ),
            dbc.Tab(
                label="Configurações", 
                children=criar_conteudo_aba_configuracoes(df_completo),
                tab_id="tab-configuracoes",
                className="py-3"
            ),
            dbc.Tab(
                label="Estoque Baixo", 
                children=criar_conteudo_aba_estoque_baixo(),
                tab_id="tab-estoque-baixo",
                className="py-3"
            ),
            dbc.Tab(
                label="Produtos em Falta", 
                children=criar_conteudo_aba_produtos_em_falta(df_completo), 
                tab_id="tab-produtos-em-falta",
                className="py-3"
            ),
        ],
        id="abas-principais",
        active_tab="tab-estoque-geral",
        className="mt-2"
    )
    


    layout = dbc.Container([
        criar_cabecalho(df_completo),
        abas_componente 
    ], fluid=True, className="p-0")
    
    return layout