# main.py
import pandas as pd
import dash
from dash import html, dcc, Input, Output, no_update # Adicionado no_update
import dash_bootstrap_components as dbc
from modules.data_loader import carregar_produtos_com_hierarquia # Ou carregar_apenas_produtos
from components.layout import criar_layout_principal

# 1. Carregamento de Dados
caminho_arquivo_csv = "data/16-05.CSV"
df_visualizar_global = carregar_produtos_com_hierarquia(caminho_arquivo_csv)

# 2. Inicialização do App Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True) # Mantido para flexibilidade com allow_duplicate
app.title = "Dashboard de Estoque"

# 3. Definição do Layout
app.layout = criar_layout_principal(
    df_completo=df_visualizar_global,
    nome_arquivo=caminho_arquivo_csv,
    page_size_tabela=20
)

# 4. Callbacks para Interatividade

# Callback principal para atualizar cards e tabela com base nos filtros
@app.callback(
    [Output('card-total-skus', 'children'),
     Output('card-qtd-total-estoque', 'children'),
     Output('card-num-categorias', 'children'),
     Output('card-num-grupos', 'children'),
     Output('tabela-estoque', 'data'),
     Output('tabela-estoque', 'columns')],
    [Input('dropdown-categoria-filtro', 'value'),
     Input('dropdown-grupo-filtro', 'value')]
)
def atualizar_dashboard_filtrado(categoria_selecionada, grupo_selecionado):
    if df_visualizar_global is None or df_visualizar_global.empty:
        colunas_vazias = [{"name": col, "id": col} for col in ['Código', 'Produto', 'Un', 'Estoque', 'Categoria', 'Grupo']]
        return "0", "0", "0", "0", [], colunas_vazias

    dff = df_visualizar_global.copy()

    if categoria_selecionada:
        dff = dff[dff['Categoria'] == categoria_selecionada]

    if grupo_selecionado:
        dff = dff[dff['Grupo'] == grupo_selecionado]

    if not dff.empty:
        total_skus_filtrado = dff['Código'].nunique()
        qtd_total_estoque_filtrado = pd.to_numeric(dff['Estoque'], errors='coerce').fillna(0).sum()
        num_categorias_filtradas = dff['Categoria'].nunique()
        num_grupos_filtrados = dff['Grupo'].nunique()
        dados_tabela_filtrada = dff.to_dict('records')
    else:
        total_skus_filtrado = 0
        qtd_total_estoque_filtrado = 0
        num_categorias_filtradas = 0
        num_grupos_filtrados = 0
        dados_tabela_filtrada = []

    colunas_desejadas = ['Código', 'Produto', 'Un', 'Estoque', 'Categoria', 'Grupo']
    colunas_base = df_visualizar_global.columns if dff.empty and not df_visualizar_global.empty else dff.columns

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
        colunas_para_dash_filtradas
    )

# Callback para resetar o filtro de Grupo quando uma Categoria é ATIVAMENTE selecionada
@app.callback(
    Output('dropdown-grupo-filtro', 'value', allow_duplicate=True),
    Input('dropdown-categoria-filtro', 'value'), # Mudado para Input simples
    prevent_initial_call=True
)
def resetar_filtro_grupo(categoria_selecionada):
    if categoria_selecionada is not None: # Só reseta se uma categoria real foi selecionada
        return None # Reseta o grupo
    return no_update # Se a categoria foi limpa (None), não mexe no grupo

# Callback para resetar o filtro de Categoria quando um Grupo é ATIVAMENTE selecionado
@app.callback(
    Output('dropdown-categoria-filtro', 'value', allow_duplicate=True),
    Input('dropdown-grupo-filtro', 'value'), # Mudado para Input simples
    prevent_initial_call=True
)
def resetar_filtro_categoria(grupo_selecionado):
    if grupo_selecionado is not None: # Só reseta se um grupo real foi selecionado
        return None # Reseta a categoria
    return no_update # Se o grupo foi limpo (None), não mexe na categoria

# Callback para o botão de Resetar Filtros
@app.callback(
    [Output('dropdown-grupo-filtro', 'value', allow_duplicate=True), # Re-adicionado allow_duplicate para clareza
     Output('dropdown-categoria-filtro', 'value', allow_duplicate=True)],# Re-adicionado allow_duplicate
    Input('btn-resetar-filtros', 'n_clicks'), # Mudado para Input simples
    prevent_initial_call=True
)
def resetar_todos_filtros(n_clicks):
    return None, None

# 5. Execução do Servidor
if __name__ == '__main__':
    if df_visualizar_global is not None and not df_visualizar_global.empty:
        print("Dados para visualização carregados com sucesso. Iniciando o servidor Dash...")
        app.run(debug=True, host='127.0.0.1', port=8050)
    else:
        print("Não foi possível iniciar o servidor pois os dados para visualização não foram carregados ou o DataFrame está vazio.")