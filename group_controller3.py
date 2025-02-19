import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# group_manager.py
import os
from dotenv import load_dotenv
from datetime import datetime
from evolutionapi.client import EvolutionClient
from group import Group
import pandas as pd

from message_sandeco import MessageSandeco


from task_scheduler import TaskScheduled

# Carregar variáveis de ambiente
load_dotenv()


class GroupController:
    def __init__(self):
        """
        Inicializa o gerenciador de grupos para a API Evolution, carregando configurações do ambiente.
        """
        self.base_url = os.getenv("EVO_BASE_URL", "http://localhost:8081")
        self.api_token = os.getenv("EVO_API_TOKEN")
        self.instance_id = os.getenv("EVO_INSTANCE_NAME")
        self.instance_token = os.getenv("EVO_INSTANCE_TOKEN")
        
        paths_this = os.path.dirname(__file__)
        
        self.csv_file = os.path.join(paths_this,"group_summary.csv")

        if not all([self.base_url, self.api_token, self.instance_id, self.instance_token]):
            raise ValueError(
                "As variáveis de ambiente necessárias (EVO_API_URL, EVO_API_TOKEN, EVO_INSTANCE_NAME, EVO_INSTANCE_TOKEN) não estão configuradas corretamente."
            )

        self.client = EvolutionClient(base_url=self.base_url, api_token=self.api_token)
        self.groups = []

    def load_summary_info(self):
        """
        Carrega ou cria o DataFrame contendo as informações de resumo dos grupos.
        """
        try:
            return pd.read_csv(self.csv_file)
        except FileNotFoundError:
            # Se o arquivo não existe, cria um DataFrame vazio
            return pd.DataFrame(columns=["group_id", "dias", "horario", "enabled", "is_links", "is_names"])
    
    def load_data_by_group(self, group_id):
        
        try:
        
            df = self.load_summary_info()
            
            resumo = df[df["group_id"] == group_id]
            
            if not resumo.empty:
                resumo = resumo.iloc[0].to_dict()
            else:
                resumo = False
        
        except Exception as e:
            resumo = False
        
        return resumo

    def fetch_groups(self):
        """
        Busca todos os grupos da instância, atualiza a lista interna de grupos e carrega os dados de resumo.
        """
        # Busca os dados de resumo do CSV
        summary_data = self.load_summary_info()

        # Busca os grupos da API
        groups_data = self.client.group.fetch_all_groups(
            instance_id=self.instance_id,
            instance_token=self.instance_token,
            get_participants=False
        )

        # Atualiza a lista de grupos com objetos `Group`
        self.groups = []
        for group in groups_data:
            # Dados básicos do grupo
            group_id = group["id"]

            # Dados de resumo (se existirem no CSV)
            resumo = summary_data[summary_data["group_id"] == group_id]
            if not resumo.empty:
                resumo = resumo.iloc[0].to_dict()  # Converte para dicionário
                horario = resumo.get("horario", "22:00")
                enabled = resumo.get("enabled", False)
                is_links = resumo.get("is_links", False)
                is_names = resumo.get("is_names", False)
            else:
                # Valores padrão para grupos sem resumo no CSV
                horario = "22:00"
                enabled = False
                is_links = False
                is_names = False

            # Criação do objeto Group
            self.groups.append(
                Group(
                    group_id=group_id,
                    name=group["subject"],
                    subject_owner=group["subjectOwner"],
                    subject_time=group["subjectTime"],
                    picture_url=group.get("pictureUrl", None),
                    size=group["size"],
                    creation=group["creation"],
                    owner=group["owner"],
                    restrict=group["restrict"],
                    announce=group["announce"],
                    is_community=group["isCommunity"],
                    is_community_announce=group["isCommunityAnnounce"],
                    horario=horario,
                    enabled=enabled,
                    is_links=is_links,
                    is_names=is_names
                )
            )
        return self.groups

    def update_summary(self, group_id, horario, enabled, is_links, is_names, script):
        """
        Atualiza ou adiciona configurações de resumo ao CSV.
        """
        try:
        
            df = self.load_summary_info()

            # Verifica se o grupo já existe no DataFrame
            if group_id in df["group_id"].values:
                df.loc[df["group_id"] == group_id, ["horario", "enabled", "is_links", "is_names"]] = [
                    horario, enabled, is_links, is_names
                ]
            else:
                # Adiciona uma nova linha com as configurações
                nova_linha = {
                    "group_id": group_id,
                    "horario": horario,
                    "enabled": enabled,
                    "is_links": is_links,
                    "is_names": is_names,
                }
                df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
                
                
            task_name = f"ResumoGrupo_{group_id}"
            
            try:
                TaskScheduled.delete_task(task_name)
            except Exception as e:
                pass
            
            if enabled:
                               
                python_script = os.path.join(script)
                
                TaskScheduled.create_task(
                    task_name, 
                    python_script, 
                    schedule_type='DAILY', 
                    time=horario
                )
                
            TaskScheduled.list_tasks()


            # Salva o DataFrame atualizado no CSV
            df.to_csv(self.csv_file, index=False)
            
            return True
        except Exception as e:
            print(f"Erro ao salvar as configurações: {e}")
            return False

    def get_groups(self):
        """
        Retorna a lista de grupos.

        :return: Lista de objetos `Group`.
        """
        return self.groups

    def find_group_by_id(self, group_id):
        """
        Encontra um grupo pelo ID.

        :param group_id: ID do grupo a ser encontrado.
        :return: Objeto `Group` correspondente ou `None` se não encontrado.
        """
        
        if not self.groups:
            self.groups = self.fetch_groups()
        
        for group in self.groups:
            if group.group_id == group_id:
                return group
        return None

    def filter_groups_by_owner(self, owner):
        """
        Filtra grupos pelo proprietário.

        :param owner: ID do proprietário.
        :return: Lista de grupos que pertencem ao proprietário especificado.
        """
        return [group for group in self.groups if group.owner == owner]
    

    def get_messages(self, group_id, start_date, end_date):
        # Convertendo as datas para o formato ISO 8601 com T e Z
        def to_iso8601(date_str):
            # Parseando a data no formato 'YYYY-MM-DD HH:MM:SS'
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            # Convertendo para o formato ISO 8601 com Z
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Ajustando os parâmetros de data
        timestamp_start = to_iso8601(start_date)
        timestamp_end = to_iso8601(end_date)

        # Buscando as mensagens do grupo
        group_mensagens = self.client.chat.get_messages(
            instance_id=self.instance_id,
            remote_jid=group_id,
            instance_token=self.instance_token,
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
            page=1,
            offset=1000
        )
        
        msgs = MessageSandeco.get_messages(group_mensagens)
        
        data_obj = datetime.strptime(timestamp_start, "%Y-%m-%dT%H:%M:%SZ")
        # Obter o timestamp
        timestamp_limite = int(data_obj.timestamp())

        
        msgs_filtradas = []
        for msg in msgs:
            if msg.message_timestamp >= timestamp_limite:
                msgs_filtradas.append(msg)

        
        return msgs_filtradas
        
        


        

           
    
#controler = GroupController()

#messages = controler.get_messages("120363372879654391@g.us", '2025-01-22 00:00:00', '2025-01-22 23:59:59')

#messages = controler.get_messages("120363391798069472@g.us", "2025-01-21 00:00:00", "2025-01-22 23:59:59")


#i=0