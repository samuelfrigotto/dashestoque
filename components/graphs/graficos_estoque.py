import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots # IMPORTAR make_subplots
import math # Para cálculos de layout de subplots

def criar_figura_vazia(titulo="Sem dados para exibir"):
    """Cria uma figura Plotly vazia com um título."""
    fig = go.Figure()
    fig.update_layout(
        title_text=titulo,
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[
            {
                "text": titulo,
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 16}
            }
        ]
    )
    return fig

def criar_grafico_estoque_por_grupo(df):
    """Cria um gráfico de barras horizontais do volume de estoque por grupo."""
    if df.empty or 'Grupo' not in df.columns or 'Estoque' not in df.columns:
        return criar_figura_vazia("Volume de Estoque por Grupo (Sem Dados)")
    
    df_plot = df.copy()
    df_plot['Estoque'] = pd.to_numeric(df_plot['Estoque'], errors='coerce').fillna(0)
    
    df_agrupado = df_plot.groupby('Grupo', as_index=False)['Estoque'].sum()
    df_agrupado = df_agrupado[df_agrupado['Estoque'] > 0]
    if df_agrupado.empty:
        return criar_figura_vazia("Volume de Estoque por Grupo (Sem Estoque > 0)")

    df_agrupado = df_agrupado.sort_values(by='Estoque', ascending=True)
    
    fig = px.bar(df_agrupado, 
                   y='Grupo', 
                   x='Estoque', 
                   orientation='h', 
                   title='Volume de Estoque por Grupo',
                   labels={'Estoque': 'Quantidade Total em Estoque', 'Grupo': 'Grupo'},
                   text_auto=True)
    fig.update_layout(
        yaxis={'categoryorder':'total ascending', 'dtick': 1},
        title_x=0.5
    )
    return fig

def criar_grafico_top_n_produtos_estoque(df, n=7):
    """
    Cria um gráfico de Donut mostrando a proporção de estoque dos
    Top N produtos com maior quantidade em estoque.
    """
    if df.empty or 'Produto' not in df.columns or 'Estoque' not in df.columns:
        return criar_figura_vazia(f"Top {n} Produtos (Sem Dados)")

    df_plot = df.copy()
    df_plot['Estoque'] = pd.to_numeric(df_plot['Estoque'], errors='coerce').fillna(0)

    top_n = df_plot[df_plot['Estoque'] > 0].nlargest(n, 'Estoque')
    
    if top_n.empty:
        return criar_figura_vazia(f"Top {n} Produtos (Sem Estoque > 0 para exibir)")
        
    fig = px.pie(top_n, 
                   values='Estoque', 
                   names='Produto', 
                   title=f'Participação dos Top {n} Produtos no Estoque',
                   hole=.4, # Cria o efeito Donut
                   labels={'Estoque': 'Quantidade em Estoque', 'Produto': 'Produto'})
    
    # Configurações para texto e legenda
    fig.update_traces(
        textposition='inside', 
        textinfo='percent', # Mostrar apenas percentual dentro das fatias
        insidetextorientation='radial' # Orientação do texto dentro da fatia
    )
    fig.update_layout(
        legend_title_text='Produtos',
        legend=dict(
            orientation="v", # Legenda vertical
            yanchor="middle",  # Ancora no meio verticalmente
            y=0.5,           # Posição Y no meio do gráfico
            xanchor="left", # Ancora à esquerda da legenda
            x=1.01           # Posição X um pouco à direita do gráfico
        ),
        title_x=0.5, # Centraliza o título do gráfico
        # Você pode ajustar a altura do gráfico aqui se necessário, e.g., height=400
        # height=380 # Exemplo de altura
        margin=dict(l=20, r=20, t=60, b=20, pad=4) # Ajustar margens para dar espaço à legenda
    )
    return fig


def _classificar_nivel_estoque(estoque_val, limite_baixo, limite_medio):
    """
    Classifica um valor de estoque individual baseado nos limites fornecidos.
    """
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

