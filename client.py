import threading
from tkinter import *
from tkinter import simpledialog

import grpc

import proto.chat_pb2 as chat
import proto.chat_pb2_grpc as rpc

address = 'localhost'
port = 11912


class Client:

    def __init__(self, u: str, window):
        # o quadro para colocar os componentes da interface do usuário
        self.window = window
        self.username = u
        # criar um canal gRPC + stub
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.ChatServerStub(channel)
        # crie um novo thread de escuta para quando novos fluxos de mensagens chegarem
        threading.Thread(target=self.__listen_for_messages, daemon=True).start()
        self.__setup_ui()
        self.window.mainloop()

    def __listen_for_messages(self):
        """
        Este método será executado em um encadeamento separado como o encadeamento principal/ui, porque a chamada for-in está bloqueando
         ao aguardar novas mensagens
        """
        for note in self.conn.ChatStream(chat.Empty()):  # esta linha irá aguardar novas mensagens do servidor!
            print("R[{}] {}".format(note.name, note.message))  # declaração de depuração
            self.chat_list.insert(END, "[{}] {}\n".format(note.name, note.message))  # adicionar a mensagem à interface do usuário

    def send_message(self, event):
        """
        Este método é chamado quando o usuário digita algo na caixa de texto
        """
        message = self.entry_message.get()  # recuperar mensagem da interface do usuário
        if message is not '':
            n = chat.Note()  # criar mensagem protobuf (chamada Nota)
            n.name = self.username  # definir o nome de usuário
            n.message = message  # definir a mensagem real da nota
            print("S[{}] {}".format(n.name, n.message))  # declaração de depuração
            self.conn.SendNote(n)  # enviar a nota para o servidor

    def __setup_ui(self):
        self.chat_list = Text()
        self.chat_list.pack(side=TOP)
        self.lbl_username = Label(self.window, text=self.username)
        self.lbl_username.pack(side=LEFT)
        self.entry_message = Entry(self.window, bd=5)
        self.entry_message.bind('<Return>', self.send_message)
        self.entry_message.focus()
        self.entry_message.pack(side=BOTTOM)


if __name__ == '__main__':
    root = Tk()  # Acabei de usar uma janela Tk muito simples para a interface do usuário de bate-papo, isso pode ser substituído por qualquer coisa
    frame = Frame(root, width=300, height=300)
    frame.pack()
    root.withdraw()
    username = None
    while username is None:
        # recuperar um nome de usuário para que possamos distinguir todos os diferentes clientes
        username = simpledialog.askstring("Username", "What's your username?", parent=root)
    root.deiconify()  # não lembro mais porque isso era necessário...
    c = Client(username, frame)  # isso inicia um cliente e, portanto, um thread que mantém a conexão com o servidor aberta
