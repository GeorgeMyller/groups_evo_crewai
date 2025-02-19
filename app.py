import os  # Importa o módulo os para interagir com o sistema de arquivos
import streamlit as st  # Importa o módulo streamlit para criar a interface web
from datetime import time  # Importa a classe time para trabalhar com horários
import pandas as pd  # Importa o módulo pandas para manipulação de dados em DataFrames

# Importa classes e funções de outros arquivos do projeto
from group_controller import GroupController  # Importa a classe GroupController, que gerencia os grupos
from groups_util import GroupUtils  # Importa a classe GroupUtils, que contém funções utilitárias para grupos
from task_scheduler import TaskScheduled  # Importa a classe TaskScheduled para gerenciar tarefas agendadas

# Cria uma instância do controlador de grupos
control = GroupController()  # Instancia o objeto que interage com a API e os dados dos grupos
# Busca os grupos usando o controlador
groups = control.fetch_groups()  # Obtém a lista de grupos disponíveis, seja do cache ou da API

# Cria uma instância da classe de utilitários para grupos
ut = GroupUtils()  # Instancia o objeto utilitário para processamento dos grupos
# Mapeia os grupos e obtém as opções para seleção pelo usuário
group_map, options = ut.map(groups)  # Organiza os grupos em um dicionário e gera opções de exibição

# Configura o layout da interface dividindo a tela em duas colunas de tamanho igual
col1, col2 = st.columns([1, 1])  # Define duas colunas lado a lado com pesos iguais

# Função para carregar os grupos agendados a partir do arquivo CSV
def load_scheduled_groups():
    try:
        # Lê o arquivo CSV que contém os grupos com resumo agendado
        df = pd.read_csv("group_summary.csv")  # Tenta ler o arquivo CSV com as configurações dos grupos
        # Filtra e retorna apenas os grupos que estão habilitados para resumo
        enabled_groups = df[df['enabled'] == True]  # Seleciona linhas onde a coluna 'enabled' é True
        return enabled_groups  # Retorna o DataFrame com os grupos habilitados
    except Exception:
        # Caso ocorra algum erro (como arquivo não encontrado), retorna um DataFrame vazio
        return pd.DataFrame()  # Retorna um DataFrame vazio para evitar erros

# Função para remover um grupo agendado, atualizando o arquivo CSV e removendo a tarefa do sistema
def delete_scheduled_group(group_id):
    try:
        # Lê o arquivo CSV com os grupos agendados
        df = pd.read_csv("group_summary.csv")  # Carrega as configurações dos grupos do arquivo CSV
        
        # Verifica se o ID do grupo existe no arquivo CSV
        if group_id not in df['group_id'].values:  # Se o group_id não estiver na coluna 'group_id'
            st.error(f"Grupo com ID {group_id} não encontrado!")  # Exibe mensagem de erro no Streamlit
            return False  # Retorna False informando que a remoção não foi possível
        
        # Define o nome da tarefa agendada baseado no group_id
        task_name = f"ResumoGrupo_{group_id}"  # Cria um nome único para a tarefa do grupo
        try:
            # Tenta remover a tarefa agendada do sistema
            TaskScheduled.delete_task(task_name)  # Chama a função para remover a tarefa agendada pelo nome
            st.success(f"Tarefa {task_name} removida do sistema")  # Informa que a tarefa foi removida com sucesso
        except Exception as e:
            # Caso não seja possível remover a tarefa, exibe um aviso com o erro
            st.warning(f"Aviso: Não foi possível remover a tarefa do sistema: {e}")
        
        # Remove o grupo do DataFrame, filtrando as linhas que não tenham o group_id
        df = df[df['group_id'] != group_id]  # Atualiza o DataFrame removendo o grupo informado
        # Salva o DataFrame atualizado de volta no arquivo CSV
        df.to_csv("group_summary.csv", index=False)  # Salva sem o índice no arquivo CSV
        st.success("Grupo removido do arquivo de configuração")  # Exibe mensagem de sucesso para o usuário
        
        return True  # Retorna True para indicar que o grupo foi removido com sucesso
        
    except Exception as e:
        # Em caso de erro, exibe a mensagem de erro e retorna False
        st.error(f"Erro ao remover grupo: {e}")
        return False

