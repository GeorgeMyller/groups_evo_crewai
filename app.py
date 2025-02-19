import os  # Módulo para operações com o sistema operacional
import streamlit as st  # Biblioteca para criar interfaces web interativas
from datetime import time, date, datetime  # Classes para manipulação de datas e horários
import time as t  # Importação do módulo time para funções como sleep
import pandas as pd  # Biblioteca para manipulação de dados em tabelas
from dotenv import load_dotenv  # Biblioteca para carregar variáveis de ambiente de um arquivo .env

# Importação de módulos do projeto
from group_controller import GroupController  # Gerencia a comunicação com a API e cache dos grupos
from groups_util import GroupUtils  # Contém funções auxiliares para manipulação dos dados dos grupos
from task_scheduler import TaskScheduled  # Gerencia agendamentos de tarefas

# Garante que o .env seja carregado do diretório correto
env_path = os.path.join(os.path.dirname(__file__), '.env')
print(f"Tentando carregar .env de: {env_path}")
load_dotenv(env_path)

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
                
                # Determina a periodicidade
                if row.get('start_date') and row.get('end_date'):
                    periodicidade = "Uma vez"
                else:
                    periodicidade = "Diariamente"
                    
                scheduled_groups_info.append({
                    "id": group_id,
                    "name": group_name,
                    "horario": row['horario'],
                    "links": "Sim" if row['is_links'] else "Não",
                    "names": "Sim" if row['is_names'] else "Não",
                    "periodicidade": periodicidade
                })
            # Monta uma lista de opções com nome e horário para mostrar no seletor
            options = [f"{info['name']} - {info['horario']}" for info in scheduled_groups_info]
            selected_idx = st.selectbox("Grupos com Resumos Agendados:", range(len(options)), format_func=lambda x: options[x])
            if selected_idx is not None:
                selected_info = scheduled_groups_info[selected_idx]
                # Exibe as informações do grupo agendado
                st.write(f"**ID:** {selected_info['id']}")
                st.write(f"**Horário:** {selected_info['horario']}")
                st.write(f"**Periodicidade:** {selected_info['periodicidade']}")
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
            
            # Adiciona seleção de periodicidade
            periodicidade = st.selectbox(
                "Periodicidade",
                ["Diariamente", "Uma vez"],
                index=0
            )
            
            # Componente para selecionar o horário de execução do resumo
            horario = None
            if periodicidade == "Diariamente":
                horario = st.time_input("Horário de Execução do Resumo:", value=time.fromisoformat(selected_group.horario))
            
            # Campos para data quando periodicidade for "Uma vez"
            start_date = None
            end_date = None
            start_time = None
            end_time = None
            if periodicidade == "Uma vez":
                col_start, col_end = st.columns(2)
                with col_start:
                    start_date = st.date_input("Data de Início:", value=date.today())
                    start_time = st.time_input("Hora de Início:", value=time.fromisoformat("00:00"))
                with col_end:
                    end_date = st.date_input("Data Final:", value=date.today())
                    end_time = st.time_input("Hora Final:", value=time.fromisoformat("23:59"))
            
            # Opções para incluir links e nomes no resumo
            is_links = st.checkbox("Incluir Links no Resumo", value=selected_group.is_links)
            is_names = st.checkbox("Incluir Nomes no Resumo", value=selected_group.is_names)
            # Localiza o script que será executado para gerar o resumo
            python_script = os.path.join(os.path.dirname(__file__), "summary.py")
            
            # Botão para salvar as novas configurações
            if st.button("Salvar Configurações"):
                task_name = f"ResumoGrupo_{selected_group.group_id}"
                
                try:
                    # Preparar os parâmetros adicionais para resumo único
                    additional_params = {}
                    if periodicidade == "Uma vez":
                        additional_params.update({
                            'start_date': start_date.strftime("%Y-%m-%d"),
                            'start_time': start_time.strftime("%H:%M"),
                            'end_date': end_date.strftime("%Y-%m-%d"),
                            'end_time': end_time.strftime("%H:%M")
                        })
                    
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
                            if periodicidade == "Diariamente":
                                TaskScheduled.create_task(
                                    task_name=task_name,
                                    python_script_path=python_script,
                                    schedule_type='DAILY',
                                    time=horario.strftime("%H:%M")
                                )
                                st.success(f"Configurações salvas! O resumo será executado diariamente às {horario.strftime('%H:%M')}")
                            else:  # Uma vez
                                # Define o horário para o próximo minuto
                                next_minute = datetime.now().replace(second=0, microsecond=0) + pd.Timedelta(minutes=1)
                                
                                TaskScheduled.create_task(
                                    task_name=task_name,
                                    python_script_path=python_script,
                                    schedule_type='ONCE',
                                    date=next_minute.strftime("%Y-%m-%d"),
                                    time=next_minute.strftime("%H:%M")
                                )
                                st.success(f"Configurações salvas! O resumo será executado em {next_minute.strftime('%d/%m/%Y às %H:%M')}")
                        else:
                            try:
                                TaskScheduled.delete_task(task_name)
                            except Exception:
                                pass
                            st.success("Configurações salvas! Agendamento desativado.")
                        
                        t.sleep(2)
                        st.rerun()
                    else:
                        st.error("Erro ao salvar as configurações. Tente novamente!")
                except Exception as e:
                    st.error(f"Erro ao configurar agendamento: {str(e)}")

