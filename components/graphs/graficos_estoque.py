# components/graphs/graficos_estoque.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
# from plotly.subplots import make_subplots # Não estamos usando subplots nesta versão
# import math # Não estamos usando math nesta versão

# Margens padrão que estávamos usando e que você pode ajustar por gráfico
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
    Cria um gráfico de linhas com área preenchida e marcadores do volume de estoque por grupo,
    ordenado numericamente pelo prefixo do grupo, com linhas de grade horizontais.
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
        # Extrai a primeira sequência de dígitos do início da string 'Grupo'
        df_agrupado['OrdemNumerica'] = df_agrupado['Grupo'].str.extract(r'^(\d+)').astype(float)
        df_agrupado = df_agrupado.sort_values(by='OrdemNumerica', ascending=True)
    except Exception as e:
        # Se a extração ou conversão falhar, ordena alfabeticamente como fallback
        print(f"Aviso: Não foi possível ordenar grupos numericamente para o gráfico, usando ordem alfabética. Erro: {e}")
        df_agrupado = df_agrupado.sort_values(by='Grupo', ascending=True)
    
    fig = px.line(df_agrupado, 
                   x='Grupo', 
                   y='Estoque', 
                   markers=True, # "bolinhas"
                   title='Volume de Estoque por Grupo',
                   labels={'Estoque': 'Quantidade Total em Estoque', 'Grupo': 'Grupo'})
    
    # Definir cores para a linha e para a área de preenchimento
    cor_da_linha = 'rgba(0, 122, 204, 0.8)' # Um azul agradável
    cor_do_preenchimento = 'rgba(0, 122, 204, 0.2)' # Mesma cor, mais transparente

    fig.update_traces(
        line=dict(width=2.5, shape='spline', color=cor_da_linha), 
        marker=dict(size=8, symbol='circle', line=dict(width=1.5, color=cor_da_linha)), # Borda do marcador com a cor da linha
        fill='tozeroy',  # <<<--- ISTO PINTA A ÁREA ABAIXO DA LINHA ATÉ Y=0
        fillcolor=cor_do_preenchimento # <<<--- COR DA ÁREA PINTADA
    )
    
    fig.update_layout(
        title_x=0.5,
        xaxis_title="Grupos de Produto",
        yaxis_title="Quantidade Total em Estoque",
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(l=70, r=30, t=70, b=110), 
        xaxis_tickangle=-45,
        showlegend=False, # Não há múltiplas linhas para legendar aqui
        yaxis=dict(
            showgrid=True, # <<<--- MOSTRAR LINHAS DE GRADE HORIZONTAIS
            gridwidth=1, 
            gridcolor='rgba(230, 230, 230, 0.7)', # Cor sutil para a grade
            zeroline=True, # Mostrar a linha do eixo Y em zero
            zerolinewidth=1.5,
            zerolinecolor='rgba(200, 200, 200, 0.9)'
        ),
        xaxis=dict(
            showgrid=False # Linhas de grade verticais geralmente não são necessárias para este tipo
        )
    )
    return fig

def criar_grafico_top_n_produtos_estoque(df, n=7, height=None): # Adicionado parâmetro height
    """
    Cria um gráfico de Donut mostrando a proporção de estoque dos
    Top N produtos com maior quantidade em estoque.
    """
    if df.empty or 'Produto' not in df.columns or 'Estoque' not in df.columns:
        fig_vazia = criar_figura_vazia(f"Top {n} Produtos por Estoque (Sem Dados)")
        if height:
            fig_vazia.update_layout(height=height)
        return fig_vazia

    df_plot = df.copy()
    df_plot['Estoque'] = pd.to_numeric(df_plot['Estoque'], errors='coerce').fillna(0)
    df_com_estoque = df_plot[df_plot['Estoque'] > 0].copy()

    if df_com_estoque.empty:
        fig_vazia = criar_figura_vazia(f"Top {n} Produtos por Estoque (Sem Estoque > 0)")
        if height:
            fig_vazia.update_layout(height=height)
        return fig_vazia

    estoque_total_geral = df_com_estoque['Estoque'].sum()
    top_n_df = df_com_estoque.nlargest(n, 'Estoque')
    
    if top_n_df.empty:
        fig_vazia = criar_figura_vazia(f"Top {n} Produtos por Estoque (Nenhum produto no Top N)")
        if height:
            fig_vazia.update_layout(height=height)
        return fig_vazia

    estoque_top_n_soma = top_n_df['Estoque'].sum()
    estoque_outros = estoque_total_geral - estoque_top_n_soma
    data_para_pie = []
    for index, row in top_n_df.iterrows():
        data_para_pie.append({'NomeExibicao': str(row['Produto']), 'Estoque': row['Estoque']})
    if estoque_outros > 0.001: # Adicionar fatia "Outros" apenas se for significativa
        data_para_pie.append({'NomeExibicao': 'Outros Produtos', 'Estoque': estoque_outros})
    
    if not data_para_pie:
        fig_vazia = criar_figura_vazia(f"Top {n} Produtos por Estoque (Sem dados para gráfico)")
        if height:
            fig_vazia.update_layout(height=height)
        return fig_vazia
        
    df_pie = pd.DataFrame(data_para_pie)
        
    fig = px.pie(df_pie, 
                   values='Estoque', 
                   names='NomeExibicao', 
                   title=f'Participação dos Top {n} Produtos no Estoque (+ Outros)',
                   hole=.4,
                   labels={'Estoque': 'Quantidade em Estoque', 'NomeExibicao': 'Produto/Segmento'})
    
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        insidetextorientation='radial',
        pull=[0.05 if nome != 'Outros Produtos' else 0 for nome in df_pie['NomeExibicao']]
    )
    fig.update_layout(
        legend_title_text='Produtos',
        legend=dict(orientation="v", yanchor="top", y=0.85, xanchor="left", x=1.01), # Ajustado y da legenda
        title_x=0.5,
        paper_bgcolor='white', 
        plot_bgcolor='white',
        margin=dict(l=20, r=150, t=60, b=20), # Margem direita para legenda
        height=height # Aplicar altura se fornecida
    )
    return fig



