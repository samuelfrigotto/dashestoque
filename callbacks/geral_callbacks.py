import pandas as pd
import dash
from dash import Input, Output, no_update, State, html, dcc 
import dash_bootstrap_components as dbc
from app_instance import app 
import io

from components.graphs.graficos_estoque import (
    criar_grafico_estoque_por_grupo,
    criar_grafico_top_n_produtos_estoque,
    criar_grafico_niveis_estoque,
    criar_figura_vazia,
    criar_grafico_categorias_com_estoque_baixo,
    criar_grafico_estoque_produtos_populares,
    criar_grafico_colunas_estoque_por_grupo,
)
from components.tables.table1 import criar_tabela_estoque, criar_tabela_produtos_criticos
from modules.config_manager import (
    carregar_definicoes_niveis_estoque, salvar_definicoes_niveis_estoque,
    carregar_configuracoes_exclusao, salvar_configuracoes_exclusao
)
from modules.inventory_manager import identificar_produtos_estoque_baixo, identificar_produtos_em_falta

def registrar_callbacks_gerais(df_global_original):

    @app.callback(
        [Output('card-total-skus', 'children'),
         Output('card-qtd-total-estoque', 'children'),
         Output('card-num-categorias', 'children'),
         Output('card-num-grupos', 'children'),
         Output('grafico-colunas-resumo-estoque', 'figure'),
         #Output('tabela-estoque', 'data'),
         #Output('tabela-estoque', 'columns'),
         Output('grafico-estoque-grupo', 'figure'),
         Output('container-tabela-alerta-estoque-baixo-geral', 'children'), 
         Output('grafico-top-n-produtos', 'figure'),
         Output('grafico-niveis-estoque', 'figure'),
         Output('grafico-estoque-populares', 'figure'),
         Output('grafico-categorias-estoque-baixo-visao-geral', 'figure')], 
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
                                     limite_baixo_str_span, limite_medio_str_span,
                                     ignore_exc_grp, ignore_exc_cat, ignore_exc_prod):

        fig_vazia_grupo = criar_figura_vazia("Volume de Estoque por Grupo")
        tabela_alerta_vazia = criar_tabela_produtos_criticos(pd.DataFrame(columns=['Produto', 'Estoque']), 'tabela-alerta-vazia-geral-cb-placeholder', "Produtos com Estoque Baixo", page_size=10, altura_tabela='250px')
        fig_vazia_top_n = criar_figura_vazia("Top 7 Produtos")
        fig_vazia_niveis = criar_figura_vazia("Produtos por Nível de Estoque")
        fig_vazia_populares = criar_figura_vazia("Estoque dos Produtos Populares")
        fig_vazia_cat_baixo_geral = criar_figura_vazia("Categorias com Estoque Baixo")
        fig_vazia_colunas_resumo = criar_grafico_colunas_estoque_por_grupo(pd.DataFrame())


        if df_global_original is None or df_global_original.empty:
            colunas_vazias_principais = [{"name": col, "id": col} for col in ['Código', 'Produto', 'Un', 'Estoque', 'Categoria', 'Grupo']]
            return ("0", "0", "0", "0", fig_vazia_colunas_resumo, [], colunas_vazias_principais,
                    fig_vazia_grupo, tabela_alerta_vazia,
                    fig_vazia_top_n, fig_vazia_niveis, fig_vazia_populares,
                    fig_vazia_cat_baixo_geral)

        config_exclusao = carregar_configuracoes_exclusao()
        dff = df_global_original.copy()
        grupos_a_excluir = config_exclusao.get("excluir_grupos", []); categorias_a_excluir = config_exclusao.get("excluir_categorias", []); produtos_codigos_a_excluir = [str(p) for p in config_exclusao.get("excluir_produtos_codigos", [])]
        if grupos_a_excluir: dff = dff[~dff['Grupo'].isin(grupos_a_excluir)]
        if categorias_a_excluir: dff = dff[~dff['Categoria'].isin(categorias_a_excluir)]
        if produtos_codigos_a_excluir: dff = dff[~dff['Código'].astype(str).isin(produtos_codigos_a_excluir)]

        dff_filtrado_interativo = dff.copy()
        if categoria_selecionada: dff_filtrado_interativo = dff_filtrado_interativo[dff_filtrado_interativo['Categoria'] == categoria_selecionada]
        if grupo_selecionado: dff_filtrado_interativo = dff_filtrado_interativo[dff_filtrado_interativo['Grupo'] == grupo_selecionado]
        if nome_produto_filtrado and nome_produto_filtrado.strip() != "": dff_filtrado_interativo = dff_filtrado_interativo[dff_filtrado_interativo['Produto'].str.contains(nome_produto_filtrado, case=False, na=False)]

        config_niveis = carregar_definicoes_niveis_estoque()
        limite_baixo_atual = config_niveis.get("limite_estoque_baixo", 10)
        limite_medio_atual = config_niveis.get("limite_estoque_medio", 100)

        df_estoque_realmente_baixo = identificar_produtos_estoque_baixo(dff_filtrado_interativo, limite_baixo_atual)
        tabela_estoque_baixo_componente = criar_tabela_produtos_criticos(
            df_estoque_realmente_baixo,
            id_tabela='tabela-alerta-estoque-baixo-geral-cb',
            titulo_alerta=f"Alerta: Estoque Baixo (≤ {limite_baixo_atual:g})",
            page_size=len(df_estoque_realmente_baixo) if not df_estoque_realmente_baixo.empty else 1,
            altura_tabela='320px'
        )

        fig_categorias_estoque_baixo_geral = criar_grafico_categorias_com_estoque_baixo(df_estoque_realmente_baixo)

        df_agrupado_para_grafico_principal = pd.DataFrame() 
        if not dff_filtrado_interativo.empty:
            df_grupo_sum = dff_filtrado_interativo.copy()
            df_grupo_sum['Estoque'] = pd.to_numeric(df_grupo_sum['Estoque'], errors='coerce').fillna(0)
            df_agrupado_para_grafico_principal = df_grupo_sum.groupby('Grupo', as_index=False)['Estoque'].sum()
            df_agrupado_para_grafico_principal = df_agrupado_para_grafico_principal[df_agrupado_para_grafico_principal['Estoque'] > 0]
        fig_estoque_grupo = criar_grafico_estoque_por_grupo(df_agrupado_para_grafico_principal) 
        fig_colunas_resumo = criar_grafico_colunas_estoque_por_grupo(dff_filtrado_interativo)


        if not dff_filtrado_interativo.empty:
            total_skus_filtrado = dff_filtrado_interativo['Código'].nunique()
            qtd_total_estoque_filtrado = pd.to_numeric(dff_filtrado_interativo['Estoque'], errors='coerce').fillna(0).sum()
            num_categorias_filtradas = dff_filtrado_interativo['Categoria'].nunique()
            num_grupos_filtrados = dff_filtrado_interativo['Grupo'].nunique()
            dados_tabela_filtrada = dff_filtrado_interativo.to_dict('records')

            fig_top_n = criar_grafico_top_n_produtos_estoque(dff_filtrado_interativo, n=7)
            fig_niveis = criar_grafico_niveis_estoque(dff_filtrado_interativo, limite_baixo_atual, limite_medio_atual)
            fig_populares = criar_grafico_estoque_produtos_populares(dff_filtrado_interativo, n=7)
        else:
            total_skus_filtrado, qtd_total_estoque_filtrado, num_categorias_filtradas, num_grupos_filtrados = 0,0,0,0
            dados_tabela_filtrada = []
            if df_agrupado_para_grafico_principal.empty: fig_estoque_grupo = fig_vazia_grupo
            fig_top_n = criar_figura_vazia(f"Top 7 Produtos (Sem dados com filtros atuais)")
            fig_niveis = criar_figura_vazia("Níveis de Estoque (Sem dados com filtros atuais)")
            fig_populares = criar_figura_vazia("Estoque dos Produtos Populares (Sem dados com filtros atuais)")
            if df_estoque_realmente_baixo.empty: fig_categorias_estoque_baixo_geral = fig_vazia_cat_baixo_geral
            fig_colunas_resumo = fig_vazia_colunas_resumo


        colunas_desejadas = ['Código', 'Produto', 'Un', 'Estoque', 'Categoria', 'Grupo']
        colunas_base = dff_filtrado_interativo.columns if not dff_filtrado_interativo.empty else df_global_original.columns
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
            fig_colunas_resumo,
            #dados_tabela_filtrada,
            #colunas_para_dash_filtradas,
            fig_estoque_grupo,
            tabela_estoque_baixo_componente,
            fig_top_n,
            fig_niveis,
            fig_populares,
            fig_categorias_estoque_baixo_geral
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
    
    @app.callback(
        Output("download-tabela-geral-excel", "data"),
        Input("btn-exportar-tabela-geral", "n_clicks"),
        State("tabela-estoque", "data"),
        prevent_initial_call=True
    )
    def exportar_tabela_principal_excel(n_clicks, dados_tabela_atual):
        if n_clicks is None or not dados_tabela_atual:
            return no_update 

        df_para_exportar = pd.DataFrame(dados_tabela_atual)
        
        colunas_export = ['Código', 'Produto', 'Un', 'Estoque', 'Categoria', 'Grupo', 'VendaMensal'] 
        colunas_presentes_para_export = [col for col in colunas_export if col in df_para_exportar.columns]
        df_para_exportar = df_para_exportar[colunas_presentes_para_export]

        return dcc.send_data_frame(df_para_exportar.to_excel, "estoque_filtrado.xlsx", sheet_name="Estoque", index=False)

    @app.callback(
        [Output("modal-grafico-donut-popup", "is_open"),
         Output("grafico-donut-modal", "figure")],
        [Input("card-clicavel-grafico-donut", "n_clicks"), 
         Input("btn-fechar-modal-donut", "n_clicks")],
        [State("modal-grafico-donut-popup", "is_open"),
         State('dropdown-categoria-filtro', 'value'), 
         State('dropdown-grupo-filtro', 'value'),
         State('input-nome-produto-filtro', 'value')],
        prevent_initial_call=True
    )
    def toggle_e_atualizar_modal_grafico_donut(n_clicks_abrir_card, n_clicks_fechar, is_open_atual,
                                               categoria_sel, grupo_sel, nome_prod_sel):
        
        ctx = dash.callback_context
        triggered_id = ctx.triggered_id if ctx.triggered_id else None
        
        figura_modal = no_update 
        abrir_modal_agora = is_open_atual

        if triggered_id == "card-clicavel-grafico-donut":
            abrir_modal_agora = not is_open_atual 
            if abrir_modal_agora:
                if df_global_original is not None and not df_global_original.empty:
                    dff = df_global_original.copy()
                    
                    config_exclusao = carregar_configuracoes_exclusao()
                    grupos_a_excluir = config_exclusao.get("excluir_grupos", [])
                    categorias_a_excluir = config_exclusao.get("excluir_categorias", [])
                    produtos_codigos_a_excluir = [str(p) for p in config_exclusao.get("excluir_produtos_codigos", [])]

                    if grupos_a_excluir: dff = dff[~dff['Grupo'].isin(grupos_a_excluir)]
                    if categorias_a_excluir: dff = dff[~dff['Categoria'].isin(categorias_a_excluir)]
                    if produtos_codigos_a_excluir: dff = dff[~dff['Código'].astype(str).isin(produtos_codigos_a_excluir)]
                    
                    if categoria_sel: dff = dff[dff['Categoria'] == categoria_sel]
                    if grupo_sel: dff = dff[dff['Grupo'] == grupo_sel]
                    if nome_prod_sel and nome_prod_sel.strip() != "": 
                        dff = dff[dff['Produto'].str.contains(nome_prod_sel, case=False, na=False)]
                    
                    figura_modal = criar_grafico_top_n_produtos_estoque(dff, n=7, height=600) 
                else:
                    figura_modal = criar_figura_vazia("Top 7 Produtos (Sem dados)")
                    figura_modal.update_layout(height=600)
            
        elif triggered_id == "btn-fechar-modal-donut":
            abrir_modal_agora = False 
        
        return abrir_modal_agora, figura_modal
    
    @app.callback(
        [Output("modal-grafico-niveis-popup", "is_open"),
         Output("grafico-niveis-modal", "figure")],
        [Input("card-clicavel-grafico-niveis", "n_clicks"),
         Input("btn-fechar-modal-niveis", "n_clicks")],
        [State("modal-grafico-niveis-popup", "is_open"),
         State('dropdown-categoria-filtro', 'value'),       
         State('dropdown-grupo-filtro', 'value'),          
         State('input-nome-produto-filtro', 'value'),     
         State('span-config-atual-limite-baixo', 'children'),
         State('span-config-atual-limite-medio', 'children')],
        prevent_initial_call=True
    )
    def toggle_e_atualizar_modal_grafico_niveis(
        n_clicks_abrir_card, n_clicks_fechar, is_open_atual,
        categoria_sel, grupo_sel, nome_prod_sel, 
        limite_baixo_str, limite_medio_str      
    ):
        ctx = dash.callback_context
        
        triggered_component_id = None
        if ctx.triggered:
            triggered_prop_id = ctx.triggered[0]['prop_id']
            triggered_component_id = triggered_prop_id.split('.')[0]

        figura_modal = no_update
        abrir_modal_agora = is_open_atual

        if triggered_component_id == "card-clicavel-grafico-niveis":
            abrir_modal_agora = not is_open_atual
            if abrir_modal_agora: 
                if df_global_original is not None and not df_global_original.empty:
                    dff_modal = df_global_original.copy()

                    config_exclusao = carregar_configuracoes_exclusao()
                    grupos_a_excluir = config_exclusao.get("excluir_grupos", [])
                    categorias_a_excluir = config_exclusao.get("excluir_categorias", [])
                    produtos_codigos_a_excluir = [str(p) for p in config_exclusao.get("excluir_produtos_codigos", [])]

                    if grupos_a_excluir:
                        dff_modal = dff_modal[~dff_modal['Grupo'].isin(grupos_a_excluir)]
                    if categorias_a_excluir:
                        dff_modal = dff_modal[~dff_modal['Categoria'].isin(categorias_a_excluir)]
                    if produtos_codigos_a_excluir:
                        dff_modal = dff_modal[~dff_modal['Código'].astype(str).isin(produtos_codigos_a_excluir)]

                    if categoria_sel:
                        dff_modal = dff_modal[dff_modal['Categoria'] == categoria_sel]
                    if grupo_sel:
                        dff_modal = dff_modal[dff_modal['Grupo'] == grupo_sel]
                    if nome_prod_sel and nome_prod_sel.strip() != "":
                        dff_modal = dff_modal[dff_modal['Produto'].str.contains(nome_prod_sel, case=False, na=False)]
                    
                    config_niveis_atuais = carregar_definicoes_niveis_estoque()
                    limite_baixo_config = config_niveis_atuais.get("limite_estoque_baixo", 10)
                    limite_medio_config = config_niveis_atuais.get("limite_estoque_medio", 100)

                    try:
                        limite_baixo = float(limite_baixo_str) if limite_baixo_str and limite_baixo_str != "N/A" else limite_baixo_config
                    except (ValueError, TypeError):
                        limite_baixo = limite_baixo_config
                    
                    try:
                        limite_medio = float(limite_medio_str) if limite_medio_str and limite_medio_str != "N/A" else limite_medio_config
                    except (ValueError, TypeError):
                        limite_medio = limite_medio_config
                        
                    if not dff_modal.empty:
                        figura_modal = criar_grafico_niveis_estoque(dff_modal, limite_baixo, limite_medio, height=500)
                    else:
                        figura_modal = criar_figura_vazia("Produtos por Nível de Estoque (Sem dados com filtros atuais)", height=500)
                else:
                    figura_modal = criar_figura_vazia("Produtos por Nível de Estoque (Dados não carregados)", height=500)

        elif triggered_component_id == "btn-fechar-modal-niveis":
            abrir_modal_agora = False
        
        return abrir_modal_agora, figura_modal
    
    @app.callback(
        Output('tabela-detalhes-nivel-estoque-modal-container', 'children'),
        [Input('grafico-niveis-modal', 'clickData')],
        [State("modal-grafico-niveis-popup", "is_open"),
         State('dropdown-categoria-filtro', 'value'),
         State('dropdown-grupo-filtro', 'value'),
         State('input-nome-produto-filtro', 'value'),
         State('span-config-atual-limite-baixo', 'children'), 
         State('span-config-atual-limite-medio', 'children')]
    )
    def atualizar_tabela_detalhes_nivel_estoque(click_data, modal_is_open,
                                                categoria_sel, grupo_sel, nome_prod_sel,
                                                limite_baixo_str, limite_medio_str):
        '''
        Atualiza a tabela de detalhes no modal de níveis de estoque.
        A tabela mostra os produtos correspondentes ao nível de estoque (barra) clicado no gráfico,
        baseando-se na primeira palavra da label da barra e considerando os filtros globais.
        '''
        if not modal_is_open or not click_data or not click_data['points']:
            return dbc.Alert("Clique em uma barra do gráfico acima para ver os produtos detalhados.", 
                             color="info", className="text-center text-muted mt-3")

        config_niveis_atuais = carregar_definicoes_niveis_estoque()
        limite_baixo_default = config_niveis_atuais.get("limite_estoque_baixo", 10)
        limite_medio_default = config_niveis_atuais.get("limite_estoque_medio", 100)

        try:
            limite_baixo = float(limite_baixo_str) if limite_baixo_str and limite_baixo_str != "N/A" else limite_baixo_default
        except (ValueError, TypeError):
            limite_baixo = limite_baixo_default
        
        try:
            limite_medio = float(limite_medio_str) if limite_medio_str and limite_medio_str != "N/A" else limite_medio_default
        except (ValueError, TypeError):
            limite_medio = limite_medio_default

        if df_global_original is None or df_global_original.empty:
            return dbc.Alert("Os dados de estoque não estão disponíveis para gerar a tabela.", color="warning", className="mt-3")

        try:
            nivel_clicado_label_completa = click_data['points'][0]['x'] 
            primeira_palavra_label = nivel_clicado_label_completa.split()[0].lower()
        except (KeyError, IndexError, AttributeError):
            return dbc.Alert("Não foi possível identificar o nível de estoque clicado. Tente novamente.", color="danger", className="mt-3")

        dff = df_global_original.copy()

        config_exclusao = carregar_configuracoes_exclusao()
        grupos_a_excluir = config_exclusao.get("excluir_grupos", [])
        categorias_a_excluir = config_exclusao.get("excluir_categorias", [])
        produtos_codigos_a_excluir = [str(p) for p in config_exclusao.get("excluir_produtos_codigos", [])]

        if grupos_a_excluir: dff = dff[~dff['Grupo'].isin(grupos_a_excluir)]
        if categorias_a_excluir: dff = dff[~dff['Categoria'].isin(categorias_a_excluir)]
        if produtos_codigos_a_excluir: dff = dff[~dff['Código'].astype(str).isin(produtos_codigos_a_excluir)]

        if categoria_sel: dff = dff[dff['Categoria'] == categoria_sel]
        if grupo_sel: dff = dff[dff['Grupo'] == grupo_sel]
        if nome_prod_sel and nome_prod_sel.strip() != "":
            dff = dff[dff['Produto'].str.contains(nome_prod_sel, case=False, na=False)]
        
        dff['Estoque'] = pd.to_numeric(dff['Estoque'], errors='coerce')
        dff.dropna(subset=['Estoque'], inplace=True)

        df_nivel_selecionado = pd.DataFrame()
        titulo_tabela = "Produtos no Nível Selecionado"
        if primeira_palavra_label == "baixo":
            df_nivel_selecionado = dff[dff['Estoque'] <= limite_baixo]
            titulo_tabela = f"Produtos com Estoque Baixo (Estoque ≤ {limite_baixo:g})"
        elif primeira_palavra_label == "médio" or primeira_palavra_label == "medio": # Mantendo a variação para "medio" por segurança
            df_nivel_selecionado = dff[(dff['Estoque'] > limite_baixo) & (dff['Estoque'] <= limite_medio)]
            titulo_tabela = f"Produtos com Estoque Médio (Estoque > {limite_baixo:g} e ≤ {limite_medio:g})"
        elif primeira_palavra_label == "alto":
            df_nivel_selecionado = dff[dff['Estoque'] > limite_medio]
            titulo_tabela = f"Produtos com Estoque Alto (Estoque > {limite_medio:g})"
        else:
            return dbc.Alert(f"Nível de estoque com primeira palavra '{primeira_palavra_label}' (derivado de '{nivel_clicado_label_completa}') não reconhecido.", color="warning", className="mt-3")

        if df_nivel_selecionado.empty:
            nome_nivel_display = nivel_clicado_label_completa.split('(')[0].strip() if '(' in nivel_clicado_label_completa else primeira_palavra_label.capitalize()
            return dbc.Alert(f"Nenhum produto encontrado para o nível '{nome_nivel_display}' com os filtros atuais.", color="info", className="mt-3")

        tabela_componente = criar_tabela_estoque(
            df_nivel_selecionado, 
            id_tabela='tabela-produtos-detalhe-nivel-modal',
            page_size=7
        )
        
        return html.Div([
            html.H6(titulo_tabela, className="mb-2 text-center fw-bold"),
            tabela_componente
        ])
    
    @app.callback(
        Output("offcanvas-filtros-estoque-geral", "is_open"),
        Input("btn-toggle-painel-esquerdo", "n_clicks"), # Usando o ID do botão definido no layout
        State("offcanvas-filtros-estoque-geral", "is_open"),
        prevent_initial_call=True
    )
    def toggle_filtros_offcanvas(n_clicks_toggle, is_open_offcanvas):
        '''
        Abre ou fecha o Offcanvas de filtros na aba de Estoque Geral.
        '''
        if n_clicks_toggle:
            return not is_open_offcanvas
        return is_open_offcanvas # ou no_update
    


