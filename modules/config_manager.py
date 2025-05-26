import json
import os

CONFIG_FILE_PATH = "dashboard_config.json"
VALORES_PADRAO_NIVEIS = {
    "limite_estoque_baixo": 10,
    "limite_estoque_medio": 100
}
VALORES_PADRAO_EXCLUSAO = {
    "excluir_grupos": [],
    "excluir_categorias": [],
    "excluir_produtos_codigos": []
}

def _carregar_config_completa():
    """Função auxiliar para carregar todo o JSON de configuração."""
    if not os.path.exists(CONFIG_FILE_PATH):
        return {**VALORES_PADRAO_NIVEIS, **VALORES_PADRAO_EXCLUSAO}
    try:
        with open(CONFIG_FILE_PATH, 'r') as f:
            config = json.load(f)
        return config
    except (json.JSONDecodeError, Exception) as e:
        print(f"Erro ao ler arquivo de configuração '{CONFIG_FILE_PATH}': {e}. Usando todos os padrões.")
        return {**VALORES_PADRAO_NIVEIS, **VALORES_PADRAO_EXCLUSAO}

def _salvar_config_completa(config_data):
    """Função auxiliar para salvar todo o JSON de configuração."""
    try:
        with open(CONFIG_FILE_PATH, 'w') as f:
            json.dump(config_data, f, indent=4)
        print(f"Configurações salvas em '{CONFIG_FILE_PATH}'")
        return True
    except Exception as e:
        print(f"Erro inesperado ao salvar configuração completa: {e}")
        return False

def carregar_definicoes_niveis_estoque():
    config_completa = _carregar_config_completa()
    niveis = {}
    niveis["limite_estoque_baixo"] = int(config_completa.get("limite_estoque_baixo", VALORES_PADRAO_NIVEIS["limite_estoque_baixo"]))
    niveis["limite_estoque_medio"] = int(config_completa.get("limite_estoque_medio", VALORES_PADRAO_NIVEIS["limite_estoque_medio"]))

    if not (isinstance(niveis["limite_estoque_baixo"], int) and \
            isinstance(niveis["limite_estoque_medio"], int) and \
            niveis["limite_estoque_baixo"] >= 0 and \
            niveis["limite_estoque_medio"] >= 0 and \
            niveis["limite_estoque_medio"] > niveis["limite_estoque_baixo"]):
        print("Valores de níveis de estoque inválidos no config, usando padrões.")
        return VALORES_PADRAO_NIVEIS.copy()
    return niveis

def salvar_definicoes_niveis_estoque(limite_baixo, limite_medio):
    try:
        val_limite_baixo = int(limite_baixo)
        val_limite_medio = int(limite_medio)

        if val_limite_baixo < 0:
            return False, "Limite para Estoque Baixo não pode ser negativo."
        if val_limite_medio <= val_limite_baixo:
            return False, "Limite para Estoque Médio deve ser maior que o Limite para Estoque Baixo."

        config_completa = _carregar_config_completa()
        config_completa["limite_estoque_baixo"] = val_limite_baixo
        config_completa["limite_estoque_medio"] = val_limite_medio
        
        if _salvar_config_completa(config_completa):
            return True, "Definições de níveis de estoque salvas com sucesso!"
        else:
            return False, "Falha ao salvar o arquivo de configuração."
            
    except (ValueError, TypeError):
        return False, "Valores inválidos. Os limites devem ser números inteiros."
    except Exception as e:
        return False, f"Erro inesperado ao salvar níveis: {str(e)}"

def carregar_configuracoes_exclusao():
    """Carrega as configurações de exclusão do arquivo JSON."""
    config_completa = _carregar_config_completa()
    exclusoes = {}
    exclusoes["excluir_grupos"] = config_completa.get("excluir_grupos", VALORES_PADRAO_EXCLUSAO["excluir_grupos"])
    exclusoes["excluir_categorias"] = config_completa.get("excluir_categorias", VALORES_PADRAO_EXCLUSAO["excluir_categorias"])
    exclusoes["excluir_produtos_codigos"] = config_completa.get("excluir_produtos_codigos", VALORES_PADRAO_EXCLUSAO["excluir_produtos_codigos"])
    
    for key in exclusoes:
        if not isinstance(exclusoes[key], list):
            exclusoes[key] = VALORES_PADRAO_EXCLUSAO.get(key, [])
            
    return exclusoes

def salvar_configuracoes_exclusao(grupos_excluir, categorias_excluir, produtos_codigos_excluir):
    """Salva as configurações de exclusão no arquivo JSON."""
    try:
        lista_grupos = grupos_excluir if grupos_excluir is not None else []
        lista_categorias = categorias_excluir if categorias_excluir is not None else []
        lista_produtos_codigos = produtos_codigos_excluir if produtos_codigos_excluir is not None else []

        lista_grupos = [str(g) for g in lista_grupos]
        lista_categorias = [str(c) for c in lista_categorias]
        lista_produtos_codigos = [str(p) for p in lista_produtos_codigos]

        config_completa = _carregar_config_completa()
        config_completa["excluir_grupos"] = lista_grupos
        config_completa["excluir_categorias"] = lista_categorias
        config_completa["excluir_produtos_codigos"] = lista_produtos_codigos

        if _salvar_config_completa(config_completa):
            return True, "Configurações de exclusão salvas com sucesso!"
        else:
            return False, "Falha ao salvar o arquivo de configuração."

    except Exception as e:
        print(f"Erro inesperado ao salvar configurações de exclusão: {e}")
        return False, f"Erro inesperado ao salvar exclusões: {str(e)}"