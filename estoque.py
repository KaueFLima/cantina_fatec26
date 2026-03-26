"""
estoque.py — Gerenciamento de Estoque
======================================
Controla os lotes de produtos da cantina usando a Fila FIFO definida
em models.py, garantindo que o primeiro lote a entrar seja o primeiro
a ser consumido (política de perecíveis).

Também mantém um histórico de compras (ListaEncadeada) para alimentar
o relatório financeiro consolidado.
"""

from datetime import date, datetime
from models import Fila, ListaEncadeada


# ---------------------------------------------------------------------------
# Registro de Compra — histórico de entradas de estoque
# ---------------------------------------------------------------------------

class RegistroCompra:
    """
    Representa uma entrada de lote no estoque (ato de compra/reposição).
    Inserido na ListaEncadeada de histórico a cada chamada de adicionar_lote.

    Atributos privados:
        __nome         : nome do produto comprado
        __preco_compra : preço unitário de custo (R$)
        __preco_venda  : preço unitário de venda definido no momento da compra (R$)
        __validade     : data de validade do lote adquirido
        __quantidade   : unidades adquiridas neste lote
        __valor_total  : custo total da compra (preco_compra × quantidade)
        __data_hora    : timestamp do registro (string formatada)
    """

    def __init__(
        self,
        nome: str,
        preco_compra: float,
        preco_venda: float,
        validade: date,
        quantidade: int,
    ):
        self.__nome         = nome
        self.__preco_compra = preco_compra
        self.__preco_venda  = preco_venda
        self.__validade     = validade
        self.__quantidade   = quantidade
        self.__valor_total  = round(preco_compra * quantidade, 2)
        self.__data_hora    = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

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

    @property
    def valor_total(self) -> float:
        return self.__valor_total

    @property
    def data_hora(self) -> str:
        return self.__data_hora

    def __repr__(self) -> str:
        return (
            f"RegistroCompra(nome='{self.__nome}', qtd={self.__quantidade}, "
            f"total=R${self.__valor_total:.2f})"
        )


# ---------------------------------------------------------------------------
# Lote de Produto — nodo da Fila de Estoque
# ---------------------------------------------------------------------------

