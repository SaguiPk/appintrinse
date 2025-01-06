from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty
from datetime import datetime, timedelta
import json
import os.path
import time
import pandas as pd
import telebot
from telas import *
from google_sheets import Url_Sheets


class MainApp(MDApp):
    def build(self):
        self.psico = ''
        self.horario = ''
        self.agenda_psico = None
        self.arq_nomes = None
        self.txt_input_nome = StringProperty('')
        self.txt_input_hora = StringProperty('')
        self.agora = datetime.now()
        #self.dic_dias = {'MONDAY':'SEGUNDA-FEIRA', 'TUESDAY':'TERÇA-FEIRA', 'WEDNESDAY':'QUARTA-FEIRA', 'THURSDAY':'QUINTA-FEIRA', 'FRIDAY':'SEXTA-FEIRA'}
        self.dic_dias = {0:'SEGUNDA-FEIRA', 1:'TERÇA-FEIRA', 2:'QUARTA-FEIRA', 3:'QUINTA-FEIRA', 4:'SEXTA-FEIRA'}
        self.dic_meses = {1:'janeiro', 2:'fevereiro', 3:'março', 4:'abril', 5:'maio', 6:'junho', 7:'julho', 8:'agosto', 9:'setembro', 10:'outubro', 11:'novembro', 12:'dezembro'}
        return Builder.load_file('main.kv')

    def atualizar_hora(self, dt):
        #locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        self.hora_formatada = self.agora.strftime("%H:%M")
        self.label_hr.text = self.hora_formatada

    def on_start(self):
# RELOGIO E DATA ---------------------------------------------------------------------
        #locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        #agora = datetime.now()
        #dia = self.agora.strftime("%A, %d de %B de %Y")

        label_dia = self.root.ids['homepage']
        label_dia = label_dia.ids['id_dia']
        label_dia.text = f'{self.dic_dias[self.agora.weekday()].lower()}, {self.agora.day} de {self.dic_meses[self.agora.month]} de {self.agora.year}' #dia

        self.label_hr = self.root.ids['homepage']
        self.label_hr = self.label_hr.ids['id_horario']
        Clock.schedule_interval(self.atualizar_hora, 1)

