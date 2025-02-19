import pandas as pd  # Biblioteca para manipulação de dados em tabelas
from group_controller import GroupController  # Permite acessar os grupos e suas informações
from task_scheduler import TaskScheduled  # Gerencia o agendamento e remoção de tarefas do sistema
import sys  


def list_groups():
    """Exibe na tela todos os grupos agendados, facilitando a escolha para remoção."""
    # Lê as informações do arquivo CSV que contém o resumo dos grupos
    df = pd.read_csv("group_summary.csv")
    control = GroupController()  # Cria instância do controlador para acessar os grupos via API
    groups = control.fetch_groups()
    # Cria um dicionário mapeando o ID do grupo para seu nome para facilitar a identificação
    group_dict = {group.group_id: group.name for group in groups}
    
    print("\n=== GRUPOS DISPONÍVEIS ===\n")
    # Itera sobre os grupos do CSV e exibe com numeração
    for i, (group_id, _) in enumerate(df.iterrows(), 1):
        group_id = df.iloc[i-1]['group_id']
        group_name = group_dict.get(group_id, "Nome não encontrado")
        print(f"{i}. {group_name} (ID: {group_id})")
    
    return df  


def delete_scheduled_group(group_id):
    """Remove um grupo agendado:
    1. Lê o CSV com as configurações dos grupos;
    2. Verifica se o grupo existe;
    3. Remove a tarefa agendada do sistema;
    4. Atualiza o CSV removendo o grupo."""
    try:
        # Lê o arquivo CSV contendo os agendamentos
        df = pd.read_csv("group_summary.csv")
        
        # Verifica se o ID passado existe no CSV
        if group_id not in df['group_id'].values:
            print(f"Grupo com ID {group_id} não encontrado!")
            return False
        
        # Define o nome da tarefa agendada baseado no ID do grupo
        task_name = f"ResumoGrupo_{group_id}"
        try:
            # Tenta remover a tarefa agendada do sistema
            TaskScheduled.delete_task(task_name)
            print(f"Tarefa {task_name} removida do sistema")
        except Exception as e:
            # Caso não seja possível remover, exibe uma mensagem de aviso
            print(f"Aviso: Não foi possível remover a tarefa do sistema: {e}")
        
        # Remove o grupo do DataFrame e salva a atualização no CSV
        df = df[df['group_id'] != group_id]
        df.to_csv("group_summary.csv", index=False)
        print("Grupo removido do arquivo de configuração")
        
        return True
        
    except Exception as e:
        # Em caso de erro, exibe a mensagem e retorna False
        print(f"Erro ao remover grupo: {e}")
        return False


def main():
    """Função principal do script, fornecendo uma interface de linha de comando para remover grupos agendados."""
    while True:
        try:
            df = list_groups()  # Chama a função para listar os grupos disponíveis
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
                    group = control.find_group_by_id(group_id)  # Procura o grupo pelo ID
                    
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