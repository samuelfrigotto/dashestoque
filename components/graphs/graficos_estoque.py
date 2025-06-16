# components/graphs/graficos_estoque.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Paletas de Cores Laranja ---
# Para gráficos de pizza, rosca ou barras com múltiplas categorias discretas
ORANGE_PALETTE_DISCRETE = px.colors.sequential.YlOrBr
# Para gráficos que mostram uma escala contínua (ex: Treemap)
ORANGE_PALETTE_CONTINUOUS = px.colors.sequential.Oranges
# Cor principal para elementos únicos (linhas, barras únicas)
MAIN_ORANGE_COLOR_RGB = '255, 127, 42' # Cor principal em RGB para usar com 'rgba'

# --- Margens Padrão ---
MARGENS_GRAFICO_PADRAO = dict(l=40, r=20, t=70, b=50)
MARGENS_GRAFICO_HORIZONTAL = dict(l=120, r=20, t=70, b=40)
MARGENS_GRAFICO_COMPACTO = dict(l=20, r=20, t=40, b=20)

def criar_figura_vazia(titulo="Sem dados para exibir", height=None):
    fig = go.Figure()
    fig.update_layout(
        title_text=titulo,
        title_x=0.5,
        xaxis={"visible": False},
        yaxis={"visible": False},
        paper_bgcolor='white', 
        plot_bgcolor='white',
        margin=MARGENS_GRAFICO_COMPACTO,
        annotations=[{
            "text": titulo, "xref": "paper", "yref": "paper",
            "showarrow": False, "font": {"size": 16}
        }]
    )
    return fig

def criar_grafico_estoque_por_grupo(df):
    """
    Cria um gráfico de linhas com área preenchida do volume de estoque por grupo,
    em tons de laranja.
    """
    if df.empty or 'Grupo' not in df.columns or 'Estoque' not in df.columns:
        return criar_figura_vazia("Volume de Estoque por Grupo (Sem Dados)")
    
    df_plot = df.copy()
    df_plot['Estoque'] = pd.to_numeric(df_plot['Estoque'], errors='coerce').fillna(0)
    
    df_agrupado = df_plot.groupby('Grupo', as_index=False)['Estoque'].sum()
    df_agrupado = df_agrupado[df_agrupado['Estoque'] > 0] 
    
    if df_agrupado.empty:
        return criar_figura_vazia("Volume de Estoque por Grupo (Sem Estoque > 0)")

    try:
        df_agrupado['OrdemNumerica'] = df_agrupado['Grupo'].str.extract(r'^(\d+)').astype(float)
        df_agrupado = df_agrupado.sort_values(by='OrdemNumerica', ascending=True)
    except Exception as e:
        print(f"Aviso: Não foi possível ordenar grupos numericamente, usando ordem alfabética. Erro: {e}")
        df_agrupado = df_agrupado.sort_values(by='Grupo', ascending=True)
    
    fig = px.line(df_agrupado, 
                  x='Grupo', 
                  y='Estoque', 
                  markers=True,
                  title='Volume de Estoque por Grupo',
                  labels={'Estoque': 'Quantidade Total em Estoque', 'Grupo': 'Grupo'})
    
    # --- ALTERAÇÃO DE COR ---
    cor_da_linha = f'rgba({MAIN_ORANGE_COLOR_RGB}, 0.9)'
    cor_do_preenchimento = f'rgba({MAIN_ORANGE_COLOR_RGB}, 0.2)'

    fig.update_traces(
        line=dict(width=2.5, shape='spline', color=cor_da_linha), 
        marker=dict(size=8, symbol='circle', line=dict(width=1.5, color=cor_da_linha)),
        fill='tozeroy',
        fillcolor=cor_do_preenchimento
    )
    
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Grupos de Produto",
        yaxis_title="Quantidade Total em Estoque",
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(l=70, r=30, t=70, b=110), 
        xaxis_tickangle=-45,
        showlegend=False,
        yaxis=dict(
            showgrid=True,
            gridwidth=1, 
            gridcolor='rgba(230, 230, 230, 0.7)',
            zeroline=True,
            zerolinewidth=1.5,
            zerolinecolor='rgba(200, 200, 200, 0.9)'
        ),
        xaxis=dict(showgrid=False)
    )
    return fig

