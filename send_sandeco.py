import os                                     # Importa o módulo os para interagir com o sistema operacional e arquivos
import time                                   # Importa o módulo time para manipular delays e tempos de espera
from dotenv import load_dotenv                # Importa a função load_dotenv para carregar variáveis de ambiente a partir de um arquivo .env
from evolutionapi.client import EvolutionClient  # Importa a classe EvolutionClient para interagir com a API Evolution
from evolutionapi.models.message import TextMessage, MediaMessage  # Importa as classes TextMessage e MediaMessage para modelar mensagens

class SendSandeco:
    
    def __init__(self) -> None:
        # Carrega as variáveis de ambiente do arquivo .env
        load_dotenv()                          # Executa o carregamento das variáveis de ambiente definidas no arquivo .env
        self.evo_api_token = os.getenv("EVO_API_TOKEN")  # Obtém o token da API Evolution a partir das variáveis de ambiente
        self.evo_instance_id = os.getenv("EVO_INSTANCE_NAME")  # Obtém o ID da instância da API Evolution
        self.evo_instance_token = os.getenv("EVO_INSTANCE_TOKEN")  # Obtém o token da instância da API Evolution
        self.evo_base_url = os.getenv("EVO_BASE_URL")  # Obtém a URL base da API Evolution

        # Inicializa o cliente Evolution com a URL base e token da API
        self.client = EvolutionClient(
            base_url=self.evo_base_url,         # Define a URL base para as requisições
            api_token=self.evo_api_token          # Define o token da API para autenticação
        )

    def textMessage(self, number, msg, mentions=[]):
        # Envia uma mensagem de texto para o número especificado

        # Cria um objeto de mensagem de texto com os parâmetros fornecidos
        text_message = TextMessage(
            number=str(number),                # Converte o número para string e o atribui ao campo de destino
            text=msg,                          # Define o texto da mensagem
            mentioned=mentions                 # Define os contatos mencionados na mensagem (opcional)
        )

        time.sleep(10)                          # Aguarda 10 segundos antes de enviar a mensagem

        # Envia a mensagem de texto utilizando o cliente Evolution
        response = self.client.messages.send_text(
            self.evo_instance_id,              # Passa o ID da instância
            text_message,                      # Passa o objeto da mensagem de texto
            self.evo_instance_token           # Passa o token da instância para autenticação
        )
        return response                         # Retorna a resposta da API Evolution após o envio da mensagem

    def PDF(self, number, pdf_file, caption=""):
        # Envia um arquivo PDF para o número especificado com uma legenda opcional

        # Verifica se o arquivo PDF existe no caminho informado
        if not os.path.exists(pdf_file):
            raise FileNotFoundError(f"Arquivo '{pdf_file}' não encontrado.")  # Lança um erro se o arquivo não for encontrado
        
        # Cria um objeto MediaMessage configurado para enviar documentos PDF
        media_message = MediaMessage(
            number=number,                                  # Define o número de destino
            mediatype="document",                           # Define o tipo de mídia como documento
            mimetype="application/pdf",                     # Define o tipo MIME específico para PDF
            caption=caption,                                # Define a legenda para o documento (se fornecida)
            fileName=os.path.basename(pdf_file),            # Extrai o nome do arquivo a partir do caminho completo
            media=""                                        # Campo de mídia vazio (será preenchido na requisição)
        )
        
        # Envia a mídia (PDF) utilizando o método send_media do cliente Evolution
        self.client.messages.send_media(
            self.evo_instance_id,              # Passa o ID da instância
            media_message,                     # Passa o objeto de mensagem de mídia
            self.evo_instance_token,           # Passa o token da instância para autenticação
            pdf_file                           # Passa o caminho do arquivo PDF a ser enviado
        )

    def audio(self, number, audio_file):
        # Envia um arquivo de áudio para o número especificado

        # Verifica se o arquivo de áudio existe no caminho informado
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Arquivo '{audio_file}' não encontrado.")  # Lança um erro caso o arquivo não exista

        # Cria um dicionário representando a mensagem de áudio com os parâmetros necessários
        audio_message = {
            "number": number,                          # Define o número do destinatário
            "mediatype": "audio",                        # Define o tipo de mídia como áudio
            "mimetype": "audio/mpeg",                    # Define o tipo MIME para arquivos de áudio MPEG
            "caption": ""                                # Define uma legenda vazia (pode ser alterada se necessário)
        }
            
        # Envia a mensagem de áudio utilizando o método send_whatsapp_audio
        self.client.messages.send_whatsapp_audio(
            self.evo_instance_id,              # Passa o ID da instância
            audio_message,                     # Passa o objeto de mensagem de áudio (dicionário)
            self.evo_instance_token,           # Passa o token da instância para autenticação
            audio_file                         # Passa o caminho do arquivo de áudio a ser enviado
        )
                    
        return "Áudio enviado"                     # Retorna uma mensagem de confirmação após o envio do áudio

    def image(self, number, image_file, caption=""):
        # Envia uma imagem para o número especificado com uma legenda opcional

        # Verifica se o arquivo de imagem existe
        if not os.path.exists(image_file):
            raise FileNotFoundError(f"Arquivo '{image_file}' não encontrado.")  # Lança um erro caso o arquivo não seja encontrado

        # Cria um objeto MediaMessage configurado para enviar imagens
        media_message = MediaMessage(
            number=number,                                  # Define o número do destinatário
            mediatype="image",                              # Define o tipo de mídia como imagem
            mimetype="image/jpeg",                          # Define o tipo MIME para imagens JPEG
            caption=caption,                                # Define a legenda da imagem
            fileName=os.path.basename(image_file),          # Extrai o nome do arquivo a partir do caminho fornecido
            media=""                                        # Campo de mídia vazio (será preenchido na requisição)
        )

        # Envia a imagem utilizando o método send_media do cliente Evolution
        self.client.messages.send_media(
            self.evo_instance_id,              # Passa o ID da instância
            media_message,                     # Passa o objeto de mensagem de mídia (imagem)
            self.evo_instance_token,           # Passa o token da instância para autenticação
            image_file                         # Passa o caminho do arquivo de imagem a ser enviado
        )
        
        return "Imagem enviada"                     # Retorna uma mensagem de confirmação após o envio da imagem

    def video(self, number, video_file, caption=""):
        # Envia um vídeo para o número especificado com uma legenda opcional

        # Verifica se o arquivo de vídeo existe no caminho informado
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Arquivo '{video_file}' não encontrado.")  # Lança um erro caso o arquivo não seja encontrado

        # Cria um objeto MediaMessage configurado para envio de vídeo
        media_message = MediaMessage(
            number=number,                                  # Define o número do destinatário
            mediatype="video",                              # Define o tipo de mídia como vídeo
            mimetype="video/mp4",                           # Define o tipo MIME para vídeos MP4
            caption=caption,                                # Define a legenda do vídeo (opcional)
            fileName=os.path.basename(video_file),          # Extrai o nome do arquivo a partir do caminho completo
            media=""                                        # Campo de mídia vazio (será definido na requisição)
        )

        # Envia o vídeo utilizando o método send_media do cliente Evolution
        self.client.messages.send_media(
            self.evo_instance_id,              # Passa o ID da instância
            media_message,                     # Passa o objeto de mensagem de mídia (vídeo)
            self.evo_instance_token,           # Passa o token da instância para autenticação
            video_file                         # Passa o caminho do arquivo de vídeo a ser enviado
        )
        
        return "Vídeo enviado"                      # Retorna uma mensagem de confirmação após o envio do vídeo

    def document(self, number, document_file, caption=""):
        # Envia um documento para o número especificado com uma legenda opcional

        # Verifica se o arquivo do documento existe no caminho informado
        if not os.path.exists(document_file):
            raise FileNotFoundError(f"Arquivo '{document_file}' não encontrado.")  # Lança um erro caso o arquivo não seja encontrado

        # Cria um objeto MediaMessage configurado para envio de documentos
        media_message = MediaMessage(
            number=number,                                  # Define o número do destinatário
            mediatype="document",                           # Define o tipo de mídia como documento
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # Define o MIME para documentos Word
            caption=caption,                                # Define a legenda para o documento (opcional)
            fileName=os.path.basename(document_file),       # Extrai o nome do arquivo a partir do caminho completo
            media=""                                        # Campo de mídia vazio (será preenchido na requisição)
        )

        # Envia o documento utilizando o método send_media do cliente Evolution
        self.client.messages.send_media(
            self.evo_instance_id,              # Passa o ID da instância
            media_message,                     # Passa o objeto de mensagem de mídia (documento)
            self.evo_instance_token,           # Passa o token da instância para autenticação
            document_file                      # Passa o caminho do arquivo do documento a ser enviado
        )
        
        return "Documento enviado"                  # Retorna uma mensagem de confirmação após o envio do documento

# Instancia um objeto SendSandeco para utilização dos métodos de envio de mensagens
sender = SendSandeco()

# Define o número de telefone/grupo para o envio (identificado pelo formato com @g.us)
celular = "120363391798069472@g.us"

# Envia uma mensagem de texto para o número/grupo definido com o conteúdo "teste de mensagem"
sender.textMessage(number=celular,
                   msg="teste de mensagem")