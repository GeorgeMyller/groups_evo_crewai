import os  # Módulo para operações com o sistema operacional
import streamlit as st  # Biblioteca para criar interfaces web interativas
from datetime import time  # Classe para manipulação de horários
import pandas as pd  # Biblioteca para manipulação de dados em tabelas

# Importação de módulos do projeto
from group_controller import GroupController  # Gerencia a comunicação com a API e cache dos grupos
from groups_util import GroupUtils  # Contém funções auxiliares para manipulação dos dados dos grupos
from task_scheduler import TaskScheduled  # Gerencia agendamentos de tarefas

# Instancia o controlador para lidar com grupos
control = GroupController()  # Cria objeto para buscar e atualizar grupos através da API
# Busca a lista de grupos disponíveis, seja pelo cache ou diretamente pela API
groups = control.fetch_groups()

# Instancia o utilitário para manipulação visual e de dados dos grupos
ut = GroupUtils()  # Facilita o processamento e mapeamento dos grupos para a interface
# Cria um dicionário e uma lista com opções para seleção em componentes do Streamlit
group_map, options = ut.map(groups)

# Divide a tela em duas colunas de mesmo tamanho para organizar a interface
col1, col2 = st.columns([1, 1])


# Função para carregar grupos agendados de um arquivo CSV
# Caso ocorra erro (por exemplo, arquivo não existe), retorna um DataFrame vazio

def load_scheduled_groups():
    """Tenta ler grupos agendados do CSV e retorna apenas aqueles habilitados."""
    try:
        df = pd.read_csv("group_summary.csv")
        return df[df['enabled'] == True]
    except Exception:
        return pd.DataFrame()


# Função para remover um grupo agendado:
# 1. Lê o CSV;
# 2. Verifica se o grupo existe;
# 3. Remove a tarefa agendada do sistema;
# 4. Atualiza o CSV sem o grupo removido.

def delete_scheduled_group(group_id):
    """Remove o grupo agendado do arquivo CSV e da lista de tarefas do sistema."""
    try:
        df = pd.read_csv("group_summary.csv")
        if group_id not in df['group_id'].values:
            st.error(f"Grupo com ID {group_id} não encontrado!")
            return False
        task_name = f"ResumoGrupo_{group_id}"
        try:
            TaskScheduled.delete_task(task_name)  # Tenta remover o agendamento da tarefa
            st.success(f"Tarefa {task_name} removida do sistema")
        except Exception as e:
            st.warning(f"Aviso: Não foi possível remover a tarefa: {e}")

        # Atualiza o CSV removendo o grupo escolhido
        df = df[df['group_id'] != group_id]
        df.to_csv("group_summary.csv", index=False)
        st.success("Grupo removido do arquivo de configuração")
        return True
    except Exception as e:
        st.error(f"Erro ao remover grupo: {e}")
        return False


with col1:
    st.header("Selecione um Grupo")  # Cabeçalho da seção para seleção de grupos
    if group_map:
        # Componente selectbox para escolha do grupo; exibe o nome e retorna o ID
        selected_group_id = st.selectbox(
            "Escolha um grupo:",
            options,
            format_func=lambda x: x[0]  # Mostra o nome do grupo para facilitar a escolha
        )[1]
        # Recupera o objeto grupo correspondente ao ID selecionado
        selected_group = group_map[selected_group_id]
        # Cria um cabeçalho visual com o nome e a imagem do grupo
        head_group = ut.head_group(selected_group.name, selected_group.picture_url)
        st.markdown(head_group, unsafe_allow_html=True)
        # Exibe detalhes adicionais do grupo em uma seção expansível
        ut.group_details(selected_group)

        st.subheader("Tarefas Agendadas")  # Subcabeçalho para a área de tarefas agendadas
        scheduled_groups = load_scheduled_groups()
        if not scheduled_groups.empty:
            # Cria um dicionário para mapear IDs aos nomes dos grupos
            group_dict = {group.group_id: group.name for group in groups}
            scheduled_groups_info = []
            # Para cada grupo agendado, extrai informações relevantes para exibição
            for _, row in scheduled_groups.iterrows():
                group_id = row['group_id']
                group_name = group_dict.get(group_id, "Nome não encontrado")
                scheduled_groups_info.append({
                    "id": group_id,
                    "name": group_name,
                    "horario": row['horario'],
                    "links": "Sim" if row['is_links'] else "Não",
                    "names": "Sim" if row['is_names'] else "Não"
                })
            # Monta uma lista de opções com nome e horário para mostrar no seletor
            options = [f"{info['name']} - {info['horario']}" for info in scheduled_groups_info]
            selected_idx = st.selectbox("Grupos com Resumos Agendados:", range(len(options)), format_func=lambda x: options[x])
            if selected_idx is not None:
                selected_info = scheduled_groups_info[selected_idx]
                # Exibe as informações do grupo agendado
                st.write(f"**ID:** {selected_info['id']}")
                st.write(f"**Horário:** {selected_info['horario']}")
                st.write(f"**Links habilitados:** {selected_info['links']}")
                st.write(f"**Nomes habilitados:** {selected_info['names']}")
                # Botão para remover o agendamento; recarrega a página se a remoção for bem-sucedida
                if st.button("Remover Agendamento"):
                    if delete_scheduled_group(selected_info['id']):
                        st.success("Agendamento removido com sucesso!")
                        st.rerun()
        else:
            st.info("Não há grupos com resumos agendados.")
    else:
        st.warning("Nenhum grupo encontrado!")

with col2:
    if group_map:
        st.header("Configurações")  # Cabeçalho para a seção de configurações do resumo
        with st.expander("Configurações do Resumo", expanded=True):
            # Checkbox para ativar a geração do resumo
            enabled = st.checkbox("Habilitar Geração do Resumo", value=selected_group.enabled)
            # Componente para selecionar o horário de execução do resumo; converte o valor para objeto time
            horario = st.time_input("Horário de Execução do Resumo:", value=time.fromisoformat(selected_group.horario))
            # Opções para incluir links e nomes no resumo
            is_links = st.checkbox("Incluir Links no Resumo", value=selected_group.is_links)
            is_names = st.checkbox("Incluir Nomes no Resumo", value=selected_group.is_names)
            # Localiza o script que será executado para gerar o resumo
            python_script = os.path.join(os.path.dirname(__file__), "summary.py")
            # Botão para salvar as novas configurações; atualiza o CSV e agenda a tarefa
            if st.button("Salvar Configurações"):
                if control.update_summary(
                    group_id=selected_group.group_id,
                    horario=horario.strftime("%H:%M"),
                    enabled=enabled,
                    is_links=is_links,
                    is_names=is_names,
                    script=python_script
                ):
                    st.success("Configurações salvas com sucesso!")
                    st.rerun()
                else:
                    st.error("Erro ao salvar as configurações. Tente novamente!")