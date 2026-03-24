"""
app.py — Interface de Linha de Comando (CLI)
=============================================
Ponto de entrada do sistema de gestão da Cantina Atlética.
Integra os módulos de estoque, pagamentos e persistência em um
menu interativo de terminal.

Execução:
    python app.py
"""

import os
import sys
from datetime import date, datetime

from estoque import GerenciadorEstoque
from pagamentos import GerenciadorPagamentos
from persistencia import salvar_dados, carregar_dados, dados_existem, excluir_dados

# ============================================================
# Utilitários de interface
# ============================================================

def limpar_tela() -> None:
    """Limpa o terminal de forma compatível com Windows e Unix."""
    os.system("cls" if os.name == "nt" else "clear")


def pausar() -> None:
    """Aguarda o usuário pressionar Enter antes de continuar."""
    input("\n  Pressione Enter para continuar...")


def cabecalho(titulo: str) -> None:
    """Exibe um cabeçalho formatado para cada seção do menu."""
    largura = 60
    print("\n" + "=" * largura)
    print(f"  🏪  {titulo.upper()}")
    print("=" * largura)


def ler_inteiro(prompt: str, minimo: int = 0, maximo: int = None) -> int:
    """
    Lê um inteiro do usuário com validação de intervalo.

    Parâmetros:
        prompt : texto exibido ao usuário.
        minimo : valor mínimo aceito (inclusive).
        maximo : valor máximo aceito (inclusive), ou None para sem limite.

    Retorna:
        O inteiro validado.
    """
    while True:
        try:
            valor = int(input(f"  {prompt}").strip())
            if valor < minimo:
                print(f"  ⚠️  Valor mínimo: {minimo}. Tente novamente.")
                continue
            if maximo is not None and valor > maximo:
                print(f"  ⚠️  Valor máximo: {maximo}. Tente novamente.")
                continue
            return valor
        except ValueError:
            print("  ⚠️  Entrada inválida. Digite um número inteiro.")


def ler_float(prompt: str, minimo: float = 0.0) -> float:
    """
    Lê um número decimal do usuário com validação.

    Parâmetros:
        prompt : texto exibido ao usuário.
        minimo : valor mínimo aceito (inclusive).

    Retorna:
        O float validado.
    """
    while True:
        try:
            valor = float(input(f"  {prompt}").strip().replace(",", "."))
            if valor < minimo:
                print(f"  ⚠️  Valor mínimo: {minimo:.2f}. Tente novamente.")
                continue
            return valor
        except ValueError:
            print("  ⚠️  Entrada inválida. Use ponto ou vírgula como separador decimal.")


def ler_data(prompt: str) -> date:
    """
    Lê uma data no formato DD/MM/AAAA e retorna um objeto datetime.date.

    Parâmetros:
        prompt : texto exibido ao usuário.

    Retorna:
        Objeto datetime.date validado.
    """
    while True:
        entrada = input(f"  {prompt}").strip()
        try:
            return datetime.strptime(entrada, "%d/%m/%Y").date()
        except ValueError:
            print("  ⚠️  Formato inválido. Use DD/MM/AAAA (ex: 31/12/2025).")


def ler_texto(prompt: str, minimo: int = 1) -> str:
    """
    Lê uma string não vazia do usuário.

    Parâmetros:
        prompt : texto exibido ao usuário.
        minimo : tamanho mínimo da string.

    Retorna:
        A string validada.
    """
    while True:
        valor = input(f"  {prompt}").strip()
        if len(valor) >= minimo:
            return valor
        print(f"  ⚠️  Entrada muito curta (mínimo {minimo} caractere(s)).")


# ============================================================
# Ações do menu
# ============================================================

def acao_adicionar_lote(estoque: GerenciadorEstoque) -> None:
    """Coleta dados e adiciona um novo lote ao estoque."""
    cabecalho("Adicionar Lote ao Estoque")

    nome = ler_texto("Nome do produto: ")
    preco_compra = ler_float("Preço de compra (R$): ", minimo=0.01)
    preco_venda = ler_float("Preço de venda  (R$): ", minimo=0.01)
    validade = ler_data("Validade (DD/MM/AAAA): ")
    quantidade = ler_inteiro("Quantidade (unidades): ", minimo=1)

    estoque.adicionar_lote(nome, preco_compra, preco_venda, validade, quantidade)


