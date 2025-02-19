"""
Sistema de Exportação de Dados de Grupos / Group Data Export System

PT-BR:
Este módulo implementa a funcionalidade de exportação dos dados dos grupos para CSV.
Recupera informações detalhadas de cada grupo como IDs, nomes, configurações e
as salva em um formato estruturado para análise posterior.

EN:
This module implements the functionality to export group data to CSV.
Retrieves detailed information from each group such as IDs, names, settings and
saves it in a structured format for later analysis.
"""

import pandas as pd  
from group_controller import GroupController

def save_groups_to_csv():
    """
    PT-BR:
    Exporta informações detalhadas de todos os grupos para um arquivo CSV.
    Inclui dados como IDs, nomes, configurações e metadados dos grupos.
    O arquivo é salvo como 'group_info.csv' no diretório atual.

    EN:
    Exports detailed information of all groups to a CSV file.
    Includes data such as IDs, names, settings and group metadata.
    The file is saved as 'group_info.csv' in the current directory.
    """
    control = GroupController()
    groups = control.fetch_groups()

    # Prepare group data for export / Prepara dados dos grupos para exportação
    group_data = []
    
    for group in groups:
        group_data.append({
            # Group identification / Identificação do grupo
            "group_id": group.group_id,
            "name": group.name,
            
            # Group metadata / Metadados do grupo
            "subject_owner": group.subject_owner,
            "subject_time": group.subject_time,
            "picture_url": group.picture_url,
            "size": group.size,
            "creation": group.creation,
            "owner": group.owner,
            
            # Group settings / Configurações do grupo
            "restrict": group.restrict,
            "announce": group.announce,
            "is_community": group.is_community,
            "is_community_announce": group.is_community_announce,
            
            # Summary settings / Configurações de resumo
            "dias": group.dias,
            "horario": group.horario,
            "enabled": group.enabled,
            "is_links": group.is_links,
            "is_names": group.is_names
        })

    # Export to CSV / Exporta para CSV
    df = pd.DataFrame(group_data)
    df.to_csv("group_info.csv", index=False)
    print("Group information saved to group_info.csv")

if __name__ == "__main__":
    save_groups_to_csv()