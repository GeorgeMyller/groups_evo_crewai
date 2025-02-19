import pandas as pd
from group_controller import GroupController
from task_scheduler import TaskScheduled

def list_scheduled_groups():
    """
    Lista todos os grupos que têm tarefas de resumo agendadas.
    """
    try:
        df = pd.read_csv("group_summary.csv")
        enabled_groups = df[df['enabled'] == True]

        if enabled_groups.empty:
            print("Nenhum grupo tem resumos agendados.")
            return

        print("\n=== GRUPOS COM RESUMOS AGENDADOS ===\n")

        control = GroupController()
        groups = control.fetch_groups()
        group_dict = {group.group_id: group.name for group in groups}

        for _, row in enabled_groups.iterrows():
            group_id = row['group_id']
            horario = row['horario']
            group_name = group_dict.get(group_id, "Nome não encontrado")
            
            print(f"Grupo: {group_name}")
            print(f"ID: {group_id}")
            print(f"Horário: {horario}")
            print(f"Links habilitados: {'Sim' if row['is_links'] else 'Não'}")
            print(f"Nomes habilitados: {'Sim' if row['is_names'] else 'Não'}")
            print("-" * 50)
        
        print("\n=== TAREFAS NO SISTEMA ===\n")
        TaskScheduled.list_tasks()
        
    except Exception as e:
        print(f"Erro ao listar grupos agendados: {str(e)}")

if __name__ == "__main__":
    list_scheduled_groups()