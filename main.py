# main.py
import pandas as pd
import dash
from dash import html, dcc, Input, Output, no_update
import dash_bootstrap_components as dbc
from modules.data_loader import carregar_produtos_com_hierarquia
from components.layout import criar_layout_principal
from components.graphs.graficos_estoque import (
    criar_grafico_estoque_por_grupo,
    criar_grafico_top_n_produtos_estoque,
    criar_grafico_niveis_estoque,
    criar_figura_vazia
)

# 1. Carregamento de Dados
caminho_arquivo_csv = "data/16-05.CSV"
df_visualizar_global = carregar_produtos_com_hierarquia(caminho_arquivo_csv)

# 2. Inicialização do App Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True)
app.title = "Dashboard de Estoque"

# 3. Definição do Layout
app.layout = criar_layout_principal(
    df_completo=df_visualizar_global,
    nome_arquivo=caminho_arquivo_csv,
    page_size_tabela=20
)

# 4. Callbacks para Interatividade

@app.callback(
    [Output('card-total-skus', 'children'),
     Output('card-qtd-total-estoque', 'children'),
     Output('card-num-categorias', 'children'),
     Output('card-num-grupos', 'children'),
     Output('tabela-estoque', 'data'),
     Output('tabela-estoque', 'columns'),
     Output('grafico-estoque-grupo', 'figure'),
     Output('grafico-top-n-produtos', 'figure'),
     Output('grafico-niveis-estoque', 'figure')],
    [Input('dropdown-categoria-filtro', 'value'),
     Input('dropdown-grupo-filtro', 'value'),
     Input('input-nome-produto-filtro', 'value')] # NOVO INPUT
)
def atualizar_dashboard_filtrado(categoria_selecionada, grupo_selecionado, nome_produto_filtrado): # Novo argumento
    fig_vazia_grupo = criar_figura_vazia("Volume de Estoque por Grupo")
    fig_vazia_top_n = criar_figura_vazia("Top 7 Produtos")
    fig_vazia_niveis = criar_figura_vazia("Produtos por Nível de Estoque")

    if df_visualizar_global is None or df_visualizar_global.empty:
        colunas_vazias = [{"name": col, "id": col} for col in ['Código', 'Produto', 'Un', 'Estoque', 'Categoria', 'Grupo']]
        return "0", "0", "0", "0", [], colunas_vazias, fig_vazia_grupo, fig_vazia_top_n, fig_vazia_niveis

    dff = df_visualizar_global.copy()

    if categoria_selecionada:
        dff = dff[dff['Categoria'] == categoria_selecionada]
    if grupo_selecionado:
        dff = dff[dff['Grupo'] == grupo_selecionado]
    
    # NOVO FILTRO POR NOME DO PRODUTO
    if nome_produto_filtrado and nome_produto_filtrado.strip() != "":
        dff = dff[dff['Produto'].str.contains(nome_produto_filtrado, case=False, na=False)]

    if not dff.empty:
        total_skus_filtrado = dff['Código'].nunique()
        qtd_total_estoque_filtrado = pd.to_numeric(dff['Estoque'], errors='coerce').fillna(0).sum()
        num_categorias_filtradas = dff['Categoria'].nunique()
        num_grupos_filtrados = dff['Grupo'].nunique()
        dados_tabela_filtrada = dff.to_dict('records')

        fig_estoque_grupo = criar_grafico_estoque_por_grupo(dff)
        fig_top_n = criar_grafico_top_n_produtos_estoque(dff, n=7)
        fig_niveis = criar_grafico_niveis_estoque(dff)
    else:
        total_skus_filtrado, qtd_total_estoque_filtrado, num_categorias_filtradas, num_grupos_filtrados = 0,0,0,0
        dados_tabela_filtrada = []
        fig_estoque_grupo = criar_figura_vazia("Volume de Estoque por Grupo (Sem dados com filtros atuais)")
        fig_top_n = criar_figura_vazia(f"Top 7 Produtos (Sem dados com filtros atuais)")
        fig_niveis = criar_figura_vazia("Níveis de Estoque (Sem dados com filtros atuais)")
        
    colunas_desejadas = ['Código', 'Produto', 'Un', 'Estoque', 'Categoria', 'Grupo']
    colunas_base = dff.columns if not dff.empty else df_visualizar_global.columns
    colunas_existentes_ordenadas = [col for col in colunas_desejadas if col in colunas_base]
    for col in colunas_base:
        if col not in colunas_existentes_ordenadas:
            colunas_existentes_ordenadas.append(col)
    colunas_para_dash_filtradas = [{"name": i, "id": i} for i in colunas_existentes_ordenadas]

    return (
        f"{total_skus_filtrado:,}",
        f"{qtd_total_estoque_filtrado:,.0f}",
        f"{num_categorias_filtradas:,}",
        f"{num_grupos_filtrados:,}",
        dados_tabela_filtrada,
        colunas_para_dash_filtradas,
        fig_estoque_grupo,
        fig_top_n,
        fig_niveis
    )






# Callback para resetar o filtro de Grupo quando uma Categoria é ATIVAMENTE selecionada
@app.callback(
    Output('dropdown-grupo-filtro', 'value', allow_duplicate=True),
    Input('dropdown-categoria-filtro', 'value'),
    prevent_initial_call=True
)
def resetar_filtro_grupo(categoria_selecionada):
    if categoria_selecionada is not None:
        return None
    return no_update

# Callback para resetar o filtro de Categoria quando um Grupo é ATIVAMENTE selecionado
@app.callback(
    Output('dropdown-categoria-filtro', 'value', allow_duplicate=True),
    Input('dropdown-grupo-filtro', 'value'),
    prevent_initial_call=True
)
def resetar_filtro_categoria(grupo_selecionado):
    if grupo_selecionado is not None:
        return None
    return no_update

# Callback para o botão de Resetar Filtros
@app.callback(
    [Output('dropdown-grupo-filtro', 'value', allow_duplicate=True),
     Output('dropdown-categoria-filtro', 'value', allow_duplicate=True),
     Output('input-nome-produto-filtro', 'value')], # NOVO OUTPUT PARA LIMPAR O INPUT DE TEXTO
    Input('btn-resetar-filtros', 'n_clicks'),
    prevent_initial_call=True
)
def resetar_todos_filtros(n_clicks):
    return None, None, '' # Retorna string vazia para o dcc.Input

# 5. Execução do Servidor
if __name__ == '__main__':
    if df_visualizar_global is not None and not df_visualizar_global.empty:
        print("Dados para visualização carregados com sucesso. Iniciando o servidor Dash...")
        app.run(debug=True, host='127.0.0.1', port=8050)
    else:
        print("Não foi possível iniciar o servidor pois os dados para visualização não foram carregados ou o DataFrame está vazio.")


