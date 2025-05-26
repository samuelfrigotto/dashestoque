# modules/config_manager.py
import json
import os

CONFIG_FILE_PATH = "config_niveis_estoque.json" # Arquivo será criado na raiz do projeto
VALORES_PADRAO_NIVEIS = {
    "limite_estoque_baixo": 10,  # Estoque <= este valor é Baixo
    "limite_estoque_medio": 100  # Estoque > Baixo E <= este valor é Médio
                                 # Estoque > Limite Médio é Alto
}

def carregar_definicoes_niveis_estoque():
    """
    Carrega as definições de níveis de estoque (limite_baixo, limite_medio) do arquivo JSON.
    Retorna os valores padrão se o arquivo não existir, estiver malformado ou incompleto.
    """
    if not os.path.exists(CONFIG_FILE_PATH):
        print(f"Arquivo de configuração '{CONFIG_FILE_PATH}' não encontrado. Usando valores padrão: {VALORES_PADRAO_NIVEIS}")
        return VALORES_PADRAO_NIVEIS.copy()
    
    try:
        with open(CONFIG_FILE_PATH, 'r') as f:
            config = json.load(f)
        
        # Validação e conversão para int, com fallback para padrão se chave ou tipo estiverem errados
        limite_baixo = int(config.get("limite_estoque_baixo", VALORES_PADRAO_NIVEIS["limite_estoque_baixo"]))
        limite_medio = int(config.get("limite_estoque_medio", VALORES_PADRAO_NIVEIS["limite_estoque_medio"]))

        # Garante que os padrões sejam usados se os valores carregados forem inválidos (ex: não numéricos antes da conversão)
        # A conversão para int acima já lidaria com ValueError, mas .get com padrão é mais seguro para chaves faltantes
        # e a lógica abaixo valida a relação entre eles.
        if not (isinstance(limite_baixo, int) and isinstance(limite_medio, int) and limite_baixo >= 0 and limite_medio >= 0 and limite_medio > limite_baixo):
            print(f"Valores de configuração inválidos em '{CONFIG_FILE_PATH}'. Usando valores padrão.")
            return VALORES_PADRAO_NIVEIS.copy()

        return {"limite_estoque_baixo": limite_baixo, "limite_estoque_medio": limite_medio}

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        print(f"Erro ao ler ou converter o arquivo de configuração '{CONFIG_FILE_PATH}': {e}. Usando valores padrão.")
        return VALORES_PADRAO_NIVEIS.copy()
    except Exception as e:
        print(f"Erro inesperado ao carregar configuração: {e}. Usando valores padrão.")
        return VALORES_PADRAO_NIVEIS.copy()


def salvar_definicoes_niveis_estoque(limite_baixo, limite_medio):
    """
    Salva as definições de níveis de estoque no arquivo JSON.
    Valida os inputs antes de salvar.
    Retorna (bool: sucesso, str: mensagem).
    """
    try:
        val_limite_baixo = int(limite_baixo)
        val_limite_medio = int(limite_medio)

        if val_limite_baixo < 0:
            return False, "Limite para Estoque Baixo não pode ser negativo."
        if val_limite_medio <= val_limite_baixo:
            return False, "Limite para Estoque Médio deve ser maior que o Limite para Estoque Baixo."

        config_para_salvar = {
            "limite_estoque_baixo": val_limite_baixo,
            "limite_estoque_medio": val_limite_medio
        }
        with open(CONFIG_FILE_PATH, 'w') as f:
            json.dump(config_para_salvar, f, indent=4)
        print(f"Configurações de níveis de estoque salvas: {config_para_salvar}")
        return True, "Definições de níveis de estoque salvas com sucesso!"
    except (ValueError, TypeError):
        return False, "Valores inválidos. Os limites devem ser números inteiros."
    except Exception as e:
        print(f"Erro inesperado ao salvar definições de níveis de estoque: {e}")
        return False, f"Erro inesperado ao salvar: {str(e)}"