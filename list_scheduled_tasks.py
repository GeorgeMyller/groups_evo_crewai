import pandas as pd                                # Importa o módulo pandas para manipulação de dados em DataFrames
from group_controller import GroupController       # Importa a classe GroupController para gerenciar grupos e buscar nomes
from task_scheduler import TaskScheduled           # Importa a classe TaskScheduled para manipular tarefas agendadas

def list_scheduled_groups():
    """Lista todos os grupos que têm tarefas de resumo agendadas"""
    try:
        # Tenta carregar os dados do arquivo CSV que contém as configurações dos grupos
        df = pd.read_csv("group_summary.csv")      # Lê o arquivo CSV e armazena seus dados em um DataFrame
        
        # Filtra o DataFrame para obter apenas as linhas onde os grupos estão habilitados para resumo
        enabled_groups = df[df['enabled'] == True]   # Seleciona apenas os grupos com resumo habilitado
        
        # Verifica se a filtragem resultou em um DataFrame vazio
        if enabled_groups.empty:
            print("Nenhum grupo tem resumos agendados.")  # Informa que nenhum grupo possui resumo agendado
            return                                    # Encerra a função, pois não há grupos a listar
        
        print("\n=== GRUPOS COM RESUMOS AGENDADOS ===\n")  # Imprime cabeçalho para a lista de grupos agendados
        
        # Obtém o controlador de grupos para buscar nomes e outras informações
        control = GroupController()                # Instancia o controlador de grupos
        groups = control.fetch_groups()            # Busca a lista de grupos (pode ser do cache ou da API)
        # Cria um dicionário que mapeia o ID do grupo para seu nome para acesso rápido
        group_dict = {group.group_id: group.name for group in groups}  
        
        # Itera sobre cada linha (grupo) do DataFrame filtrado
        for _, row in enabled_groups.iterrows():
            group_id = row['group_id']             # Extrai o ID do grupo da linha atual
            horario = row['horario']               # Extrai o horário configurado para o resumo
            # Busca o nome do grupo no dicionário; usa "Nome não encontrado" se o grupo não existir
            group_name = group_dict.get(group_id, "Nome não encontrado")
            
            print(f"Grupo: {group_name}")          # Imprime o nome do grupo
            print(f"ID: {group_id}")               # Imprime o ID do grupo
            print(f"Horário: {horario}")           # Imprime o horário configurado
            # Imprime se os links estão habilitados: 'Sim' se True, 'Não' se False
            print(f"Links habilitados: {'Sim' if row['is_links'] else 'Não'}")
            # Imprime se os nomes estão habilitados: 'Sim' se True, 'Não' se False
            print(f"Nomes habilitados: {'Sim' if row['is_names'] else 'Não'}")
            print("-" * 50)                        # Imprime uma linha separadora para facilitar a visualização
        
        print("\n=== TAREFAS NO SISTEMA ===\n")     # Imprime cabeçalho para a lista de tarefas no sistema
        # Chama o método list_tasks() da classe TaskScheduled para listar as tarefas agendadas no sistema operacional
        TaskScheduled.list_tasks()
        
    except Exception as e:
        # Caso ocorra algum erro, imprime a mensagem de erro para depuração
        print(f"Erro ao listar grupos agendados: {str(e)}")

# Verifica se o script está sendo executado diretamente (e não importado como módulo)
if __name__ == "__main__":
    list_scheduled_groups()                        # Chama a função que lista os grupos com resumos agendados