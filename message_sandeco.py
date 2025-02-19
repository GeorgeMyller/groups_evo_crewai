import base64

"""
Processador de Mensagens do WhatsApp / WhatsApp Message Processor

PT-BR:
Esta classe processa e estrutura diferentes tipos de mensagens do WhatsApp (texto, áudio,
imagem e documentos), extraindo e organizando seus metadados e conteúdo.

EN:
This class processes and structures different types of WhatsApp messages (text, audio,
image, and documents), extracting and organizing their metadata and content.
"""

class MessageSandeco:
    # Message Types / Tipos de Mensagem
    TYPE_TEXT = "conversation"
    TYPE_AUDIO = "audioMessage"
    TYPE_IMAGE = "imageMessage"
    TYPE_DOCUMENT = "documentMessage"
    
    # Message Scopes / Escopos de Mensagem
    SCOPE_GROUP = "group"
    SCOPE_PRIVATE = "private"
    
    def __init__(self, raw_data):
        """
        PT-BR:
        Inicializa uma mensagem a partir dos dados brutos.
        
        Parâmetros:
            raw_data: Dados brutos da mensagem do WhatsApp

        EN:
        Initializes a message from raw data.
        
        Parameters:
            raw_data: Raw WhatsApp message data
        """
        if "data" not in raw_data:
            enveloped_data = {
                "event": None,
                "instance": None,
                "destination": None,
                "date_time": None,
                "server_url": None,
                "apikey": None,
                "data": raw_data
            }
        else:
            enveloped_data = raw_data
        
        self.data = enveloped_data
        self.extract_common_data()
        self.extract_specific_data()
    
    def extract_common_data(self):
        """
        PT-BR:
        Extrai metadados comuns da mensagem (remetente, timestamp, IDs, etc).
        Define os atributos básicos compartilhados por todos os tipos de mensagem.

        EN:
        Extracts common message metadata (sender, timestamp, IDs, etc).
        Sets basic attributes shared by all message types.
        """
        self.event = self.data.get("event")
        self.instance = self.data.get("instance")
        self.destination = self.data.get("destination")
        self.date_time = self.data.get("date_time")
        self.server_url = self.data.get("server_url")
        self.apikey = self.data.get("apikey")
        
        data = self.data.get("data", {})
        key = data.get("key", {})
        
        self.remote_jid = key.get("remoteJid")
        self.message_id = key.get("id")
        self.from_me = key.get("fromMe")
        self.push_name = data.get("pushName")
        self.status = data.get("status")
        self.instance_id = data.get("instanceId")
        self.source = data.get("source")
        self.message_timestamp = data.get("messageTimestamp")
        self.message_type = data.get("messageType")
        self.sender = data.get("sender")
        self.participant = key.get("participant")
        
        self.determine_scope()
    
    def determine_scope(self):
        """
        PT-BR:
        Determina se a mensagem é de grupo ou privada.
        Extrai ID do grupo e número de telefone com base no escopo.

        EN:
        Determines if the message is from a group or private chat.
        Extracts group ID and phone number based on scope.
        """
        if self.remote_jid.endswith("@g.us"):
            self.scope = self.SCOPE_GROUP
            self.group_id = self.remote_jid.split("@")[0]
            self.phone = self.participant.split("@")[0] if self.participant else None
        elif self.remote_jid.endswith("@s.whatsapp.net"):
            self.scope = self.SCOPE_PRIVATE
            self.phone = self.remote_jid.split("@")[0]
            self.group_id = None
        else:
            self.scope = "unknown"
            self.phone = None
            self.group_id = None
    
    def extract_specific_data(self):
        """
        PT-BR:
        Extrai dados específicos baseado no tipo da mensagem.
        Chama o método apropriado para processar texto, áudio, imagem ou documento.

        EN:
        Extracts specific data based on message type.
        Calls appropriate method to process text, audio, image, or document.
        """
        if self.message_type == self.TYPE_TEXT:
            self.extract_text_message()
        elif self.message_type == self.TYPE_AUDIO:
            self.extract_audio_message()
        elif self.message_type == self.TYPE_IMAGE:
            self.extract_image_message()
        elif self.message_type == self.TYPE_DOCUMENT:
            self.extract_document_message()
    
    def extract_text_message(self):
        """
        PT-BR:
        Extrai o conteúdo de uma mensagem de texto.
        Define o atributo text_message com o conteúdo da conversa.

        EN:
        Extracts text message content.
        Sets text_message attribute with conversation content.
        """
        self.text_message = self.data["data"]["message"].get("conversation")
    
    def extract_audio_message(self):
        """
        PT-BR:
        Extrai metadados de mensagens de áudio.
        Inclui URL, tipo MIME, duração, chaves de mídia e outros detalhes.

        EN:
        Extracts audio message metadata.
        Includes URL, MIME type, duration, media keys, and other details.
        """
        audio_data = self.data["data"]["message"]["audioMessage"]
        self.audio_base64_bytes = self.data["data"]["message"].get("base64")
        self.audio_url = audio_data.get("url")
        self.audio_mimetype = audio_data.get("mimetype")
        self.audio_file_sha256 = audio_data.get("fileSha256")
        self.audio_file_length = audio_data.get("fileLength")
        self.audio_duration_seconds = audio_data.get("seconds")
        self.audio_media_key = audio_data.get("mediaKey")
        self.audio_ptt = audio_data.get("ptt")
        self.audio_file_enc_sha256 = audio_data.get("fileEncSha256")
        self.audio_direct_path = audio_data.get("directPath")
        self.audio_waveform = audio_data.get("waveform")
        self.audio_view_once = audio_data.get("viewOnce", False)
    
    def extract_image_message(self):
        """
        PT-BR:
        Extrai metadados de mensagens com imagem.
        Inclui URL, dimensões, legenda, miniaturas e outros detalhes.

        EN:
        Extracts image message metadata.
        Includes URL, dimensions, caption, thumbnails, and other details.
        """
        image_data = self.data["data"]["message"]["imageMessage"]
        self.image_url = image_data.get("url")
        self.image_mimetype = image_data.get("mimetype")
        self.image_caption = image_data.get("caption")
        self.image_file_sha256 = image_data.get("fileSha256")
        self.image_file_length = image_data.get("fileLength")
        self.image_height = image_data.get("height")
        self.image_width = image_data.get("width")
        self.image_media_key = image_data.get("mediaKey")
        self.image_file_enc_sha256 = image_data.get("fileEncSha256")
        self.image_direct_path = image_data.get("directPath")
        self.image_media_key_timestamp = image_data.get("mediaKeyTimestamp")
        self.image_thumbnail_base64 = image_data.get("jpegThumbnail")
        self.image_scans_sidecar = image_data.get("scansSidecar")
        self.image_scan_lengths = image_data.get("scanLengths")
        self.image_mid_quality_file_sha256 = image_data.get("midQualityFileSha256")
        self.image_base64 = self.data["data"]["message"].get("base64")
    
    def extract_document_message(self):
        """
        PT-BR:
        Extrai metadados de mensagens com documentos.
        Inclui URL, nome do arquivo, tipo MIME, legenda e outros detalhes.

        EN:
        Extracts document message metadata.
        Includes URL, filename, MIME type, caption, and other details.
        """
        document_data = self.data["data"]["message"]["documentMessage"]
        self.document_url = document_data.get("url")
        self.document_mimetype = document_data.get("mimetype")
        self.document_title = document_data.get("title")
        self.document_file_sha256 = document_data.get("fileSha256")
        self.document_file_length = document_data.get("fileLength")
        self.document_media_key = document_data.get("mediaKey")
        self.document_file_name = document_data.get("fileName")
        self.document_file_enc_sha256 = document_data.get("fileEncSha256")
        self.document_direct_path = document_data.get("directPath")
        self.document_caption = document_data.get("caption", None)
        self.document_base64_bytes = self.decode_base64(self.data["data"]["message"].get("base64"))
    
    def decode_base64(self, base64_string):
        """
        PT-BR:
        Decodifica uma string base64 para bytes.
        
        Parâmetros:
            base64_string: String codificada em base64
            
        Retorna:
            bytes/None: Dados decodificados ou None se a string for inválida

        EN:
        Decodes a base64 string to bytes.
        
        Parameters:
            base64_string: Base64 encoded string
            
        Returns:
            bytes/None: Decoded data or None if string is invalid
        """
        if base64_string:
            return base64.b64decode(base64_string)
        return None
    
    def get(self):
        """
        PT-BR:
        Retorna todos os atributos da mensagem.
        
        Retorna:
            dict: Dicionário com todos os atributos da mensagem

        EN:
        Returns all message attributes.
        
        Returns:
            dict: Dictionary with all message attributes
        """
        return self.__dict__
    
    def get_text(self):
        """
        PT-BR:
        Obtém o texto principal da mensagem.
        Para imagens e documentos, retorna a legenda.
        
        Retorna:
            str: Texto da mensagem ou legenda

        EN:
        Gets the main text content of the message.
        For images and documents, returns the caption.
        
        Returns:
            str: Message text or caption
        """
        text = ""
        if self.message_type == self.TYPE_TEXT:
            text = self.text_message
        elif self.message_type == self.TYPE_IMAGE:
            text = self.image_caption
        elif self.message_type == self.TYPE_DOCUMENT:
            text = self.document_caption
        return text
    
    def get_name(self):
        """
        PT-BR:
        Obtém o nome do remetente da mensagem.
        
        Retorna:
            str: Nome do remetente

        EN:
        Gets the sender's name of the message.
        
        Returns:
            str: Sender's name
        """
        return self.push_name
    
    @staticmethod
    def get_messages(messages):
        """
        PT-BR:
        Converte um dicionário de mensagens em objetos MessageSandeco.
        
        Parâmetros:
            messages: Dicionário com registros de mensagens
            
        Retorna:
            List[MessageSandeco]: Lista de objetos de mensagem processados

        EN:
        Converts a dictionary of messages into MessageSandeco objects.
        
        Parameters:
            messages: Dictionary with message records
            
        Returns:
            List[MessageSandeco]: List of processed message objects
        """
        msgs = messages['messages']['records']
        mensagens = [MessageSandeco(msg) for msg in msgs]
        return mensagens