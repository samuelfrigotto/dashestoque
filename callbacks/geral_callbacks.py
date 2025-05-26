# callbacks/geral_callbacks.py
import pandas as pd
from dash import Input, Output, no_update, State, html, dcc # <<<--- ADICIONADO html, dcc
import dash_bootstrap_components as dbc
from app_instance import app 

# Importar funções de criação de gráficos
from components.graphs.graficos_estoque import (
    criar_grafico_estoque_por_grupo,
    criar_grafico_top_n_produtos_estoque,
    criar_grafico_niveis_estoque,
    criar_figura_vazia,
    criar_grafico_categorias_com_estoque_baixo 
)
# Importar funções do config_manager
from modules.config_manager import carregar_definicoes_niveis_estoque, salvar_definicoes_niveis_estoque
# Importar funções do inventory_manager
from modules.inventory_manager import identificar_produtos_estoque_baixo 
# IMPORTAR A FUNÇÃO DE CRIAR TABELA
from components.tables.table1 import criar_tabela_estoque # <<<--- ADICIONADO

def registrar_callbacks_gerais(df_global):
    """
    Registra todos os callbacks relacionados à aba principal e filtros.
    df_global: O DataFrame principal carregado (ex: df_visualizar_global).
    """

    # Callback principal da aba "Visão Geral" (atualizar_dashboard_filtrado)
    # (Este callback permanece o mesmo da sua última versão funcional)
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
         Input('span-config-atual-limite-medio', 'children')]
    )
    def atualizar_dashboard_filtrado(categoria_selecionada, grupo_selecionado, nome_produto_filtrado, 
                                     ignore_lim_b_span, ignore_lim_m_span):
        
        fig_vazia_grupo = criar_figura_vazia("Volume de Estoque por Grupo")
        fig_vazia_top_n = criar_figura_vazia("Top 7 Produtos")
        
        config_niveis = carregar_definicoes_niveis_estoque()
        limite_baixo_atual = config_niveis.get("limite_estoque_baixo", 10)
        limite_medio_atual = config_niveis.get("limite_estoque_medio", 100)
        fig_vazia_niveis = criar_figura_vazia("Produtos por Nível de Estoque")

        if df_global is None or df_global.empty:
            colunas_vazias = [{"name": col, "id": col} for col in ['Código', 'Produto', 'Un', 'Estoque', 'Categoria', 'Grupo']]
            return "0", "0", "0", "0", [], colunas_vazias, fig_vazia_grupo, fig_vazia_top_n, fig_vazia_niveis

        dff = df_global.copy()

        if categoria_selecionada:
            dff = dff[dff['Categoria'] == categoria_selecionada]
        if grupo_selecionado:
            dff = dff[dff['Grupo'] == grupo_selecionado]
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
            fig_niveis = criar_grafico_niveis_estoque(dff, limite_baixo_atual, limite_medio_atual)
        else:
            total_skus_filtrado, qtd_total_estoque_filtrado, num_categorias_filtradas, num_grupos_filtrados = 0,0,0,0
            dados_tabela_filtrada = []
            fig_estoque_grupo = criar_figura_vazia("Volume de Estoque por Grupo (Sem dados com filtros atuais)")
            fig_top_n = criar_figura_vazia(f"Top 7 Produtos (Sem dados com filtros atuais)")
            fig_niveis = criar_figura_vazia("Níveis de Estoque (Sem dados com filtros atuais)")
            
        colunas_desejadas = ['Código', 'Produto', 'Un', 'Estoque', 'Categoria', 'Grupo']
        colunas_base = dff.columns if not dff.empty else df_global.columns
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

    # Callbacks de reset de filtros (permanecem os mesmos)
    @app.callback(
        Output('dropdown-grupo-filtro', 'value', allow_duplicate=True),
        Input('dropdown-categoria-filtro', 'value'),
        prevent_initial_call=True
    )
    def resetar_filtro_grupo(categoria_selecionada):
        if categoria_selecionada is not None:
            return None
        return no_update

    @app.callback(
        Output('dropdown-categoria-filtro', 'value', allow_duplicate=True),
        Input('dropdown-grupo-filtro', 'value'),
        prevent_initial_call=True
    )
    def resetar_filtro_categoria(grupo_selecionado):
        if grupo_selecionado is not None:
            return None
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
    
    # Callback para salvar as definições de níveis de estoque (permanece o mesmo)
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
        if n_clicks is None:
            return no_update, no_update, no_update, no_update, no_update

        if limite_baixo_input is None or limite_medio_input is None:
            mensagem = dbc.Alert("Ambos os limites devem ser preenchidos.", color="danger", dismissable=True, duration=7000)
            return mensagem, no_update, no_update, no_update, no_update

        sucesso, msg_retorno_salvar = salvar_definicoes_niveis_estoque(limite_baixo_input, limite_medio_input)
        
        cor_alerta = "success" if sucesso else "danger"
        status_mensagem_componente = dbc.Alert(msg_retorno_salvar, color=cor_alerta, dismissable=True, duration=7000)
        
        config_recarregada = carregar_definicoes_niveis_estoque()
        val_baixo_recarregado = config_recarregada.get("limite_estoque_baixo")
        val_medio_recarregado = config_recarregada.get("limite_estoque_medio")
        
        return (
            status_mensagem_componente, 
            str(val_baixo_recarregado), 
            str(val_medio_recarregado),
            val_baixo_recarregado,
            val_medio_recarregado
        )

    # NOVO CALLBACK para popular a aba de Estoque Baixo
    @app.callback(
        Output('conteudo-dinamico-aba-estoque-baixo', 'children'),
        [Input('span-config-atual-limite-baixo', 'children'), # Gatilho quando o limite baixo salvo muda
         Input('abas-principais', 'active_tab')] # Gatilho quando a aba é selecionada
    )
    def atualizar_conteudo_aba_estoque_baixo(limite_baixo_salvo_str, aba_ativa):
        if aba_ativa != "tab-estoque-baixo" or df_global is None or df_global.empty:
            return "" 

        config_niveis = carregar_definicoes_niveis_estoque()
        try:
            # O valor vem do span, que já foi convertido para string pelo callback salvar_configuracoes_niveis
            # A função carregar_definicoes_niveis_estoque retorna int/float para os limites
            limite_baixo = config_niveis.get("limite_estoque_baixo") 
            if limite_baixo is None: # Fallback adicional
                return dbc.Alert("Configuração de limite de estoque baixo não encontrada.", color="warning")
            limite_baixo = float(limite_baixo) # Garante que é float para a função de identificação
        except (ValueError, TypeError) as e:
            print(f"Erro ao converter limite baixo: {e}, valor string: {limite_baixo_salvo_str}")
            return dbc.Alert(f"Configuração de limite de estoque baixo inválida: '{limite_baixo_salvo_str}'.", color="danger")

        df_produtos_baixos = identificar_produtos_estoque_baixo(df_global, limite_baixo)

        if df_produtos_baixos.empty:
            return dbc.Alert(f"Nenhum produto encontrado com estoque baixo (Estoque ≤ {limite_baixo:g}).", color="info", className="mt-3")

        grafico = dcc.Graph( # <<<--- USA dcc
            id='grafico-categorias-estoque-baixo-tab',
            figure=criar_grafico_categorias_com_estoque_baixo(df_produtos_baixos)
        )

        tabela = criar_tabela_estoque( # <<<--- USA criar_tabela_estoque
            df_produtos_baixos, 
            id_tabela='tabela-produtos-estoque-baixo-tab',
            page_size=10
        )

        return html.Div([ # <<<--- USA html
            html.P(f"Encontrados {len(df_produtos_baixos)} produto(s) com estoque baixo (Estoque ≤ {limite_baixo:g}).", className="mt-3"),
            dbc.Row([
                dbc.Col(dbc.Card(grafico), width=12, className="mb-3")
            ]),
            html.Hr(),
            tabela
        ])