def criar_grafico_top_n_produtos_estoque(df, n=7, height=None):
    """
    Cria um gráfico de Donut mostrando a proporção de estoque dos Top N produtos,
    em tons de laranja.
    """
    if df.empty or 'Produto' not in df.columns or 'Estoque' not in df.columns:
        fig_vazia = criar_figura_vazia(f"Top {n} Produtos por Estoque (Sem Dados)")
        if height: fig_vazia.update_layout(height=height)
        return fig_vazia

    df_plot = df.copy()
    df_plot['Estoque'] = pd.to_numeric(df_plot['Estoque'], errors='coerce').fillna(0)
    df_com_estoque = df_plot[df_plot['Estoque'] > 0].copy()

    if df_com_estoque.empty:
        fig_vazia = criar_figura_vazia(f"Top {n} Produtos por Estoque (Sem Estoque > 0)")
        if height: fig_vazia.update_layout(height=height)
        return fig_vazia

    estoque_total_geral = df_com_estoque['Estoque'].sum()
    top_n_df = df_com_estoque.nlargest(n, 'Estoque')
    
    if top_n_df.empty:
        fig_vazia = criar_figura_vazia(f"Top {n} Produtos por Estoque (Nenhum produto no Top N)")
        if height: fig_vazia.update_layout(height=height)
        return fig_vazia

    estoque_top_n_soma = top_n_df['Estoque'].sum()
    estoque_outros = estoque_total_geral - estoque_top_n_soma
    data_para_pie = [{'NomeExibicao': str(row['Produto']), 'Estoque': row['Estoque']} for _, row in top_n_df.iterrows()]
    if estoque_outros > 0.001:
        data_para_pie.append({'NomeExibicao': 'Outros Produtos', 'Estoque': estoque_outros})
    
    if not data_para_pie:
        fig_vazia = criar_figura_vazia(f"Top {n} Produtos por Estoque (Sem dados para gráfico)")
        if height: fig_vazia.update_layout(height=height)
        return fig_vazia
        
    df_pie = pd.DataFrame(data_para_pie)
        
    fig = px.pie(df_pie, 
                 values='Estoque', 
                 names='NomeExibicao', 
                 title=f'Participação dos Top {n} Produtos no Estoque (+ Outros)',
                 hole=.4,
                 labels={'Estoque': 'Quantidade em Estoque', 'NomeExibicao': 'Produto/Segmento'},
                 # --- ALTERAÇÃO DE COR ---
                 color_discrete_sequence=px.colors.sequential.Oranges_r)
    
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        insidetextorientation='radial',
        pull=[0.05 if nome != 'Outros Produtos' else 0 for nome in df_pie['NomeExibicao']]
    )
    fig.update_layout(
        legend_title_text='Produtos',
        legend=dict(orientation="v", yanchor="top", y=0.85, xanchor="left", x=1.01),
        title_x=0.5,
        paper_bgcolor='white', 
        plot_bgcolor='white',
        margin=dict(l=20, r=150, t=60, b=20),
        height=height
    )
    return fig

def _classificar_nivel_estoque(estoque_val, limite_baixo, limite_medio):
    try:
        lim_b = float(limite_baixo)
        lim_m = float(limite_medio)
    except (ValueError, TypeError):
        return 'Desconhecido (Limites Inválidos)'
    if pd.isna(estoque_val):
        return 'Desconhecido'
    try:
        val = float(estoque_val)
    except (ValueError, TypeError):
        return 'Desconhecido'
    if val <= lim_b:
        return f'Baixo (≤{lim_b:g})'
    elif val <= lim_m:
        return f'Médio ({lim_b:g} < E ≤ {lim_m:g})'
    else: 
        return f'Alto (>{lim_m:g})'

