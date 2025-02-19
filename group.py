# group.py

class Group:  # Define a classe Group que representa um grupo com suas propriedades e configurações
    def __init__(self,  # Método construtor que inicializa um novo objeto Group com os parâmetros fornecidos
                 group_id,  # Parâmetro: ID único do grupo
                 name,  # Parâmetro: Nome do grupo
                 subject_owner,  # Parâmetro: Dono do assunto/título do grupo
                 subject_time,  # Parâmetro: Timestamp da última alteração do título do grupo
                 picture_url,  # Parâmetro: URL da imagem do grupo
                 size,  # Parâmetro: Número de participantes do grupo
                 creation,  # Parâmetro: Timestamp da criação do grupo
                 owner,  # Parâmetro: Dono do grupo
                 restrict,  # Parâmetro: Indica se o grupo possui restrições
                 announce,  # Parâmetro: Indica se o grupo está em modo "somente administrador"
                 is_community,  # Parâmetro: Indica se o grupo é uma comunidade
                 is_community_announce,  # Parâmetro: Indica se o grupo é de anúncios de comunidade
                 dias=1,  # Parâmetro opcional: Quantidade de dias para o resumo (padrão: 1)
                 horario="22:00",  # Parâmetro opcional: Horário de execução do resumo (padrão: "22:00")
                 enabled=False,  # Parâmetro opcional: Indica se o resumo está habilitado (padrão: False)
                 is_links=False,  # Parâmetro opcional: Indica se links são incluídos no resumo (padrão: False)
                 is_names=False):  # Parâmetro opcional: Indica se nomes são incluídos no resumo (padrão: False)
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
        self.group_id = group_id  # Atribui o ID único do grupo à propriedade do objeto
        self.name = name  # Atribui o nome do grupo à propriedade do objeto
        self.subject_owner = subject_owner  # Atribui o dono do assunto à propriedade do objeto
        self.subject_time = subject_time  # Atribui o timestamp da última alteração do título à propriedade do objeto
        self.picture_url = picture_url  # Atribui a URL da imagem à propriedade do objeto
        self.size = size  # Atribui o tamanho (número de participantes) à propriedade do objeto
        self.creation = creation  # Atribui o timestamp de criação do grupo à propriedade do objeto
        self.owner = owner  # Atribui o dono do grupo à propriedade do objeto
        self.restrict = restrict  # Atribui a flag de restrição do grupo à propriedade do objeto
        self.announce = announce  # Atribui a flag de anúncio (modo somente administradores) à propriedade do objeto
        self.is_community = is_community  # Atribui a indicação se o grupo é uma comunidade
        self.is_community_announce = is_community_announce  # Atribui a indicação se o grupo é de anúncios de comunidade

        # Configurações de resumo
        self.dias = dias  # Define a quantidade de dias considerada para a geração do resumo
        self.horario = horario  # Define o horário em que o resumo deve ser executado
        self.enabled = enabled  # Define se a geração do resumo está habilitada
        self.is_links = is_links  # Define se o resumo deve incluir links
        self.is_names = is_names  # Define se o resumo deve incluir nomes

    def __repr__(self):  # Método especial que retorna uma representação em string do objeto Group
        """
        Retorna uma representação legível do grupo.
        """
        return (  # Utiliza uma f-string para formatar a saída com as propriedades principais do grupo
            f"Group(id={self.group_id}, subject={self.name}, owner={self.owner}, size={self.size})"
        )