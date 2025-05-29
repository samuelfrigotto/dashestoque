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
)
from components.tables.table1 import criar_tabela_estoque, criar_tabela_produtos_criticos
from modules.config_manager import (
    carregar_definicoes_niveis_estoque, salvar_definicoes_niveis_estoque,
    carregar_configuracoes_exclusao, salvar_configuracoes_exclusao
)
from modules.inventory_manager import identificar_produtos_estoque_baixo, identificar_produtos_em_falta

def registrar_callbacks_gerais(df_global_original):
    # callbacks/geral_callbacks.py
# ... (Suas importações existentes: pd, Input, Output, etc., app, funções de gráfico, 
#      funções de tabela, config_manager, inventory_manager)
# Certifique-se que criar_grafico_categorias_com_estoque_baixo está importada de components.graphs.graficos_estoque
# e identificar_produtos_estoque_baixo de modules.inventory_manager

# Dentro da função registrar_callbacks_gerais(df_global_original):

    @app.callback(
        [Output('card-total-skus', 'children'),
         Output('card-qtd-total-estoque', 'children'),
         Output('card-num-categorias', 'children'),
         Output('card-num-grupos', 'children'),
         Output('tabela-estoque', 'data'),
         Output('tabela-estoque', 'columns'),
         Output('grafico-estoque-grupo', 'figure'),
         Output('container-tabela-alerta-estoque-baixo-geral', 'children'), # Tabela de alerta (estoque baixo)
         Output('grafico-top-n-produtos', 'figure'),
         Output('grafico-niveis-estoque', 'figure'),
         Output('grafico-estoque-populares', 'figure'),
         Output('grafico-categorias-estoque-baixo-visao-geral', 'figure')], # <<< NOVO OUTPUT
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
        
        # Figuras vazias para todos os gráficos
        fig_vazia_grupo = criar_figura_vazia("Volume de Estoque por Grupo")
        tabela_alerta_vazia = criar_tabela_produtos_criticos(pd.DataFrame(columns=['Produto', 'Estoque']), 'tabela-alerta-vazia-geral-cb-placeholder', "Produtos com Estoque Baixo", page_size=10, altura_tabela='250px')
        fig_vazia_top_n = criar_figura_vazia("Top 7 Produtos")
        fig_vazia_niveis = criar_figura_vazia("Produtos por Nível de Estoque")
        fig_vazia_populares = criar_figura_vazia("Estoque dos Produtos Populares")
        fig_vazia_cat_baixo_geral = criar_figura_vazia("Categorias com Estoque Baixo")

        if df_global_original is None or df_global_original.empty:
            colunas_vazias_principais = [{"name": col, "id": col} for col in ['Código', 'Produto', 'Un', 'Estoque', 'Categoria', 'Grupo']]
            return ("0", "0", "0", "0", [], colunas_vazias_principais, 
                    fig_vazia_grupo, tabela_alerta_vazia, 
                    fig_vazia_top_n, fig_vazia_niveis, fig_vazia_populares,
                    fig_vazia_cat_baixo_geral)

        # --- Lógica de Filtros (Exclusão e Interativos) ---
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

        # --- Carregar Limites ---
        config_niveis = carregar_definicoes_niveis_estoque()
        limite_baixo_atual = config_niveis.get("limite_estoque_baixo", 10)
        limite_medio_atual = config_niveis.get("limite_estoque_medio", 100)

        # --- Dados para Tabela de Alerta de Estoque Baixo (na Visão Geral) ---
        df_estoque_realmente_baixo = identificar_produtos_estoque_baixo(dff_filtrado_interativo, limite_baixo_atual)
        tabela_estoque_baixo_componente = criar_tabela_produtos_criticos(
            df_estoque_realmente_baixo,
            id_tabela='tabela-alerta-estoque-baixo-geral-cb', 
            titulo_alerta=f"Alerta: Estoque Baixo (≤ {limite_baixo_atual:g})",
            page_size=len(df_estoque_realmente_baixo) if not df_estoque_realmente_baixo.empty else 1,
            altura_tabela='400px' # <<<--- AJUSTE A ALTURA AQUI (era 350px, mudei para 400px)
        )
        
        # --- Gerar o Gráfico: Categorias com Estoque Baixo ---
        # Usa o mesmo df_estoque_realmente_baixo
        fig_categorias_estoque_baixo_geral = criar_grafico_categorias_com_estoque_baixo(df_estoque_realmente_baixo)
        
        # --- Outros Gráficos e Dados para Tabela Principal ---
        df_agrupado_para_grafico = pd.DataFrame()
        if not dff_filtrado_interativo.empty:
            df_grupo_sum = dff_filtrado_interativo.copy()
            df_grupo_sum['Estoque'] = pd.to_numeric(df_grupo_sum['Estoque'], errors='coerce').fillna(0)
            df_agrupado_para_grafico = df_grupo_sum.groupby('Grupo', as_index=False)['Estoque'].sum()
            df_agrupado_para_grafico = df_agrupado_para_grafico[df_agrupado_para_grafico['Estoque'] > 0]
        fig_estoque_grupo = criar_grafico_estoque_por_grupo(df_agrupado_para_grafico)

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
            if df_agrupado_para_grafico.empty: fig_estoque_grupo = fig_vazia_grupo
            fig_top_n = criar_figura_vazia(f"Top 7 Produtos (Sem dados com filtros atuais)")
            fig_niveis = criar_figura_vazia("Níveis de Estoque (Sem dados com filtros atuais)")
            fig_populares = criar_figura_vazia("Estoque dos Produtos Populares (Sem dados com filtros atuais)")
            if df_estoque_realmente_baixo.empty: fig_categorias_estoque_baixo_geral = fig_vazia_cat_baixo_geral
            
        # ... (lógica das colunas da tabela principal como antes) ...
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
            dados_tabela_filtrada,
            colunas_para_dash_filtradas,
            fig_estoque_grupo,
            tabela_estoque_baixo_componente, # Tabela de alerta (já estava)
            fig_top_n,
            fig_niveis,
            fig_populares,
            fig_categorias_estoque_baixo_geral # <<< RETORNA A FIGURA DO NOVO GRÁFICO
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
        State("tabela-estoque", "data"), # Pega os dados ATUAIS da tabela (já filtrados)
        prevent_initial_call=True
    )
    def exportar_tabela_principal_excel(n_clicks, dados_tabela_atual):
        if n_clicks is None or not dados_tabela_atual:
            return no_update # Ou levante um PreventUpdate

        # Os dados_tabela_atual já estão no formato de lista de dicionários
        df_para_exportar = pd.DataFrame(dados_tabela_atual)
        
        # Selecionar e reordenar colunas para exportação, se necessário
        # (Opcional, se quiser que o Excel tenha colunas específicas ou ordem diferente)
        colunas_export = ['Código', 'Produto', 'Un', 'Estoque', 'Categoria', 'Grupo', 'VendaMensal'] # Incluindo VendaMensal se existir
        colunas_presentes_para_export = [col for col in colunas_export if col in df_para_exportar.columns]
        df_para_exportar = df_para_exportar[colunas_presentes_para_export]

        # Usar dcc.send_data_frame para facilitar a criação do arquivo Excel
        return dcc.send_data_frame(df_para_exportar.to_excel, "estoque_filtrado.xlsx", sheet_name="Estoque", index=False)

    @app.callback(
        [Output("collapse-painel-esquerdo", "is_open"),
         Output("coluna-painel-esquerdo", "lg"), # Ajusta a largura da coluna do painel
         Output("coluna-painel-esquerdo", "className"), # Para esconder completamente se necessário
         Output("coluna-conteudo-principal", "lg"), # Ajusta a largura da coluna de conteúdo
         Output("btn-toggle-painel-esquerdo", "children"),
         Output("btn-toggle-painel-esquerdo", "title")], # Mudar tooltip do botão
        [Input("btn-toggle-painel-esquerdo", "n_clicks")],
        [State("collapse-painel-esquerdo", "is_open")],
        prevent_initial_call=True
    )
    def toggle_painel_esquerdo(n_clicks, is_open):
        nova_classe_painel = "p-3 bg-light border-end" # Classe padrão quando visível
        
        if n_clicks:
            if is_open: # Se está aberto, vamos fechar
                novo_lg_painel = 0 # Ocupa 0 colunas no grid grande
                novo_lg_conteudo = 12 # Conteúdo principal ocupa tudo
                novo_children_botao = html.I(className="bi bi-layout-sidebar-inset-reverse")
                novo_tooltip_botao = "Mostrar Painel de Filtros e KPIs"
                # Adicionar d-none para realmente esconder em telas menores também se lg=0 não for suficiente
                # ou se quisermos remover o padding/borda quando escondido.
                # No entanto, dbc.Collapse já lida com o esconder. Ajustar lg é para redistribuir espaço.
                # Se usarmos d-none, o Collapse pode não animar corretamente.
                # Vamos focar em ajustar as larguras 'lg' e deixar o Collapse fazer o resto.
                # Para realmente esconder e não ocupar espaço no grid, precisamos de `className="d-none"`
                # e remover o `lg` ou setar para `None`.
                # Mas dbc.Collapse já faz o display:none. O ajuste de 'lg' é para o grid quando ele está visível
                # e para quando o outro se expande.

                # Quando escondido pelo Collapse, ele não ocupa espaço no grid.
                # Então, só precisamos mudar a largura da coluna de conteúdo.
                return not is_open, 3, nova_classe_painel, 12, novo_children_botao, novo_tooltip_botao

            else: # Se está fechado, vamos abrir
                novo_lg_painel = 3 # Volta para a largura original
                novo_lg_conteudo = 9 # Conteúdo principal volta para a largura original
                novo_children_botao = html.I(className="bi bi-layout-sidebar-inset")
                novo_tooltip_botao = "Ocultar Painel de Filtros e KPIs"
                return not is_open, novo_lg_painel, nova_classe_painel, novo_lg_conteudo, novo_children_botao, novo_tooltip_botao
        return no_update, no_update, no_update, no_update, no_update, no_update
    
    @app.callback(
        [Output("modal-grafico-donut-popup", "is_open"),
         Output("grafico-donut-modal", "figure")],
        [Input("card-clicavel-grafico-donut", "n_clicks"), # <<< Input agora é o card clicável
         Input("btn-fechar-modal-donut", "n_clicks")],
        [State("modal-grafico-donut-popup", "is_open"),
         State('dropdown-categoria-filtro', 'value'), # Filtros atuais
         State('dropdown-grupo-filtro', 'value'),
         State('input-nome-produto-filtro', 'value')],
        prevent_initial_call=True
    )
    def toggle_e_atualizar_modal_grafico_donut(n_clicks_abrir_card, n_clicks_fechar, is_open_atual,
                                               categoria_sel, grupo_sel, nome_prod_sel):
        
        ctx = dash.callback_context
        triggered_id = ctx.triggered_id if ctx.triggered_id else None # Pode ser None na primeira chamada após prevent_initial_call se não houver n_clicks=0
        
        figura_modal = no_update 
        abrir_modal_agora = is_open_atual # Mantém o estado se nenhum gatilho relevante

        if triggered_id == "card-clicavel-grafico-donut":
            abrir_modal_agora = not is_open_atual # Alterna o estado ao clicar no card
            if abrir_modal_agora: # Se for para abrir o modal
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
                    
                    # Usar uma altura maior para o gráfico no modal
                    figura_modal = criar_grafico_top_n_produtos_estoque(dff, n=7, height=600) 
                else:
                    figura_modal = criar_figura_vazia("Top 7 Produtos (Sem dados)")
                    figura_modal.update_layout(height=600) # Aplicar altura à figura vazia também
            # Se estiver fechando pelo card (clicando de novo), não precisa atualizar a figura
            
        elif triggered_id == "btn-fechar-modal-donut":
            abrir_modal_agora = False # Força o fechamento
            # Não precisa atualizar a figura ao fechar
        
        return abrir_modal_agora, figura_modal
    
    @app.callback(
        [Output("modal-grafico-niveis-popup", "is_open"),
         Output("grafico-niveis-modal", "figure")],
        [Input("card-clicavel-grafico-niveis", "n_clicks"),
         Input("btn-fechar-modal-niveis", "n_clicks")],
        [State("modal-grafico-niveis-popup", "is_open"),
         # Pegar os valores dos filtros para gerar o gráfico correto no modal
         State('dropdown-categoria-filtro', 'value'),
         State('dropdown-grupo-filtro', 'value'),
         State('input-nome-produto-filtro', 'value'),
         # Pegar os limites de estoque atuais das configurações (via spans)
         State('span-config-atual-limite-baixo', 'children'),
         State('span-config-atual-limite-medio', 'children')],
        prevent_initial_call=True
    )
    def toggle_e_atualizar_modal_grafico_niveis(
        n_clicks_abrir_card, n_clicks_fechar, is_open_atual,
        categoria_sel, grupo_sel, nome_prod_sel,
        limite_baixo_str, limite_medio_str # Recebe dos spans
    ):
        ctx = dash.callback_context # Lembre-se de ter 'import dash'
        triggered_id = ctx.triggered_id if ctx.triggered_id else None
        
        figura_modal = no_update
        abrir_modal_agora = is_open_atual

        if triggered_id == "card-clicavel-grafico-niveis":
            abrir_modal_agora = not is_open_atual
            if abrir_modal_agora: # Se for para abrir o modal
                if df_global_original is not None and not df_global_original.empty:
                    dff = df_global_original.copy()
                    
                    # Aplicar filtros de exclusão globais
                    config_exclusao = carregar_configuracoes_exclusao()
                    # ... (lógica de aplicar exclusões em dff como no callback principal) ...
                    grupos_a_excluir = config_exclusao.get("excluir_grupos", []); categorias_a_excluir = config_exclusao.get("excluir_categorias", []); produtos_codigos_a_excluir = [str(p) for p in config_exclusao.get("excluir_produtos_codigos", [])]
                    if grupos_a_excluir: dff = dff[~dff['Grupo'].isin(grupos_a_excluir)]
                    if categorias_a_excluir: dff = dff[~dff['Categoria'].isin(categorias_a_excluir)]
                    if produtos_codigos_a_excluir: dff = dff[~dff['Código'].astype(str).isin(produtos_codigos_a_excluir)]

                    # Aplicar filtros interativos da aba principal
                    if categoria_sel: dff = dff[dff['Categoria'] == categoria_sel]
                    if grupo_sel: dff = dff[dff['Grupo'] == grupo_sel]
                    if nome_prod_sel and nome_prod_sel.strip() != "": 
                        dff = dff[dff['Produto'].str.contains(nome_prod_sel, case=False, na=False)]
                    
                    # Carregar os limites de estoque atuais (já estão como string dos spans)
                    # Ou, melhor, carregar diretamente do config_manager para garantir os valores corretos
                    config_niveis_atuais = carregar_definicoes_niveis_estoque()
                    limite_baixo = config_niveis_atuais.get("limite_estoque_baixo", 10)
                    limite_medio = config_niveis_atuais.get("limite_estoque_medio", 100)

                    # Gerar o gráfico de Níveis com uma altura maior para o modal
                    figura_modal = criar_grafico_niveis_estoque(dff, limite_baixo, limite_medio, height=550) 
                else:
                    figura_modal = criar_figura_vazia("Produtos por Nível de Estoque (Sem dados)")
                    figura_modal.update_layout(height=550)
            
        elif triggered_id == "btn-fechar-modal-niveis":
            abrir_modal_agora = False
        
        return abrir_modal_agora, figura_modal
