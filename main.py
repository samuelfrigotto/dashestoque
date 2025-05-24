# main.py
import dash
import dash_bootstrap_components as dbc # Ainda pode ser útil para temas ou outros componentes globais
from modules.data_loader import carregar_produtos_com_hierarquia # Ou a outra função de carregamento
from components.layout import criar_layout_principal

# 1. Carregamento de Dados
caminho_arquivo_csv = "data/16-05.CSV"
# Escolha qual função usar para carregar os dados:
# df_visualizar = carregar_apenas_produtos(caminho_arquivo_csv)
df_visualizar = carregar_produtos_com_hierarquia(caminho_arquivo_csv)

# 2. Inicialização do App Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard de Estoque"

# 3. Definição do Layout usando a função do módulo 'components.layout'
# Os valores de num_linhas_para_exibir e page_size_tabela são os que você usava antes.
app.layout = criar_layout_principal(
    df_completo=df_visualizar, 
    nome_arquivo=caminho_arquivo_csv,
    num_linhas_para_exibir=1000,
    page_size_tabela=1000 
)

# 4. Execução do Servidor
if __name__ == '__main__':
    # A lógica de verificar se df_visualizar está vazio agora é tratada internamente
    # pelos componentes de layout/tabela, mas a mensagem no console ainda é útil.
    if not df_visualizar.empty:
        print("Dados para visualização carregados com sucesso. Iniciando o servidor Dash...")
        app.run(debug=True, host='127.0.0.1', port=8050)
    else:
        print("Não foi possível iniciar o servidor pois os dados para visualização não foram carregados ou o DataFrame está vazio.")