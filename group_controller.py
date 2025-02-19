import sys  # Importa o módulo sys para funcionalidades do sistema operacional
import os  # Importa o módulo os para interagir com o sistema de arquivos
import json  # Importa o módulo json para manipular funções relacionadas a JSON
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Adiciona o diretório pai ao PATH para facilitar importações

# group_manager.py
import os  # Importa o módulo os novamente (pode ser redundante, mas garante acesso a funções de sistema)
from dotenv import load_dotenv  # Importa a função load_dotenv para carregar variáveis de ambiente de um arquivo .env
from datetime import datetime  # Importa a classe datetime para manipulação de datas e horas
from evolutionapi.client import EvolutionClient  # Importa EvolutionClient de evolutionapi.client para interagir com a API Evolution
from group import Group  # Importa a classe Group definida no arquivo group.py
import pandas as pd  # Importa o módulo pandas, comumente usado para manipulação de DataFrames

from message_sandeco import MessageSandeco  # Importa a classe ou funções de MessageSandeco para manipular mensagens

from task_scheduler import TaskScheduled  # Importa TaskScheduled para gerenciar agendamento de tarefas

# Carregar variáveis de ambiente
load_dotenv()  # Chama a função load_dotenv para carregar as variáveis de ambiente definidas no arquivo .env

 
class GroupController:  # Define a classe GroupController, responsável por gerenciar grupos e suas operações
    def __init__(self):  # Método construtor que inicializa a instância do GroupController

        """ 
        Inicializa o gerenciador de grupos para a API Evolution, carregando configurações do ambiente. 
        """
        self.base_url = os.getenv("EVO_BASE_URL")  # Obtém a URL base da API Evolution a partir das variáveis de ambiente
        self.api_token = os.getenv("EVO_API_TOKEN")  # Obtém o token de autenticação da API a partir das variáveis de ambiente
        self.instance_id = os.getenv("EVO_INSTANCE_NAME")  # Obtém o nome/ID da instância da API a partir das variáveis de ambiente
        self.instance_token = os.getenv("EVO_INSTANCE_TOKEN")  # Obtém o token da instância da API

        paths_this = os.path.dirname(__file__)  # Determina o diretório atual onde o arquivo está localizado

        self.csv_file = os.path.join(paths_this, "group_summary.csv")  # Define o caminho para o arquivo CSV de resumo dos grupos
        self.cache_file = os.path.join(paths_this, "groups_cache.json")  # Define o caminho para o arquivo JSON de cache dos grupos

        if not all([self.base_url, self.api_token, self.instance_id, self.instance_token]):  # Verifica se todas as variáveis necessárias foram configuradas
            raise ValueError(  # Caso alguma variável esteja faltando, levanta um erro de valor
                "As variáveis de ambiente necessárias (EVOLUTION_API_URL, EVOLUTION_API_TOKEN, EVOLUTION_INSTANCE_NAME, EVOLUTION_INSTANCE_TOKEN) não estão configuradas corretamente."
            )

        self.client = EvolutionClient(base_url=self.base_url, api_token=self.api_token)  # Inicializa o cliente da API Evolution com os parâmetros configurados
        self.groups = []  # Inicializa uma lista vazia que armazenará os objetos Group


    def _load_cache(self):  # Método privado para carregar os dados de cache, se existirem
        """Carrega dados do cache se existirem."""
        try:  # Inicia um bloco que tenta executar a leitura do cache
            if not os.path.exists(self.cache_file):  # Verifica se o arquivo de cache não existe
                return None  # Se não existir, retorna None
            with open(self.cache_file, 'r') as f:  # Abre o arquivo de cache em modo leitura
                return json.load(f)  # Carrega e retorna os dados do arquivo JSON
        except Exception as e:  # Caso ocorra qualquer exceção durante a leitura
            print(f"Erro ao carregar cache: {str(e)}")  # Imprime a mensagem de erro no console
            return None  # Retorna None indicando falha no carregamento do cache


    def _save_cache(self, groups_data):  # Método privado para salvar os dados de cache com um timestamp
        """Salva dados no cache com timestamp."""
        try:  # Tenta executar a operação de escrita no cache
            cache_data = {  # Cria um dicionário para armazenar os dados de cache
                'timestamp': datetime.now().isoformat(),  # Armazena a data e hora atual no formato ISO
                'groups': groups_data  # Armazena os dados dos grupos
            }
            with open(self.cache_file, 'w') as f:  # Abre o arquivo de cache em modo escrita
                json.dump(cache_data, f)  # Escreve o dicionário de cache no arquivo em formato JSON
        except Exception as e:  # Caso ocorra um erro durante o salvamento
            print(f"Erro ao salvar cache: {str(e)}")  # Imprime a mensagem de erro no console


    def _fetch_from_api(self):  # Método privado para buscar os grupos diretamente da API com mecanismo de retries
        """Busca grupos da API com retry mechanism."""
        import time  # Importa o módulo time para manipulação de tempos e delays
        from evolutionapi.exceptions import EvolutionAPIError  # Importa a exceção específica da API Evolution

        max_retries = 3  # Define o número máximo de tentativas para buscar os dados
        base_delay = 15  # Define um delay base de 15 segundos para aguardar entre as tentativas em caso de erro

        for attempt in range(max_retries):  # Loop que tentará buscar os dados até o número máximo de tentativas
            try:  # Tenta executar a chamada para a API
                return self.client.group.fetch_all_groups(  # Retorna os grupos obtidos pela API
                    instance_id=self.instance_id,  # Passa o instance_id configurado
                    instance_token=self.instance_token,  # Passa o token da instância
                    get_participants=False  # Indica que não é necessário trazer informações dos participantes
                )
            except EvolutionAPIError as e:  # Se ocorrer um erro relacionado à API
                if 'rate-overlimit' in str(e) and attempt < max_retries - 1:  # Se o erro estiver relacionado ao limite de requisições e ainda houver tentativas
                    wait_time = base_delay * (2 ** attempt)  # Calcula o tempo de espera que aumenta exponencialmente: 15s, 30s, 60s
                    print(f"Rate limit atingido. Aguardando {wait_time} segundos antes de tentar novamente...")  # Informa o usuário sobre o delay
                    time.sleep(wait_time)  # Pausa a execução pelo tempo calculado
                else:  # Se o erro não for por rate limit ou não restar mais tentativas
                    raise  # Levanta a exceção para ser tratada fora do método
        raise Exception("Não foi possível buscar os grupos após várias tentativas")  # Caso todas as tentativas falhem, lança uma exceção explicativa


    def fetch_groups(self, force_refresh=False):  # Método público que busca todos os grupos, utilizando cache se possível
        """
        Busca todos os grupos da instância, usando cache quando possível.
  
        Args:
            force_refresh (bool): Se True, ignora o cache e força atualização da API
        """
        # Busca os dados de resumo do CSV
        summary_data = self.load_summary_info()  # Carrega o resumo dos grupos a partir do arquivo CSV

        groups_data = None  # Inicializa a variável que armazenará os dados dos grupos

        if not force_refresh:  # Se não for forçada a atualização
            cache_data = self._load_cache()  # Tenta carregar os dados do cache
            if cache_data and "groups" in cache_data:  # Se os dados do cache existirem e contiverem a chave "groups"
                print("Usando dados do cache...")  # Informa que os dados do cache serão usados
                groups_data = cache_data["groups"]  # Atribui os dados dos grupos vindos do cache
            else:  # Caso o cache não exista ou não contenha os dados necessários
                print("Cache não encontrado. Buscando da API...")  # Informa que será feita a chamada à API
                groups_data = self._fetch_from_api()  # Busca os dados dos grupos na API
                self._save_cache(groups_data)  # Salva os dados obtidos no cache
        else:  # Se force_refresh for True, ignorando o cache
            try:
                print("Forçando atualização da API...")  # Informa que a atualização será forçada
                groups_data = self._fetch_from_api()  # Busca os dados diretamente da API
                self._save_cache(groups_data)  # Salva os dados no cache
            except Exception as e:  # Se ocorrer algum erro durante a tentativa de atualização
                if "rate-overlimit" in str(e):  # Verifica se o erro é por exceder o limite de requisições
                    print("Rate limit atingido. Verificando cache para fallback...")  # Informa que será consultado o cache como alternativa
                    cache_data = self._load_cache()  # Tenta carregar os dados do cache
                    if cache_data and "groups" in cache_data:  # Se os dados do cache estiverem disponíveis
                        groups_data = cache_data["groups"]  # Usa os dados do cache
                    else:  # Se não houver dados de cache disponíveis
                        raise e  # Levanta a exceção original
                else:  # Se o erro não for de rate limit
                    raise e  # Levanta a exceção para tratamento externo

        # Processa os dados dos grupos obtidos
        self.groups = []  # Reinicializa a lista de grupos
        for group in groups_data:  # Percorre cada grupo retornado dos dados
            group_id = group["id"]  # Extrai o identificador do grupo a partir dos dados

            # Dados de resumo (se existirem no CSV)
            resumo = summary_data[summary_data["group_id"] == group_id]  # Filtra o DataFrame para encontrar dados correspondentes ao group_id
            if not resumo.empty:  # Se o resumo não estiver vazio (ou seja, há informações disponíveis)
                resumo = resumo.iloc[0].to_dict()  # Converte a primeira linha do resumo em um dicionário
                horario = resumo.get("horario", "22:00")  # Obtém o horário do resumo ou define "22:00" como padrão
                enabled = resumo.get("enabled", False)  # Obtém a flag enabled ou define False como padrão
                is_links = resumo.get("is_links", False)  # Obtém a flag is_links ou define False como padrão
                is_names = resumo.get("is_names", False)  # Obtém a flag is_names ou define False como padrão
            else:  # Se não houver resumo disponível para o grupo
                horario = "22:00"  # Define o horário padrão "22:00"
                enabled = False  # Define enabled como False
                is_links = False  # Define is_links como False
                is_names = False  # Define is_names como False

            # Criação do objeto Group com base nas informações coletadas
            self.groups.append(
                Group(
                    group_id=group_id,  # Define o ID do grupo
                    name=group["subject"],  # Define o nome do grupo a partir do campo 'subject'
                    subject_owner=group.get("subjectOwner", "remoteJid"),  # Define o owner do grupo, usando valor padrão se necessário
                    subject_time=group["subjectTime"],  # Define o horário do assunto do grupo
                    picture_url=group.get("pictureUrl", None),  # Define a URL da imagem do grupo, se disponível
                    size=group["size"],  # Define o tamanho (número de membros) do grupo
                    creation=group["creation"],  # Define a data de criação do grupo
                    owner=group.get("owner", None),  # Define o dono do grupo, se disponível
                    restrict=group["restrict"],  # Indica se o grupo possui restrições configuradas
                    announce=group["announce"],  # Indica se o grupo possui anúncio configurado
                    is_community=group["isCommunity"],  # Indica se o grupo é uma comunidade
                    is_community_announce=group["isCommunityAnnounce"],  # Indica se há anúncio na comunidade
                    horario=horario,  # Define o horário configurado (virou do CSV ou o padrão)
                    enabled=enabled,  # Define se a função está ativada, conforme o CSV ou padrão
                    is_links=is_links,  # Define se os links estão configurados para esse grupo
                    is_names=is_names  # Define se os nomes estão configurados para esse grupo
                )
            )
        return self.groups  # Retorna a lista de grupos processados


    def load_summary_info(self):  # Método para carregar ou criar um DataFrame com as informações de resumo dos grupos
        """ 
        Carrega ou cria o DataFrame contendo as informações de resumo dos grupos. 
        """
        try:
            return pd.read_csv(self.csv_file)  # Tenta ler o arquivo CSV com os dados de resumo
        except FileNotFoundError:  # Se o arquivo CSV não for encontrado
            # Se o arquivo não existe, cria um DataFrame vazio
            return pd.DataFrame(columns=["group_id", "dias", "horario", "enabled", "is_links", "is_names"])  # Retorna um DataFrame vazio com as colunas especificadas


    def load_data_by_group(self, group_id):  # Método para carregar os dados de resumo específicos de um grupo
        try:
            df = self.load_summary_info()  # Carrega o DataFrame com os dados de resumo
            resumo = df[df["group_id"] == group_id]  # Filtra o DataFrame para encontrar o grupo com o group_id especificado

            if not resumo.empty:  # Se houver dados para o grupo
                resumo = resumo.iloc[0].to_dict()  # Converte a primeira linha do resultado em um dicionário
            else:  # Se não houver dados para o grupo
                resumo = False  # Define resumo como False para indicar ausência de dados

        except Exception as e:  # Em caso de erro durante o processo
            resumo = False  # Define resumo como False

        return resumo  # Retorna os dados do grupo ou False se não encontrados


    def update_summary(self, group_id, horario, enabled, is_links, is_names, script):  
        # Método para atualizar ou adicionar configurações de resumo ao CSV
        """ 
        Atualiza ou adiciona configurações de resumo ao CSV. 
        """
        try:
            # Load existing data
            df = self.load_summary_info()  # Carrega os dados atuais do CSV em um DataFrame

            # Update or add new row
            if group_id in df["group_id"].values:  # Verifica se o group_id já existe no DataFrame
                df.loc[df["group_id"] == group_id, ["horario", "enabled", "is_links", "is_names"]] = [
                    horario, enabled, is_links, is_names  # Atualiza as colunas correspondentes com os novos valores
                ]
            else:
                nova_linha = {  # Cria um dicionário representando a nova linha com as configurações do grupo
                    "group_id": group_id,  # Define a chave group_id com o identificador do grupo
                    "horario": horario,    # Define o horário configurado
                    "enabled": enabled,    # Define se o resumo está ativado
                    "is_links": is_links,  # Define se links estão configurados
                    "is_names": is_names,  # Define se nomes estão configurados
                }
                df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)  # Adiciona a nova linha ao DataFrame, reindexando as linhas

            # Handle task scheduling
            task_name = f"ResumoGrupo_{group_id}"  # Cria um nome único para a tarefa do grupo, combinando uma string com o group_id

            # Always try to remove existing task first
            try:
                TaskScheduled.delete_task(task_name)  # Tenta remover uma tarefa já agendada com o mesmo nome
            except Exception:  # Se ocorrer algum erro (por exemplo, se a tarefa não existir)
                pass  # Ignora o erro e continua a execução

            # Create new task if enabled
            if enabled:  # Se a configuração estiver ativada
                python_script = os.path.join(script)  # Define o caminho para o script Python que deverá ser executado
                TaskScheduled.create_task(
                    task_name,   # Nome da tarefa
                    python_script,  # Caminho do script que será agendado
                    schedule_type='DAILY',  # Tipo de agendamento (diário)
                    time=horario  # Define o horário de execução da tarefa
                )

            # Save CSV changes
            df.to_csv(self.csv_file, index=False)  # Salva as alterações feitas no DataFrame de volta ao arquivo CSV, sem os índices
            return True  # Retorna True para indicar sucesso na operação

        except Exception as e:  # Se ocorrer algum erro durante a atualização
            print(f"Erro ao salvar as configurações: {e}")  # Imprime uma mensagem de erro
            return False  # Retorna False para indicar que a operação falhou


    def get_groups(self):  # Método que retorna a lista de grupos armazenada no objeto
        """ 
        Retorna a lista de grupos. 
  
        :return: Lista de objetos `Group`. 
        """
        return self.groups  # Retorna a lista de grupos já processada e armazenada na instância


    def find_group_by_id(self, group_id):  # Método para buscar um grupo específico pelo seu ID
        """ 
        Encontra um grupo pelo ID.
  
        :param group_id: ID do grupo a ser encontrado.
        :return: Objeto `Group` correspondente ou `None` se não encontrado.
        """
        if not self.groups:  # Se a lista de grupos estiver vazia
            self.groups = self.fetch_groups()  # Busca os grupos utilizando o método fetch_groups

        for group in self.groups:  # Itera sobre cada grupo na lista
            if group.group_id == group_id:  # Verifica se o ID do grupo atual corresponde ao procurado
                return group  # Retorna o grupo encontrado
        return None  # Se nenhum grupo correspondente for encontrado, retorna None


    def filter_groups_by_owner(self, owner):  # Método para filtrar grupos com base no proprietário
        """ 
        Filtra grupos pelo proprietário.
  
        :param owner: ID do proprietário.
        :return: Lista de grupos que pertencem ao proprietário especificado.
        """
        return [group for group in self.groups if group.owner == owner]  # Retorna uma lista contendo apenas os grupos cujo owner corresponde ao parâmetro


    def get_messages(self, group_id, start_date, end_date):  # Método para obter mensagens de um grupo dentro de um intervalo de datas
        # Convertendo as datas para o formato ISO 8601 com T e Z
        def to_iso8601(date_str):  # Função interna para converter uma string de data para o formato ISO 8601
            # Parseando a data no formato 'YYYY-MM-DD HH:MM:SS'
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")  # Converte a string para um objeto datetime, assumindo o formato específico
            # Convertendo para o formato ISO 8601 com Z
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")  # Formata a data no padrão ISO 8601 e adiciona o sufixo "Z" para indicar UTC

        # Ajustando os parâmetros de data
        timestamp_start = to_iso8601(start_date)  # Converte a data de início para o formato ISO 8601
        timestamp_end = to_iso8601(end_date)  # Converte a data de término para o formato ISO 8601

        # Buscando as mensagens do grupo
        group_mensagens = self.client.chat.get_messages(  # Chama a função da API para obter as mensagens do grupo
            instance_id=self.instance_id,  # Usa o instance_id configurado
            remote_jid=group_id,  # Passa o identificador do grupo
            instance_token=self.instance_token,  # Usa o token da instância
            timestamp_start=timestamp_start,  # Define o início do intervalo de tempo
            timestamp_end=timestamp_end,  # Define o final do intervalo de tempo
            page=1,  # Número da página para paginação (inicialmente 1)
            offset=1000  # Offset para a paginação, determinando quantas mensagens pular (valor fixo de 1000)
        )

        msgs = MessageSandeco.get_messages(group_mensagens)  # Processa as mensagens retornadas pela API usando a função get_messages de MessageSandeco

        data_obj = datetime.strptime(timestamp_start, "%Y-%m-%dT%H:%M:%SZ")  # Converte a data convertida de início de volta para um objeto datetime
        # Obter o timestamp
        timestamp_limite = int(data_obj.timestamp())  # Obtém o timestamp (segundos desde a época) a partir do objeto datetime

        msgs_filtradas = []  # Inicializa uma lista para armazenar as mensagens filtradas
        for msg in msgs:  # Itera sobre cada mensagem obtida
            if msg.message_timestamp >= timestamp_limite:  # Verifica se o timestamp da mensagem é maior ou igual ao limite calculado
                msgs_filtradas.append(msg)  # Se sim, adiciona a mensagem à lista de mensagens filtradas

        return msgs_filtradas  # Retorna a lista de mensagens filtradas


# Trecho de código comentado para execução ou testes
"""controler = GroupController() 
 
grupos = controler.fetch_groups() 
 
for grupo in grupos: 
    print(f"ID: {grupo.group_id} Grupo: {grupo.name}")  
 
messages = controler.get_messages("553184175033-1435076483@g.us","2025-02-04 00:00:00","2025-02-06 23:59:59") 
print(messages) 
i=0""" 
 
#controler = GroupController() 
 
#messages = controler.get_messages("120363372879654391@g.us", '2025-01-22 00:00:00', '2025-01-22 23:59:59') 
 
#messages = controler.get_messages("120363391798069472@g.us", "2025-01-21 00:00:00", "2025-01-22 23:59:59") 
 
 
#i=0