def criar_grafico_niveis_estoque(df, limite_baixo=10, limite_medio=100, height=None):
    """
    Cria um gráfico de barras da contagem de produtos por nível de estoque,
    com uma paleta de cores laranja aprimorada para todas as categorias.
    """
    if df.empty or 'Estoque' not in df.columns:
        fig_vazia = criar_figura_vazia("Produtos por Nível de Estoque")
        if height: fig_vazia.update_layout(height=height)
        return fig_vazia

    df_plot = df.copy()
    df_plot['EstoqueNum'] = pd.to_numeric(df_plot['Estoque'], errors='coerce') 
    df_plot['NivelEstoque'] = df_plot['EstoqueNum'].apply(lambda x: _classificar_nivel_estoque(x, limite_baixo, limite_medio))
    
    contagem_niveis = df_plot['NivelEstoque'].value_counts().reset_index()
    contagem_niveis.columns = ['NivelEstoque', 'Contagem']
    
    cat_baixo_label = f'Baixo (≤{float(limite_baixo):g})'
    cat_medio_label = f'Médio ({float(limite_baixo):g} < E ≤ {float(limite_medio):g})'
    cat_alto_label = f'Alto (>{float(limite_medio):g})'
    
    # Ordem de exibição no gráfico (do mais importante para o menos)
    ordem_niveis_plot = [cat_alto_label, cat_medio_label, cat_baixo_label, 'Desconhecido', 'Desconhecido (Limites Inválidos)']
    
    niveis_presentes_dados = df_plot['NivelEstoque'].unique()
    ordem_final_para_plot = [nivel for nivel in ordem_niveis_plot if nivel in niveis_presentes_dados]

    contagem_niveis['NivelEstoque'] = pd.Categorical(contagem_niveis['NivelEstoque'], categories=ordem_final_para_plot, ordered=True)
    contagem_niveis = contagem_niveis.sort_values('NivelEstoque').dropna(subset=['NivelEstoque'])
    
    if contagem_niveis.empty or contagem_niveis['Contagem'].sum() == 0:
        fig_vazia = criar_figura_vazia("Níveis de Estoque (Sem Produtos para Classificar)")
        if height: fig_vazia.update_layout(height=height)
        return fig_vazia

    # --- COR DO BOTÃO ALTERADA ---
    # Ajustada a cor da categoria "Desconhecido" para um tom de laranja.
    mapa_cores = {
        cat_baixo_label: 'rgba(255, 87, 34, 0.8)',   # Laranja avermelhado (Deep Orange)
        cat_medio_label: 'rgba(251, 140, 0, 0.8)',  # Laranja
        cat_alto_label: 'rgba(255, 193, 7, 0.8)',   # Ambar (quase amarelo)
        'Desconhecido': 'rgba(245, 172, 123, 0.8)',  # Laranja claro/pêssego para "Desconhecido"
        'Desconhecido (Limites Inválidos)': 'rgba(205, 133, 63, 0.8)' # Laranja/marrom para erros
    }

    fig = px.bar(contagem_niveis, 
                 x='NivelEstoque', 
                 y='Contagem', 
                 title='Produtos por Nível de Estoque',
                 labels={'Contagem': 'Nº de Produtos', 'NivelEstoque': 'Nível de Estoque'},
                 color='NivelEstoque',
                 color_discrete_map=mapa_cores)
                 
    fig.update_traces(textposition='outside')
    fig.update_layout(
        showlegend=False, 
        title_x=0.5, 
        xaxis_title=None,
        yaxis_showgrid=True,
        yaxis_gridcolor='lightgray',
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=MARGENS_GRAFICO_PADRAO,
        height=height
    )
    return fig


def criar_grafico_categorias_com_estoque_baixo(df_estoque_baixo, top_n=10):
    if df_estoque_baixo is None or df_estoque_baixo.empty or 'Categoria' not in df_estoque_baixo.columns or 'Código' not in df_estoque_baixo.columns:
        return criar_figura_vazia(f"Categorias com Estoque Baixo (Sem Dados)")

    contagem_categorias = df_estoque_baixo.groupby('Categoria')['Código'].nunique().reset_index()
    contagem_categorias.rename(columns={'Código': 'NumeroDeProdutosBaixos'}, inplace=True)
    contagem_categorias_top_n = contagem_categorias.nlargest(top_n, 'NumeroDeProdutosBaixos')
    
    if contagem_categorias_top_n.empty:
        return criar_figura_vazia(f"Categorias com Estoque Baixo (Sem produtos baixos)")

    contagem_categorias_top_n = contagem_categorias_top_n.sort_values(by='NumeroDeProdutosBaixos', ascending=True)

    fig = px.bar(contagem_categorias_top_n,
                 y='Categoria',
                 x='NumeroDeProdutosBaixos',
                 orientation='h',
                 title=f'Top {top_n} Categorias por Nº de Produtos em Estoque Baixo',
                 labels={'NumeroDeProdutosBaixos': 'Nº de Produtos Baixos', 'Categoria': 'Categoria'},
                 color_discrete_sequence=[f'rgba({MAIN_ORANGE_COLOR_RGB}, 0.8)'])
    fig.update_traces(textposition='outside')
    fig.update_layout(
        yaxis={'categoryorder':'total ascending', 'dtick': 1, 'ticksuffix': '  '},
        xaxis_showgrid=True,
        xaxis_gridcolor='lightgray',
        title_x=0.5,
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=MARGENS_GRAFICO_HORIZONTAL
    )
    return fig

