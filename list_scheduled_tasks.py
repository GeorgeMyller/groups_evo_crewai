import pandas as pd
from group_controller import GroupController
from task_scheduler import TaskScheduled

def list_scheduled_groups():
    """
    PT-BR:
    Lista todos os grupos que têm tarefas de resumo agendadas.
    Exibe informações detalhadas sobre cada grupo, incluindo nome, ID e configurações.

    EN:
    Lists all groups that have scheduled summary tasks.
    Displays detailed information about each group, including name, ID and settings.
    """
    try:
        df = pd.read_csv("group_summary.csv")
        enabled_groups = df[df['enabled'] == True]

        if enabled_groups.empty:
            print("Nenhum grupo tem resumos agendados. / No groups have scheduled summaries.")
            return

        print("\n=== GRUPOS COM RESUMOS AGENDADOS / GROUPS WITH SCHEDULED SUMMARIES ===\n")

        control = GroupController()
        groups = control.fetch_groups()
        group_dict = {group.group_id: group.name for group in groups}

        for _, row in enabled_groups.iterrows():
            group_id = row['group_id']
            horario = row['horario']
            group_name = group_dict.get(group_id, "Nome não encontrado / Name not found")
            
            print(f"Grupo / Group: {group_name}")
            print(f"ID: {group_id}")
            print(f"Horário / Time: {horario}")
            print(f"Links habilitados / Links enabled: {'Sim / Yes' if row['is_links'] else 'Não / No'}")
            print(f"Nomes habilitados / Names enabled: {'Sim / Yes' if row['is_names'] else 'Não / No'}")
            print("-" * 50)
        
        print("\n=== TAREFAS NO SISTEMA / SYSTEM TASKS ===\n")
        TaskScheduled.list_tasks()
        
    except Exception as e:
        print(f"Erro ao listar grupos agendados / Error listing scheduled groups: {str(e)}")

if __name__ == "__main__":
    list_scheduled_groups()