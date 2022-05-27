from concurrent import futures

import grpc
import time

import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc


class ChatServer(rpc.ChatServerServicer):  # herdando aqui do arquivo protobuf rpc que é gerado

    def __init__(self):
        # Lista com todo o histórico do chat
        self.chats = []

    # O fluxo que será usado para enviar novas mensagens aos clientes
    def ChatStream(self, request_iterator, context):
        """
        Esta é uma chamada do tipo de fluxo de resposta. Isso significa que o servidor pode continuar enviando mensagens
        Todo cliente abre essa conexão e espera o servidor enviar novas mensagens

        :param request_iterator:
        :param context:
        :return:
        """
        lastindex = 0
        # Para cada cliente, um loop infinito é iniciado (no próprio thread gerenciado do gRPC)
        while True:
            # Check if there are any new messages
            while len(self.chats) > lastindex:
                n = self.chats[lastindex]
                lastindex += 1
                yield n

    def SendNote(self, request: chat.Note, context):
        """
        Este método é chamado quando um cliente envia uma Nota para o servidor.

        :param request:
        :param context:
        :return:
        """
        # isso é apenas para o console do servidor
        print("[{}] {}".format(request.name, request.message))
        # Adicione-o ao histórico de bate-papo
        self.chats.append(request)
        return chat.Empty()  # algo precisa ser retornado requerido pela linguagem protobuf, apenas retornamos a msg vazia


if __name__ == '__main__':
    port = 11912 # uma porta aleatória para o servidor rodar
     # os workers é como a quantidade de threads que podem ser abertos ao mesmo tempo, quando há 10 clientes conectados
     # então não há mais clientes capazes de se conectar ao servidor.
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))  # criar um servidor gRPC
    rpc.add_ChatServerServicer_to_server(ChatServer(), server)  # registrar o servidor no gRPC
    # gRPC basicamente gerencia toda a lógica de threading e resposta do servidor, o que é perfeito!
    print('Starting server. Listening...')
    server.add_insecure_port('[::]:' + str(port))
    server.start()
    # O servidor inicia em segundo plano (em outro thread), então continue esperando
    # se não esperarmos aqui, a thread principal terminará, o que encerrará todas as threads filhas e, portanto, as threads
    # do servidor não continuará funcionando e parará o servidor
    while True:
        time.sleep(64 * 64 * 100)
