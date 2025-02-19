"""
Sistema de Gerenciamento de Grupos e Agendamento / Group Management and Scheduling System

PT-BR:
Este módulo implementa uma interface web baseada em Streamlit para gerenciar e agendar resumos de grupos.
Fornece funcionalidades para visualizar detalhes dos grupos, configurar geração de resumos
e gerenciar tarefas agendadas.

EN:
This module implements a Streamlit-based web interface for managing and scheduling group summaries.
It provides functionality to view group details, configure summary generation settings,
and manage scheduled tasks.
"""

import os
import streamlit as st
from datetime import time, date, datetime
import time as t
import pandas as pd
from dotenv import load_dotenv

from group_controller import GroupController
from groups_util import GroupUtils
from task_scheduler import TaskScheduled

# Environment setup / Configuração do ambiente
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

# Initialize core components / Inicialização dos componentes principais
control = GroupController()
groups = control.fetch_groups()
ut = GroupUtils()
group_map, options = ut.map(groups)

# UI Layout / Layout da Interface
col1, col2 = st.columns([1, 1])


def load_scheduled_groups():
    """
    PT-BR:
    Carrega e retorna os grupos agendados que estão ativos do arquivo CSV.
    
    Retorna:
        DataFrame: Contém apenas as informações de agendamento dos grupos ativos.
        Se o arquivo não existir, retorna um DataFrame vazio.

    EN:
    Load and return enabled scheduled groups from CSV.
    
    Returns:
        DataFrame: Contains only enabled groups' scheduling information.
        If file doesn't exist, returns empty DataFrame.
    """
    try:
        df = pd.read_csv("group_summary.csv")
        return df[df['enabled'] == True]
    except Exception:
        return pd.DataFrame()


