import pandas as pd
from dash import Input, Output, no_update, State, html, dcc 
import dash_bootstrap_components as dbc
from app_instance import app 

from components.graphs.graficos_estoque import (
    criar_grafico_estoque_por_grupo,
    criar_grafico_top_n_produtos_estoque,
    criar_grafico_niveis_estoque,
    criar_figura_vazia,
    criar_grafico_categorias_com_estoque_baixo 
)
from modules.config_manager import (
    carregar_definicoes_niveis_estoque, 
    salvar_definicoes_niveis_estoque,
    carregar_configuracoes_exclusao,
    salvar_configuracoes_exclusao   
)
from modules.inventory_manager import identificar_produtos_estoque_baixo 
from components.tables.table1 import criar_tabela_estoque

def registrar_callbacks_gerais(df_global_original):
    """
    Registra todos os callbacks.
    df_global_original: O DataFrame principal carregado, antes de qualquer filtro de exclusão.
    """

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
         Input('input-nome-produto-filtro', 'value'),
         Input('span-config-atual-limite-baixo', 'children'), 
         Input('span-config-atual-limite-medio', 'children'),
         Input('span-excluidos-grupos', 'children'),
         Input('span-excluidos-categorias', 'children'),
         Input('span-excluidos-produtos-codigos', 'children')]
    )
    def atualizar_dashboard_filtrado(categoria_selecionada, grupo_selecionado, nome_produto_filtrado, 
                                     ignore_lim_b_span, ignore_lim_m_span,
                                     ignore_exc_grp, ignore_exc_cat, ignore_exc_prod):
        
        fig_vazia_grupo = criar_figura_vazia("Volume de Estoque por Grupo")
        fig_vazia_top_n = criar_figura_vazia("Top 7 Produtos")
        fig_vazia_niveis = criar_figura_vazia("Produtos por Nível de Estoque")

        if df_global_original is None or df_global_original.empty:
            colunas_vazias = [{"name": col, "id": col} for col in ['Código', 'Produto', 'Un', 'Estoque', 'Categoria', 'Grupo']]
            return "0", "0", "0", "0", [], colunas_vazias, fig_vazia_grupo, fig_vazia_top_n, fig_vazia_niveis

        config_exclusao = carregar_configuracoes_exclusao()
        grupos_a_excluir = config_exclusao.get("excluir_grupos", [])
        categorias_a_excluir = config_exclusao.get("excluir_categorias", [])
        produtos_codigos_a_excluir = config_exclusao.get("excluir_produtos_codigos", [])
        
 
        produtos_codigos_a_excluir = [str(p) for p in produtos_codigos_a_excluir]

        dff = df_global_original.copy()

        if grupos_a_excluir:
            dff = dff[~dff['Grupo'].isin(grupos_a_excluir)]
        if categorias_a_excluir:
            dff = dff[~dff['Categoria'].isin(categorias_a_excluir)]
        if produtos_codigos_a_excluir:
            dff = dff[~dff['Código'].astype(str).isin(produtos_codigos_a_excluir)]

        if categoria_selecionada:
            dff = dff[dff['Categoria'] == categoria_selecionada]
        if grupo_selecionado:
            dff = dff[dff['Grupo'] == grupo_selecionado]
        if nome_produto_filtrado and nome_produto_filtrado.strip() != "":
            dff = dff[dff['Produto'].str.contains(nome_produto_filtrado, case=False, na=False)]

        config_niveis = carregar_definicoes_niveis_estoque()
        limite_baixo_atual = config_niveis.get("limite_estoque_baixo", 10)
        limite_medio_atual = config_niveis.get("limite_estoque_medio", 100)

        if not dff.empty:
            total_skus_filtrado = dff['Código'].nunique()
            qtd_total_estoque_filtrado = pd.to_numeric(dff['Estoque'], errors='coerce').fillna(0).sum()
            num_categorias_filtradas = dff['Categoria'].nunique()
            num_grupos_filtrados = dff['Grupo'].nunique()
            dados_tabela_filtrada = dff.to_dict('records')

            fig_estoque_grupo = criar_grafico_estoque_por_grupo(dff)
            fig_top_n = criar_grafico_top_n_produtos_estoque(dff, n=7)
            fig_niveis = criar_grafico_niveis_estoque(dff, limite_baixo_atual, limite_medio_atual)
        else:
            total_skus_filtrado, qtd_total_estoque_filtrado, num_categorias_filtradas, num_grupos_filtrados = 0,0,0,0
            dados_tabela_filtrada = []
            fig_estoque_grupo = criar_figura_vazia("Volume de Estoque por Grupo (Sem dados com filtros atuais)")
            fig_top_n = criar_figura_vazia(f"Top 7 Produtos (Sem dados com filtros atuais)")
            fig_niveis = criar_figura_vazia("Níveis de Estoque (Sem dados com filtros atuais)")
            
        colunas_desejadas = ['Código', 'Produto', 'Un', 'Estoque', 'Categoria', 'Grupo']

        colunas_base = dff.columns if not dff.empty else df_global_original.columns 
        
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
    @app.callback(
        Output('dropdown-grupo-filtro', 'value', allow_duplicate=True),
        Input('dropdown-categoria-filtro', 'value'),
        prevent_initial_call=True
    )
    def resetar_filtro_grupo(categoria_selecionada):
        if categoria_selecionada is not None: return None
        return no_update

    @app.callback(
        Output('dropdown-categoria-filtro', 'value', allow_duplicate=True),
        Input('dropdown-grupo-filtro', 'value'),
        prevent_initial_call=True
    )
    def resetar_filtro_categoria(grupo_selecionado):
        if grupo_selecionado is not None: return None
        return no_update

    @app.callback(
        [Output('dropdown-grupo-filtro', 'value', allow_duplicate=True),
         Output('dropdown-categoria-filtro', 'value', allow_duplicate=True),
         Output('input-nome-produto-filtro', 'value', allow_duplicate=True)],
        Input('btn-resetar-filtros', 'n_clicks'),
        prevent_initial_call=True
    )
    def resetar_todos_filtros(n_clicks):
        return None, None, ''

    @app.callback(
        [Output('div-status-config-niveis', 'children'),
         Output('span-config-atual-limite-baixo', 'children'),
         Output('span-config-atual-limite-medio', 'children'),
         Output('input-limite-config-baixo', 'value', allow_duplicate=True),
         Output('input-limite-config-medio', 'value', allow_duplicate=True)],
        [Input('btn-salvar-config-niveis', 'n_clicks')],
        [State('input-limite-config-baixo', 'value'),
         State('input-limite-config-medio', 'value')],
        prevent_initial_call=True
    )
    def salvar_configuracoes_niveis(n_clicks, limite_baixo_input, limite_medio_input):
        if limite_baixo_input is None or limite_medio_input is None:
            mensagem = dbc.Alert("Ambos os limites de níveis devem ser preenchidos.", color="danger", dismissable=True, duration=7000)
            return mensagem, no_update, no_update, no_update, no_update

        sucesso, msg_retorno_salvar = salvar_definicoes_niveis_estoque(limite_baixo_input, limite_medio_input)
        cor_alerta = "success" if sucesso else "danger"
        status_mensagem_componente = dbc.Alert(msg_retorno_salvar, color=cor_alerta, dismissable=True, duration=7000)
        config_recarregada = carregar_definicoes_niveis_estoque()
        val_baixo_recarregado = config_recarregada.get("limite_estoque_baixo")
        val_medio_recarregado = config_recarregada.get("limite_estoque_medio")
        return status_mensagem_componente, str(val_baixo_recarregado), str(val_medio_recarregado), val_baixo_recarregado, val_medio_recarregado


    @app.callback(
        [Output('div-status-salvar-exclusoes', 'children'),
         Output('span-excluidos-grupos', 'children'),
         Output('span-excluidos-categorias', 'children'),
         Output('span-excluidos-produtos-codigos', 'children'),
         Output('dropdown-excluir-grupos', 'value', allow_duplicate=True),
         Output('dropdown-excluir-categorias', 'value', allow_duplicate=True),
         Output('dropdown-excluir-produtos-codigos', 'value', allow_duplicate=True)],
        [Input('btn-salvar-exclusoes', 'n_clicks')],
        [State('dropdown-excluir-grupos', 'value'),
         State('dropdown-excluir-categorias', 'value'),
         State('dropdown-excluir-produtos-codigos', 'value')],
        prevent_initial_call=True
    )
    def salvar_config_exclusoes(n_clicks_salvar_exc, grupos_sel, categorias_sel, produtos_cod_sel):
        if n_clicks_salvar_exc is None:
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update

        sucesso, msg_retorno = salvar_configuracoes_exclusao(grupos_sel, categorias_sel, produtos_cod_sel)
        
        cor_alerta = "success" if sucesso else "danger"
        status_msg_componente = dbc.Alert(msg_retorno, color=cor_alerta, dismissable=True, duration=7000)
        
        config_exc_recarregada = carregar_configuracoes_exclusao()
        grupos_exc_atuais = config_exc_recarregada.get("excluir_grupos", [])
        cat_exc_atuais = config_exc_recarregada.get("excluir_categorias", [])
        prod_cod_exc_atuais = config_exc_recarregada.get("excluir_produtos_codigos", [])
        
        return (
            status_msg_componente,
            ", ".join(grupos_exc_atuais) if grupos_exc_atuais else "Nenhum",
            ", ".join(cat_exc_atuais) if cat_exc_atuais else "Nenhuma",
            ", ".join(prod_cod_exc_atuais) if prod_cod_exc_atuais else "Nenhum",
            grupos_exc_atuais, 
            cat_exc_atuais,   
            prod_cod_exc_atuais
        )


    @app.callback(
        Output('conteudo-dinamico-aba-estoque-baixo', 'children'),
        [Input('span-config-atual-limite-baixo', 'children'),
         Input('abas-principais', 'active_tab')]
    )
    def atualizar_conteudo_aba_estoque_baixo(limite_baixo_salvo_str, aba_ativa):
        if aba_ativa != "tab-estoque-baixo" or df_global_original is None or df_global_original.empty:
            return "" 

        config_niveis = carregar_definicoes_niveis_estoque()
        try:
            limite_baixo = float(config_niveis.get("limite_estoque_baixo")) 
        except (ValueError, TypeError):
            return dbc.Alert("Configuração de limite de estoque baixo inválida.", color="danger")


        config_exclusao = carregar_configuracoes_exclusao()
        grupos_a_excluir = config_exclusao.get("excluir_grupos", [])
        categorias_a_excluir = config_exclusao.get("excluir_categorias", [])
        produtos_codigos_a_excluir = [str(p) for p in config_exclusao.get("excluir_produtos_codigos", [])]

        df_para_analise_baixo = df_global_original.copy()

        if grupos_a_excluir:
            df_para_analise_baixo = df_para_analise_baixo[~df_para_analise_baixo['Grupo'].isin(grupos_a_excluir)]
        if categorias_a_excluir:
            df_para_analise_baixo = df_para_analise_baixo[~df_para_analise_baixo['Categoria'].isin(categorias_a_excluir)]
        if produtos_codigos_a_excluir:
            df_para_analise_baixo = df_para_analise_baixo[~df_para_analise_baixo['Código'].astype(str).isin(produtos_codigos_a_excluir)]

        df_produtos_baixos = identificar_produtos_estoque_baixo(df_para_analise_baixo, limite_baixo)

        if df_produtos_baixos.empty:
            return dbc.Alert(f"Nenhum produto encontrado com estoque baixo (Estoque ≤ {limite_baixo:g}) após aplicar exclusões e filtros.", color="info", className="mt-3")

        grafico = dcc.Graph(
            id='grafico-categorias-estoque-baixo-tab',
            figure=criar_grafico_categorias_com_estoque_baixo(df_produtos_baixos)
        )
        tabela = criar_tabela_estoque(
            df_produtos_baixos, 
            id_tabela='tabela-produtos-estoque-baixo-tab',
            page_size=10
        )
        return html.Div([
            html.P(f"Encontrados {len(df_produtos_baixos)} produto(s) com estoque baixo (Estoque ≤ {limite_baixo:g}).", className="mt-3"),
            dbc.Row([dbc.Col(dbc.Card(grafico), width=12, className="mb-3")]),
            html.Hr(),
            tabela
        ])
