import google.generativeai as gemini
import pyttsx3
import speech_recognition as sr
import tkinter as tk
import threading
import time
from pygame import mixer
import sqlite3 as sql
import math


def main():
    global x
    global historico
    global numero

    Ligar.configure(text="Interromper", bg= 'pink', command=interromper)

    Enviar.pack(side='left')

    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        audio = r.listen(source)

    while not (x == 'enviar' or x == 'interromper'): time.sleep(0.1)


    if x == 'interromper':
        Ligar.configure(text="Falar", bg= 'light green', command=iniciar)
        Enviar.pack_forget()
        mostrar_buttons()

    else:

        Enviar.pack_forget()

        Ligar.configure(text='Falar', command=iniciar, bg='light green')

        try:
            texto = r.recognize_google(audio, language="pt-BR")

            Fala.insert('1.0', texto.replace(('*'), ('\n')))

            resposta = chat.send_message(texto)
            resposta = resposta.text.replace('*', '\n').replace('\n\n', '\n').replace('\n\n\n', '\n\n')

            Resposta.insert('1.0', resposta)

            numero += 1

            historico.append({numero: [texto, resposta]})

            texto_em_audio(resposta)

        except Exception as e:

            if 'block_reason:' in str(e):
                Resposta.insert('1.0', 'Mensagem bloqueada, tente de novo.')
                texto_em_audio('Mensagem bloqueada, tente de novo.')
            
            else:
                Resposta.insert('1.0', 'Não entendi o que você disse, tente de novo.')
                texto_em_audio('Não entendi o que você disse, tente de novo.')
        
        reprodução()
        mostrar_buttons()


def texto_em_audio(texto):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('rate', 250)
    engine.setProperty('voice', voices[0].id)
    engine.save_to_file(texto, 'audio.wav')
    engine.runAndWait()

def mostrar_buttons():
    pausar.pack(side='left')
    reproduzir.pack(side='left')
    Enviar_texto.pack(side='left')
    lista.pack(side='left')
    narrar_seleção.pack(side='left')

def enviar():
    global x
    x = 'enviar'

def iniciar():
    global x
    global mixer
    try:
        mixer.music.stop()
        mixer.quit()
    except: pass
    x = ''
    try:
        narrar_seleção.pack_forget()
        lista.pack_forget()
        pausar.pack_forget()
        reproduzir.pack_forget()
        Enviar_texto.pack_forget()
        Fala.delete('1.0', 'end')
        Resposta.delete('1.0', 'end')
    except: pass
    threading.Thread(target=main).start()

def interromper():
    global x
    x = 'interromper'

def pausar_audio():
    global mixer
    mixer.music.pause()
    pausar.configure(text='despausar audio', command=despausar, bg='light green')

def despausar():
    global mixer
    mixer.music.unpause()
    pausar.configure(text='pausar audio', command=pausar_audio, bg='pink')

def reprodução():
    if audio:
        mixer.init()
        mixer.music.load('audio.wav')
        mixer.music.play()

def enviar_texto():
    global numero
    global historico
    try:
        mixer.music.stop()
        mixer.quit()
    except: pass
    Resposta.delete('1.0', 'end')
    texto = Fala.get('1.0', 'end-1c')
    resposta = chat.send_message(texto)
    resposta = resposta.text.replace('*', '\n').replace('\n\n', '\n').replace('\n\n\n', '\n\n')
    numero += 1
    historico.append({numero: [texto, resposta]})
    Resposta.insert('1.0', resposta)
    texto_em_audio(resposta)
    mostrar_buttons()
    reprodução()

def permitir_audio():
    global audio
    if audio:
        audio = False
        Controle_audio.configure(text='Áudio off', bg='pink')
        try:
            mixer.music.stop()
            mixer.quit()
        except: pass

    else:
        audio = True
        Controle_audio.configure(text='Áudio on', bg='light green')


