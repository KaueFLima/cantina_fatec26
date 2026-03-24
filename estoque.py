"""
estoque.py — Gerenciamento de Estoque
======================================
Controla os lotes de produtos da cantina usando a Fila FIFO definida
em models.py, garantindo que o primeiro lote a entrar seja o primeiro
a ser consumido (política de perecíveis).
"""

from datetime import date
from models import Fila


class LoteProduto:
    """
    Representa um lote específico de um produto no estoque.

    Atributos privados:
        __nome         : nome do produto
        __preco_compra : preço pago na aquisição do lote (R$)
        __preco_venda  : preço cobrado na venda ao cliente (R$)
        __validade     : data de validade do lote (datetime.date)
        __quantidade   : unidades disponíveis neste lote
    """

    def __init__(
        self,
        nome: str,
        preco_compra: float,
        preco_venda: float,
        validade: date,
        quantidade: int,
    ):
        if quantidade < 0:
            raise ValueError("A quantidade não pode ser negativa.")
        if preco_compra < 0 or preco_venda < 0:
            raise ValueError("Os preços não podem ser negativos.")

        self.__nome = nome.strip().title()
        self.__preco_compra = preco_compra
        self.__preco_venda = preco_venda
        self.__validade = validade
        self.__quantidade = quantidade

    # ---- Propriedades (somente leitura, exceto quantidade) ----

    @property
    def nome(self) -> str:
        return self.__nome

    @property
    def preco_compra(self) -> float:
        return self.__preco_compra

    @property
    def preco_venda(self) -> float:
        return self.__preco_venda

    @property
    def validade(self) -> date:
        return self.__validade

    @property
    def quantidade(self) -> int:
        return self.__quantidade

    @quantidade.setter
    def quantidade(self, novo_valor: int) -> None:
        if novo_valor < 0:
            raise ValueError("A quantidade não pode ser negativa.")
        self.__quantidade = novo_valor

    # ---- Verificação de validade ----

    def esta_vencido(self) -> bool:
        """Retorna True se o lote já passou da data de validade."""
        return date.today() > self.__validade

    def dias_para_vencer(self) -> int:
        """Retorna o número de dias restantes até o vencimento (negativo = vencido)."""
        return (self.__validade - date.today()).days

    def __str__(self) -> str:
        alerta = " ⚠️ VENCIDO" if self.esta_vencido() else ""
        return (
            f"Produto: {self.__nome:<20} | "
            f"Compra: R${self.__preco_compra:>7.2f} | "
            f"Venda: R${self.__preco_venda:>7.2f} | "
            f"Validade: {self.__validade.strftime('%d/%m/%Y')} | "
            f"Qtd: {self.__quantidade:>4}{alerta}"
        )

    def __repr__(self) -> str:
        return (
            f"LoteProduto(nome='{self.__nome}', qtd={self.__quantidade}, "
            f"validade={self.__validade})"
        )


# ---------------------------------------------------------------------------
# Gerenciador de Estoque
# ---------------------------------------------------------------------------