def criar_grafico_niveis_estoque(df, limite_baixo=10, limite_medio=100): 
    """
    Cria um gráfico de barras da contagem de produtos por nível de estoque,
    usando limites configuráveis.
    """
    if df.empty or 'Estoque' not in df.columns:
        return criar_figura_vazia("Níveis de Estoque (Sem Dados)")

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
        'Desconhecido (Estoque NaN)', 
        'Desconhecido (Estoque Inválido)',
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
        return criar_figura_vazia("Níveis de Estoque (Sem Produtos para Classificar)")

    mapa_cores = {
        cat_baixo_label: 'rgba(255, 76, 76, 0.8)',
        cat_medio_label: 'rgba(255, 191, 0, 0.8)', 
        cat_alto_label: 'rgba(76, 175, 80, 0.8)', 
        'Desconhecido (Estoque NaN)': 'rgba(158, 158, 158, 0.8)',
        'Desconhecido (Estoque Inválido)': 'rgba(158, 158, 158, 0.8)',
        'Desconhecido (Limites Inválidos)': 'rgba(100, 100, 100, 0.8)'
    }

    fig = px.bar(contagem_niveis, 
                   x='NivelEstoque', 
                   y='Contagem', 
                   title='Produtos por Nível de Estoque',
                   labels={'Contagem': ' ', 'NivelEstoque': 'Nível de Estoque'},
                   text_auto=True,
                   color='NivelEstoque',
                   color_discrete_map=mapa_cores
                  )
    fig.update_layout(showlegend=False, title_x=0.5, xaxis_title=None)
    return fig



def criar_grafico_categorias_com_estoque_baixo(df_estoque_baixo, top_n=10):
    """
    Cria um gráfico de barras mostrando as Top N categorias com mais produtos em estoque baixo.
    df_estoque_baixo: DataFrame já filtrado contendo apenas produtos em estoque baixo.
    """
    if df_estoque_baixo is None or df_estoque_baixo.empty or 'Categoria' not in df_estoque_baixo.columns or 'Código' not in df_estoque_baixo.columns:
        return criar_figura_vazia(f"Categorias com Estoque Baixo (Sem Dados)")

    contagem_categorias = df_estoque_baixo.groupby('Categoria')['Código'].nunique().reset_index()
    contagem_categorias.rename(columns={'Código': 'NumeroDeProdutosBaixos'}, inplace=True)
    
    contagem_categorias_top_n = contagem_categorias.nlargest(top_n, 'NumeroDeProdutosBaixos')
    
    if contagem_categorias_top_n.empty:
        return criar_figura_vazia(f"Categorias com Estoque Baixo (Sem produtos baixos para exibir)")

    contagem_categorias_top_n = contagem_categorias_top_n.sort_values(by='NumeroDeProdutosBaixos', ascending=True)

    fig = px.bar(contagem_categorias_top_n,
                   y='Categoria',
                   x='NumeroDeProdutosBaixos',
                   orientation='h',
                   title=f'Top {top_n} Categorias por Nº de Produtos em Estoque Baixo',
                   labels={'NumeroDeProdutosBaixos': 'Nº de Produtos em Estoque Baixo', 'Categoria': 'Categoria'},
                   text_auto=True)
    fig.update_layout(yaxis={'categoryorder':'total ascending', 'dtick': 1}, title_x=0.5)
    return fig