def historico_buttons():
    def get_table_content():
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_content = {}

        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name};")
            content = cursor.fetchall()
            table_content[table_name] = content

        return table_content
    

    def mensagens_das_conversas(table_name):

        mensagens = tk.Toplevel(janela, bg='light blue')
        mensagens.title("Mensagens")
        mensagens.geometry('396x360')

        frame = tk.Frame(mensagens, bg='light blue')
        canvas = tk.Canvas(frame, bg='light blue')
        scrollbar = tk.Scrollbar(frame, orient='vertical', command=canvas.yview, bg='light blue')
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        canvas.pack(side='left', fill='both', expand=True)
        canvas.bind('<Configure>', on_configure)
        buttons_frame = tk.Frame(canvas, padx=6, bg='light blue')
        
        for tupla in table_names[table_name]:
            button = tk.Button(buttons_frame, bg='light green', text=tupla[1][:40], command=lambda fala_resposta=[tupla[1], tupla[2]] : mostrar_conversa(fala_resposta), font=('Arial',14))
            button.pack(pady=3)

        canvas.create_window((0, 0), window=buttons_frame, anchor='nw')
        frame.pack(fill='both', expand=True)
        
        mensagens.mainloop()

    
    def mostrar_conversa(fala_resposta):
        Fala.delete("1.0", tk.END)
        Resposta.delete("1.0", tk.END)
        Fala.insert('1.0', fala_resposta[0])
        Resposta.insert('1.0', fala_resposta[1])
        texto_em_audio(fala_resposta[1])
        reprodução()

        try:
            mostrar_buttons()
        except: pass


    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox('all'))


    table_names = get_table_content()
    
    lista_conversas = tk.Toplevel(janela, bg='light blue')
    lista_conversas.title("Conversas")
    lista_conversas.geometry('150x360')

    frame = tk.Frame(lista_conversas, bg='light blue')
    canvas = tk.Canvas(frame, bg='light blue')
    scrollbar = tk.Scrollbar(frame, orient='vertical', command=canvas.yview, bg='light blue')
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')
    canvas.pack(side='left', fill='both', expand=True)
    canvas.bind('<Configure>', on_configure)
    buttons_frame = tk.Frame(canvas, padx=6, bg='light blue')

    for table_name, listas in table_names.items():
        button = tk.Button(buttons_frame, bg='light green', text=table_name, command=lambda name=table_name: mensagens_das_conversas(name), font=('Arial', 14))
        button.pack(pady=3)
    
    canvas.create_window((0, 0), window=buttons_frame, anchor='nw')
    frame.pack(fill='both', expand=True)

    lista_conversas.mainloop()


def ajuste_tamanho():
    width = janela.winfo_width()
    height = janela.winfo_height()
    Fala.configure(width=math.floor((width * 78) / 720), height=math.floor((height * 2) / 720))
    Resposta.configure(width=math.floor((width * 78) / 720), height=math.floor((height * 36) / 720))

def narrar():
    global mixer
    try:
        mixer.music.stop()
        mixer.quit()
    except: pass
    texto_selhecionado = Resposta.get("sel.first", "sel.last")
    texto_em_audio(texto_selhecionado) 
    reprodução()


banco = sql.connect('conversas.db')
cursor = banco.cursor()

audio = False
numero = 0
historico = []

x = ''
gemini.configure(api_key="")

model = gemini.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

janela = tk.Tk()
janela.title('Fale com o Gemini Pro')
janela.geometry('720x720')
janela.configure(bg='light blue')

button_frame = tk.Frame(janela, bg='light blue')
button_frame.pack(pady=6)

Ligar = tk.Button(button_frame, text='Falar', command=iniciar, bg='light green', font=('Arial', 14))
Ligar.pack(side='left')

pausar = tk.Button(button_frame, text='Pausar áudio', command=pausar_audio, bg='pink', font=('Arial', 14))

Controle_audio = tk.Button(button_frame, text='Áudio off', command=permitir_audio, bg='pink', font=('Arial', 14))
Controle_audio.pack(side='left')

reproduzir = tk.Button(button_frame, text='Repetir áudio', command=reprodução, bg='light yellow', font=('Arial', 14))

Enviar = tk.Button(button_frame, text='Enviar', command=enviar, bg='light green', font=('Arial', 14))

Enviar_texto = tk.Button(button_frame, text='Enviar', command=enviar_texto, bg='light green', font=('Arial', 14))
Enviar_texto.pack(side='left')

narrar_seleção = tk.Button(button_frame, text='Narrar seleção', command=narrar, bg='light green', font=('Arial', 14))

lista = tk.Button(button_frame, text='Histórico', command=historico_buttons, bg='light green', font=('Arial', 14))
lista.pack(side='left')

Fala = tk.Text(janela, height=2, width=78, font=("Arial", 12), wrap="word", bg='light grey')
Fala.pack()

Resposta = tk.Text(janela, height=36, width=78, font=("Arial", 12), wrap="word", bg='light grey')
Resposta.pack(pady=6)

def ajuste(evento):
    ajuste_tamanho()

janela.bind('<Configure>', ajuste)

janela.mainloop()

if historico:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = len(cursor.fetchall())

    if tabelas == 99:
        tabelas_ordenadas = sorted(tabelas, key=lambda tabela: tabela[0])
        tabela_antiga = tabelas_ordenadas[0][0]
        cursor.execute(f"DROP TABLE IF EXISTS {tabela_antiga}")
        cursor.execute(f'CREATE TABLE {str(tabela_antiga)} (id INTEGER, fala TEXT, resposta TEXT)')
        for mensagem in historico:
            for item in mensagem:
                cursor.execute(f'INSERT INTO {str(tabela_antiga)} VALUES (?, ?, ?)', (item, mensagem[item][0], mensagem[item][1]))

    cursor.execute(f'CREATE TABLE Conversa{str(tabelas + 1)} (id INTEGER, fala TEXT, resposta TEXT)')
    for mensagem in historico:
        for item in mensagem:
            cursor.execute(f'INSERT INTO Conversa{str(tabelas + 1)} VALUES (?, ?, ?)', (item, mensagem[item][0], mensagem[item][1]))

banco.commit()
cursor.close()
banco.close()