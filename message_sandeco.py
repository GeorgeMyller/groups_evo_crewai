import base64  # Importa o módulo base64 para realizar operações de codificação e decodificação em base64

class MessageSandeco:
    
    # Definição de constantes para identificar os tipos de mensagem
    TYPE_TEXT = "conversation"            # Constante para mensagens de texto
    TYPE_AUDIO = "audioMessage"           # Constante para mensagens de áudio
    TYPE_IMAGE = "imageMessage"           # Constante para mensagens de imagem
    TYPE_DOCUMENT = "documentMessage"     # Constante para mensagens de documento
    
    # Constantes para definir o escopo da mensagem
    SCOPE_GROUP = "group"                 # Escopo para mensagens de grupo
    SCOPE_PRIVATE = "private"             # Escopo para mensagens privadas
    
    def __init__(self, raw_data):
        # Construtor que inicializa o objeto com os dados brutos da mensagem
        
        # Verifica se o dicionário recebido é do formato completo (possui a chave 'data')
        if "data" not in raw_data:
            # Se não possui, assume que o formato é simples e "envolve" os dados em um dicionário padrão
            enveloped_data = {
                "event": None,            # Nenhum evento definido
                "instance": None,         # Nenhuma instância definida
                "destination": None,      # Sem destino definido
                "date_time": None,        # Sem data/hora definida
                "server_url": None,       # Sem URL de servidor
                "apikey": None,           # Sem chave de API
                "data": raw_data          # Todo o conteúdo simples é armazenado na chave 'data'
            }
        else:
            # Se já possui a chave 'data', assume que o formato já está completo
            enveloped_data = raw_data
        
        self.data = enveloped_data       # Armazena os dados (envolvidos ou completos) no atributo 'data'
        self.extract_common_data()       # Chama método para extrair dados comuns da mensagem
        self.extract_specific_data()     # Chama método para extrair dados específicos de acordo com o tipo da mensagem

    def extract_common_data(self):
        """Extrai os dados comuns e define os atributos da classe."""
        self.event = self.data.get("event")         # Extrai o evento da mensagem
        self.instance = self.data.get("instance")   # Extrai a instância da mensagem
        self.destination = self.data.get("destination")  # Extrai o destino da mensagem
        self.date_time = self.data.get("date_time")   # Extrai a data/hora do evento
        self.server_url = self.data.get("server_url") # Extrai a URL do servidor
        self.apikey = self.data.get("apikey")         # Extrai a chave de API
        
        data = self.data.get("data", {})              # Extrai o conteúdo da mensagem, default para dicionário vazio se não existir
        key = data.get("key", {})                     # Extrai a chave 'key' do conteúdo, se disponível
        
        # Atribuição dos atributos diretos da mensagem
        self.remote_jid = key.get("remoteJid")        # Número remoto associado à mensagem
        self.message_id = key.get("id")               # ID único da mensagem
        self.from_me = key.get("fromMe")              # Flag que indica se a mensagem foi enviada pelo próprio usuário
        self.push_name = data.get("pushName")         # Nome que aparece no dispositivo do remetente
        self.status = data.get("status")              # Status da mensagem (ex.: enviada, entregue)
        self.instance_id = data.get("instanceId")     # ID da instância que enviou a mensagem
        self.source = data.get("source")              # Fonte da mensagem
        self.message_timestamp = data.get("messageTimestamp")  # Timestamp da mensagem
        self.message_type = data.get("messageType")   # Tipo de mensagem (texto, áudio, imagem, documento)
        self.sender = data.get("sender")              # Identificação do remetente (específico para grupos)
        self.participant = key.get("participant")     # Participante que enviou a mensagem no grupo

        # Determina o escopo (grupo ou privado) da mensagem
        self.determine_scope()

    def determine_scope(self):
        """Determina se a mensagem é de grupo ou privada e define os atributos correspondentes."""
        if self.remote_jid.endswith("@g.us"):
            self.scope = self.SCOPE_GROUP         # Define o escopo como grupo
            self.group_id = self.remote_jid.split("@")[0]  # Extrai o ID do grupo a partir do remote_jid
            # Define o número do remetente do grupo, se disponível
            self.phone = self.participant.split("@")[0] if self.participant else None
        elif self.remote_jid.endswith("@s.whatsapp.net"):
            self.scope = self.SCOPE_PRIVATE       # Define o escopo como privado
            self.phone = self.remote_jid.split("@")[0]  # Extrai o número do contato a partir do remote_jid
            self.group_id = None                   # Mensagens privadas não possuem grupo
        else:
            self.scope = "unknown"                 # Caso o formato não seja reconhecido, define como desconhecido
            self.phone = None                      # Nenhum número extraído
            self.group_id = None                   # Nenhum grupo associado

    def extract_specific_data(self):
        """Extrai dados específicos e os define como atributos da classe."""
        # Verifica o tipo de mensagem para chamar o método de extração correspondente
        if self.message_type == self.TYPE_TEXT:
            self.extract_text_message()           # Extrai conteúdo de mensagem de texto
        elif self.message_type == self.TYPE_AUDIO:
            self.extract_audio_message()          # Extrai conteúdo de mensagem de áudio
        elif self.message_type == self.TYPE_IMAGE:
            self.extract_image_message()          # Extrai conteúdo de mensagem de imagem
        elif self.message_type == self.TYPE_DOCUMENT:
            self.extract_document_message()       # Extrai conteúdo de mensagem de documento

    def extract_text_message(self):
        """Extrai dados de uma mensagem de texto e define como atributos."""
        # Acessa o conteúdo da mensagem e obtém o texto da conversa
        self.text_message = self.data["data"]["message"].get("conversation")

    def extract_audio_message(self):
        """Extrai dados de uma mensagem de áudio e define como atributos da classe."""
        audio_data = self.data["data"]["message"]["audioMessage"]  # Extrai os dados do áudio da mensagem
        self.audio_base64_bytes = self.data["data"]["message"].get("base64")  # Extrai a string base64, se existir
        self.audio_url = audio_data.get("url")                  # Extrai a URL do áudio
        self.audio_mimetype = audio_data.get("mimetype")        # Extrai o tipo MIME do áudio
        self.audio_file_sha256 = audio_data.get("fileSha256")    # Extrai o hash SHA256 do arquivo de áudio
        self.audio_file_length = audio_data.get("fileLength")    # Extrai o tamanho do arquivo de áudio
        self.audio_duration_seconds = audio_data.get("seconds")  # Extrai a duração do áudio em segundos
        self.audio_media_key = audio_data.get("mediaKey")        # Extrai a chave de mídia do áudio
        self.audio_ptt = audio_data.get("ptt")                   # Verifica se é mensagem "push-to-talk"
        self.audio_file_enc_sha256 = audio_data.get("fileEncSha256")  # Extrai o hash do arquivo encriptado
        self.audio_direct_path = audio_data.get("directPath")    # Extrai o caminho direto para o áudio
        self.audio_waveform = audio_data.get("waveform")         # Extrai os dados do waveform da mensagem
        self.audio_view_once = audio_data.get("viewOnce", False) # Determina se a mensagem é visualizada apenas uma vez

    def extract_image_message(self):
        """Extrai dados de uma mensagem de imagem e define como atributos."""
        image_data = self.data["data"]["message"]["imageMessage"]  # Extrai os dados da imagem da mensagem
        self.image_url = image_data.get("url")                  # Extrai a URL da imagem
        self.image_mimetype = image_data.get("mimetype")        # Extrai o tipo MIME da imagem
        self.image_caption = image_data.get("caption")          # Extrai a legenda da imagem
        self.image_file_sha256 = image_data.get("fileSha256")    # Extrai o hash SHA256 do arquivo da imagem
        self.image_file_length = image_data.get("fileLength")    # Extrai o tamanho do arquivo da imagem
        self.image_height = image_data.get("height")           # Extrai a altura da imagem
        self.image_width = image_data.get("width")             # Extrai a largura da imagem
        self.image_media_key = image_data.get("mediaKey")      # Extrai a chave de mídia da imagem
        self.image_file_enc_sha256 = image_data.get("fileEncSha256")  # Extrai o hash do arquivo encriptado da imagem
        self.image_direct_path = image_data.get("directPath")  # Extrai o caminho direto para a imagem
        self.image_media_key_timestamp = image_data.get("mediaKeyTimestamp")  # Extrai o timestamp da chave de mídia
        self.image_thumbnail_base64 = image_data.get("jpegThumbnail")  # Extrai a miniatura da imagem em base64
        self.image_scans_sidecar = image_data.get("scansSidecar")  # Extrai dados adicionais de escaneamento
        self.image_scan_lengths = image_data.get("scanLengths")    # Extrai os comprimentos dos scans
        self.image_mid_quality_file_sha256 = image_data.get("midQualityFileSha256")  # Hash para versão de qualidade média
        self.image_base64 = self.data["data"]["message"].get("base64")  # Extrai a string base64 da imagem, se existir

    def extract_document_message(self):
        """Extrai dados de uma mensagem de documento e define como atributos da classe."""
        document_data = self.data["data"]["message"]["documentMessage"]  # Extrai os dados do documento da mensagem
        self.document_url = document_data.get("url")             # Extrai a URL do documento
        self.document_mimetype = document_data.get("mimetype")   # Extrai o tipo MIME do documento
        self.document_title = document_data.get("title")         # Extrai o título do documento
        self.document_file_sha256 = document_data.get("fileSha256")  # Extrai o hash SHA256 do arquivo do documento
        self.document_file_length = document_data.get("fileLength")  # Extrai o tamanho do arquivo do documento
        self.document_media_key = document_data.get("mediaKey")   # Extrai a chave de mídia do documento
        self.document_file_name = document_data.get("fileName")   # Extrai o nome do arquivo do documento
        self.document_file_enc_sha256 = document_data.get("fileEncSha256")  # Extrai o hash do arquivo encriptado do documento
        self.document_direct_path = document_data.get("directPath")  # Extrai o caminho direto para o documento
        self.document_caption = document_data.get("caption", None)  # Extrai a legenda do documento, se existir
        # Decodifica a string base64 associada ao documento e converte para bytes
        self.document_base64_bytes = self.decode_base64(self.data["data"]["message"].get("base64"))

    def decode_base64(self, base64_string):
        """Converte uma string base64 em bytes."""
        if base64_string:
            return base64.b64decode(base64_string)  # Retorna os bytes decodificados a partir da string base64
        return None  # Se a string estiver vazia ou nula, retorna None

    def get(self):
        """Retorna todos os atributos como um dicionário."""
        return self.__dict__  # Retorna o dicionário interno que contém todos os atributos do objeto

    def get_text(self):
        """Retorna o texto da mensagem, dependendo do tipo."""
        text = ""  # Inicializa a variável para armazenar o texto da mensagem
        if self.message_type == self.TYPE_TEXT:
            text = self.text_message  # Para mensagens de texto, utiliza o atributo text_message
        elif self.message_type == self.TYPE_IMAGE:
            text = self.image_caption  # Para mensagens de imagem, utiliza a legenda da imagem
        elif self.message_type == self.TYPE_DOCUMENT:
            text = self.document_caption  # Para mensagens de documento, utiliza a legenda do documento
        return text  # Retorna o texto extraído

    def get_name(self):
        """Retorna o nome do remetente."""
        return self.push_name  # Retorna o nome indicado no push_name

    @staticmethod
    def get_messages(messages):
        """Retorna uma lista de objetos `MessageSandeco` a partir de uma lista de mensagens."""
        msgs = messages['messages']['records']  # Acessa a lista de registros de mensagens no dicionário recebido
        
        mensagens = []  # Inicializa a lista que armazenará os objetos MessageSandeco
        for msg in msgs:
            mensagens.append(MessageSandeco(msg))  # Para cada mensagem, cria um objeto MessageSandeco e adiciona à lista
        
        return mensagens  # Retorna a lista de objetos MessageSandeco