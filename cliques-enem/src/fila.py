class No:
    """
    classe auxiliar que representa cada elemento dentro da Fila como um nó
    guarda a informação (dado) e aponta para o próximo elemento da fila
    """
    def __init__(self, dado):
        self.dado = dado
        self.proximo = None

class Fila:
    #implementação da fila em si
    def __init__(self):
        self.primeiro = None  #aponta para o primeiro elemento da fila (quem vai sair primeiro)
        self.ultimo = None     #aponta para o último elemento da fila (quem acabou de entrar)
        self.tamanho = 0    #mantém o controle do número de elementos na fila

    def enfileirar(self, dado):
        #Adiciona um novo elemento ao final da fila.
        novo_no = No(dado)
        if self.esta_vazia():
            #se a fila está vazia, o novo nó é o primeiro e o último ao mesmo tempo
            self.primeiro = novo_no
            self.ultimo = novo_no
        else:
            #caso contrário, o novo nó se torna o próximo do último e depois é o novo último
            self.ultimo.proximo = novo_no
            self.ultimo = novo_no
        
        self.tamanho += 1

    def desenfileirar(self):
        #remove e retorna o elemento do início da fila
        if self.esta_vazia():
            raise IndexError("A fila está vazia. Não é possível desenfileirar.")
            self.ultimo = None
            
        #pega o dado do primeiro da fila
        dado_removido = self.primeiro.dado
        
        #o segundo da fila passa a ser o novo 'primeiro'
        self.primeiro = self.primeiro.proximo
        self.tamanho -= 1
        
        return dado_removido

    def esta_vazia(self):
        #verifica se a fila está vazia
        return self.tamanho == 0
    
    def obter_tamanho(self):
        #Rretorna o número de elementos na fila
        return self.tamanho