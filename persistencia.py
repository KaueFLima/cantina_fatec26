"""
persistencia.py — Armazenamento Não Volátil com Pickle
========================================================
Salva e carrega o estado completo dos gerenciadores (Fila de Estoque
e Lista Encadeada de Pagamentos) em arquivo binário via Pickle.

O Pickle serializa os objetos Python inteiros — incluindo os nodos
encadeados e seus ponteiros — preservando toda a estrutura de dados
entre sessões do programa.
"""

import os
import pickle
import shutil
from datetime import datetime

# Caminho do arquivo principal de dados
ARQUIVO_DADOS = "dados_cantina.pkl"
# Arquivo de backup (sobrescrito a cada salvamento)
ARQUIVO_BACKUP = "dados_cantina.bak.pkl"


def salvar_dados(gerenciador_estoque, gerenciador_pagamentos) -> bool:
    """
    Serializa e salva os dois gerenciadores em arquivo binário (.pkl).
    Antes de salvar, copia o arquivo atual para backup.

    Parâmetros:
        gerenciador_estoque    : instância de GerenciadorEstoque.
        gerenciador_pagamentos : instância de GerenciadorPagamentos.

    Retorna:
        True em caso de sucesso, False em caso de erro.
    """
    # Cria backup do arquivo anterior, se existir
    if os.path.exists(ARQUIVO_DADOS):
        try:
            shutil.copy2(ARQUIVO_DADOS, ARQUIVO_BACKUP)
        except OSError:
            pass  # backup falhou, mas não é crítico

    dados = {
        "versao": "1.0",
        "salvo_em": datetime.now().isoformat(),
        "estoque": gerenciador_estoque,
        "pagamentos": gerenciador_pagamentos,
    }

    try:
        with open(ARQUIVO_DADOS, "wb") as arquivo:
            pickle.dump(dados, arquivo, protocol=pickle.HIGHEST_PROTOCOL)

        tamanho_kb = os.path.getsize(ARQUIVO_DADOS) / 1024
        print(
            f"\n  💾 Dados salvos com sucesso em '{ARQUIVO_DADOS}' "
            f"({tamanho_kb:.1f} KB) às {dados['salvo_em'][:19].replace('T', ' ')}."
        )
        return True

    except (OSError, pickle.PicklingError) as erro:
        print(f"\n  ❌ Erro ao salvar dados: {erro}")
        return False


def carregar_dados(
    classe_estoque, classe_pagamentos
):
    """
    Carrega e desserializa os gerenciadores a partir do arquivo .pkl.
    Se o arquivo não existir ou estiver corrompido, tenta o backup.

    Parâmetros:
        classe_estoque    : classe GerenciadorEstoque (para instância nova se falhar).
        classe_pagamentos : classe GerenciadorPagamentos (para instância nova se falhar).

    Retorna:
        Tupla (gerenciador_estoque, gerenciador_pagamentos).
        Em caso de falha, retorna duas novas instâncias vazias.
    """
    for caminho in [ARQUIVO_DADOS, ARQUIVO_BACKUP]:
        if not os.path.exists(caminho):
            continue

        try:
            with open(caminho, "rb") as arquivo:
                dados = pickle.load(arquivo)

            estoque = dados.get("estoque")
            pagamentos = dados.get("pagamentos")

            # Valida se os objetos carregados são das classes corretas
            if not isinstance(estoque, classe_estoque):
                raise TypeError("Tipo inválido para 'estoque' no arquivo.")
            if not isinstance(pagamentos, classe_pagamentos):
                raise TypeError("Tipo inválido para 'pagamentos' no arquivo.")

            origem = "backup" if caminho == ARQUIVO_BACKUP else "principal"
            print(
                f"\n  ✅ Dados carregados do arquivo {origem} '{caminho}'. "
                f"(Salvo em: {dados.get('salvo_em', 'desconhecido')[:19].replace('T', ' ')})"
            )
            return estoque, pagamentos

        except (OSError, pickle.UnpicklingError, TypeError, KeyError) as erro:
            print(f"\n  ⚠️  Falha ao carregar '{caminho}': {erro}")
            continue

    # Nenhum arquivo válido encontrado — retorna instâncias novas
    print("\n  🆕 Nenhum dado salvo encontrado. Iniciando sistema do zero.")
    return classe_estoque(), classe_pagamentos()


def dados_existem() -> bool:
    """
    Verifica se existe algum arquivo de dados salvo.

    Retorna:
        True se o arquivo principal ou o backup existir.
    """
    return os.path.exists(ARQUIVO_DADOS) or os.path.exists(ARQUIVO_BACKUP)


def excluir_dados() -> bool:
    """
    Remove os arquivos de dados e backup (operação irreversível).

    Retorna:
        True se ao menos um arquivo foi removido.
    """
    removidos = False
    for caminho in [ARQUIVO_DADOS, ARQUIVO_BACKUP]:
        if os.path.exists(caminho):
            os.remove(caminho)
            print(f"  🗑️  Arquivo '{caminho}' removido.")
            removidos = True

    if not removidos:
        print("  ℹ️  Nenhum arquivo de dados encontrado para excluir.")

    return removidos
