"""
Sistema de Remoção de Tarefas Agendadas / Scheduled Tasks Removal System

PT-BR:
Este módulo fornece funcionalidades para listar e remover tarefas agendadas do sistema.
Permite a visualização e gerenciamento de grupos através de uma interface de linha de comando.

EN:
This module provides functionality to list and remove scheduled tasks from the system.
Allows viewing and managing groups through a command-line interface.
"""

import pandas as pd
from group_controller import GroupController
from task_scheduler import TaskScheduled
import sys


def list_groups():
    """
    PT-BR:
    Lista todos os grupos agendados no sistema com suas respectivas informações.
    
    Retorna:
        DataFrame: Contém as informações dos grupos agendados do arquivo CSV.
    
    EN:
    Lists all scheduled groups in the system with their respective information.
    
    Returns:
        DataFrame: Contains scheduled groups information from the CSV file.
    """
    df = pd.read_csv("group_summary.csv")
    control = GroupController()
    groups = control.fetch_groups()
    group_dict = {group.group_id: group.name for group in groups}
    
    print("\n=== GRUPOS DISPONÍVEIS / AVAILABLE GROUPS ===\n")
    for i, (group_id, _) in enumerate(df.iterrows(), 1):
        group_id = df.iloc[i-1]['group_id']
        group_name = group_dict.get(group_id, "Nome não encontrado / Name not found")
        print(f"{i}. {group_name} (ID: {group_id})")
    
    return df


def delete_scheduled_group(group_id):
    """
    PT-BR:
    Remove um grupo agendado do sistema e do arquivo de configuração.
    
    Argumentos:
        group_id: ID do grupo a ser removido
    
    Retorna:
        bool: True se a remoção foi bem-sucedida, False caso contrário
    
    EN:
    Removes a scheduled group from both system and configuration file.
    
    Args:
        group_id: ID of the group to be removed
    
    Returns:
        bool: True if removal was successful, False otherwise
    """
    try:
        df = pd.read_csv("group_summary.csv")
        
        if group_id not in df['group_id'].values:
            print(f"Grupo não encontrado / Group not found: ID {group_id}")
            return False
        
        task_name = f"ResumoGrupo_{group_id}"
        try:
            TaskScheduled.delete_task(task_name)
            print(f"Tarefa removida do sistema / Task removed from system: {task_name}")
        except Exception as e:
            print(f"Aviso / Warning: Não foi possível remover a tarefa / Could not remove task: {e}")
        
        df = df[df['group_id'] != group_id]
        df.to_csv("group_summary.csv", index=False)
        print("Grupo removido do arquivo de configuração / Group removed from configuration file")
        
        return True
        
    except Exception as e:
        print(f"Erro ao remover grupo / Error removing group: {e}")
        return False


def main():
    """
    PT-BR:
    Função principal que implementa a interface de linha de comando para
    gerenciamento e remoção de grupos agendados.
    
    EN:
    Main function that implements the command-line interface for
    managing and removing scheduled groups.
    """
    while True:
        try:
            df = list_groups()
            if df.empty:
                print("Não há grupos agendados para remover. / No scheduled groups to remove.")
                break
                
            print("\nEscolha o número do grupo para remover (ou 'q' para sair) / Choose group number to remove (or 'q' to quit):")
            choice = input().strip()
            
            if choice.lower() == 'q':
                break
                
            try:
                index = int(choice) - 1
                if 0 <= index < len(df):
                    group_id = df.iloc[index]['group_id']
                    control = GroupController()
                    group = control.find_group_by_id(group_id)
                    
                    if group:
                        print(f"\nVocê escolheu remover / You chose to remove:")
                        print(f"Grupo / Group: {group.name}")
                        print(f"ID: {group_id}")
                        confirm = input("\nConfirma a remoção? / Confirm removal? (s/n): ").strip().lower()
                        
                        if confirm == 's':
                            if delete_scheduled_group(group_id):
                                print("Grupo removido com sucesso! / Group successfully removed!")
                            else:
                                print("Falha ao remover o grupo. / Failed to remove group.")
                    else:
                        print("Grupo não encontrado no sistema. / Group not found in system.")
                else:
                    print("Número inválido! / Invalid number!")
            except ValueError:
                print("Por favor, digite um número válido! / Please enter a valid number!")
                
        except Exception as e:
            print(f"Erro / Error: {e}")
            break


if __name__ == "__main__":
    main()