def acao_listar_estoque(estoque: GerenciadorEstoque) -> None:
    """Exibe o estoque atual."""
    cabecalho("Estoque Atual")
    estoque.listar_estoque()


def acao_realizar_venda(
    estoque: GerenciadorEstoque, pagamentos: GerenciadorPagamentos
) -> None:
    """Realiza uma venda: debita estoque e registra pagamento PIX."""
    cabecalho("Realizar Venda")

    # Mostra o estoque antes para facilitar a escolha
    estoque.listar_estoque()

    print()
    nome = ler_texto("Nome do produto a vender: ")
    quantidade = ler_inteiro("Quantidade: ", minimo=1)

    valor = estoque.vender_produto(nome, quantidade)

    if valor is not None:
        pagamentos.registrar_pagamento(nome, quantidade, valor)


def acao_editar_quantidade(estoque: GerenciadorEstoque) -> None:
    """Edita manualmente a quantidade de um produto no estoque."""
    cabecalho("Editar Quantidade de Produto")
    estoque.listar_estoque()

    print()
    nome = ler_texto("Nome do produto a editar: ")
    nova_qtd = ler_inteiro("Nova quantidade: ", minimo=0)

    estoque.editar_quantidade(nome, nova_qtd)


def acao_remover_vencidos(estoque: GerenciadorEstoque) -> None:
    """Remove todos os lotes vencidos do estoque."""
    cabecalho("Remover Produtos Vencidos")
    confirmacao = input("  ⚠️  Confirma remoção de todos os lotes vencidos? (s/N): ").strip().lower()
    if confirmacao == "s":
        estoque.remover_vencidos()
    else:
        print("  ℹ️  Operação cancelada.")


def acao_historico_pagamentos(pagamentos: GerenciadorPagamentos) -> None:
    """Exibe o histórico completo de pagamentos."""
    cabecalho("Histórico de Pagamentos")
    pagamentos.listar_historico()


def acao_buscar_pagamento(pagamentos: GerenciadorPagamentos) -> None:
    """Busca uma transação específica pelo ID."""
    cabecalho("Buscar Pagamento por ID")
    id_transacao = ler_texto("ID da transação (8 caracteres): ", minimo=8)
    registro = pagamentos.buscar_por_id(id_transacao)
    if registro:
        print(f"\n  ✅ Transação encontrada:\n  {registro}")
    else:
        print(f"\n  ❌ Nenhuma transação encontrada com ID '{id_transacao.upper()}'.")


def acao_cancelar_pagamento(pagamentos: GerenciadorPagamentos) -> None:
    """Cancela (remove) uma transação pelo ID."""
    cabecalho("Cancelar Pagamento")
    id_transacao = ler_texto("ID da transação a cancelar: ", minimo=8)
    confirmacao = input(f"  ⚠️  Confirma cancelamento de '{id_transacao.upper()}'? (s/N): ").strip().lower()
    if confirmacao == "s":
        pagamentos.cancelar_pagamento(id_transacao)
    else:
        print("  ℹ️  Operação cancelada.")


def acao_relatorio_vendas(pagamentos: GerenciadorPagamentos) -> None:
    """Exibe o relatório consolidado de vendas."""
    cabecalho("Relatório de Vendas")
    pagamentos.relatorio_vendas()


def acao_relatorio_consumo(estoque: GerenciadorEstoque) -> None:
    """Exibe o relatório de consumo e margens do estoque."""
    cabecalho("Relatório de Consumo / Margens")
    estoque.relatorio_consumo()


def acao_salvar(estoque: GerenciadorEstoque, pagamentos: GerenciadorPagamentos) -> None:
    """Salva os dados em arquivo."""
    salvar_dados(estoque, pagamentos)


def acao_resetar_dados() -> bool:
    """
    Exclui os arquivos de dados após confirmação dupla.
    Retorna True se o reset foi confirmado e executado.
    """
    cabecalho("Resetar Todos os Dados")
    print("  ⚠️  ATENÇÃO: Esta ação é IRREVERSÍVEL e apagará todos os dados salvos!")
    conf1 = input("  Digite 'CONFIRMAR' para prosseguir: ").strip()
    if conf1 != "CONFIRMAR":
        print("  ℹ️  Reset cancelado.")
        return False
    conf2 = input("  Tem absoluta certeza? Digite 'SIM': ").strip()
    if conf2 != "SIM":
        print("  ℹ️  Reset cancelado.")
        return False

    excluir_dados()
    return True


