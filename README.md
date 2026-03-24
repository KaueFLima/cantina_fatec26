# Cantina_Fatec26
Cantina Virtual da Fatec

Pré Requisitos:
Python
Faker (Biblioteca Python)

Para rodar o aplicativo, clone o repositório e execute o arquivo "app.py"


Funcionalidade:

Adicionar lote                Insere produto com preço, validade e quantidade na fila FIFO 
Listar estoque                Percorre a fila e exibe lotes em ordem (mais antigo primeiro) 
Realizar venda                Debita do lote mais antigo + registra pagamento PIX simulado  
Editar quantidade             Altera manualmente a quantidade de um lote na fila            
Remover vencidos              Varre a fila e descarta lotes com validade expirada           
Relatório de consumo          Exibe margens de lucro e investimento por produto             
Histórico de pagamentos       Lista todas as transações PIX registradas                     
Buscar/cancelar pagamento     Localiza ou remove transação pelo ID único                    
Relatório de vendas           Consolidado por produto, categoria (Aluno/Prof.) e curso      
Salvar / Carregar (Pickle)    Persiste toda a estrutura encadeada entre sessões             
