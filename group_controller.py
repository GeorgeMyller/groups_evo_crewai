import sys
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from evolutionapi.client import EvolutionClient
from group import Group
import pandas as pd
from message_sandeco import MessageSandeco
from task_scheduler import TaskScheduled

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class GroupController:
    """Gerencia grupos, cache, consultas à API e agendamento de tarefas."""
    
    def __init__(self):
        """Inicializa o controlador de grupos com configurações do ambiente."""
        # Carrega .env do diretório do arquivo
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(env_path, override=True)
        
        # Carrega e valida a URL base
        self.base_url = os.getenv("EVO_BASE_URL", 'http://localhost:8081')
        self.api_token = os.getenv("EVO_API_TOKEN")
        self.instance_id = os.getenv("EVO_INSTANCE_NAME")
        self.instance_token = os.getenv("EVO_INSTANCE_TOKEN")
        
        # Configura caminhos dos arquivos
        paths_this = os.path.dirname(__file__)
        self.csv_file = os.path.join(paths_this, "group_summary.csv")
        self.cache_file = os.path.join(paths_this, "groups_cache.json")
        
        # Valida configurações necessárias
        if not all([self.api_token, self.instance_id, self.instance_token]):
            raise ValueError("API_TOKEN, INSTANCE_NAME ou INSTANCE_TOKEN não configurados.")
            
        print(f"Inicializando EvolutionClient com URL: {self.base_url}")
        self.client = EvolutionClient(base_url=self.base_url, api_token=self.api_token)
        self.groups = []

    def _load_cache(self):
        """Carrega dados do cache para evitar chamadas desnecessárias à API."""
        if not os.path.exists(self.cache_file):
            return None
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except json.decoder.JSONDecodeError as e:
            print(f"Cache com formato inválido. Removendo o arquivo: {e}")
            os.remove(self.cache_file)
            return None
        except Exception as e:
            print(f"Erro ao carregar cache: {str(e)}")
            return None

    def _save_cache(self, groups_data):
        """Salva dados dos grupos no cache com um timestamp, garantindo que groups_data seja JSON serializável."""
        try:
            # Verifica se groups_data é do tipo serializável (list ou dict), senão ajusta
            if not isinstance(groups_data, (list, dict)):
                print("groups_data não é serializável. Ajustando para lista vazia.")
                groups_data = []
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'groups': groups_data
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            print(f"Erro ao salvar cache: {str(e)}")

    def _fetch_from_api(self):
        """Busca grupos diretamente da API com retries em caso de limite de requisições."""
        import time
        from evolutionapi.exceptions import EvolutionAPIError
        
        # Verifica se as configurações ainda estão válidas
        if '<' in self.base_url or '>' in self.base_url:
            print("URL inválida detectada, redefinindo para padrão...")
            self.base_url = 'http://localhost:8081'
            self.client = EvolutionClient(base_url=self.base_url, api_token=self.api_token)
            
        max_retries = 3
        base_delay = 15
        for attempt in range(max_retries):
            try:
                print(f"Tentativa {attempt + 1}: Fazendo requisição para {self.base_url}")
                return self.client.group.fetch_all_groups(
                    instance_id=self.instance_id,
                    instance_token=self.instance_token,
                    get_participants=False
                )
            except EvolutionAPIError as e:
                if 'rate-overlimit' in str(e) and attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt)
                    print(f"Rate limit atingido. Aguardando {wait_time} segundos...")
                    time.sleep(wait_time)
                else:
                    print(f"Erro na API: {str(e)}")
                    raise
        raise Exception("Não foi possível buscar os grupos após várias tentativas")

    def fetch_groups(self, force_refresh=False):
        """Obtém a lista de grupos usando cache ou consulta à API."""
        summary_data = self.load_summary_info()
        groups_data = None
        if not force_refresh:
            cache_data = self._load_cache()
            if cache_data and "groups" in cache_data:
                print("Usando dados do cache...")
                groups_data = cache_data["groups"]
            else:
                print("Cache não encontrado. Buscando da API...")
                groups_data = self._fetch_from_api()
                self._save_cache(groups_data)
        else:
            try:
                print("Forçando atualização da API...")
                groups_data = self._fetch_from_api()
                self._save_cache(groups_data)
            except Exception as e:
                if "rate-overlimit" in str(e):
                    print("Rate limit atingido. Verificando cache para fallback...")
                    cache_data = self._load_cache()
                    if cache_data and "groups" in cache_data:
                        groups_data = cache_data["groups"]
                    else:
                        raise e
                else:
                    raise e
        self.groups = []
        for group in groups_data:
            group_id = group["id"]
            resumo = summary_data[summary_data["group_id"] == group_id]
            if not resumo.empty:
                resumo = resumo.iloc[0].to_dict()
                horario = resumo.get("horario", "22:00")
                enabled = resumo.get("enabled", False)
                is_links = resumo.get("is_links", False)
                is_names = resumo.get("is_names", False)
            else:
                horario = "22:00"
                enabled = False
                is_links = False
                is_names = False
            self.groups.append(
                Group(
                    group_id=group_id,
                    name=group["subject"],
                    subject_owner=group.get("subjectOwner", "remoteJid"),
                    subject_time=group["subjectTime"],
                    picture_url=group.get("pictureUrl", None),
                    size=group["size"],
                    creation=group["creation"],
                    owner=group.get("owner", None),
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

    def load_summary_info(self):
        """Carrega ou cria o DataFrame de informações resumidas dos grupos."""
        try:
            return pd.read_csv(self.csv_file)
        except FileNotFoundError:
            return pd.DataFrame(columns=["group_id", "dias", "horario", "enabled", "is_links", "is_names"])

    def load_data_by_group(self, group_id):
        """Carrega os dados de resumo para um grupo específico."""
        try:
            df = self.load_summary_info()
            resumo = df[df["group_id"] == group_id]
            return resumo.iloc[0].to_dict() if not resumo.empty else False
        except Exception:
            return False

    def update_summary(self, group_id, horario, enabled, is_links, is_names, script, start_date=None, start_time=None, end_date=None, end_time=None):
        """Atualiza o CSV com as novas configurações do resumo."""
        try:
            df = pd.read_csv("group_summary.csv")
        except FileNotFoundError:
            df = pd.DataFrame(columns=["group_id", "horario", "enabled", "is_links", "is_names", "script", 
                                     "start_date", "start_time", "end_date", "end_time"])
        
        # Remove qualquer entrada existente para o grupo
        df = df[df['group_id'] != group_id]
        
        # Adiciona a nova configuração
        nova_config = {
            "group_id": group_id,
            "horario": horario,
            "enabled": enabled,
            "is_links": is_links,
            "is_names": is_names,
            "script": script,
            "start_date": start_date if start_date else None,
            "start_time": start_time if start_time else None,
            "end_date": end_date if end_date else None,
            "end_time": end_time if end_time else None
        }
        
        df = pd.concat([df, pd.DataFrame([nova_config])], ignore_index=True)
        df.to_csv("group_summary.csv", index=False)
        
        return True

    def get_groups(self):
        """Retorna a lista de grupos processada."""
        return self.groups

    def find_group_by_id(self, group_id):
        """Procura um grupo pelo seu identificador."""
        if not self.groups:
            self.groups = self.fetch_groups()
        for group in self.groups:
            if group.group_id == group_id:
                return group
        return None

    def filter_groups_by_owner(self, owner):
        """Filtra os grupos de um determinado proprietário."""
        return [group for group in self.groups if group.owner == owner]

    def get_messages(self, group_id, start_date, end_date):
        """Obtém e filtra as mensagens de um grupo entre duas datas."""
        def to_iso8601(date_str):
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        timestamp_start = to_iso8601(start_date)
        timestamp_end = to_iso8601(end_date)
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
        timestamp_limite = int(data_obj.timestamp())
        msgs_filtradas = [msg for msg in msgs if msg.message_timestamp >= timestamp_limite]
        return msgs_filtradas
