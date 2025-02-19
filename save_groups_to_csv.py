import pandas as pd  
from group_controller import GroupController

def save_groups_to_csv():
    """Salva informações dos grupos em um arquivo CSV."""
    control = GroupController()
    groups = control.fetch_groups()

    group_data = []
    
    for group in groups:
        group_data.append({
            "group_id": group.group_id,
            "name": group.name,
            "subject_owner": group.subject_owner,
            "subject_time": group.subject_time,
            "picture_url": group.picture_url,
            "size": group.size,
            "creation": group.creation,
            "owner": group.owner,
            "restrict": group.restrict,
            "announce": group.announce,
            "is_community": group.is_community,
            "is_community_announce": group.is_community_announce,
            "dias": group.dias,
            "horario": group.horario,
            "enabled": group.enabled,
            "is_links": group.is_links,
            "is_names": group.is_names
        })

    df = pd.DataFrame(group_data)
    df.to_csv("group_info.csv", index=False)
    print("Group information saved to group_info.csv")

if __name__ == "__main__":
    save_groups_to_csv()