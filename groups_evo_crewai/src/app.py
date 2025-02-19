# filepath: groups_evo_crewai/src/app.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

print("COMEÇANDO A EXECUTAR O SCRIPT\n")
print("AGUARDE...\n")

import time
import argparse
from datetime import datetime, timedelta
from group_controller import GroupController
from summary_crew import SummaryCrew
from send_sandeco import SendSandeco

parser = argparse.ArgumentParser()
parser.add_argument("--task_name", required=True, help="Nome da tarefa agendada")
args = parser.parse_args()

group_id = args.task_name.split("_")[1]

control = GroupController()
df = control.load_data_by_group(group_id)
nome = control.find_group_by_id(group_id).name

if not df:
    control.update_summary(group_id, '22:00', True, False, False, __file__)
    df = control.load_data_by_group(group_id)

print("----------------------\n")
print("EXECUTANDO TAREFA AGENDADA\n")
print(f"Resumo do grupo : {nome}\n")

if df and df.get('enabled', False):
    data_atual = datetime.now()
    data_anterior = data_atual - timedelta(days=1)

    formato = "%Y-%m-%d %H:%M:%S"
    data_atual_formatada = data_atual.strftime(formato)
    data_anterior_formatada = data_anterior.strftime(formato)

    print(f"Data atual: {data_atual_formatada}")
    print(f"Data de 1 dia anterior: {data_anterior_formatada}")

    msgs = control.get_messages(group_id, data_anterior_formatada, data_atual_formatada)

    cont = len(msgs)
    print(f"Total de mensagens: {cont}")

    time.sleep(20)

    pull_msg = f"""
        Dados sobre as mensagens do grupo
        Data Inicial: {data_anterior_formatada}
        Data Final: {data_atual_formatada}
        
        MENSAGENS DOS USUÁRIOS PARA O RESUMO:
        --------------------------
        
        """

    for msg in reversed(msgs):
        pull_msg = pull_msg + f"""
            Nome: *{msg.get_name()}*
            Postagem: "{msg.get_text()}"  
            data: {time.strftime("%d/%m %H:%M", time.localtime(msg.message_timestamp))}'     
            """

    print(pull_msg)

    inputs = {
        "msgs": pull_msg
    }

    summary_crew = SummaryCrew()
    resposta = summary_crew.kickoff(inputs=inputs)

    evo_send = SendSandeco()
    evo_send.textMessage(group_id, resposta)

    log_path = os.path.dirname(__file__)
    nome_arquivo = os.path.join(log_path, "log_summary.txt")

    with open(nome_arquivo, "a", encoding="utf-8") as arquivo:
        log = f"""[{data_atual}] [INFO] [GRUPO: {nome}] [GROUP_ID: {group_id}] - Mensagem: Resumo gerado e enviado com sucesso!"""
        arquivo.write(log)
else:
    print("Grupo não encontrado ou resumo não está habilitado para este grupo.")