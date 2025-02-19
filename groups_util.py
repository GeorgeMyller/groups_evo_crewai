import pandas as pd                     # Importa o módulo pandas para manipulação de dados
import base64                           # Importa o módulo base64 para codificar dados em base64
import requests                         # Importa o módulo requests para realizar requisições HTTP
import streamlit as st                  # Importa o módulo streamlit para criar interfaces web interativas
from PIL import Image                   # Importa a classe Image da biblioteca PIL para manipulação de imagens
from io import BytesIO                  # Importa BytesIO para manipulação de streams de bytes
from datetime import datetime           # Importa a classe datetime para manipulação de datas e horas

class GroupUtils:
    """
    Classe de utilitários para manipulação de imagens, datas e grupos.
    """
    
    def resized_image_to_base64(self, image):
        buffered = BytesIO()                                              # Cria um objeto BytesIO para armazenar dados de imagem em memória
        image.save(buffered, format="PNG")                                # Salva a imagem no objeto 'buffered' no formato PNG
        # Codifica os dados da imagem em base64 e decodifica para string
        return base64.b64encode(buffered.getvalue()).decode("utf-8")        

    def format_date(self, timestamp):
        try:
            dt = datetime.fromtimestamp(int(timestamp))                 # Converte o timestamp para um objeto datetime
            return dt.strftime("%d-%m-%Y %H:%M")                           # Formata a data no formato dia-mês-ano hora:minuto
        except (ValueError, TypeError):                                   # Trata erros de conversão ou tipo
            return "Data inválida"                                          # Retorna mensagem de data inválida caso ocorra erro

    def get_image(self, url, size=(30, 30)):
        try:
            if not url:                                                   # Verifica se a URL está vazia ou nula
                raise ValueError("URL vazio")                             # Lança exceção se não houver URL
            response = requests.get(url, stream=True, timeout=5)            # Realiza uma requisição GET com streaming e timeout de 5 segundos
            # Abre a imagem a partir do conteúdo da resposta, converte para RGBA e redimensiona para o tamanho especificado
            image = Image.open(response.raw).convert("RGBA").resize(size)   
            return image                                                  # Retorna a imagem processada
        except Exception:                                                 # Se ocorrer erro durante a requisição ou processamento
            # Retorna uma nova imagem RGBA com fundo cinza (RGB: 200,200,200) como padrão
            return Image.new("RGBA", size, (200, 200, 200))                 

    def map(self, groups):
        # Cria um dicionário mapeando o id do grupo para o próprio objeto group para acesso rápido
        self.group_map = {group.group_id: group for group in groups}      
        # Cria uma lista de tuplas com o nome e o id do grupo para exibição em seletores
        self.options = [(group.name, group.group_id) for group in groups]  
        return self.group_map, self.options                              # Retorna o dicionário e a lista de opções

    def head_group(self, title, url_image):
        resized_image = self.get_image(url_image)                        # Obtém e redimensiona a imagem a partir da URL fornecida
        
        # Monta o HTML para exibir uma imagem circular junto com o título do grupo
        image_title = f"""
        <div style="display: flex; align-items: center;">
            <img src="data:image/png;base64,{self.resized_image_to_base64(resized_image)}" 
             alt="Grupo" 
             style="width:30px; height:30px; border-radius: 50%; margin-right: 10px;">
            <h3 style="margin: 0;">{title}</h3>
        </div>
        """
        return image_title                                               # Retorna o HTML construído

    # Função para retornar apenas os ícones adequados ao valor booleano
    def status_icon(self, value):
        return "✅" if value else "❌"                                    # Retorna "✅" se value for True; caso contrário, "❌"

    def group_details(self, selected_group):
        # Cria uma área expansível na interface para exibir informações gerais do grupo
        with st.expander("Informações Gerais", expanded=False):
            st.write("**Criador:**", selected_group.owner)              # Exibe o criador do grupo
            st.write("**Tamanho do Grupo:**", selected_group.size)        # Exibe o tamanho (número de participantes) do grupo
            # Exibe a data de criação formatada usando a função format_date
            st.write("**Data de Criação:**", self.format_date(selected_group.creation))
            # Exibe se o grupo é restrito, utilizando o ícone retornado pela função status_icon
            st.write(f"**Grupo Restrito:** {self.status_icon(selected_group.restrict)}")
            # Exibe se o grupo está em modo 'somente administradores'
            st.write(f"**Modo Apenas Administradores:** {self.status_icon(selected_group.announce)}")
            # Exibe se o grupo é uma comunidade
            st.write(f"**É Comunidade:** {self.status_icon(selected_group.is_community)}")
            # Exibe se o grupo é de anúncios de comunidade
            st.write(f"**É Comunidade de Anúncios:** {self.status_icon(selected_group.is_community_announce)}")