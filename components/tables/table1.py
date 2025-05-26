# components/tables/table1.py
import pandas as pd
from dash import dash_table, html
import dash_bootstrap_components as dbc

def criar_tabela_estoque(df_dados_tabela, id_tabela='tabela-estoque', page_size=20):
    if df_dados_tabela.empty:
        return dbc.Alert("Nenhum dado para exibir na tabela.", color="warning", className="text-center")

    colunas_desejadas = ['Código', 'Produto', 'Un', 'Estoque', 'Categoria', 'Grupo']
    colunas_existentes_ordenadas = [col for col in colunas_desejadas if col in df_dados_tabela.columns]
    for col in df_dados_tabela.columns:
        if col not in colunas_existentes_ordenadas and col not in ['VendaMensal']:
            colunas_existentes_ordenadas.append(col)
    
    colunas_para_dash = [{"name": i, "id": i} for i in colunas_existentes_ordenadas]

    return dash_table.DataTable(
        id=id_tabela,
        columns=colunas_para_dash,
        data=df_dados_tabela.to_dict('records'),
        page_size=page_size, # Paginação controlada aqui
        
        # export_format='xlsx', # REMOVIDO para usarmos um botão customizado
        # export_headers='display', # REMOVIDO
        
        fixed_rows={'headers': True}, 
        style_table={
            # 'height': '450px',      # REMOVIDA altura fixa
            # 'overflowY': 'auto',    # REMOVIDA rolagem vertical interna
            'overflowX': 'auto', 
            'minWidth': '100%',
            'border': '1px solid #e9ecef',
            'borderRadius': '0.375rem',
        },
        style_header={
            'backgroundColor': '#f8f9fa', 'fontWeight': 'bold',
            'borderBottom': '2px solid #dee2e6', 'padding': '0.75rem', 'textAlign': 'left',
            'position': 'sticky', 'top': 0, 'zIndex': 1 
        },
        style_cell={
            'textAlign': 'left', 'minWidth': '100px', 'width': '150px', 'maxWidth': '350px',
            'overflow': 'hidden', 'textOverflow': 'ellipsis',
            'padding': '0.75rem', 'borderRight': '1px solid #e9ecef',
            'borderBottom': '1px solid #e9ecef', 
            'whiteSpace': 'normal', 'height': 'auto'
        },
        style_cell_conditional=[
            {'if': {'column_id': 'Produto'}, 'minWidth': '250px', 'width': '350px'},
            {'if': {'column_id': 'Estoque'}, 'textAlign': 'right', 'minWidth': '100px', 'width': '120px', 'maxWidth': '150px'},
            {'if': {'column_id': 'Código'}, 'minWidth': '100px', 'width': '120px', 'maxWidth': '180px'},
            {'if': {'column_id': 'Un'}, 'minWidth': '60px', 'width': '80px', 'maxWidth': '100px', 'textAlign': 'center'}
        ],
        style_data_conditional=[
            {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(0, 0, 0, 0.03)'},
            {'if': {'state': 'active'}, 
             'backgroundColor': 'rgba(0, 123, 255, 0.1)',
             'border': '1px solid rgba(0, 123, 255, 0.2)'}
        ]
    )

def criar_tabela_produtos_criticos(df_produtos, id_tabela, titulo_alerta, page_size=5, altura_tabela='300px'):
    """
    Cria uma DataTable compacta para produtos críticos (baixo estoque).
    Esta tabela MANTÉM o scroll vertical interno e mostra todos os itens via page_size grande.
    """
    if df_produtos.empty:
        return dbc.Alert(f"{titulo_alerta}: Nenhum produto encontrado.", color="info", className="mt-2")

    colunas_para_dash = [
        {"name": "Produto", "id": "Produto"},
        {"name": "Estoque Atual", "id": "Estoque"}
    ]
    dados_para_tabela = df_produtos[['Produto', 'Estoque']].to_dict('records')

    # Para mostrar todos os itens na área de scroll, page_size deve ser >= len(dados)
    page_size_real = max(1, len(dados_para_tabela)) 

    return html.Div([
        html.H6(titulo_alerta, className="mt-3 text-danger fw-bold"),
        dash_table.DataTable(
            id=id_tabela,
            columns=colunas_para_dash,
            data=dados_para_tabela,
            page_size=page_size_real, # MOSTRA TODOS OS ITENS DENTRO DA ÁREA DE SCROLL
            style_table={
                'height': altura_tabela, # ALTURA FIXA PARA SCROLL
                'overflowY': 'auto',    # SCROLL VERTICAL INTERNO
                'overflowX': 'auto',
                'width': '100%', 
                'border': '1px solid #dee2e6', 
                'borderRadius': '0.25rem',
            },
            style_header={
                'backgroundColor': '#f8f9fa', 'fontWeight': 'bold',
                'borderBottom': '2px solid #dee2e6', 'padding': '8px',
                'textAlign': 'left', 'position': 'sticky', 'top': 0, 'zIndex': 1
            },
            style_cell={
                'textAlign': 'left', 'padding': '8px',
                'borderRight': '1px solid #f0f0f0', 'borderBottom': '1px solid #f0f0f0',
                'overflow': 'hidden', 'textOverflow': 'ellipsis', 'maxWidth': 0
            },
            style_cell_conditional=[
                {'if': {'column_id': 'Produto'}, 'minWidth': '200px', 'width': '70%'},
                {'if': {'column_id': 'Estoque'}, 'textAlign': 'right', 'minWidth': '80px', 'width': '30%'}
            ],
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgba(0,0,0,0.025)'},
                {'if': {'filter_query': '{Estoque} <= 0', 'column_id': 'Estoque'}, 
                 'backgroundColor': 'rgba(220, 53, 69, 0.7)', 'color': 'white', 'fontWeight': 'bold'},
            ]
        )
    ])