def _classificar_nivel_estoque(estoque_val, limite_baixo, limite_medio):
    try:
        lim_b = float(limite_baixo)
        lim_m = float(limite_medio)
    except (ValueError, TypeError):
        return 'Desconhecido (Limites Inválidos)'
    if pd.isna(estoque_val):
        return 'Desconhecido' # Simplificado de 'Desconhecido (Estoque NaN)'
    try:
        val = float(estoque_val)
    except (ValueError, TypeError):
        return 'Desconhecido' # Simplificado de 'Desconhecido (Estoque Inválido)'

    if val <= lim_b:
        return f'Baixo (≤{lim_b:g})'
    elif val <= lim_m:
        return f'Médio ({lim_b:g} < E ≤ {lim_m:g})'
    else: 
        return f'Alto (>{lim_m:g})'

def criar_grafico_niveis_estoque(df, limite_baixo=10, limite_medio=100, height=None):
    if df.empty or 'Estoque' not in df.columns:
        fig_vazia = criar_figura_vazia("Produtos por Nível de Estoque")
        if height: 
            fig_vazia.update_layout(height=height)
        return fig_vazia

    df_plot = df.copy()
    df_plot['EstoqueNum'] = pd.to_numeric(df_plot['Estoque'], errors='coerce') 
    df_plot['NivelEstoque'] = df_plot['EstoqueNum'].apply(
        lambda x: _classificar_nivel_estoque(x, limite_baixo, limite_medio)
    )
    
    contagem_niveis = df_plot['NivelEstoque'].value_counts().reset_index()
    contagem_niveis.columns = ['NivelEstoque', 'Contagem']
    
    cat_baixo_label = f'Baixo (≤{float(limite_baixo):g})'
    cat_medio_label = f'Médio ({float(limite_baixo):g} < E ≤ {float(limite_medio):g})'
    cat_alto_label = f'Alto (>{float(limite_medio):g})'
    
    ordem_niveis_plot = [
        cat_baixo_label, 
        cat_medio_label, 
        cat_alto_label, 
        'Desconhecido', 
        'Desconhecido (Limites Inválidos)'
    ]
    
    niveis_presentes_dados = df_plot['NivelEstoque'].unique()
    ordem_final_para_plot = [nivel for nivel in ordem_niveis_plot if nivel in niveis_presentes_dados]

    contagem_niveis['NivelEstoque'] = pd.Categorical(
        contagem_niveis['NivelEstoque'], 
        categories=ordem_final_para_plot, 
        ordered=True
    )
    contagem_niveis = contagem_niveis.sort_values('NivelEstoque').dropna(subset=['NivelEstoque'])
    
    if contagem_niveis.empty or contagem_niveis['Contagem'].sum() == 0:
        fig_vazia = criar_figura_vazia("Níveis de Estoque (Sem Produtos para Classificar)")
        if height: # Aplicar altura à figura vazia também
            fig_vazia.update_layout(height=height)
        return fig_vazia

    mapa_cores = {
        cat_baixo_label: 'rgba(220, 53, 69, 0.8)',
        cat_medio_label: 'rgba(255, 193, 7, 0.8)', 
        cat_alto_label: 'rgba(25, 135, 84, 0.8)', 
        'Desconhecido': 'rgba(108, 117, 125, 0.8)',
        'Desconhecido (Limites Inválidos)': 'rgba(52, 58, 64, 0.8)'
    }

    fig = px.bar(contagem_niveis, 
                   x='NivelEstoque', 
                   y='Contagem', 
                   title='Produtos por Nível de Estoque',
                   labels={'Contagem': 'Nº de Produtos', 'NivelEstoque': 'Nível de Estoque'},
                   text_auto=True,
                   color='NivelEstoque',
                   color_discrete_map=mapa_cores)
    fig.update_traces(textposition='outside')
    fig.update_layout(
        showlegend=False, title_x=0.5, xaxis_title=None,
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=MARGENS_GRAFICO_PADRAO, # Usando uma de suas constantes de margem
        height=height # Aplicar altura se fornecida
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
                   title=f'Top {top_n} Categorias por Nº de Produtos em Estoque Baixo', # TÍTULO INTERNO
                   labels={'NumeroDeProdutosBaixos': 'Nº de Produtos Baixos', 'Categoria': 'Categoria'},
                   text_auto=True)
    fig.update_traces(textposition='outside')
    fig.update_layout(
        yaxis={'categoryorder':'total ascending', 'dtick': 1, 'ticksuffix': '  '}, 
        title_x=0.5,
        paper_bgcolor='white', # FUNDO BRANCO
        plot_bgcolor='white',  # FUNDO BRANCO
        margin=MARGENS_GRAFICO_HORIZONTAL # Margem para rótulos Y
    )
    return fig

