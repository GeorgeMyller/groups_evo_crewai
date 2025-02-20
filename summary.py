"""
Sistema de Geração e Envio de Resumos de Grupos / Group Message Summary Generation and Sending System

PT-BR:
Este módulo implementa a geração automática de resumos das mensagens dos grupos.
Processa as mensagens de um período específico e utiliza CrewAI para gerar
um resumo inteligente que é enviado de volta ao grupo.

EN:
This module implements automatic group message summary generation.
It processes messages from a specific time period and uses CrewAI to generate
an intelligent summary that is sent back to the group.
"""

import sys
import os
import time
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv
from group_controller import GroupController
from summary_crew import SummaryCrew
from send_sandeco import SendSandeco

# Load environment variables / Carrega variáveis de ambiente
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Get WhatsApp number from environment / Obtém número do WhatsApp do ambiente
personal_number = os.getenv("WHATSAPP_NUMBER")
if personal_number:
    # Garante que o número está no formato correto
    personal_number = personal_number.strip()
    if not personal_number.endswith('@s.whatsapp'):
        personal_number = f"{personal_number}@s.whatsapp"

print(f"\nConfigurações carregadas:")
print(f"Número do WhatsApp: {personal_number}")
print(f"Base URL: {os.getenv('EVO_BASE_URL')}")
print(f"Instance Name: {os.getenv('EVO_INSTANCE_NAME')}")

# Initialize SendSandeco / Inicializa SendSandeco
evo_send = SendSandeco()

# Command line argument initialization / Inicialização dos argumentos de linha de comando
parser = argparse.ArgumentParser(description="Group Summary Generator / Gerador de Resumos de Grupo")
parser.add_argument("--task_name", required=True, 
                   help="Scheduled task identifier (formato: ResumoGrupo_[ID]) / Nome da tarefa agendada")
args = parser.parse_args()

# Extract group ID from task name / Extrai o ID do grupo do nome da tarefa
group_id = args.task_name.split("_")[1]

control = GroupController()
df = control.load_data_by_group(group_id)
nome = control.find_group_by_id(group_id).name

# Ensure group summary information is present in group_summary.csv
# Garante que as informações do resumo do grupo estejam no arquivo group_summary.csv
if not df:
    control.update_summary(group_id, '22:00', True, False, False, __file__)
    df = control.load_data_by_group(group_id)

print("EXECUTANDO TAREFA AGENDADA")
print(f"Resumo do grupo : {nome}")

if df and df.get('enabled', False):
    """
    Message Processing and Summary Generation / Processamento de Mensagens e Geração do Resumo
    
    PT-BR:
    - Calcula o intervalo de tempo para coleta (últimas 24 horas)
    - Recupera e formata as mensagens do período
    - Gera o resumo usando CrewAI
    - Envia o resultado de volta ao grupo
    
    EN:
    - Calculates time range for collection (last 24 hours)
    - Retrieves and formats messages from the period
    - Generates summary using CrewAI
    - Sends result back to the group
    """
    # Calculate time range for message collection
    # Calcula o intervalo de tempo para coleta de mensagens
    data_atual = datetime.now()
    data_anterior = data_atual - timedelta(days=1)

    formato = "%Y-%m-%d %H:%M:%S"
    data_atual_formatada = data_atual.strftime(formato)
    data_anterior_formatada = data_anterior.strftime(formato)

    print(f"Data atual: {data_atual_formatada}")
    print(f"Data de 1 dia anterior: {data_anterior_formatada}")

    # Retrieve messages for the specified time period
    # Recupera mensagens para o período especificado
    msgs = control.get_messages(group_id, data_anterior_formatada, data_atual_formatada)

    cont = len(msgs)
    print(f"Total de mensagens: {cont}")

    # Delay for processing
    # Aguarda processamento
    time.sleep(20)

    # Message data formatting for CrewAI / Formatação dos dados para o CrewAI
    pull_msg = f"""
    Group Message Data / Dados sobre as mensagens do grupo
    Initial Date / Data Inicial: {data_anterior_formatada}
    Final Date / Data Final: {data_atual_formatada}
    
    USER MESSAGES FOR SUMMARY / MENSAGENS DOS USUÁRIOS PARA O RESUMO:
    --------------------------
    """

    for msg in reversed(msgs):
        pull_msg += f"""
        Nome: *{msg.get_name()}*
        Postagem: "{msg.get_text()}"  
        data: {time.strftime("%d/%m %H:%M", time.localtime(msg.message_timestamp))}'     
        """

    print(pull_msg)
    
    # Summary generation and delivery / Geração e entrega do resumo
    inputs = {
        "msgs": pull_msg
    }
    
    summary_crew = SummaryCrew()
    resposta = summary_crew.kickoff(inputs=inputs)

    # Send summary based on configuration / Envia resumo com base na configuração
    if df.get('send_to_group', True):
        evo_send.textMessage(group_id, resposta)
        print(f"Resumo enviado para o grupo: {nome}")

    # Envia para o número pessoal se estiver definido
    if personal_number:
        try:
            mensagem = f"Resumo do grupo {nome}:\n\n{resposta}"
            evo_send.textMessage(personal_number, mensagem)
            print(f"Resumo enviado para número pessoal: {personal_number}")
        except Exception as e:
            print(f"Erro ao enviar para número pessoal: {str(e)}")

    # Success logging / Registro de sucesso
    log_path = os.path.dirname(__file__)
    nome_arquivo = os.path.join(log_path, "log_summary.txt")

    with open(nome_arquivo, "a", encoding="utf-8") as arquivo:
        destinations = []
        if df.get('send_to_group', True):
            destinations.append("grupo")
        if personal_number:  # Atualizado aqui também
            destinations.append("número pessoal")
        
        destinations_str = " e ".join(destinations)
        log = f"[{data_atual}] [INFO] [GRUPO: {nome}] [GROUP_ID: {group_id}] - Mensagem: Resumo gerado e enviado com sucesso para {destinations_str}!"
        arquivo.write(log)
else:
    print("Grupo não encontrado ou resumo não está habilitado para este grupo. / Group not found or summary is not enabled for this group.")