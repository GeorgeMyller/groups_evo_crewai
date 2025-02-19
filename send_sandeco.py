"""
Sistema de Envio de Mensagens WhatsApp / WhatsApp Message Sending System

PT-BR:
Este módulo implementa uma interface para envio de diferentes tipos de mensagens via WhatsApp
utilizando a API Evolution. Suporta envio de textos, PDFs, áudios, imagens, vídeos e documentos.
Fornece uma camada de abstração para facilitar a integração com a API.

EN:
This module implements an interface for sending different types of WhatsApp messages
using the Evolution API. Supports sending texts, PDFs, audio, images, videos and documents.
Provides an abstraction layer to facilitate API integration.
"""

import os
import time
from dotenv import load_dotenv
from evolutionapi.client import EvolutionClient
from evolutionapi.models.message import TextMessage, MediaMessage

class SendSandeco:
    """
    PT-BR:
    Classe para gerenciamento de envio de mensagens WhatsApp.
    Utiliza credenciais do arquivo .env para autenticação com a API Evolution.
    
    EN:
    WhatsApp message sending management class.
    Uses credentials from .env file for Evolution API authentication.
    """
    
    def __init__(self) -> None:
        # Environment setup and client initialization / Configuração do ambiente e inicialização do cliente
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
        """
        PT-BR:
        Envia uma mensagem de texto para o número especificado.
        
        Argumentos:
            number (str): Número/ID do destinatário
            msg (str): Conteúdo da mensagem
            mentions (list): Lista de menções na mensagem
            
        Retorna:
            dict: Resposta da API
            
        EN:
        Sends a text message to the specified number.
        
        Args:
            number (str): Recipient number/ID
            msg (str): Message content
            mentions (list): List of mentions in the message
            
        Returns:
            dict: API response
        """
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
        """
        PT-BR:
        Envia um arquivo PDF para o número especificado.
        
        Argumentos:
            number (str): Número/ID do destinatário
            pdf_file (str): Caminho do arquivo PDF
            caption (str): Legenda opcional para o arquivo
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            
        EN:
        Sends a PDF file to the specified number.
        
        Args:
            number (str): Recipient number/ID
            pdf_file (str): PDF file path
            caption (str): Optional file caption
            
        Raises:
            FileNotFoundError: If file is not found
        """
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
        """
        PT-BR:
        Envia um arquivo de áudio para o número especificado.
        
        Argumentos:
            number (str): Número/ID do destinatário
            audio_file (str): Caminho do arquivo de áudio
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            
        Retorna:
            str: Mensagem de confirmação
            
        EN:
        Sends an audio file to the specified number.
        
        Args:
            number (str): Recipient number/ID
            audio_file (str): Audio file path
            
        Raises:
            FileNotFoundError: If file is not found
            
        Returns:
            str: Confirmation message
        """
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
        """
        PT-BR:
        Envia uma imagem para o número especificado.
        
        Argumentos:
            number (str): Número/ID do destinatário
            image_file (str): Caminho do arquivo de imagem
            caption (str): Legenda opcional para a imagem
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            
        Retorna:
            str: Mensagem de confirmação
            
        EN:
        Sends an image to the specified number.
        
        Args:
            number (str): Recipient number/ID
            image_file (str): Image file path
            caption (str): Optional image caption
            
        Raises:
            FileNotFoundError: If file is not found
            
        Returns:
            str: Confirmation message
        """
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
        """
        PT-BR:
        Envia um vídeo para o número especificado.
        
        Argumentos:
            number (str): Número/ID do destinatário
            video_file (str): Caminho do arquivo de vídeo
            caption (str): Legenda opcional para o vídeo
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            
        Retorna:
            str: Mensagem de confirmação
            
        EN:
        Sends a video to the specified number.
        
        Args:
            number (str): Recipient number/ID
            video_file (str): Video file path
            caption (str): Optional video caption
            
        Raises:
            FileNotFoundError: If file is not found
            
        Returns:
            str: Confirmation message
        """
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
        """
        PT-BR:
        Envia um documento para o número especificado.
        
        Argumentos:
            number (str): Número/ID do destinatário
            document_file (str): Caminho do arquivo do documento
            caption (str): Legenda opcional para o documento
            
        Raises:
            FileNotFoundError: Se o arquivo não for encontrado
            
        Retorna:
            str: Mensagem de confirmação
            
        EN:
        Sends a document to the specified number.
        
        Args:
            number (str): Recipient number/ID
            document_file (str): Document file path
            caption (str): Optional document caption
            
        Raises:
            FileNotFoundError: If file is not found
            
        Returns:
            str: Confirmation message
        """
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

# Example usage / Exemplo de uso
sender = SendSandeco()
celular = "120363391798069472@g.us"  # Group ID example / Exemplo de ID de grupo
sender.textMessage(number=celular, msg="teste de mensagem")