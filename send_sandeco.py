import os
import time
from dotenv import load_dotenv
from evolutionapi.client import EvolutionClient
from evolutionapi.models.message import TextMessage, MediaMessage

class SendSandeco:
    
    def __init__(self) -> None:
        load_dotenv()
        self.evo_api_token = os.getenv("EVO_API_TOKEN")
        self.evo_instance_id = os.getenv("EVO_INSTANCE_NAME")
        self.evo_instance_token = os.getenv("EVO_INSTANCE_TOKEN")
        self.evo_base_url = os.getenv("EVO_BASE_URL")

        self.client = EvolutionClient(
            base_url=self.evo_base_url,
            api_token=self.evo_api_token
        )

    def textMessage(self, number, msg, mentions=[]):
        """Envia uma mensagem de texto para o número especificado."""
        text_message = TextMessage(
            number=str(number),
            text=msg,
            mentioned=mentions
        )

        time.sleep(10)

        response = self.client.messages.send_text(
            self.evo_instance_id,
            text_message,
            self.evo_instance_token
        )
        return response

    def PDF(self, number, pdf_file, caption=""):
        """Envia um arquivo PDF para o número especificado com uma legenda opcional."""
        if not os.path.exists(pdf_file):
            raise FileNotFoundError(f"Arquivo '{pdf_file}' não encontrado.")
        
        media_message = MediaMessage(
            number=number,
            mediatype="document",
            mimetype="application/pdf",
            caption=caption,
            fileName=os.path.basename(pdf_file),
            media=""
        )
        
        self.client.messages.send_media(
            self.evo_instance_id,
            media_message,
            self.evo_instance_token,
            pdf_file
        )

    def audio(self, number, audio_file):
        """Envia um arquivo de áudio para o número especificado."""
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Arquivo '{audio_file}' não encontrado.")

        audio_message = {
            "number": number,
            "mediatype": "audio",
            "mimetype": "audio/mpeg",
            "caption": ""
        }
            
        self.client.messages.send_whatsapp_audio(
            self.evo_instance_id,
            audio_message,
            self.evo_instance_token,
            audio_file
        )
                    
        return "Áudio enviado"

    def image(self, number, image_file, caption=""):
        """Envia uma imagem para o número especificado com uma legenda opcional."""
        if not os.path.exists(image_file):
            raise FileNotFoundError(f"Arquivo '{image_file}' não encontrado.")

        media_message = MediaMessage(
            number=number,
            mediatype="image",
            mimetype="image/jpeg",
            caption=caption,
            fileName=os.path.basename(image_file),
            media=""
        )

        self.client.messages.send_media(
            self.evo_instance_id,
            media_message,
            self.evo_instance_token,
            image_file
        )
        
        return "Imagem enviada"

    def video(self, number, video_file, caption=""):
        """Envia um vídeo para o número especificado com uma legenda opcional."""
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Arquivo '{video_file}' não encontrado.")

        media_message = MediaMessage(
            number=number,
            mediatype="video",
            mimetype="video/mp4",
            caption=caption,
            fileName=os.path.basename(video_file),
            media=""
        )

        self.client.messages.send_media(
            self.evo_instance_id,
            media_message,
            self.evo_instance_token,
            video_file
        )
        
        return "Vídeo enviado"

    def document(self, number, document_file, caption=""):
        """Envia um documento para o número especificado com uma legenda opcional."""
        if not os.path.exists(document_file):
            raise FileNotFoundError(f"Arquivo '{document_file}' não encontrado.")

        media_message = MediaMessage(
            number=number,
            mediatype="document",
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            caption=caption,
            fileName=os.path.basename(document_file),
            media=""
        )

        self.client.messages.send_media(
            self.evo_instance_id,
            media_message,
            self.evo_instance_token,
            document_file
        )
        
        return "Documento enviado"

# Instancia um objeto SendSandeco para utilização dos métodos de envio de mensagens
sender = SendSandeco()

# Define o número de telefone/grupo para o envio (identificado pelo formato com @g.us)
celular = "120363391798069472@g.us"

# Envia uma mensagem de texto para o número/grupo definido com o conteúdo "teste de mensagem"
sender.textMessage(number=celular, msg="teste de mensagem")