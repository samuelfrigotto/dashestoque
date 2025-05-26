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
    onde cada aba carrega seu conteúdo de um módulo separado,
    com melhorias de estilização e espaçamento.
    """
    # Título principal da aplicação com mais destaque e margem
    titulo_app = dbc.Row(
        dbc.Col(html.H1("Dashboard de Controle de Estoque - Bebidas", 
                        className="text-center my-4 display-5 fw-bold"), width=12) 
                        # display-5 para um bom tamanho, fw-bold para negrito
    )
    
    # Informação do arquivo, centralizada e com margem inferior
    info_arquivo_componente = dbc.Row(
        dbc.Col(html.P(f"Analisando dados do arquivo: {nome_arquivo}", 
                        className="text-center text-muted mb-4"), width=12)
    )

    # Componente de Abas com margem superior e padding interno ajustado nas abas
    abas_componente = dbc.Tabs(
        [
            dbc.Tab(
                label="Visão Geral do Estoque", 
                children=criar_conteudo_aba_estoque_geral(df_completo, page_size_tabela),
                tab_id="tab-estoque-geral",
                className="py-3" # py-3 para padding vertical (topo e base) dentro da aba
            ),
            dbc.Tab(
                label="Definições de Níveis", 
                children=criar_conteudo_aba_configuracoes(),
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
        className="mt-2" # Margem acima do componente de abas
    )

    # Contêiner principal com padding geral
    layout = dbc.Container([
        titulo_app,
        info_arquivo_componente,
        abas_componente 
    ], fluid=True, style={'paddingTop': '20px', 'paddingBottom': '50px'}) # Padding no topo e base do container geral
    
    return layout