# app.py

import sys                                      # Importa o módulo sys para interagir com parâmetros e funcionalidades do sistema
import os                                       # Importa o módulo os para interagir com o sistema de arquivos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Adiciona o diretório pai ao PATH para permitir importações de módulos do projeto

print("COMEÇANDO A EXECUTAR O SCRIPT\n")       # Imprime uma mensagem indicando o início da execução do script
print("AGUARDE...\n")                           # Imprime uma mensagem solicitando ao usuário que aguarde

import os                                       # Importa novamente o módulo os (pode ser redundante)
import time                                     # Importa o módulo time para manipular delays e tempos de espera
import argparse                                 # Importa argparse para fazer o parser de argumentos de linha de comando
from datetime import datetime, timedelta        # Importa datetime e timedelta para manipulação de datas e cálculos de intervalos
from group_controller import GroupController    # Importa a classe GroupController para manipular dados e operações dos grupos
from summary_crew import SummaryCrew            # Importa a classe SummaryCrew para gerar resumos com IA
from send_sandeco import SendSandeco            # Importa a classe SendSandeco para enviar mensagens via API da Evolution

# Cria o parser para argumentos de linha de comando
parser = argparse.ArgumentParser()              # Instancia um objeto ArgumentParser para gerenciar argumentos do script
parser.add_argument("--task_name", required=True, help="Nome da tarefa agendada")  # Define o argumento obrigatório "task_name"
args = parser.parse_args()                      # Faz o parse dos argumentos passados na linha de comando

group_id = args.task_name.split("_")[1]         # Extrai o group_id a partir do argumento task_name, assumindo que está no formato "Algo_<group_id>"

control = GroupController()                     # Instancia o controlador de grupos para acessar funções de manipulação de dados e API
df = control.load_data_by_group(group_id)         # Carrega as informações do grupo específico a partir do CSV, utilizando o group_id
nome = control.find_group_by_id(group_id).name    # Busca o objeto grupo pelo ID e obtém seu nome

# Garante que as informações do resumo do grupo estejam inseridas no arquivo group_summary.csv
if not df:                                      # Verifica se não há dados para o grupo (df é falso ou vazio)
    control.update_summary(group_id, '22:00', True, False, False, __file__)  # Atualiza/insere as configurações de resumo para o grupo com horário '22:00', habilitado e sem links ou nomes
    df = control.load_data_by_group(group_id)   # Recarrega os dados do grupo após a atualização

print("----------------------\n")                # Imprime uma linha separadora para melhor visualização no console
print("EXECUTANDO TAREFA AGENDADA\n")            # Informa que a tarefa agendada está sendo executada
print(f"Resumo do grupo : {nome}\n")             # Exibe o nome do grupo para o qual o resumo está sendo gerado

if df and df.get('enabled', False):             # Verifica se os dados do grupo existem e se o resumo está habilitado para esse grupo
    data_atual = datetime.now()                 # Obtém a data e hora atual
    data_anterior = data_atual - timedelta(days=1)  # Calcula a data de 1 dia antes da data atual

    formato = "%Y-%m-%d %H:%M:%S"                # Define o formato desejado para as datas
    data_atual_formatada = data_atual.strftime(formato)      # Formata a data atual para uma string
    data_anterior_formatada = data_anterior.strftime(formato)  # Formata a data de 1 dia anterior para uma string

    print(f"Data atual: {data_atual_formatada}")  # Exibe a data atual formatada no console
    print(f"Data de 1 dia anterior: {data_anterior_formatada}")  # Exibe a data de um dia anterior formatada

    msgs = control.get_messages(group_id, data_anterior_formatada, data_atual_formatada)  # Busca as mensagens do grupo entre as datas formatadas

    cont = len(msgs)                            # Calcula o total de mensagens retornadas
    print(f"Total de mensagens: {cont}")         # Exibe o total de mensagens encontradas

    time.sleep(20)                              # Aguarda 20 segundos antes de processar as mensagens (pode ser para garantir a disponibilidade de dados)

    pull_msg = f"""
        Dados sobre as mensagens do grupo
        Data Inicial: {data_anterior_formatada}
        Data Final: {data_atual_formatada}
        
        MENSAGENS DOS USUÁRIOS PARA O RESUMO:
        --------------------------
        
        """  # Inicializa a string pull_msg com cabeçalho e informações sobre o intervalo de datas

    for msg in reversed(msgs):                   # Itera sobre as mensagens na ordem inversa (do mais antigo para o mais recente)
            pull_msg = pull_msg + f"""
            Nome: *{msg.get_name()}*
            Postagem: "{msg.get_text()}"  
            data: {time.strftime("%d/%m %H:%M", time.localtime(msg.message_timestamp))}'     
            """  # Acrescenta cada mensagem à string pull_msg formatando com nome, texto e data da mensagem

    print(pull_msg)                             # Exibe a mensagem completa de pull_msg no console
    
    inputs = {
        "msgs": pull_msg                       # Prepara um dicionário com as mensagens para envio como input ao SummaryCrew
    }
    
    summary_crew = SummaryCrew()               # Instancia a classe SummaryCrew para gerar o resumo usando IA
    resposta = summary_crew.kickoff(inputs=inputs)  # Executa o processo de resumo com os inputs e armazena o resultado em "resposta"

    evo_send = SendSandeco()                   # Instancia o objeto SendSandeco para enviar mensagens via API
    evo_send.textMessage(group_id, resposta)   # Envia a mensagem de texto com o resumo gerado para o grupo identificado pelo group_id

    log_path = os.path.dirname(__file__)       # Determina o diretório atual onde o script está localizado
    nome_arquivo = os.path.join(log_path, "log_summary.txt")  # Define o caminho completo para o arquivo de log

    with open(nome_arquivo, "a", encoding="utf-8") as arquivo:  # Abre o arquivo de log no modo de anexação para não sobrescrever os logs anteriores
        log = f"""[{data_atual}] [INFO] [GRUPO: {nome}] [GROUP_ID: {group_id}] - Mensagem: Resumo gerado e enviado com sucesso!"""  
        # Cria uma string de log contendo data, informações do grupo e status do envio do resumo
        arquivo.write(log)                      # Escreve a mensagem de log no arquivo
else:
    print("Grupo não encontrado ou resumo não está habilitado para este grupo.")  # Informa que não há dados ou que o resumo não está habilitado