def criar_grafico_estoque_produtos_populares(df, n=7):
    if df is None or df.empty or 'Produto' not in df.columns or \
       'VendaMensal' not in df.columns or 'Estoque' not in df.columns:
        return criar_figura_vazia(f"Venda vs. Estoque dos Top {n} Produtos (Sem Dados)")

    df_plot = df.copy()
    df_plot['VendaMensalNum'] = pd.to_numeric(df_plot['VendaMensal'], errors='coerce').fillna(0)
    df_plot['EstoqueNum'] = pd.to_numeric(df_plot['Estoque'], errors='coerce').fillna(0)

    produtos_populares_df = df_plot[df_plot['VendaMensalNum'] > 0].nlargest(n, 'VendaMensalNum')
    
    if produtos_populares_df.empty:
        return criar_figura_vazia(f"Venda vs. Estoque dos Top {n} Produtos (Sem produtos com vendas)")

    produtos_populares_df = produtos_populares_df.sort_values(by='VendaMensalNum', ascending=False)
    
    fig = go.Figure()
    
    # --- ALTERAÇÃO DE COR ---
    # Usando paleta sequencial de laranja para as barras de estoque
    cores_estoque_palette = px.colors.sequential.Oranges_r # Reversa: mais vendido = laranja mais escuro
    cor_vendas = 'rgba(255, 87, 34, 0.9)' # Laranja avermelhado para vendas, para contraste

    for i, (idx, row) in enumerate(produtos_populares_df.iterrows()):
        fig.add_trace(go.Bar(
            name=str(row['Produto']),
            x=[str(row['Produto'])],
            y=[row['EstoqueNum']],
            textposition='outside',
            marker_color=cores_estoque_palette[i % len(cores_estoque_palette)],
            offsetgroup=0
        ))

    fig.add_trace(go.Bar(
        name='Vendas no Mês',
        x=produtos_populares_df['Produto'].tolist(),
        y=produtos_populares_df['VendaMensalNum'].tolist(),
        marker_color=cor_vendas,
        offsetgroup=1
    ))

    fig.update_layout(
        barmode='group',
        title_text=f'Estoque vs. Venda Mensal (Top {n} Produtos Populares)',
        title_x=0.5,
        xaxis_title=None,
        xaxis_showticklabels=False,
        yaxis_title="Quantidade",
        yaxis_showgrid=True,
        yaxis_gridcolor='lightgray',
        paper_bgcolor='white',
        plot_bgcolor='white',
        legend_title_text='Legenda:',
        legend=dict(
            orientation="v", yanchor="top", y=1,
            xanchor="left", x=1.02,
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1
        ),
        margin=dict(l=50, r=200, t=80, b=30)
    )
    return fig

def criar_grafico_colunas_estoque_por_grupo(df_filtrado):
    titulo_grafico = "Estoque por Grupo (Treemap)"
    nova_altura_grafico = 450

    if df_filtrado.empty or 'Grupo' not in df_filtrado.columns or 'Estoque' not in df_filtrado.columns:
        fig = px.treemap(title=f"{titulo_grafico} - Sem dados")
        fig.update_layout(height=nova_altura_grafico, margin=dict(t=50, b=5, l=5, r=5), paper_bgcolor='white', font_color="black")
        return fig

    df_filtrado['Estoque'] = pd.to_numeric(df_filtrado['Estoque'], errors='coerce').fillna(0)
    # Adicionado .copy() para evitar avisos do pandas
    df_para_treemap = df_filtrado[df_filtrado['Estoque'] > 0].copy()

    if df_para_treemap.empty:
        fig = px.treemap(title=f"{titulo_grafico} - Sem dados positivos")
        fig.update_layout(height=nova_altura_grafico, margin=dict(t=50, b=5, l=5, r=5), paper_bgcolor='white', font_color="black")
        return fig

    # --- ALTERAÇÃO PRINCIPAL AQUI ---
    # 1. Criamos uma nova coluna 'NomeGrupo' que remove o prefixo numérico.
    #    Ex: "005 BEBIDAS QUENTES" se torna "BEBIDAS QUENTES"
    df_para_treemap['NomeGrupo'] = df_para_treemap['Grupo'].str.replace(r'^\d+\s*', '', regex=True)

    fig = px.treemap(
        df_para_treemap,
        # 2. Usamos a nova coluna 'NomeGrupo' para criar os caminhos (rótulos) do gráfico.
        path=[px.Constant("Todos os Grupos"), 'NomeGrupo'],
        values='Estoque',
        title=titulo_grafico,
        color='Estoque',
        color_continuous_scale=ORANGE_PALETTE_CONTINUOUS,
        # 3. Atualizamos o custom_data para que o nome limpo apareça também ao passar o mouse.
        custom_data=['NomeGrupo', 'Estoque']
    )
    fig.update_traces(
        textinfo='label + percent root',
        # O hovertemplate agora usa o 'NomeGrupo' (customdata[0])
        hovertemplate='<b>%{customdata[0]}</b><br>Estoque: %{customdata[1]:,.0f}<extra></extra>',
        textposition='middle center',
        textfont=dict(family="Arial Black, sans-serif", size=11, color="black"),
        marker_line_width=1,
        marker_line_color='rgba(255,255,255,0.5)'
    )
    fig.update_layout(
        height=nova_altura_grafico,
        margin=dict(t=50, b=15, l=15, r=15),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font_color="black",
        title_font_size=18,
        title_x=0.5
    )
    return fig