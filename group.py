# group.py

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
                 is_names=False):
        """
        Inicializa um grupo com todas as propriedades relevantes e as configurações de resumo.

        :param group_id: ID único do grupo.
        :param name: Nome do grupo.
        :param subject_owner: Dono do assunto/título do grupo.
        :param subject_time: Timestamp da última alteração do título.
        :param picture_url: URL da imagem do grupo.
        :param size: Tamanho do grupo (número de participantes).
        :param creation: Timestamp da criação do grupo.
        :param owner: Dono do grupo.
        :param restrict: Indica se o grupo tem restrições.
        :param announce: Indica se o grupo está em modo "somente administrador".
        :param is_community: Indica se o grupo é uma comunidade.
        :param is_community_announce: Indica se é um grupo de anúncios de uma comunidade.
        :param dias: Quantidade de dias para o resumo (valor padrão: 1).
        :param horario: Horário de execução do resumo (valor padrão: "22:00").
        :param enabled: Indica se o resumo está habilitado (valor padrão: False).
        :param is_links: Indica se links estão incluídos no resumo (valor padrão: False).
        :param is_names: Indica se nomes estão incluídos no resumo (valor padrão: False).
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

        # Configurações de resumo
        self.dias = dias
        self.horario = horario
        self.enabled = enabled
        self.is_links = is_links
        self.is_names = is_names

    def __repr__(self):
        """
        Retorna uma representação legível do grupo.
        """
        return (
            f"Group(id={self.group_id}, subject={self.name}, owner={self.owner}, size={self.size})"
        )