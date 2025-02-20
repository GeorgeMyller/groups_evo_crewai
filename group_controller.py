"""
Controlador de Grupos do WhatsApp / WhatsApp Groups Controller

PT-BR:
Esta classe gerencia grupos do WhatsApp, incluindo cache local, consultas à API Evolution
e configurações de resumos automáticos. Fornece funcionalidades para buscar, filtrar
e atualizar informações dos grupos.

EN:
This class manages WhatsApp groups, including local caching, Evolution API queries,
and automatic summary settings. Provides functionality to fetch, filter,
and update group information.
"""

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
    def __init__(self):
        """
        PT-BR:
        Inicializa o controlador com configurações do ambiente e validações.
        Configura conexão com API Evolution e caminhos de arquivos locais.

        EN:
        Initializes the controller with environment settings and validations.
        Sets up Evolution API connection and local file paths.
        """
        # Environment setup / Configuração do ambiente
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(env_path, override=True)
        
        # API Configuration / Configuração da API
        self.base_url = os.getenv("EVO_BASE_URL", 'http://localhost:8081')
        self.api_token = os.getenv("EVO_API_TOKEN")
        self.instance_id = os.getenv("EVO_INSTANCE_NAME")
        self.instance_token = os.getenv("EVO_INSTANCE_TOKEN")
        
        # File paths / Caminhos dos arquivos
        paths_this = os.path.dirname(__file__)
        self.csv_file = os.path.join(paths_this, "group_summary.csv")
        self.cache_file = os.path.join(paths_this, "groups_cache.json")
        
        if not all([self.api_token, self.instance_id, self.instance_token]):
            raise ValueError("API_TOKEN, INSTANCE_NAME ou INSTANCE_TOKEN não configurados. / API_TOKEN, INSTANCE_NAME or INSTANCE_TOKEN not configured.")
            
        print(f"Inicializando EvolutionClient com URL / Initializing EvolutionClient with URL: {self.base_url}")
        self.client = EvolutionClient(base_url=self.base_url, api_token=self.api_token)
        self.groups = []

    def _load_cache(self):
        """
        PT-BR:
        Carrega dados do cache local para otimizar requisições.
        Retorna None se o cache estiver inválido ou não existir.

        EN:
        Loads data from local cache to optimize requests.
        Returns None if cache is invalid or doesn't exist.
        """
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
        """
        PT-BR:
        Salva dados dos grupos no cache com timestamp.
        Garante que os dados sejam serializáveis em JSON.

        Parâmetros:
            groups_data: Dados dos grupos a serem salvos

        EN:
        Saves group data to cache with timestamp.
        Ensures data is JSON serializable.

        Parameters:
            groups_data: Group data to be saved
        """
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
        """
        PT-BR:
        Busca grupos da API Evolution com sistema de retry.
        Implementa espera exponencial em caso de limite de requisições.

        Raises:
            Exception: Se não conseguir buscar após várias tentativas

        EN:
        Fetches groups from Evolution API with retry system.
        Implements exponential backoff for rate limits.

        Raises:
            Exception: If unable to fetch after several attempts
        """
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
        """
        PT-BR:
        Obtém lista de grupos usando cache ou API.
        
        Parâmetros:
            force_refresh: Força atualização da API ignorando cache

        Retorna:
            List[Group]: Lista de objetos Group

        EN:
        Gets group list using cache or API.
        
        Parameters:
            force_refresh: Forces API update ignoring cache

        Returns:
            List[Group]: List of Group objects
        """
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
                send_to_group = resumo.get("send_to_group", True)
                send_to_personal = resumo.get("send_to_personal", False)
            else:
                horario = "22:00"
                enabled = False
                is_links = False
                is_names = False
                send_to_group = True
                send_to_personal = False

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
                    is_names=is_names,
                    send_to_group=send_to_group,
                    send_to_personal=send_to_personal
                )
            )
        return self.groups

    def load_summary_info(self):
        """
        PT-BR:
        Carrega ou cria DataFrame com informações de resumo dos grupos.
        
        Retorna:
            DataFrame: Contém configurações de resumo de todos os grupos

        EN:
        Loads or creates DataFrame with group summary information.
        
        Returns:
            DataFrame: Contains summary settings for all groups
        """
        try:
            return pd.read_csv(self.csv_file)
        except FileNotFoundError:
            return pd.DataFrame(columns=[
                "group_id", "dias", "horario", "enabled", 
                "is_links", "is_names", "send_to_group", 
                "send_to_personal"
            ])

    def load_data_by_group(self, group_id):
        """
        PT-BR:
        Carrega configurações de resumo para um grupo específico.
        
        Parâmetros:
            group_id: Identificador do grupo

        Retorna:
            dict/False: Dicionário com configurações ou False se não encontrado

        EN:
        Loads summary settings for a specific group.
        
        Parameters:
            group_id: Group identifier

        Returns:
            dict/False: Dictionary with settings or False if not found
        """
        try:
            df = self.load_summary_info()
            resumo = df[df["group_id"] == group_id]
            return resumo.iloc[0].to_dict() if not resumo.empty else False
        except Exception:
            return False

    def update_summary(self, group_id, horario, enabled, is_links, is_names, script, send_to_group=True, send_to_personal=False, start_date=None, start_time=None, end_date=None, end_time=None):
        """
        PT-BR:
        Atualiza configurações de resumo de um grupo no CSV.
        
        Parâmetros:
            group_id: ID do grupo
            horario: Horário de execução
            enabled: Resumo ativado
            is_links: Incluir links
            is_names: Incluir nomes
            script: Caminho do script
            send_to_group: Enviar para o grupo
            send_to_personal: Enviar para número pessoal
            start_date: Data inicial (opcional)
            start_time: Hora inicial (opcional)
            end_date: Data final (opcional)
            end_time: Hora final (opcional)

        Retorna:
            bool: True se atualizado com sucesso

        EN:
        Updates group summary settings in CSV.
        
        Parameters:
            group_id: Group ID
            horario: Execution time
            enabled: Summary enabled
            is_links: Include links
            is_names: Include names
            script: Script path
            send_to_group: Send to group
            send_to_personal: Send to personal number
            start_date: Start date (optional)
            start_time: Start time (optional)
            end_date: End date (optional)
            end_time: End time (optional)

        Returns:
            bool: True if successfully updated
        """
        try:
            df = pd.read_csv("group_summary.csv")
        except FileNotFoundError:
            df = pd.DataFrame(columns=["group_id", "horario", "enabled", "is_links", "is_names", "script", 
                                     "send_to_group", "send_to_personal",
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
            "send_to_group": send_to_group,
            "send_to_personal": send_to_personal,
            "start_date": start_date if start_date else None,
            "start_time": start_time if start_time else None,
            "end_date": end_date if end_date else None,
            "end_time": end_time if end_time else None
        }
        
        df = pd.concat([df, pd.DataFrame([nova_config])], ignore_index=True)
        df.to_csv("group_summary.csv", index=False)
        
        return True

    def get_groups(self):
        """
        PT-BR:
        Retorna lista de grupos processada.
        
        Retorna:
            List[Group]: Lista atual de objetos Group

        EN:
        Returns processed group list.
        
        Returns:
            List[Group]: Current list of Group objects
        """
        return self.groups

    def find_group_by_id(self, group_id):
        """
        PT-BR:
        Localiza um grupo pelo seu ID.
        
        Parâmetros:
            group_id: ID do grupo a ser encontrado

        Retorna:
            Group/None: Objeto Group ou None se não encontrado

        EN:
        Finds a group by its ID.
        
        Parameters:
            group_id: Group ID to find

        Returns:
            Group/None: Group object or None if not found
        """
        if not self.groups:
            self.groups = self.fetch_groups()
        for group in self.groups:
            if group.group_id == group_id:
                return group
        return None

    def filter_groups_by_owner(self, owner):
        """
        PT-BR:
        Filtra grupos por proprietário.
        
        Parâmetros:
            owner: ID do proprietário

        Retorna:
            List[Group]: Lista de grupos do proprietário

        EN:
        Filters groups by owner.
        
        Parameters:
            owner: Owner ID

        Returns:
            List[Group]: List of owner's groups
        """
        return [group for group in self.groups if group.owner == owner]

    def get_messages(self, group_id, start_date, end_date):
        """
        PT-BR:
        Obtém e filtra mensagens de um grupo em um período.
        
        Parâmetros:
            group_id: ID do grupo
            start_date: Data inicial (formato: YYYY-MM-DD HH:MM:SS)
            end_date: Data final (formato: YYYY-MM-DD HH:MM:SS)

        Retorna:
            List[Message]: Lista de mensagens filtradas

        EN:
        Gets and filters group messages within a period.
        
        Parameters:
            group_id: Group ID
            start_date: Start date (format: YYYY-MM-DD HH:MM:SS)
            end_date: End date (format: YYYY-MM-DD HH:MM:SS)

        Returns:
            List[Message]: List of filtered messages
        """
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