def criar_grafico_estoque_produtos_populares(df, n=7):
    """
    Cria um gráfico de linhas comparando Estoque Atual vs. Venda Mensal
    para os N produtos mais vendidos (populares).
    A popularidade é baseada na coluna 'VendaMensal'.
    O eixo X são os Produtos, e há duas linhas (Estoque, VendaMensal).
    """
    if df is None or df.empty or 'Produto' not in df.columns or \
       'VendaMensal' not in df.columns or 'Estoque' not in df.columns:
        return criar_figura_vazia(f"Venda vs. Estoque dos Top {n} Produtos (Sem Dados)")

    df_plot = df.copy()
    # Usar nomes diferentes para as colunas numéricas para evitar conflito no melt se já existirem 'Quantidade' ou 'Metrica'
    df_plot['VendaMensalNum'] = pd.to_numeric(df_plot['VendaMensal'], errors='coerce').fillna(0)
    df_plot['EstoqueNum'] = pd.to_numeric(df_plot['Estoque'], errors='coerce').fillna(0)

    # Selecionar os top N produtos com base em 'VendaMensal'
    # Considerar apenas produtos com vendas > 0 para serem "populares"
    produtos_populares_df = df_plot[df_plot['VendaMensalNum'] > 0].nlargest(n, 'VendaMensalNum')
    
    if produtos_populares_df.empty:
        return criar_figura_vazia(f"Venda vs. Estoque dos Top {n} Produtos (Sem produtos com vendas)")

    # Preparar dados no formato longo para px.line
    # Renomear as métricas para a legenda ficar mais amigável
    df_melted = produtos_populares_df.melt(
        id_vars=['Produto'], 
        value_vars=['EstoqueNum', 'VendaMensalNum'], # Ordem aqui pode influenciar a ordem na legenda
        var_name='Metrica', 
        value_name='Quantidade'
    )
    
    # Renomear valores na coluna 'Metrica' para a legenda
    df_melted['Metrica'] = df_melted['Metrica'].replace({
        'EstoqueNum': 'Estoque Atual',
        'VendaMensalNum': 'Vendas no Mês'
    })
    
    # Ordenar os produtos no eixo X pela VendaMensal original (do mais vendido para o menos)
    ordem_produtos_eixo_x = produtos_populares_df.sort_values(by='VendaMensalNum', ascending=False)['Produto'].tolist()
    df_melted['Produto'] = pd.Categorical(df_melted['Produto'], categories=ordem_produtos_eixo_x, ordered=True)
    
    # Ordenar o DataFrame para garantir que as linhas sejam desenhadas corretamente
    df_melted.sort_values(by=['Produto', 'Metrica'], inplace=True)

    fig = px.line(df_melted,
                   x='Produto',         # Produtos no eixo X
                   y='Quantidade',      # Valores no eixo Y
                   color='Metrica',     # Cria uma linha para 'Estoque Atual' e uma para 'Vendas no Mês'
                   markers=True,        # Adiciona marcadores nos pontos
                   title=f'Venda Mensal vs. Estoque Atual (Top {n} Produtos Populares)',
                   labels={'Quantidade': 'Quantidade', 'Produto': 'Produtos Populares', 'Metrica': 'Métrica'},
                   color_discrete_map={ # Cores específicas para as linhas
                       'Vendas no Mês': 'rgba(40, 167, 69, 0.9)',  # Verde (success Bootstrap)
                       'Estoque Atual': 'rgba(23, 162, 184, 0.9)' # Azul/Ciano (info Bootstrap)
                   },
                   line_shape='spline' # Para linhas mais suaves (opcional)
                  )
    
    fig.update_layout(
        title_x=0.5, # Centraliza o título
        xaxis_title="Produtos Populares",
        yaxis_title="Quantidade",
        legend_title_text='Métrica:', # Título da Legenda
        legend=dict(
            orientation="h",    # Legenda horizontal
            yanchor="bottom",   # Ancorar na base da legenda
            y=1.02,             # Posicionar acima da área de plotagem
            xanchor="right",    # Ancorar à direita da legenda
            x=1                 # Posicionar à direita da área de plotagem
        ),
        xaxis_tickangle=-45 # Inclinar rótulos do eixo X se os nomes dos produtos forem longos
    )
    # Assegurar que os marcadores sejam visíveis e talvez com texto
    fig.update_traces(
        marker=dict(size=8), 
        # text=df_melted['Quantidade'], # Se quiser mostrar o valor no ponto (pode poluir)
        # textposition="top center"    # Posição do texto se habilitado
    )

    return fig

