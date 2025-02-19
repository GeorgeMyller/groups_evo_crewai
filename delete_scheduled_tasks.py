import pandas as pd
from group_controller import GroupController
from task_scheduler import TaskScheduled
import sys

def list_groups():
    """Lista todos os grupos disponíveis para escolha"""
    df = pd.read_csv("group_summary.csv")
    control = GroupController()
    groups = control.fetch_groups()
    group_dict = {group.group_id: group.name for group in groups}
    
    print("\n=== GRUPOS DISPONÍVEIS ===\n")
    for i, (group_id, _) in enumerate(df.iterrows(), 1):
        group_id = df.iloc[i-1]['group_id']
        group_name = group_dict.get(group_id, "Nome não encontrado")
        print(f"{i}. {group_name} (ID: {group_id})")
    
    return df

def delete_scheduled_group(group_id):
    """Remove um grupo específico das tarefas agendadas"""
    try:
        # Carrega o CSV atual
        df = pd.read_csv("group_summary.csv")
        
        # Verifica se o grupo existe
        if group_id not in df['group_id'].values:
            print(f"Grupo com ID {group_id} não encontrado!")
            return False
        
        # Remove a tarefa do sistema operacional
        task_name = f"ResumoGrupo_{group_id}"
        try:
            TaskScheduled.delete_task(task_name)
            print(f"Tarefa {task_name} removida do sistema")
        except Exception as e:
            print(f"Aviso: Não foi possível remover a tarefa do sistema: {e}")
        
        # Remove o grupo do CSV
        df = df[df['group_id'] != group_id]
        df.to_csv("group_summary.csv", index=False)
        print(f"Grupo removido do arquivo de configuração")
        
        return True
        
    except Exception as e:
        print(f"Erro ao remover grupo: {e}")
        return False

def main():
    while True:
        try:
            df = list_groups()
            if df.empty:
                print("Não há grupos agendados para remover.")
                break
                
            print("\nEscolha o número do grupo para remover (ou 'q' para sair):")
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
                        print(f"\nVocê escolheu remover:")
                        print(f"Grupo: {group.name}")
                        print(f"ID: {group_id}")
                        confirm = input("\nConfirma a remoção? (s/n): ").strip().lower()
                        
                        if confirm == 's':
                            if delete_scheduled_group(group_id):
                                print("Grupo removido com sucesso!")
                            else:
                                print("Falha ao remover o grupo.")
                    else:
                        print("Grupo não encontrado no sistema.")
                else:
                    print("Número inválido!")
            except ValueError:
                print("Por favor, digite um número válido!")
                
        except Exception as e:
            print(f"Erro: {e}")
            break

if __name__ == "__main__":
    main()