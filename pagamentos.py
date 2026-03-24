"""
pagamentos.py — Sistema de Pagamentos via PIX
===============================================
Registra e gerencia os pagamentos da cantina usando a Lista Encadeada
definida em models.py. Os dados do pagador são gerados pelo Faker
para fins de simulação de um ambiente acadêmico.
"""

import random
import uuid
from datetime import datetime

from faker import Faker
from models import ListaEncadeada

# Instância do Faker configurada para português do Brasil
_faker = Faker("pt_BR")

# Constantes de domínio
CATEGORIAS = ["Aluno", "Servidor", "Professor"]
CURSOS = ["IA", "ESG"]
METODO_PAGAMENTO = "PIX"


class RegistroPagamento:
    """
    Representa um único registro de pagamento PIX na cantina.

    Os dados do pagador (nome, categoria, curso, chave PIX) são gerados
    automaticamente pelo Faker para simular um ambiente real de pagamentos
    em uma atlética acadêmica.

    Atributos privados:
        __id_transacao : identificador único da transação (UUID curto)
        __nome_pagador : nome completo gerado pelo Faker
        __categoria    : 'Aluno', 'Servidor' ou 'Professor'
        __curso        : 'IA' ou 'ESG'
        __chave_pix    : chave PIX simulada (CPF mascarado)
        __produto      : nome do produto comprado
        __quantidade   : quantidade comprada
        __valor_unit   : preço unitário de venda (R$)
        __valor_total  : valor total pago (R$)
        __data_hora    : timestamp da transação (string formatada)
    """

    def __init__(self, produto: str, quantidade: int, valor_total: float):
        # Dados da transação
        self.__id_transacao: str = uuid.uuid4().hex[:8].upper()
        self.__produto: str = produto
        self.__quantidade: int = quantidade
        self.__valor_total: float = valor_total
        self.__valor_unit: float = round(valor_total / quantidade, 2) if quantidade else 0.0
        self.__data_hora: str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Dados do pagador — gerados pelo Faker (simulação)
        self.__nome_pagador: str = _faker.name()
        self.__categoria: str = random.choice(CATEGORIAS)
        self.__curso: str = random.choice(CURSOS)
        self.__chave_pix: str = _faker.cpf()  # CPF como chave PIX

    # ---- Propriedades (somente leitura) ----

    @property
    def id_transacao(self) -> str:
        return self.__id_transacao

    @property
    def nome_pagador(self) -> str:
        return self.__nome_pagador

    @property
    def categoria(self) -> str:
        return self.__categoria

    @property
    def curso(self) -> str:
        return self.__curso

    @property
    def chave_pix(self) -> str:
        return self.__chave_pix

    @property
    def produto(self) -> str:
        return self.__produto

    @property
    def quantidade(self) -> int:
        return self.__quantidade

    @property
    def valor_unit(self) -> float:
        return self.__valor_unit

    @property
    def valor_total(self) -> float:
        return self.__valor_total

    @property
    def data_hora(self) -> str:
        return self.__data_hora

    def __str__(self) -> str:
        return (
            f"[{self.__id_transacao}] {self.__data_hora} | "
            f"{self.__nome_pagador:<30} ({self.__categoria} / {self.__curso}) | "
            f"PIX: {self.__chave_pix} | "
            f"{self.__produto} x{self.__quantidade} "
            f"@ R${self.__valor_unit:.2f} = R${self.__valor_total:.2f}"
        )

    def __repr__(self) -> str:
        return (
            f"RegistroPagamento(id='{self.__id_transacao}', "
            f"produto='{self.__produto}', total={self.__valor_total:.2f})"
        )


# ---------------------------------------------------------------------------
# Gerenciador de Pagamentos
# ---------------------------------------------------------------------------

