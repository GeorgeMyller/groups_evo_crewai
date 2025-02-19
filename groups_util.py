"""
Utilitários para Gerenciamento de Grupos / Group Management Utilities

PT-BR:
Esta classe fornece ferramentas para manipulação de imagens de grupos,
formatação de datas, e apresentação de informações na interface do usuário.

EN:
This class provides tools for handling group images, date formatting,
and presenting information in the user interface.
"""

import pandas as pd
import base64
import requests
import streamlit as st
from PIL import Image
from io import BytesIO
from datetime import datetime

class GroupUtils:
    def resized_image_to_base64(self, image):
        """
        PT-BR:
        Converte uma imagem redimensionada para string base64.
        
        Parâmetros:
            image: Imagem PIL para converter
            
        Retorna:
            str: String base64 da imagem

        EN:
        Converts a resized image to base64 string.
        
        Parameters:
            image: PIL Image to convert
            
        Returns:
            str: Base64 string of the image
        """
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def format_date(self, timestamp):
        """
        PT-BR:
        Formata um timestamp Unix para data legível.
        
        Parâmetros:
            timestamp: Timestamp Unix
            
        Retorna:
            str: Data formatada (DD-MM-YYYY HH:MM)

        EN:
        Formats a Unix timestamp to readable date.
        
        Parameters:
            timestamp: Unix timestamp
            
        Returns:
            str: Formatted date (DD-MM-YYYY HH:MM)
        """
        try:
            dt = datetime.fromtimestamp(int(timestamp))
            return dt.strftime("%d-%m-%Y %H:%M")
        except (ValueError, TypeError):
            return "Data inválida / Invalid date"

    def get_image(self, url, size=(30, 30)):
        """
        PT-BR:
        Obtém e redimensiona uma imagem de uma URL.
        
        Parâmetros:
            url: URL da imagem
            size: Tuple com dimensões desejadas (largura, altura)
            
        Retorna:
            Image: Imagem PIL processada

        EN:
        Gets and resizes an image from URL.
        
        Parameters:
            url: Image URL
            size: Tuple with desired dimensions (width, height)
            
        Returns:
            Image: Processed PIL Image
        """
        try:
            if not url:
                raise ValueError("URL vazio / Empty URL")
            response = requests.get(url, stream=True, timeout=5)
            image = Image.open(response.raw).convert("RGBA").resize(size)
            return image
        except Exception:
            return Image.new("RGBA", size, (200, 200, 200))

    def map(self, groups):
        """
        PT-BR:
        Cria mapeamentos de grupos para uso na interface.
        
        Parâmetros:
            groups: Lista de objetos Group
            
        Retorna:
            tuple: (dicionário de grupos, lista de opções)

        EN:
        Creates group mappings for interface use.
        
        Parameters:
            groups: List of Group objects
            
        Returns:
            tuple: (groups dictionary, options list)
        """
        self.group_map = {group.group_id: group for group in groups}
        self.options = [(group.name, group.group_id) for group in groups]
        return self.group_map, self.options

    def head_group(self, title, url_image):
        """
        PT-BR:
        Gera HTML para cabeçalho do grupo com imagem.
        
        Parâmetros:
            title: Título do grupo
            url_image: URL da imagem do grupo
            
        Retorna:
            str: HTML formatado com imagem e título

        EN:
        Generates HTML for group header with image.
        
        Parameters:
            title: Group title
            url_image: Group image URL
            
        Returns:
            str: Formatted HTML with image and title
        """
        resized_image = self.get_image(url_image)
        image_title = f"""
        <div style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{self.resized_image_to_base64(resized_image)}" 
             alt="Grupo / Group" 
             style="width:30px; height:30px; border-radius: 50%; margin-right: 10px;">
            <h3 style="margin: 0;">{title}</h3>
        </div>
        """
        return image_title

    def status_icon(self, value):
        """
        PT-BR:
        Retorna ícone apropriado para status booleano.
        
        Parâmetros:
            value: Valor booleano
            
        Retorna:
            str: Emoji ✅ para True, ❌ para False

        EN:
        Returns appropriate icon for boolean status.
        
        Parameters:
            value: Boolean value
            
        Returns:
            str: Emoji ✅ for True, ❌ for False
        """
        return "✅" if value else "❌"

    def group_details(self, selected_group):
        """
        PT-BR:
        Exibe informações detalhadas do grupo na interface Streamlit.
        
        Parâmetros:
            selected_group: Objeto Group com informações do grupo

        EN:
        Displays detailed group information in Streamlit interface.
        
        Parameters:
            selected_group: Group object with group information
        """
        with st.expander("Informações Gerais / General Information", expanded=False):
            st.write("**Criador / Creator:**", selected_group.owner)
            st.write("**Tamanho do Grupo / Group Size:**", selected_group.size)
            st.write("**Data de Criação / Creation Date:**", self.format_date(selected_group.creation))
            st.write(f"**Grupo Restrito / Restricted Group:** {self.status_icon(selected_group.restrict)}")
            st.write(f"**Modo Apenas Administradores / Admin-Only Mode:** {self.status_icon(selected_group.announce)}")
            st.write(f"**É Comunidade / Is Community:** {self.status_icon(selected_group.is_community)}")
            st.write(f"**É Comunidade de Anúncios / Is Announcement Community:** {self.status_icon(selected_group.is_community_announce)}")