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
import logging
from dotenv import load_dotenv
from evolutionapi.client import EvolutionClient
from evolutionapi.models.message import TextMessage, MediaMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

        if not all([self.evo_api_token, self.evo_instance_id, self.evo_instance_token, self.evo_base_url]):
            raise EnvironmentError("Missing one or more required environment variables.")

        self.client = EvolutionClient(
            base_url=self.evo_base_url,
            api_token=self.evo_api_token
        )

    def _send_media(self, number, media_file, mediatype, mimetype, caption):
        if not os.path.exists(media_file):
            raise FileNotFoundError(f"Arquivo '{media_file}' não encontrado.")

        media_message = MediaMessage(
            number=number,
            mediatype=mediatype,
            mimetype=mimetype,
            caption=caption,
            fileName=os.path.basename(media_file),
            media=""
        )

        self.client.messages.send_media(
            self.evo_instance_id,
            media_message,
            self.evo_instance_token,
            media_file
        )

    def textMessage(self, number, msg, mentions=[]):
        """
        PT-BR:
        Envia uma mensagem de texto para o número especificado.
        
        Argumentos:
            number (str): Número do destinatário (formato: código do país + DDD + número, ex: 5511999999999)
            msg (str): Conteúdo da mensagem
            mentions (list): Lista de menções na mensagem
            
        Retorna:
            dict: Resposta da API
        """
        try:
            formatted_number = str(number)
            
            # Se não for um grupo e não tiver o sufixo whatsapp
            if not formatted_number.endswith('@g.us') and not formatted_number.endswith('@s.whatsapp'):
                # Remove quaisquer caracteres especiais
                formatted_number = ''.join(filter(str.isdigit, formatted_number))
                
                # Garante que começa com o código do país
                if not formatted_number.startswith('351'):
                    formatted_number = '351' + formatted_number
                
                # Adiciona o sufixo whatsapp
                formatted_number = f"{formatted_number}@s.whatsapp"
            
            logging.info(f"Número original: {number}")
            logging.info(f"Número formatado: {formatted_number}")
            logging.info(f"Mensagem: {msg[:100]}...")
            logging.info(f"Instance ID: {self.evo_instance_id}")
            logging.info(f"Base URL: {self.evo_base_url}")
            
            text_message = TextMessage(
                number=formatted_number,
                text=msg,
                mentioned=mentions
            )

            # Pequeno delay antes do envio
            time.sleep(3)
            
            logging.info("Enviando mensagem...")
            try:
                response = self.client.messages.send_text(
                    self.evo_instance_id,
                    text_message,
                    self.evo_instance_token
                )
                logging.info(f"Resposta da API: {response}")
                logging.info("Mensagem enviada com sucesso!")
                return response
            except Exception as api_error:
                logging.error(f"Erro na API Evolution: {str(api_error)}")
                logging.error(f"Detalhes da requisição: Instance ID: {self.evo_instance_id}, Token: {'*' * len(self.evo_instance_token)}")
                raise api_error
            
        except Exception as e:
            logging.error(f"Erro ao enviar mensagem: Número: {formatted_number}, Erro: {str(e)}")
            raise Exception(f"Erro ao enviar mensagem: {str(e)}")

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
        self._send_media(number, pdf_file, "document", "application/pdf", caption)

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
        self._send_media(number, audio_file, "audio", "audio/mpeg", "")

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
        self._send_media(number, image_file, "image", "image/jpeg", caption)

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
        self._send_media(number, video_file, "video", "video/mp4", caption)

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
        self._send_media(number, document_file, "document", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", caption)

number = os.getenv('WHATSAPP_NUMBER')  # Get number from .env

if not number:
    raise EnvironmentError("Missing required environment variable: NUMBER")

sender = SendSandeco()

celular = number

sender.textMessage(number=celular,
                  msg="teste de mensagem")
logging.info("teste de mensagem")