# Coluna 1: Seletor de grupo e exibição das tarefas agendadas
with col1:
    st.header("Selecione um Grupo")  # Exibe um cabeçalho para a seção de seleção de grupo
    if group_map:  # Verifica se existem grupos mapeados
        # Cria um seletor (selectbox) para escolher um grupo dentre as opções disponíveis
        selected_group_id = st.selectbox(
            "Escolha um grupo:",
            options,  # Lista de opções geradas a partir dos grupos
            format_func=lambda x: x[0]  # Define a forma de exibição; mostra o primeiro elemento de cada opção
        )[1]  # Seleciona o segundo elemento (geralmente o ID) da opção escolhida
 
        # Obtém o objeto do grupo selecionado utilizando o dicionário group_map
        selected_group = group_map[selected_group_id]  # Busca o grupo com base no ID selecionado
        # Gera um cabeçalho estilizado para o grupo selecionado
        head_group = ut.head_group(selected_group.name, selected_group.picture_url)  # Cria um cabeçalho com nome e imagem do grupo
        st.markdown(head_group, unsafe_allow_html=True)  # Exibe o cabeçalho usando Markdown com HTML permitido

        # Exibe os detalhes do grupo com informações adicionais
        ut.group_details(selected_group)  # Chama função de utilitário para mostrar detalhes do grupo

        # Seção para exibição das tarefas agendadas (grupos com resumo configurado)
        st.subheader("Tarefas Agendadas")  # Exibe um subtítulo para a seção de tarefas agendadas
        scheduled_groups = load_scheduled_groups()  # Carrega os grupos que estão com resumo agendado a partir do CSV
        
        if not scheduled_groups.empty:  # Verifica se o DataFrame com grupos agendados não está vazio
            # Cria um dicionário mapeando o ID do grupo com o nome para auxiliar na exibição
            group_dict = {group.group_id: group.name for group in groups}  # Mapeia cada grupo para seu nome
            scheduled_groups_info = []  # Inicializa uma lista para armazenar informações dos grupos agendados
            
            # Itera sobre cada linha do DataFrame para extrair informações de cada grupo agendado
            for _, row in scheduled_groups.iterrows():
                group_id = row['group_id']  # Extrai o ID do grupo da linha
                group_name = group_dict.get(group_id, "Nome não encontrado")  # Obtém o nome do grupo ou uma mensagem padrão se não encontrado
                # Adiciona as informações do grupo em um dicionário e inclui na lista
                scheduled_groups_info.append({
                    "id": group_id,  # ID do grupo
                    "name": group_name,  # Nome do grupo
                    "horario": row['horario'],  # Horário agendado para o resumo
                    "links": "Sim" if row['is_links'] else "Não",  # Indica se os links estão habilitados
                    "names": "Sim" if row['is_names'] else "Não"  # Indica se os nomes estão habilitados
                })
            
            # Cria uma lista de opções formatadas para exibição no seletor de grupos agendados
            options = [f"{info['name']} - {info['horario']}" for info in scheduled_groups_info]
            # Cria um selectbox para que o usuário selecione um dos grupos agendados
            selected_idx = st.selectbox("Grupos com Resumos Agendados:", 
                                      range(len(options)),  # Passa o índice de cada opção
                                      format_func=lambda x: options[x])  # Exibe a opção formatada a partir do índice
            
            # Se um item for selecionado, exibe os detalhes do grupo agendado selecionado
            if selected_idx is not None:
                selected_info = scheduled_groups_info[selected_idx]  # Recupera as informações do grupo selecionado
                st.write(f"**ID:** {selected_info['id']}")  # Exibe o ID do grupo em destaque
                st.write(f"**Horário:** {selected_info['horario']}")  # Exibe o horário agendado
                st.write(f"**Links habilitados:** {selected_info['links']}")  # Exibe se os links estão habilitados
                st.write(f"**Nomes habilitados:** {selected_info['names']}")  # Exibe se os nomes estão habilitados
                
                # Botão para remover o agendamento do grupo
                if st.button("Remover Agendamento"):
                    # Se a remoção ocorrer com sucesso, exibe uma mensagem de sucesso e recarrega a página
                    if delete_scheduled_group(selected_info['id']):
                        st.success("Agendamento removido com sucesso!")
                        st.rerun()  # Recarrega a interface para atualizar a lista de agendamentos
        else:
            # Exibe uma mensagem informativa se não houver nenhum grupo agendado
            st.info("Não há grupos com resumos agendados.")
    else:
        # Se não houver grupos mapeados, exibe um aviso para o usuário
        st.warning("Nenhum grupo encontrado!")

# Coluna 2: Exibição dos detalhes do grupo selecionado e configuração das opções de resumo
with col2:
    if group_map:  # Verifica se há algum grupo mapeado para exibir os detalhes
        st.header("Configurações")  # Exibe o cabeçalho da seção de configurações
        
        # Cria uma área expansível para as configurações do resumo
        with st.expander("Configurações do Resumo", expanded=True):
            # Checkbox para ativar ou desativar a geração do resumo
            enabled = st.checkbox(
                "Habilitar Geração do Resumo", 
                value=selected_group.enabled  # Valor padrão vindo das configurações atuais do grupo
            )

            # Input para que o usuário selecione o horário de execução do resumo
            horario = st.time_input(
                "Horário de Execução do Resumo:", 
                value=time.fromisoformat(selected_group.horario)  # Converte o horário armazenado em objeto time
            )

            # Checkbox para optar por incluir links no resumo gerado
            is_links = st.checkbox(
                "Incluir Links no Resumo", 
                value=selected_group.is_links  # Define o estado do checkbox conforme a configuração atual
            )
            # Checkbox para optar por incluir nomes no resumo gerado
            is_names = st.checkbox(
                "Incluir Nomes no Resumo", 
                value=selected_group.is_names  # Define o estado do checkbox conforme a configuração atual
            )

            # Define o caminho para o script Python que será executado para gerar o resumo
            python_script = os.path.join(os.path.dirname(__file__), "summary.py")  # Concatena o diretório atual com o nome do script
            
            # Botão para salvar as configurações atualizadas do resumo
            if st.button("Salvar Configurações"):
                # Chama o método update_summary do controlador para atualizar as configurações no CSV
                if control.update_summary(
                    group_id=selected_group.group_id,  # Passa o ID do grupo
                    horario=horario.strftime("%H:%M"),  # Formata o horário para string "HH:MM"
                    enabled=enabled,  # Passa o estado habilitado ou não
                    is_links=is_links,  # Passa a opção de incluir links
                    is_names=is_names,  # Passa a opção de incluir nomes
                    script=python_script  # Passa o caminho para o script Python
                ):
                    st.success("Configurações salvas com sucesso!")  # Exibe mensagem de sucesso se salvar corretamente
                    st.rerun()  # Recarrega a página para atualizar as informações exibidas
                else:
                    st.error("Erro ao salvar as configurações. Tente novamente!")  # Exibe mensagem de erro se ocorrer alguma falha