class GerenciadorEstoque:
    """
    Gerencia o estoque da cantina por meio de uma Fila FIFO encadeada.
    Cada nodo da fila representa um lote de produto.

    O produto mais antigo (inserido primeiro) sempre será vendido primeiro,
    respeitando a regra de perecíveis.
    """

    def __init__(self):
        self.__fila_estoque: Fila = Fila()

    # ---- Acesso interno à estrutura (para persistência) ----

    def get_fila(self) -> Fila:
        """Retorna a fila interna (usado pelo módulo de persistência)."""
        return self.__fila_estoque

    def set_fila(self, fila: Fila) -> None:
        """Substitui a fila interna (usado ao carregar dados do Pickle)."""
        self.__fila_estoque = fila

    # ---- Operações de estoque ----

    def adicionar_lote(
        self,
        nome: str,
        preco_compra: float,
        preco_venda: float,
        validade: date,
        quantidade: int,
    ) -> None:
        """
        Cria um novo LoteProduto e o enfileira no estoque.

        Parâmetros:
            nome         : nome do produto.
            preco_compra : preço de custo (R$).
            preco_venda  : preço de venda ao cliente (R$).
            validade     : objeto datetime.date com a data de validade.
            quantidade   : número de unidades do lote.
        """
        try:
            lote = LoteProduto(nome, preco_compra, preco_venda, validade, quantidade)
            self.__fila_estoque.enfileirar(lote)
            print(f"\n  ✅ Lote de '{lote.nome}' adicionado ao estoque "
                  f"({quantidade} unidade(s), vence em {lote.dias_para_vencer()} dia(s)).")
        except ValueError as erro:
            print(f"\n  ❌ Erro ao adicionar lote: {erro}")

    def vender_produto(self, nome: str, quantidade_venda: int) -> float | None:
        """
        Realiza a venda FIFO de um produto:
          1. Localiza o lote mais antigo do produto na fila.
          2. Decrementa a quantidade vendida.
          3. Se o lote zerar, remove o nodo da fila.

        Parâmetros:
            nome             : nome do produto a ser vendido.
            quantidade_venda : quantidade a ser retirada do estoque.

        Retorna:
            O valor total da venda (R$), ou None em caso de falha.
        """
        nome_normalizado = nome.strip().title()

        # Busca o lote mais antigo do produto (FIFO)
        lote = self.__fila_estoque.buscar(
            lambda l: l.nome == nome_normalizado
        )

        if lote is None:
            print(f"\n  ❌ Produto '{nome_normalizado}' não encontrado no estoque.")
            return None

        if lote.esta_vencido():
            print(f"\n  ⚠️  Atenção: o lote de '{nome_normalizado}' está VENCIDO "
                  f"({lote.validade.strftime('%d/%m/%Y')}). Venda bloqueada.")
            return None

        if lote.quantidade < quantidade_venda:
            print(
                f"\n  ❌ Estoque insuficiente para '{nome_normalizado}'. "
                f"Disponível: {lote.quantidade} unidade(s)."
            )
            return None

        # Efetua o abatimento de estoque
        lote.quantidade -= quantidade_venda
        valor_total = lote.preco_venda * quantidade_venda

        print(f"\n  🛒 Venda realizada: {quantidade_venda}x '{nome_normalizado}' "
              f"— Total: R${valor_total:.2f}")

        # Se o lote esgotou, remove da fila
        if lote.quantidade == 0:
            self.__fila_estoque.remover(lambda l: l is lote)
            print(f"  🔄 Lote de '{nome_normalizado}' esgotado e removido da fila.")

        return valor_total

    def editar_quantidade(self, nome: str, nova_quantidade: int) -> None:
        """
        Atualiza manualmente a quantidade do primeiro lote encontrado para
        o produto informado, percorrendo a estrutura encadeada.

        Parâmetros:
            nome            : nome do produto.
            nova_quantidade : nova quantidade a ser atribuída.
        """
        nome_normalizado = nome.strip().title()
        lote = self.__fila_estoque.buscar(
            lambda l: l.nome == nome_normalizado
        )

        if lote is None:
            print(f"\n  ❌ Produto '{nome_normalizado}' não encontrado no estoque.")
            return

        try:
            quantidade_anterior = lote.quantidade
            lote.quantidade = nova_quantidade
            print(
                f"\n  ✅ Quantidade de '{nome_normalizado}' atualizada: "
                f"{quantidade_anterior} → {nova_quantidade}."
            )
        except ValueError as erro:
            print(f"\n  ❌ Erro ao editar: {erro}")

    def remover_vencidos(self) -> int:
        """
        Percorre toda a fila e remove os lotes vencidos.

        Retorna:
            Número de lotes removidos.
        """
        removidos = 0
        # Coleta os lotes vencidos primeiro (não altera a fila durante a iteração)
        lotes_vencidos = [l for l in self.__fila_estoque.listar() if l.esta_vencido()]

        for lote in lotes_vencidos:
            self.__fila_estoque.remover(lambda l, ref=lote: l is ref)
            print(f"  🗑️  Lote vencido removido: {lote.nome} "
                  f"(venceu em {lote.validade.strftime('%d/%m/%Y')})")
            removidos += 1

        if removidos == 0:
            print("\n  ✅ Nenhum lote vencido encontrado.")
        else:
            print(f"\n  🗑️  {removidos} lote(s) vencido(s) removido(s) do estoque.")

        return removidos

    def listar_estoque(self) -> None:
        """
        Percorre a fila e imprime o estoque atual em formato tabular.
        """
        lotes = self.__fila_estoque.listar()

        if not lotes:
            print("\n  📦 Estoque vazio.")
            return

        print("\n" + "=" * 70)
        print("  📦  ESTOQUE ATUAL — ORDEM FIFO (mais antigo primeiro)")
        print("=" * 70)

        for i, lote in enumerate(lotes, start=1):
            prefixo = "  [VENCIDO] " if lote.esta_vencido() else f"  {i:>3}. "
            print(f"{prefixo}{lote}")

        print("=" * 70)
        print(f"  Total de lotes na fila: {self.__fila_estoque.tamanho}")

    def relatorio_consumo(self) -> None:
        """
        Percorre a fila e exibe um relatório de produtos disponíveis,
        com margem de lucro calculada por lote.
        """
        lotes = self.__fila_estoque.listar()

        if not lotes:
            print("\n  📦 Nenhum produto em estoque para relatório.")
            return

        print("\n" + "=" * 70)
        print("  📊  RELATÓRIO DE CONSUMO / MARGEM DE LUCRO")
        print("=" * 70)
        print(f"  {'Produto':<20} {'Compra':>8} {'Venda':>8} {'Margem':>8} "
              f"{'Qtd':>5} {'Dias p/ Vencer':>14}")
        print("-" * 70)

        total_investido = 0.0
        total_receita_potencial = 0.0

        atual_lotes = self.__fila_estoque.listar()  # visão temporária
        for lote in atual_lotes:
            margem = lote.preco_venda - lote.preco_compra
            dias = lote.dias_para_vencer()
            alerta = " ⚠️" if lote.esta_vencido() else (" !" if dias <= 7 else "")
            print(
                f"  {lote.nome:<20} "
                f"R${lote.preco_compra:>6.2f} "
                f"R${lote.preco_venda:>6.2f} "
                f"R${margem:>6.2f} "
                f"{lote.quantidade:>5} "
                f"{dias:>10} dias{alerta}"
            )
            total_investido += lote.preco_compra * lote.quantidade
            total_receita_potencial += lote.preco_venda * lote.quantidade

        print("-" * 70)
        print(f"  {'TOTAIS':<20} {'':>8} {'':>8} {'':>8} "
              f"{'':>5} {'':>14}")
        print(f"  Investimento total : R${total_investido:.2f}")
        print(f"  Receita potencial  : R${total_receita_potencial:.2f}")
        print(f"  Lucro potencial    : R${total_receita_potencial - total_investido:.2f}")
        print("=" * 70)
