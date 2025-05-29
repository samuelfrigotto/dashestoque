from app_instance import app, server 
from modules.data_loader import carregar_produtos_com_hierarquia
from components.layout import criar_layout_principal
from callbacks.geral_callbacks import registrar_callbacks_gerais
caminho_arquivo_csv = "data/DAMI29-05.CSV"
df_visualizar_global = carregar_produtos_com_hierarquia(caminho_arquivo_csv)
registrar_callbacks_gerais(df_visualizar_global) 

app.layout = criar_layout_principal(
    df_completo=df_visualizar_global,
    nome_arquivo=caminho_arquivo_csv,
    page_size_tabela=20
)

if __name__ == '__main__':
    if df_visualizar_global is not None and not df_visualizar_global.empty:
        print("Dados para visualização carregados com sucesso. Iniciando o servidor Dash...")
        app.run(debug=True, host='127.0.0.1', port=8050)
    else:
        print("Não foi possível iniciar o servidor pois os dados para visualização não foram carregados ou o DataFrame está vazio.")