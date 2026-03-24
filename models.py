"""
models.py — Estruturas de Dados Manuais
========================================
Implementação manual de Nodo, Fila (FIFO) e Lista Encadeada
utilizando ponteiros (self.proximo), sem uso de list, set ou dict
para armazenamento principal dos dados.
"""


class Nodo:
    """
    Unidade básica de armazenamento nas estruturas encadeadas.
    Cada nodo guarda um dado e aponta para o próximo nodo.
    """

    def __init__(self, dado):
        """
        Parâmetros:
            dado: qualquer objeto a ser armazenado no nodo.
        """
        self.dado = dado
        self.proximo = None  # ponteiro para o próximo nodo

    def __repr__(self):
        return f"Nodo({self.dado})"


# ---------------------------------------------------------------------------
# FILA (FIFO) — usada para o estoque de produtos perecíveis
# ---------------------------------------------------------------------------

class Fila:
    """
    Fila encadeada com política FIFO (First In, First Out).
    O primeiro lote a entrar no estoque é o primeiro a ser consumido.

    Atributos privados:
        __inicio : aponta para o nodo mais antigo (frente da fila)
        __fim    : aponta para o nodo mais recente (fundo da fila)
        __tamanho: contador de nodos presentes
    """

    def __init__(self):
        self.__inicio = None
        self.__fim = None
        self.__tamanho = 0

    # ---- Propriedades ----

    @property
    def tamanho(self) -> int:
        """Retorna o número de nodos na fila."""
        return self.__tamanho

    def esta_vazia(self) -> bool:
        """Retorna True se a fila não contiver nenhum nodo."""
        return self.__inicio is None

    # ---- Operações principais ----

    def enfileirar(self, dado) -> None:
        """
        Insere um novo dado no final da fila (entrada de lote).

        Parâmetros:
            dado: objeto a ser inserido.
        """
        novo_nodo = Nodo(dado)
        if self.__fim is None:
            # Fila estava vazia: início e fim apontam para o mesmo nodo
            self.__inicio = novo_nodo
            self.__fim = novo_nodo
        else:
            self.__fim.proximo = novo_nodo
            self.__fim = novo_nodo
        self.__tamanho += 1

    def desenfileirar(self):
        """
        Remove e retorna o dado do início da fila (saída do lote mais antigo).

        Retorna:
            O dado do nodo removido, ou None se a fila estiver vazia.
        """
        if self.__inicio is None:
            return None

        dado_removido = self.__inicio.dado
        self.__inicio = self.__inicio.proximo

        # Se a fila ficou vazia após remoção, atualiza o ponteiro do fim
        if self.__inicio is None:
            self.__fim = None

        self.__tamanho -= 1
        return dado_removido

    def buscar(self, criterio) -> object:
        """
        Percorre a fila e retorna o PRIMEIRO dado que satisfaça o critério.

        Parâmetros:
            criterio: função lambda/callable que recebe um dado e retorna bool.

        Retorna:
            O dado encontrado, ou None se não houver correspondência.
        """
        atual = self.__inicio
        while atual is not None:
            if criterio(atual.dado):
                return atual.dado
            atual = atual.proximo
        return None

    def remover(self, criterio) -> object:
        """
        Percorre a fila e remove o PRIMEIRO nodo cujo dado satisfaça o critério.

        Parâmetros:
            criterio: função lambda/callable que recebe um dado e retorna bool.

        Retorna:
            O dado do nodo removido, ou None se não encontrado.
        """
        atual = self.__inicio
        anterior = None

        while atual is not None:
            if criterio(atual.dado):
                if anterior is None:
                    # Remoção do nodo do início
                    self.__inicio = atual.proximo
                    if self.__inicio is None:
                        self.__fim = None
                else:
                    # Remoção de nodo intermediário ou final
                    anterior.proximo = atual.proximo
                    if atual.proximo is None:
                        self.__fim = anterior

                self.__tamanho -= 1
                return atual.dado

            anterior = atual
            atual = atual.proximo

        return None  # não encontrado

    def listar(self) -> list:
        """
        Percorre toda a fila e retorna uma lista Python temporária com os dados.
        NOTA: a lista retornada é apenas uma visão auxiliar para exibição/relatório;
        os dados reais residem nos nodos encadeados.

        Retorna:
            Lista temporária com todos os dados na ordem da fila.
        """
        resultado = []
        atual = self.__inicio
        while atual is not None:
            resultado.append(atual.dado)
            atual = atual.proximo
        return resultado

    def __repr__(self):
        itens = self.listar()
        return f"Fila({len(itens)} nodo(s))"


# ---------------------------------------------------------------------------
# LISTA ENCADEADA SIMPLES — usada para o histórico de pagamentos
# ---------------------------------------------------------------------------

class ListaEncadeada:
    """
    Lista encadeada simples para registro histórico de operações.
    Novos registros são inseridos no final (ordem cronológica).

    Atributos privados:
        __cabeca  : aponta para o primeiro nodo da lista
        __tamanho : contador de nodos presentes
    """

    def __init__(self):
        self.__cabeca = None
        self.__tamanho = 0

    # ---- Propriedades ----

    @property
    def tamanho(self) -> int:
        """Retorna o número de nodos na lista."""
        return self.__tamanho

    def esta_vazia(self) -> bool:
        """Retorna True se a lista estiver vazia."""
        return self.__cabeca is None

    # ---- Operações principais ----

    def inserir(self, dado) -> None:
        """
        Insere um novo dado no FINAL da lista (ordem cronológica).

        Parâmetros:
            dado: objeto a ser inserido.
        """
        novo_nodo = Nodo(dado)

        if self.__cabeca is None:
            self.__cabeca = novo_nodo
        else:
            atual = self.__cabeca
            while atual.proximo is not None:
                atual = atual.proximo
            atual.proximo = novo_nodo

        self.__tamanho += 1

    def remover(self, criterio) -> object:
        """
        Remove o PRIMEIRO nodo cujo dado satisfaça o critério.

        Parâmetros:
            criterio: função lambda/callable que recebe um dado e retorna bool.

        Retorna:
            O dado removido, ou None se não encontrado.
        """
        atual = self.__cabeca
        anterior = None

        while atual is not None:
            if criterio(atual.dado):
                if anterior is None:
                    self.__cabeca = atual.proximo
                else:
                    anterior.proximo = atual.proximo

                self.__tamanho -= 1
                return atual.dado

            anterior = atual
            atual = atual.proximo

        return None  # não encontrado

    def buscar(self, criterio) -> object:
        """
        Percorre a lista e retorna o PRIMEIRO dado que satisfaça o critério.

        Parâmetros:
            criterio: função lambda/callable que recebe um dado e retorna bool.

        Retorna:
            O dado encontrado, ou None.
        """
        atual = self.__cabeca
        while atual is not None:
            if criterio(atual.dado):
                return atual.dado
            atual = atual.proximo
        return None

    def listar(self) -> list:
        """
        Percorre toda a lista e retorna uma lista Python temporária com os dados.
        NOTA: lista auxiliar apenas para exibição; dados reais estão nos nodos.

        Retorna:
            Lista temporária com todos os dados em ordem de inserção.
        """
        resultado = []
        atual = self.__cabeca
        while atual is not None:
            resultado.append(atual.dado)
            atual = atual.proximo
        return resultado

    def __repr__(self):
        return f"ListaEncadeada({self.__tamanho} nodo(s))"
