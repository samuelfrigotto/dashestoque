import pandas as pd
from dash import dash_table
import dash_bootstrap_components as dbc

def criar_tabela_estoque(df_dados_tabela, id_tabela='tabela-estoque', page_size=20):
    """
    Cria um componente DataTable do Dash para exibir o DataFrame fornecido.
    df_dados_tabela: DataFrame já preparado para exibição (ex: df.head(1000)).
    """
    if df_dados_tabela.empty:
        return dbc.Alert("Nenhum dado para exibir na tabela.", color="warning", className="text-center")

    colunas_desejadas = ['Código', 'Produto', 'Un', 'Estoque', 'Categoria', 'Grupo']
    colunas_existentes_ordenadas = [col for col in colunas_desejadas if col in df_dados_tabela.columns]

    for col in df_dados_tabela.columns:
        if col not in colunas_existentes_ordenadas:
            colunas_existentes_ordenadas.append(col)
    
    colunas_para_dash = [{"name": i, "id": i} for i in colunas_existentes_ordenadas]

    return dash_table.DataTable(
        id=id_tabela,
        columns=colunas_para_dash,
        data=df_dados_tabela.to_dict('records'),
        page_size=page_size,
        style_table={'overflowX': 'auto', 'minWidth': '100%'},
        style_cell={
            'textAlign': 'left',
            'minWidth': '100px', 'width': '150px', 'maxWidth': '300px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'padding': '5px'
        },
        style_header={
            'backgroundColor': 'lightgrey',
            'fontWeight': 'bold'
        }
    )