def delete_scheduled_group(group_id):
    """
    PT-BR:
    Remove um grupo agendado tanto do arquivo CSV quanto das tarefas do sistema.
    
    Argumentos:
        group_id: O ID do grupo a ser removido
        
    Retorna:
        bool: True se a remoção foi bem-sucedida, False caso contrário

    EN:
    Remove a scheduled group from both CSV configuration and system tasks.
    
    Args:
        group_id: The ID of the group to be removed
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        df = pd.read_csv("group_summary.csv")
        if group_id not in df['group_id'].values:
            st.error(f"Group ID {group_id} not found!")
            return False
            
        task_name = f"ResumoGrupo_{group_id}"
        try:
            TaskScheduled.delete_task(task_name)
            st.success(f"Task {task_name} removed from system")
        except Exception as e:
            st.warning(f"Warning: Could not remove task: {e}")

        df = df[df['group_id'] != group_id]
        df.to_csv("group_summary.csv", index=False)
        st.success("Group removed from configuration file")
        return True
    except Exception as e:
        st.error(f"Error removing group: {e}")
        return False


with col1:
    # Group Selection Section / Seção de Seleção de Grupo
    st.header("Selecione um Grupo / Select a Group")
    if group_map:
        selected_group_id = st.selectbox(
            "Escolha um grupo / Choose a group:",
            options,
            format_func=lambda x: x[0]
        )[1]
        selected_group = group_map[selected_group_id]
        head_group = ut.head_group(selected_group.name, selected_group.picture_url)
        st.markdown(head_group, unsafe_allow_html=True)
        ut.group_details(selected_group)

        # Scheduled Tasks Section / Seção de Tarefas Agendadas
        st.subheader("Tarefas Agendadas / Scheduled Tasks")
        scheduled_groups = load_scheduled_groups()
        if not scheduled_groups.empty:
            # Processing scheduled groups / Processando grupos agendados
            group_dict = {group.group_id: group.name for group in groups}
            scheduled_groups_info = []
            for _, row in scheduled_groups.iterrows():
                group_id = row['group_id']
                group_name = group_dict.get(group_id, "Nome não encontrado / Name not found")
                
                if row.get('start_date') and row.get('end_date'):
                    periodicidade = "Uma vez / Once"
                else:
                    periodicidade = "Diariamente / Daily"
                    
                scheduled_groups_info.append({
                    "id": group_id,
                    "name": group_name,
                    "horario": row['horario'],
                    "links": "Sim / Yes" if row['is_links'] else "Não / No",
                    "names": "Sim / Yes" if row['is_names'] else "Não / No",
                    "periodicidade": periodicidade
                })
            
            # Display scheduled groups / Exibição dos grupos agendados
            options = [f"{info['name']} - {info['horario']}" for info in scheduled_groups_info]
            selected_idx = st.selectbox("Grupos com Resumos Agendados / Groups with Scheduled Summaries:", 
                                      range(len(options)), 
                                      format_func=lambda x: options[x])
            
            if selected_idx is not None:
                selected_info = scheduled_groups_info[selected_idx]
                st.write(f"**ID:** {selected_info['id']}")
                st.write(f"**Horário / Time:** {selected_info['horario']}")
                st.write(f"**Periodicidade / Frequency:** {selected_info['periodicidade']}")
                st.write(f"**Links habilitados / Links enabled:** {selected_info['links']}")
                st.write(f"**Nomes habilitados / Names enabled:** {selected_info['names']}")
                
                if st.button("Remover Agendamento / Remove Schedule"):
                    if delete_scheduled_group(selected_info['id']):
                        st.success("Agendamento removido com sucesso! / Schedule successfully removed!")
                        st.rerun()
        else:
            st.info("Não há grupos com resumos agendados. / No groups with scheduled summaries.")
    else:
        st.warning("Nenhum grupo encontrado! / No groups found!")

with col2:
    if group_map:
        # Configuration Section / Seção de Configurações
        st.header("Configurações / Settings")
        with st.expander("Configurações do Resumo / Summary Settings", expanded=True):
            # Configuration inputs / Entradas de configuração
            enabled = st.checkbox("Habilitar Geração do Resumo / Enable Summary Generation", 
                                value=selected_group.enabled)
            
            periodicidade = st.selectbox(
                "Periodicidade / Frequency",
                ["Diariamente / Daily", "Uma vez / Once"],
                index=0
            )
            
            # Time scheduling logic / Lógica de agendamento de horários
            horario = None
            if periodicidade.startswith("Diariamente"):
                try:
                    default_time = time.fromisoformat(selected_group.horario)
                except ValueError:
                    # If time format is invalid, use default time 22:00
                    default_time = time.fromisoformat("22:00")
                horario = st.time_input("Horário de Execução do Resumo / Summary Execution Time:", 
                                      value=default_time)
            
            start_date = None
            end_date = None
            start_time = None
            end_time = None
            if periodicidade.startswith("Uma vez"):
                col_start, col_end = st.columns(2)
                with col_start:
                    start_date = st.date_input("Data de Início / Start Date:", value=date.today())
                    start_time = st.time_input("Hora de Início / Start Time:", value=time.fromisoformat("00:00"))
                with col_end:
                    end_date = st.date_input("Data Final / End Date:", value=date.today())
                    end_time = st.time_input("Hora Final / End Time:", value=time.fromisoformat("23:59"))
            
            # Summary content options / Opções de conteúdo do resumo
            is_links = st.checkbox("Incluir Links no Resumo / Include Links in Summary", 
                                 value=selected_group.is_links)
            is_names = st.checkbox("Incluir Nomes no Resumo / Include Names in Summary", 
                                 value=selected_group.is_names)
            python_script = os.path.join(os.path.dirname(__file__), "summary.py")
            
            # Save configuration button / Botão de salvar configurações
            if st.button("Salvar Configurações / Save Settings"):
                task_name = f"ResumoGrupo_{selected_group.group_id}"
                
                try:
                    # Process configuration parameters / Processar parâmetros de configuração
                    additional_params = {}
                    if periodicidade.startswith("Uma vez"):
                        additional_params.update({
                            'start_date': start_date.strftime("%Y-%m-%d"),
                            'start_time': start_time.strftime("%H:%M"),
                            'end_date': end_date.strftime("%Y-%m-%d"),
                            'end_time': end_time.strftime("%H:%M")
                        })
                    
                    # Update summary configuration / Atualizar configuração do resumo
                    if control.update_summary(
                        group_id=selected_group.group_id,
                        horario=horario.strftime("%H:%M") if horario else None,
                        enabled=enabled,
                        is_links=is_links,
                        is_names=is_names,
                        script=python_script,
                        **additional_params
                    ):
                        if enabled:
                            # Schedule task based on periodicity / Agendar tarefa baseado na periodicidade
                            if periodicidade.startswith("Diariamente"):
                                TaskScheduled.create_task(
                                    task_name=task_name,
                                    python_script_path=python_script,
                                    schedule_type='DAILY',
                                    time=horario.strftime("%H:%M")
                                )
                                st.success(f"Configurações salvas! O resumo será executado diariamente às {horario.strftime('%H:%M')} / Settings saved! Summary will run daily at {horario.strftime('%H:%M')}")
                            else:
                                next_minute = datetime.now().replace(second=0, microsecond=0) + pd.Timedelta(minutes=1)
                                
                                TaskScheduled.create_task(
                                    task_name=task_name,
                                    python_script_path=python_script,
                                    schedule_type='ONCE',
                                    date=next_minute.strftime("%Y-%m-%d"),
                                    time=next_minute.strftime("%H:%M")
                                )
                                st.success(f"Configurações salvas! O resumo será executado em {next_minute.strftime('%d/%m/%Y às %H:%M')} / Settings saved! Summary will run on {next_minute.strftime('%d/%m/%Y at %H:%M')}")
                        else:
                            try:
                                TaskScheduled.delete_task(task_name)
                            except Exception:
                                pass
                            st.success("Configurações salvas! Agendamento desativado. / Settings saved! Scheduling disabled.")
                        
                        t.sleep(2)
                        st.rerun()
                    else:
                        st.error("Erro ao salvar as configurações. Tente novamente! / Error saving settings. Please try again!")
                except Exception as e:
                    st.error(f"Erro ao configurar agendamento / Error configuring schedule: {str(e)}")