def criar_grafico_estoque_produtos_populares(df, n=7):
    '''
    Cria um gráfico de barras agrupadas comparando Estoque Atual vs. Venda Mensal
    para os N produtos mais vendidos. O eixo X não mostra nomes de produtos.
    A legenda identifica "Vendas no Mês" (verde) e os produtos para suas barras de "Estoque Atual".
    O gráfico inclui linhas de grade horizontais.
    '''
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
    
    cores_estoque_palette = px.colors.qualitative.Plotly 

    for i, (idx, row) in enumerate(produtos_populares_df.iterrows()):
        fig.add_trace(go.Bar(
            name=str(row['Produto']),
            x=[str(row['Produto'])],
            y=[row['EstoqueNum']],
            text=[f"{row['EstoqueNum']:.0f}"],
            textposition='outside',
            marker_color=cores_estoque_palette[i % len(cores_estoque_palette)],
            offsetgroup=0
        ))

    fig.add_trace(go.Bar(
        name='Vendas no Mês',
        x=produtos_populares_df['Produto'].tolist(),
        y=produtos_populares_df['VendaMensalNum'].tolist(),
        text=[f"{v:.0f}" for v in produtos_populares_df['VendaMensalNum']],
        textposition='outside',
        marker_color='rgba(40, 167, 69, 0.9)',
        offsetgroup=1
    ))

    fig.update_layout(
        barmode='group',
        title_text=f'Estoque vs. Venda Mensal (Top {n} Produtos Populares)',
        title_x=0.5,
        xaxis_title=None,
        xaxis_showticklabels=False,
        yaxis_title="Quantidade",
        yaxis_showgrid=True,  # Adiciona linhas de grade horizontais
        yaxis_gridcolor='lightgray',  # Define a cor das linhas de grade
        paper_bgcolor='white',
        plot_bgcolor='white',
        legend_title_text='Legenda:',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="rgba(0,0,0,0.1)",
            borderwidth=1
        ),
        margin=dict(l=50, r=200, t=80, b=30)
    )
    return fig

def criar_grafico_colunas_estoque_por_grupo(df_filtrado):
    '''
    Cria um gráfico de TREEMAP mostrando o estoque total por grupo.
    Entrada: DataFrame filtrado com as colunas 'Grupo' e 'Estoque'.
    Saída: Figura do Plotly (Treemap).
    '''
    titulo_grafico = "Estoque por Grupo (Treemap)"
    nova_altura_grafico = 450 # Altura que definimos anteriormente

    if df_filtrado.empty or 'Grupo' not in df_filtrado.columns or 'Estoque' not in df_filtrado.columns:
        fig = px.treemap(title=f"{titulo_grafico} - Sem dados")
        fig.update_layout(
            height=nova_altura_grafico,
            margin=dict(t=50, b=5, l=5, r=5),
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="black"
        )
        return fig

    df_filtrado['Estoque'] = pd.to_numeric(df_filtrado['Estoque'], errors='coerce').fillna(0)
    df_para_treemap = df_filtrado[df_filtrado['Estoque'] > 0]

    if df_para_treemap.empty:
        fig = px.treemap(title=f"{titulo_grafico} - Sem dados positivos")
        fig.update_layout(
            height=nova_altura_grafico,
            margin=dict(t=50, b=5, l=5, r=5),
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="black"
        )
        return fig

    fig = px.treemap(
        df_para_treemap,
        path=[px.Constant("Todos os Grupos"), 'Grupo'],
        values='Estoque',
        title=titulo_grafico,
        color='Estoque',
        color_continuous_scale=px.colors.sequential.YlGn, # <--- ALTERAÇÃO AQUI
        custom_data=['Grupo', 'Estoque']
    )
    fig.update_traces(
        textinfo='label+value+percent root',
        hovertemplate='<b>%{customdata[0]}</b><br>Estoque: %{customdata[1]:,.0f}<extra></extra>',
        textposition='middle center',
        textfont=dict(
            family="Arial Black, sans-serif",
            size=11,
            color="black" # Mantido como preto, mas observe o contraste com a nova escala
        ),
        marker_line_width=1,
        marker_line_color='rgba(255,255,255,0.5)'
    )
    fig.update_layout(
        height=nova_altura_grafico,
        margin=dict(t=50, b=15, l=15, r=15),
        paper_bgcolor='rgba(0,0,0,0)',
        font_color="black",
        title_font_size=18,
        title_x=0.5
    )
    return fig