class GerenciadorPagamentos:
    """
    Gerencia o histórico de pagamentos por meio de uma Lista Encadeada.
    Cada nodo da lista representa uma transação PIX registrada.
    """

    def __init__(self):
        self.__historico: ListaEncadeada = ListaEncadeada()

    # ---- Acesso interno à estrutura (para persistência) ----

    def get_historico(self) -> ListaEncadeada:
        """Retorna a lista encadeada interna (usado pelo módulo de persistência)."""
        return self.__historico

    def set_historico(self, historico: ListaEncadeada) -> None:
        """Substitui a lista interna (usado ao carregar dados do Pickle)."""
        self.__historico = historico

    # ---- Operações de pagamento ----

    def registrar_pagamento(
        self, produto: str, quantidade: int, valor_total: float
    ) -> RegistroPagamento:
        """
        Cria um RegistroPagamento com dados simulados do Faker e insere
        na Lista Encadeada de histórico.

        Parâmetros:
            produto     : nome do produto vendido.
            quantidade  : unidades vendidas.
            valor_total : valor total cobrado (R$).

        Retorna:
            O objeto RegistroPagamento recém-criado.
        """
        registro = RegistroPagamento(produto, quantidade, valor_total)
        self.__historico.inserir(registro)

        print(
            f"\n  💳 Pagamento PIX registrado com sucesso!"
            f"\n     ID: {registro.id_transacao} | "
            f"Pagador: {registro.nome_pagador} | "
            f"Valor: R${registro.valor_total:.2f}"
        )
        return registro

    def buscar_por_id(self, id_transacao: str) -> RegistroPagamento | None:
        """
        Busca um registro pelo ID da transação percorrendo a lista encadeada.

        Parâmetros:
            id_transacao : string com o ID (8 caracteres hex em maiúsculas).

        Retorna:
            O RegistroPagamento correspondente, ou None se não encontrado.
        """
        return self.__historico.buscar(
            lambda r: r.id_transacao == id_transacao.upper()
        )

    def cancelar_pagamento(self, id_transacao: str) -> bool:
        """
        Remove um registro de pagamento da lista encadeada.

        Parâmetros:
            id_transacao : ID da transação a ser cancelada.

        Retorna:
            True se o registro foi encontrado e removido, False caso contrário.
        """
        removido = self.__historico.remover(
            lambda r: r.id_transacao == id_transacao.upper()
        )
        if removido:
            print(f"\n  🚫 Pagamento {id_transacao.upper()} cancelado e removido do histórico.")
            return True
        else:
            print(f"\n  ❌ Transação '{id_transacao}' não encontrada.")
            return False

    def listar_historico(self) -> None:
        """
        Percorre a lista encadeada e imprime todas as transações registradas.
        """
        registros = self.__historico.listar()

        if not registros:
            print("\n  📋 Nenhum pagamento registrado ainda.")
            return

        print("\n" + "=" * 100)
        print("  💳  HISTÓRICO DE PAGAMENTOS PIX")
        print("=" * 100)

        for i, reg in enumerate(registros, start=1):
            print(f"  {i:>3}. {reg}")

        print("=" * 100)
        print(f"  Total de transações: {self.__historico.tamanho}")

    def relatorio_vendas(self) -> None:
        """
        Percorre a lista encadeada e gera um relatório consolidado de vendas,
        agrupando manualmente por produto e categoria ao longo dos nodos.
        """
        if self.__historico.esta_vazia():
            print("\n  📊 Nenhuma venda registrada para gerar relatório.")
            return

        print("\n" + "=" * 70)
        print("  📊  RELATÓRIO DE VENDAS — CONSOLIDADO")
        print("=" * 70)

        # --- Acumuladores por produto (percorremos a lista encadeada) ---
        # Usamos a lista auxiliar para iterar (dados reais estão nos nodos)
        registros = self.__historico.listar()

        total_geral = 0.0
        total_transacoes = 0

        # Contagem manual por categoria (sem dict — usamos pares de variáveis)
        total_aluno = 0.0
        qtd_aluno = 0
        total_servidor = 0.0
        qtd_servidor = 0
        total_professor = 0.0
        qtd_professor = 0

        # Contagem por curso
        total_ia = 0.0
        qtd_ia = 0
        total_esg = 0.0
        qtd_esg = 0

        print(f"\n  {'#':<4} {'Produto':<20} {'Qtd':>4} {'Unit':>8} "
              f"{'Total':>9} {'Categoria':<12} {'Curso':<6} {'Data/Hora'}")
        print("  " + "-" * 85)

        for i, reg in enumerate(registros, start=1):
            print(
                f"  {i:<4} {reg.produto:<20} {reg.quantidade:>4} "
                f"R${reg.valor_unit:>6.2f} R${reg.valor_total:>7.2f} "
                f"{reg.categoria:<12} {reg.curso:<6} {reg.data_hora}"
            )

            total_geral += reg.valor_total
            total_transacoes += 1

            # Acumulação por categoria
            if reg.categoria == "Aluno":
                total_aluno += reg.valor_total
                qtd_aluno += 1
            elif reg.categoria == "Servidor":
                total_servidor += reg.valor_total
                qtd_servidor += 1
            elif reg.categoria == "Professor":
                total_professor += reg.valor_total
                qtd_professor += 1

            # Acumulação por curso
            if reg.curso == "IA":
                total_ia += reg.valor_total
                qtd_ia += 1
            elif reg.curso == "ESG":
                total_esg += reg.valor_total
                qtd_esg += 1

        print("  " + "=" * 85)
        print(f"\n  💰 TOTAL ARRECADADO: R${total_geral:.2f}  ({total_transacoes} transações)")

        print("\n  --- Por Categoria ---")
        print(f"  Aluno      : {qtd_aluno:>3} transação(ões) — R${total_aluno:.2f}")
        print(f"  Servidor   : {qtd_servidor:>3} transação(ões) — R${total_servidor:.2f}")
        print(f"  Professor  : {qtd_professor:>3} transação(ões) — R${total_professor:.2f}")

        print("\n  --- Por Curso ---")
        print(f"  IA         : {qtd_ia:>3} transação(ões) — R${total_ia:.2f}")
        print(f"  ESG        : {qtd_esg:>3} transação(ões) — R${total_esg:.2f}")
        print("=" * 70)