# FAZ A CONEXAO COM A PLANILHA --------------------------------------------------------
        self.psico_select = {}
        conexao = True #api.conexao

        if conexao:
            home = self.root.ids['homepage']
            texto = home.ids['id_conexao']
            texto.color = (0,1,0,1)
            texto.text = 'Conectado'
        else:
            pass

        if self.arq_nomes is None:
            if os.path.exists('nomes_psicos.json'):
                if int(time.time() - os.path.getmtime('nomes_psicos.json')) > 46800:
                    os.remove('nomes_psicos.json')
                    self.arq_nomes = Url_Sheets().titulos()
                    #self.arq_nomes = api.requerir_nomes()

                else:
                    with open('nomes_psicos.json', 'r') as arquivo:
                        dados = json.load(arquivo)
                    self.arq_nomes = dados
            else:
                self.arq_nomes = Url_Sheets().titulos()
                #self.arq_nomes = api.requerir_nomes()

                if self.arq_nomes is False:
                    sheets_url = Url_Sheets().titulos()
                    self.arq_nomes = sheets_url

        def selecionar(but):
            gerenciador_tela = self.root.ids['screen_manager']
            gerenciador_tela.current = 'nomecliente'
            botao_clicado = but
            psico = botao_clicado.id
            self.psico = psico
            # ESTRAIO A PLALINHA DO PSICO ----------------------------------------------------
            if os.path.exists(f'agenda_{psico}.csv'):
                if int(time.time() - os.path.getmtime(f'agenda_{psico}.csv')) > 3600:
                    os.remove(f'agenda_{psico}.csv')
                    self.agenda_psico = Url_Sheets().planilha(f'{psico}')
                    # self.agenda_psico = api.requerir_agenda(f'{self.psico}')
                else:
                    self.agenda_psico = pd.read_csv(f'agenda_{psico}.csv', sep=';')
            else:
                self.agenda_psico = Url_Sheets().planilha(f'{psico}')
                # self.agenda_psico = api.requerir_agenda(f'{self.psico}')

        for psico in self.arq_nomes:
            but = MDButton(MDButtonText(text=f'{psico}', bold=True, pos_hint={'center_x':.5, 'center_y': .5}, theme_font_size="Custom", font_size='20', theme_text_color="Custom", text_color=(130/255, 20/255, 235/255, 1), theme_font_name='Custom', font_name='Gotham-Rounded-Medium'), style="elevated", radius=[11,], theme_width="Custom", height="70dp", size_hint_x= 0.5)
            but.id = f'{psico}'
            page_psicos =self.root.ids['psicos']
            page_psicos.ids['main_scroll'].add_widget(but)
            but.bind(on_press=lambda x: selecionar(x))
            self.psico_select[but] = psico

    def mudar_tela(self, id_tela):
        tela_psicos = self.root.ids['psicos']
        gerenciador_tela = self.root.ids['screen_manager']
        gerenciador_tela.current = id_tela

    def casa(self, time=0):
        gerenciador_tela = self.root.ids['screen_manager']
        nome_cliente = self.root.ids['nomecliente']
        input = nome_cliente.ids['id_input']
        input_hora = nome_cliente.ids['id_input_hora']
        envio_msg = self.root.ids['enviomsg']
        texto_msg = envio_msg.ids['id_msg']
        nome_cliente = self.root.ids['nomecliente']
        msg_erro = nome_cliente.ids['msg_erro']
        msg_erro.text = ' '
        texto_msg.text = ''
        input.text = ''
        input_hora.text = ''
        gerenciador_tela.current = 'homepage'


    def verificador(self, nome_paciente, horario_paciente):
        self.txt_input_nome = nome_paciente.text
        self.txt_input_hora = horario_paciente.text

        # Verifica se os campos estão vazios, se não estiver vazio:
        if self.txt_input_nome != '' and self.txt_input_hora != '':
            tela_enviomsg = self.root.ids['enviomsg']
            id_msg = tela_enviomsg.ids['id_msg']
            id_msg.text = ''
            self.paciente = nome_paciente.text
            self.horario = horario_paciente.text
            if ':' not in self.horario:
                self.horario = self.horario[:2] + ':' + self.horario[2:]
            #agendas = pd.read_excel(r'HORÁRIOS.xlsx', sheet_name=None)

            # colunas = list(self.agenda_psico.keys())
            lista_dias = ['SEGUNDA-FEIRA', 'TERÇA-FEIRA', 'QUARTA-FEIRA', 'QUINTA-FEIRA', 'SEXTA-FEIRA'] #colunas[1:-4]  # 5 dias

            df_hrs = self.agenda_psico['HORA/DIA']  # das 7h30 até 21h -> 28 horarios(linhas)

            #locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
            dia_hoje = self.agora.weekday()  #f'{self.agora.strftime("%A")}'
            dia_hoje = self.dic_dias[dia_hoje]

            pacientes_dia = self.agenda_psico[f'{dia_hoje.upper()}']

            def calcular_diferenca_em_segundos(hora1, hora2, tempo):

                segundos1 = hora1.hour * 3600 + hora1.minute * 60
                segundos2 = hora2.hour * 3600 + hora2.minute * 60
                diferenca_segundos = segundos2 - segundos1

                delta = timedelta(seconds=abs(diferenca_segundos))
                horas, resto = divmod(delta.seconds, 3600)
                minutos, segundos = divmod(resto, 60)

                resultado = []

                if diferenca_segundos <= 0:
                    if diferenca_segundos <= tempo:
                        resultado.append('Sessão já encerrada. Consulte a recepção.')
                    else:
                        resultado.append('Aguarde, você já será chamada(o).')
                else:
                    if horas != 0:
                        # print(f'Sua sessão começará daqui a {horas}hrs {minutos}min {segundos}seg')
                        resultado.append(f'Começará daqui a {horas}hrs {minutos}min.\n\nEntão, sente-se e relaxe :)\n\nA Psicóloga(o), já foi avisado')
                    else:  # h=0
                        if minutos != 0:
                            # print(f'Sua sessão começará daqui a {horas}hrs {minutos}min {segundos}seg')
                            resultado.append(f'Começará daqui a {minutos}min.\n\nEntão, sente-se e relaxe :)\n\nA Psicóloga(o), já foi avisado')
                        else:  # h=0
                            if segundos != 0:
                                # print(f'Sua sessão começará daqui a {horas}hrs {minutos}min {segundos}seg')
                                resultado.append(f'Começará daqui a {segundos}seg.\n\n')
                            else:
                                pass
                return resultado

            dia_semana_hoje = [dia_hoje.upper(), lista_dias[1]]
            chave_dsh = dia_semana_hoje[0]
            encontrou = False

            if encontrou is False:
                # Procura a pessoa no dia de hoje
                for i, nome in enumerate(self.agenda_psico[f'{chave_dsh}']):
                    horario_agenda_str = df_hrs.iloc[i]
                    horario_agenda = datetime.strptime(horario_agenda_str, "%H:%M")
                    str_hr_agenda = horario_agenda.strftime("%H:%M")
                    self.paciente = self.paciente.upper().strip()
                    nome = str(nome).strip()
                    # Verifica se o nome e horario do campo são os mesmo da linha i
                    if self.paciente in nome and self.horario == str_hr_agenda:
                        horarios_str = df_hrs.iloc[i]
                        horarios = datetime.strptime(horarios_str, "%H:%M")
                        str_hrs = horarios.strftime("%H:%M")
                        paciente_seguinte = pacientes_dia.iloc[i + 1]
                        try:
                            if nome == paciente_seguinte:
                                tempo_sessao = -3600  # 1 hora
                            else:
                                tempo_sessao = -1800  # 30 minutos
                        except:
                            tempo_sessao = -1800  # 30 minutos

                        resultado = calcular_diferenca_em_segundos(self.agora.time(), horarios, tempo_sessao)

                        id_msg.text = (f'[size=30]Bem Vindo {nome.title()}[/size]\n\n'
                                       f'[size=20]Hoje {chave_dsh.lower()} sua sessão é as {str_hrs}[/size]\n'
                                       f'[size=20]{resultado[0]}[/size]\n')

                        encontrou = True

                        bot = telebot.TeleBot(token='8079890566:AAEMXjtoZtI67YZPiA-hdDtorzCkf49Iums')
                        bot.send_message(chat_id='7389489862', text=f'{nome_paciente.text.upper()}')

                        Clock.schedule_once(callback=self.casa, timeout=10)

                        break
                    else:
                        pass

                # Se não encontrou no dia de hoje, vai procurar nos outros dias
                if encontrou is False:
                    for dia in lista_dias:
                        for i, pessoa in enumerate(self.agenda_psico[f'{dia}']):
                                if pd.notna(pessoa) and self.paciente in pessoa:
                                    horario_pessoa = df_hrs.iloc[i]
                                    id_msg.text = (f'[size=30]Bem Vindo {self.paciente.title()}[/size]\n\n'
                                                   f'[size=20]Sua sessão está agendada para {dia.lower()} as {horario_pessoa}[/size]\n'
                                                   f'[size=25]Consulte a recepção![/size]')
                                    encontrou = True
                                    Clock.schedule_once(callback=self.casa, timeout=10)
                                    break
                                else:
                                    pass
                    # Se não encontrar em nenhum dia
                    if encontrou is False:
                        id_msg.text = (f'[size=25]Paciente não encontrado. Consulte a recepção por gentileza ;)[/size]')
                        Clock.schedule_once(callback=self.casa, timeout=10)

            else:
                pass

            gerenciador_tela = self.root.ids['screen_manager']
            gerenciador_tela.current = 'enviomsg'
            nome_paciente.text = ''
            horario_paciente.text = ''

        else:
            #print('vazio')
            nome_cliente = self.root.ids['nomecliente']
            msg_erro = nome_cliente.ids['msg_erro']
            msg_erro.text = 'PREENCHA TODOS OS CAMPOS'

MainApp().run()