class LoteProduto:
    """
    Representa um lote específico de um produto no estoque.
    Cada lote tem sua própria data de validade e quantidade independentes.

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

        self.__nome         = nome.strip().title()
        self.__preco_compra = preco_compra
        self.__preco_venda  = preco_venda
        self.__validade     = validade
        self.__quantidade   = quantidade

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

    def esta_vencido(self) -> bool:
        """Retorna True se o lote já passou da data de validade."""
        return date.today() > self.__validade

    def dias_para_vencer(self) -> int:
        """Retorna os dias restantes até o vencimento (negativo = vencido)."""
        return (self.__validade - date.today()).days

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
    Gerencia o estoque da cantina por meio de:
      - __fila_estoque      : Fila FIFO de LoteProduto (inventário ativo)
      - __historico_compras : ListaEncadeada de RegistroCompra (auditoria)

    O produto mais antigo é sempre vendido primeiro (FIFO de perecíveis).
    Cada adição de lote gera um RegistroCompra para o relatório financeiro.
    """

    def __init__(self):
        self.__fila_estoque:      Fila           = Fila()
        self.__historico_compras: ListaEncadeada = ListaEncadeada()

    # ---- Acesso às estruturas internas (para persistência) ----

    def get_fila(self) -> Fila:
        return self.__fila_estoque

    def set_fila(self, fila: Fila) -> None:
        self.__fila_estoque = fila

    def get_historico_compras(self) -> ListaEncadeada:
        """Retorna o histórico de compras (uso do relatório financeiro)."""
        return self.__historico_compras

    def set_historico_compras(self, historico: ListaEncadeada) -> None:
        """Substitui o histórico de compras (uso ao carregar dados do Pickle)."""
        self.__historico_compras = historico

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
        Cria um LoteProduto, enfileira no estoque e registra a compra no histórico.
        A data de validade é informada individualmente para cada lote adicionado.
        """
        try:
            lote = LoteProduto(nome, preco_compra, preco_venda, validade, quantidade)
            self.__fila_estoque.enfileirar(lote)

            # Registra a entrada no histórico de compras para o relatório financeiro
            compra = RegistroCompra(
                lote.nome, preco_compra, preco_venda, validade, quantidade
            )
            self.__historico_compras.inserir(compra)

            print(
                f"\n  ✅ Lote de '{lote.nome}' adicionado ao estoque "
                f"({quantidade} unidade(s), vence em {lote.dias_para_vencer()} dia(s))."
            )
        except ValueError as erro:
            print(f"\n  ❌ Erro ao adicionar lote: {erro}")

    def vender_produto(self, nome: str, quantidade_venda: int) -> float | None:
        """
        Realiza a venda FIFO de um produto:
          1. Localiza o lote mais antigo do produto na fila.
          2. Decrementa a quantidade vendida.
          3. Se o lote zerar, remove o nodo da fila.

        Retorna o valor total da venda (R$), ou None em caso de falha.
        """
        nome_normalizado = nome.strip().title()
        lote = self.__fila_estoque.buscar(lambda l: l.nome == nome_normalizado)

        if lote is None:
            print(f"\n  ❌ Produto '{nome_normalizado}' não encontrado no estoque.")
            return None

        if lote.esta_vencido():
            print(
                f"\n  ⚠️  Atenção: o lote de '{nome_normalizado}' está VENCIDO "
                f"({lote.validade.strftime('%d/%m/%Y')}). Venda bloqueada."
            )
            return None

        if lote.quantidade < quantidade_venda:
            print(
                f"\n  ❌ Estoque insuficiente para '{nome_normalizado}'. "
                f"Disponível: {lote.quantidade} unidade(s) neste lote."
            )
            return None

        lote.quantidade -= quantidade_venda
        valor_total = lote.preco_venda * quantidade_venda

        print(
            f"\n  🛒 Venda realizada: {quantidade_venda}x '{nome_normalizado}' "
            f"— Total: R${valor_total:.2f}"
        )

        # Lote esgotado: remove da fila usando identidade de objeto (l is lote)
        # para evitar ambiguidade entre lotes homônimos com mesma quantidade
        if lote.quantidade == 0:
            self.__fila_estoque.remover(lambda l: l is lote)
            print(f"  🔄 Lote de '{nome_normalizado}' esgotado e removido da fila.")

        return valor_total

    def editar_quantidade(self, nome: str, nova_quantidade: int) -> None:
        """
        Atualiza manualmente a quantidade do lote mais antigo do produto,
        percorrendo a estrutura encadeada.
        """
        nome_normalizado = nome.strip().title()
        lote = self.__fila_estoque.buscar(lambda l: l.nome == nome_normalizado)

        if lote is None:
            print(f"\n  ❌ Produto '{nome_normalizado}' não encontrado no estoque.")
            return

        try:
            anterior = lote.quantidade
            lote.quantidade = nova_quantidade
            print(
                f"\n  ✅ Quantidade de '{nome_normalizado}' atualizada: "
                f"{anterior} → {nova_quantidade}."
            )
        except ValueError as erro:
            print(f"\n  ❌ Erro ao editar: {erro}")

    def remover_vencidos(self) -> int:
        """Percorre toda a fila e remove os lotes vencidos."""
        removidos = 0
        lotes_vencidos = [l for l in self.__fila_estoque.listar() if l.esta_vencido()]

        for lote in lotes_vencidos:
            self.__fila_estoque.remover(lambda l, ref=lote: l is ref)
            print(
                f"  🗑️  Lote vencido removido: {lote.nome} "
                f"(venceu em {lote.validade.strftime('%d/%m/%Y')})"
            )
            removidos += 1

        if removidos == 0:
            print("\n  ✅ Nenhum lote vencido encontrado.")
        else:
            print(f"\n  🗑️  {removidos} lote(s) vencido(s) removido(s) do estoque.")

        return removidos

    def listar_estoque(self) -> None:
        """
        Percorre a fila e exibe o estoque AGRUPADO POR PRODUTO.
        Cada produto lista todos os seus lotes com a data de validade individual.
        """
        lotes = self.__fila_estoque.listar()

        if not lotes:
            print("\n  📦 Estoque vazio.")
            return

        # Coleta nomes únicos preservando a ordem de inserção (sem dict/set)
        nomes_unicos = []
        for lote in lotes:
            if lote.nome not in nomes_unicos:
                nomes_unicos.append(lote.nome)

        print("\n" + "=" * 68)
        print("  📦  ESTOQUE ATUAL — AGRUPADO POR PRODUTO  (FIFO por lote)")
        print("=" * 68)

        for nome in nomes_unicos:
            lotes_produto = [l for l in lotes if l.nome == nome]
            total_unidades = sum(l.quantidade for l in lotes_produto)
            tem_vencido = any(l.esta_vencido() for l in lotes_produto)
            aviso = "  ⚠️  POSSUI LOTE VENCIDO" if tem_vencido else ""

            print(f"\n  📦 {nome:<24}  Total: {total_unidades} unidade(s){aviso}")
            print(f"     {'Lote':>4}  {'Validade':<12}  {'Qtd':>5}  "
                  f"{'Venda':>9}  Situação")
            print("     " + "─" * 52)

            for i, lote in enumerate(lotes_produto, start=1):
                dias = lote.dias_para_vencer()
                if lote.esta_vencido():
                    situacao = "VENCIDO ⚠️"
                elif dias <= 7:
                    situacao = f"vence em {dias}d ⚠️"
                else:
                    situacao = f"vence em {dias}d"
                print(
                    f"     {i:>4}.  "
                    f"{lote.validade.strftime('%d/%m/%Y'):<12}  "
                    f"{lote.quantidade:>5}  "
                    f"R${lote.preco_venda:>7.2f}  "
                    f"{situacao}"
                )

        print("\n" + "=" * 68)
        print(
            f"  Produtos distintos: {len(nomes_unicos):>3} | "
            f"Lotes na fila: {self.__fila_estoque.tamanho:>3}"
        )

    def consultar_produto(self, nome: str) -> None:
        """
        Exibe detalhes completos de todos os lotes de um produto específico,
        com data de validade, quantidades e preços individuais por lote.

        Parâmetros:
            nome : nome do produto a ser consultado.
        """
        nome_normalizado = nome.strip().title()
        lotes = [l for l in self.__fila_estoque.listar() if l.nome == nome_normalizado]

        if not lotes:
            print(f"\n  ❌ Produto '{nome_normalizado}' não encontrado no estoque.")
            return

        total_unidades = sum(l.quantidade for l in lotes)

        print(f"\n" + "=" * 70)
        print(f"  🔍  PRODUTO: {nome_normalizado}")
        print("=" * 70)
        print(f"  Lotes em estoque: {len(lotes)} | Total de unidades: {total_unidades}")
        print()
        print(f"  {'Lote':>4}  {'Validade':<12}  {'Qtd':>5}  "
              f"{'Custo':>9}  {'Venda':>9}  {'Margem':>8}  Situação")
        print("  " + "─" * 67)

        for i, lote in enumerate(lotes, start=1):
            dias   = lote.dias_para_vencer()
            margem = lote.preco_venda - lote.preco_compra
            if lote.esta_vencido():
                situacao = "VENCIDO ⚠️"
            elif dias <= 7:
                situacao = f"vence em {dias}d ⚠️"
            else:
                situacao = f"vence em {dias}d"
            print(
                f"  {i:>4}.  "
                f"{lote.validade.strftime('%d/%m/%Y'):<12}  "
                f"{lote.quantidade:>5}  "
                f"R${lote.preco_compra:>7.2f}  "
                f"R${lote.preco_venda:>7.2f}  "
                f"R${margem:>6.2f}  "
                f"{situacao}"
            )

        print("  " + "=" * 70)
