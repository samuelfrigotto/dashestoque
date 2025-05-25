# components/graphs/graficos_estoque.py
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go # Para figuras vazias mais controladas

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
                "font": {
                    "size": 16
                }
            }
        ]
    )
    return fig

def criar_grafico_estoque_por_grupo(df):
    """Cria um gráfico de barras horizontais do volume de estoque por grupo."""
    if df.empty or 'Grupo' not in df.columns or 'Estoque' not in df.columns:
        return criar_figura_vazia("Volume de Estoque por Grupo (Sem Dados)")
    
    # Garantir que Estoque é numérico para a soma, tratando NaNs como 0
    df_plot = df.copy()
    df_plot['Estoque'] = pd.to_numeric(df_plot['Estoque'], errors='coerce').fillna(0)
    
    df_agrupado = df_plot.groupby('Grupo', as_index=False)['Estoque'].sum()
    # Filtrar grupos com estoque zero para não poluir o gráfico, a menos que não haja nenhum
    df_agrupado = df_agrupado[df_agrupado['Estoque'] > 0]
    if df_agrupado.empty:
        return criar_figura_vazia("Volume de Estoque por Grupo (Sem Estoque > 0)")

    df_agrupado = df_agrupado.sort_values(by='Estoque', ascending=True) # Para barras horizontais, ascendente faz o maior ficar no topo
    
    fig = px.bar(df_agrupado, 
                   y='Grupo', 
                   x='Estoque', 
                   orientation='h', 
                   title='Volume de Estoque por Grupo',
                   labels={'Estoque': 'Quantidade Total em Estoque', 'Grupo': 'Grupo'},
                   text_auto=True)
    fig.update_layout(
        yaxis={'categoryorder':'total ascending', 'dtick': 1}, # Garante que todos os nomes de grupo apareçam se forem muitos
        title_x=0.5 # Centraliza o título
    )
    return fig

def criar_grafico_top_n_produtos_estoque(df, n=7):
    """Cria um gráfico de barras verticais dos top N produtos com maior estoque."""
    if df.empty or 'Produto' not in df.columns or 'Estoque' not in df.columns:
        return criar_figura_vazia(f"Top {n} Produtos (Sem Dados)")

    df_plot = df.copy()
    df_plot['Estoque'] = pd.to_numeric(df_plot['Estoque'], errors='coerce').fillna(0)

    top_n = df_plot.nlargest(n, 'Estoque')
    top_n = top_n[top_n['Estoque'] > 0] # Mostrar apenas se tiver estoque
    if top_n.empty:
        return criar_figura_vazia(f"Top {n} Produtos (Sem Estoque > 0)")
        
    fig = px.bar(top_n, 
                   x='Produto', 
                   y='Estoque', 
                   title=f'Top {n} Produtos com Maior Estoque',
                   labels={'Estoque': 'Quantidade em Estoque', 'Produto': 'Produto'},
                   text_auto=True,
                   color='Produto') # Adiciona cores diferentes por produto
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False, # Legenda não é tão útil aqui se as cores são apenas para distinção
        title_x=0.5
    )
    return fig

def _classificar_nivel_estoque(estoque_val):
    """Classifica um valor de estoque individual."""
    if pd.isna(estoque_val) or not isinstance(estoque_val, (int, float)):
        return 'Desconhecido'
    if estoque_val <= 10:
        return 'Baixo (0-10)'
    elif estoque_val <= 100:
        return 'Médio (11-100)'
    else:
        return 'Alto (>100)'

def criar_grafico_niveis_estoque(df):
    """Cria um gráfico de barras da contagem de produtos por nível de estoque."""
    if df.empty or 'Estoque' not in df.columns:
        return criar_figura_vazia("Níveis de Estoque (Sem Dados)")

    df_plot = df.copy()
    # Garante que 'Estoque' é numérico antes de aplicar a classificação
    df_plot['Estoque'] = pd.to_numeric(df_plot['Estoque'], errors='coerce') 

    df_plot['NivelEstoque'] = df_plot['Estoque'].apply(_classificar_nivel_estoque)
    
    contagem_niveis = df_plot['NivelEstoque'].value_counts().reset_index()
    contagem_niveis.columns = ['NivelEstoque', 'Contagem']
    
    # Definir uma ordem categórica para os níveis
    ordem_niveis = ['Baixo (0-10)', 'Médio (11-100)', 'Alto (>100)', 'Desconhecido']
    contagem_niveis['NivelEstoque'] = pd.Categorical(contagem_niveis['NivelEstoque'], categories=ordem_niveis, ordered=True)
    contagem_niveis = contagem_niveis.sort_values('NivelEstoque')
    
    if contagem_niveis.empty or contagem_niveis['Contagem'].sum() == 0:
        return criar_figura_vazia("Níveis de Estoque (Sem Produtos para Classificar)")

    fig = px.bar(contagem_niveis, 
                   x='NivelEstoque', 
                   y='Contagem', 
                   title='Produtos por Nível de Estoque',
                   labels={'Contagem': 'Número de Produtos', 'NivelEstoque': 'Nível de Estoque'},
                   text_auto=True,
                   color='NivelEstoque',
                   color_discrete_map={ # Cores personalizadas (opcional)
                       'Baixo (0-10)': 'rgba(255, 76, 76, 0.8)', # Vermelho
                       'Médio (11-100)': 'rgba(255, 191, 0, 0.8)', # Laranja/Amarelo
                       'Alto (>100)': 'rgba(76, 175, 80, 0.8)', # Verde
                       'Desconhecido': 'rgba(158, 158, 158, 0.8)' # Cinza
                   })
    fig.update_layout(showlegend=False, title_x=0.5)
    return fig