# ============================================================
# Menu principal
# ============================================================

MENU_PRINCIPAL = """
╔══════════════════════════════════════════════════════════╗
║          🏪  CANTINA DA ATLÉTICA ACADÊMICA  🏪           ║
╠══════════════════════════════════════════════════════════╣
║  ESTOQUE                                                 ║
║  [1] Adicionar lote ao estoque                          ║
║  [2] Listar estoque                                      ║
║  [3] Editar quantidade de produto                        ║
║  [4] Remover lotes vencidos                              ║
║  [5] Relatório de consumo / margens                      ║
╠══════════════════════════════════════════════════════════╣
║  VENDAS & PAGAMENTOS                                     ║
║  [6] Realizar venda (débito + PIX)                       ║
║  [7] Histórico de pagamentos                             ║
║  [8] Buscar pagamento por ID                             ║
║  [9] Cancelar pagamento                                  ║
║  [10] Relatório de vendas                                ║
╠══════════════════════════════════════════════════════════╣
║  SISTEMA                                                 ║
║  [11] Salvar dados                                       ║
║  [12] Resetar todos os dados                             ║
║  [0]  Salvar e sair                                      ║
╚══════════════════════════════════════════════════════════╝
"""


def menu_principal() -> None:
    """
    Loop principal da aplicação. Carrega os dados ao iniciar e
    salva automaticamente ao sair (opção 0).

    Usa uma lista mutável de um elemento para permitir o rebind dos
    gerenciadores em caso de reset (Python não permite rebind de
    variáveis de escopo superior via 'nonlocal' com lambda).
    """
    limpar_tela()
    print("\n  Inicializando Sistema da Cantina Atlética...")

    # Carrega dados existentes ou cria gerenciadores novos
    ctx_estoque, ctx_pagamentos = carregar_dados(GerenciadorEstoque, GerenciadorPagamentos)

    # Contêiner mutável para permitir substituição dos gerenciadores no reset
    ctx = {"estoque": ctx_estoque, "pagamentos": ctx_pagamentos}

    while True:
        # As lambdas leem ctx["estoque"] e ctx["pagamentos"] em tempo de execução,
        # portanto refletem qualquer substituição feita pelo reset.
        acoes = {
            "1":  lambda: acao_adicionar_lote(ctx["estoque"]),
            "2":  lambda: acao_listar_estoque(ctx["estoque"]),
            "3":  lambda: acao_editar_quantidade(ctx["estoque"]),
            "4":  lambda: acao_remover_vencidos(ctx["estoque"]),
            "5":  lambda: acao_relatorio_consumo(ctx["estoque"]),
            "6":  lambda: acao_realizar_venda(ctx["estoque"], ctx["pagamentos"]),
            "7":  lambda: acao_historico_pagamentos(ctx["pagamentos"]),
            "8":  lambda: acao_buscar_pagamento(ctx["pagamentos"]),
            "9":  lambda: acao_cancelar_pagamento(ctx["pagamentos"]),
            "10": lambda: acao_relatorio_vendas(ctx["pagamentos"]),
            "11": lambda: acao_salvar(ctx["estoque"], ctx["pagamentos"]),
        }

        print(MENU_PRINCIPAL)
        opcao = input("  ➤  Escolha uma opção: ").strip()

        if opcao == "0":
            # Salva automaticamente ao sair
            salvar_dados(ctx["estoque"], ctx["pagamentos"])
            print("\n  👋  Até logo! Sistema encerrado com sucesso.\n")
            sys.exit(0)

        elif opcao == "12":
            if acao_resetar_dados():
                # Substitui os gerenciadores por instâncias novas e vazias
                ctx["estoque"] = GerenciadorEstoque()
                ctx["pagamentos"] = GerenciadorPagamentos()
                print("\n  ✅ Sistema resetado com sucesso. Novos dados em memória.")

        elif opcao in acoes:
            try:
                acoes[opcao]()
            except KeyboardInterrupt:
                print("\n  ℹ️  Operação interrompida.")
        else:
            print("\n  ❌ Opção inválida. Escolha entre 0 e 12.")

        pausar()


# ============================================================
# Ponto de entrada
# ============================================================

if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n  ⚡ Programa interrompido pelo usuário (Ctrl+C).")
        sys.exit(0)
