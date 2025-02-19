import pandas as pd  # Importa o módulo pandas para manipulação de DataFrames
from group_controller import GroupController  # Importa a classe GroupController para gerenciar grupos e buscar informações

def save_groups_to_csv():
    control = GroupController()  # Instancia o controlador de grupos
    groups = control.fetch_groups()  # Busca a lista de grupos disponíveis, utilizando o cache ou a API

    # Cria uma lista de dicionários com informações de cada grupo
    group_data = []  # Inicializa uma lista vazia para armazenar os dados dos grupos
    for group in groups:  # Itera sobre cada grupo na lista de grupos
        group_data.append({  # Adiciona um dicionário com os dados do grupo à lista
            "group_id": group.group_id,  # Armazena o ID único do grupo
            "name": group.name,  # Armazena o nome do grupo
            "subject_owner": group.subject_owner,  # Armazena o dono do assunto/título do grupo
            "subject_time": group.subject_time,  # Armazena o timestamp da última alteração do título do grupo
            "picture_url": group.picture_url,  # Armazena a URL da imagem do grupo
            "size": group.size,  # Armazena o número de participantes do grupo
            "creation": group.creation,  # Armazena o timestamp de criação do grupo
            "owner": group.owner,  # Armazena o dono do grupo
            "restrict": group.restrict,  # Indica se o grupo possui restrições
            "announce": group.announce,  # Indica se o grupo está em modo 'somente administradores'
            "is_community": group.is_community,  # Indica se o grupo é uma comunidade
            "is_community_announce": group.is_community_announce,  # Indica se o grupo é de anúncios de comunidade
            "dias": group.dias,  # Armazena a quantidade de dias para o resumo
            "horario": group.horario,  # Armazena o horário programado para o resumo
            "enabled": group.enabled,  # Indica se a geração do resumo está habilitada
            "is_links": group.is_links,  # Indica se os links estão incluídos no resumo
            "is_names": group.is_names  # Indica se os nomes estão incluídos no resumo
        })

    # Converte a lista de dicionários para um DataFrame do pandas
    df = pd.DataFrame(group_data)  # Cria um DataFrame com os dados dos grupos

    # Salva o DataFrame em um arquivo CSV
    df.to_csv("group_info.csv", index=False)  # Escreve o DataFrame no arquivo CSV sem incluir o índice
    print("Group information saved to group_info.csv")  # Imprime uma mensagem informando que a informação foi salva

if __name__ == "__main__":
    save_groups_to_csv()  # Chama a função save_groups_to_csv se o script for executado diretamente