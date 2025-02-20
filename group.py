"""
Classe de Modelo para Grupos de WhatsApp / WhatsApp Group Model Class

PT-BR:
Esta classe representa um grupo do WhatsApp com suas propriedades e configurações
para geração de resumos automáticos.

EN:
This class represents a WhatsApp group with its properties and settings
for automatic summary generation.
"""

class Group:
    def __init__(self,
                 group_id,
                 name,
                 subject_owner,
                 subject_time,
                 picture_url,
                 size,
                 creation,
                 owner,
                 restrict,
                 announce,
                 is_community,
                 is_community_announce,
                 dias=1,
                 horario="22:00",
                 enabled=False,
                 is_links=False,
                 is_names=False,
                 send_to_group=True,
                 send_to_personal=False):
        """
        PT-BR:
        Inicializa um grupo com suas propriedades e configurações de resumo.

        Parâmetros:
            group_id: ID único do grupo
            name: Nome do grupo
            subject_owner: Responsável pelo título do grupo
            subject_time: Momento da última alteração do título
            picture_url: URL da imagem do grupo
            size: Número de participantes
            creation: Data de criação
            owner: Administrador principal
            restrict: Indica se possui restrições
            announce: Modo somente administrador
            is_community: Se é uma comunidade
            is_community_announce: Se é grupo de anúncios
            dias: Período do resumo (padrão: 1)
            horario: Horário do resumo (padrão: "22:00")
            enabled: Resumo ativado (padrão: False)
            is_links: Incluir links (padrão: False)
            is_names: Incluir nomes (padrão: False)
            send_to_group: Enviar para o grupo (padrão: True)
            send_to_personal: Enviar para pessoal (padrão: False)

        EN:
        Initializes a group with its properties and summary settings.

        Parameters:
            group_id: Unique group ID
            name: Group name
            subject_owner: Group title owner
            subject_time: Last title change timestamp
            picture_url: Group image URL
            size: Number of participants
            creation: Creation date
            owner: Main administrator
            restrict: Has restrictions
            announce: Admin-only mode
            is_community: Is a community
            is_community_announce: Is announcement group
            dias: Summary period (default: 1)
            horario: Summary time (default: "22:00")
            enabled: Summary enabled (default: False)
            is_links: Include links (default: False)
            is_names: Include names (default: False)
            send_to_group: Send to group (default: True)
            send_to_personal: Send to personal (default: False)
        """
        self.group_id = group_id
        self.name = name
        self.subject_owner = subject_owner
        self.subject_time = subject_time
        self.picture_url = picture_url
        self.size = size
        self.creation = creation
        self.owner = owner
        self.restrict = restrict
        self.announce = announce
        self.is_community = is_community
        self.is_community_announce = is_community_announce
        # Summary settings / Configurações de resumo
        self.dias = dias
        self.horario = horario
        self.enabled = enabled
        self.is_links = is_links
        self.is_names = is_names
        self.send_to_group = send_to_group
        self.send_to_personal = send_to_personal

    def __repr__(self):
        """
        PT-BR:
        Retorna uma representação textual do grupo.
        
        EN:
        Returns a string representation of the group.
        """
        return (
            f"Group(id={self.group_id}, subject={self.name}, owner={self.owner}, size={self.size})"
        )