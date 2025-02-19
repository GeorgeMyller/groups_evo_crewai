<<<<<<< HEAD
# Groups Evolution CrewAI 👥💡

## Descrição do Projeto 🇧🇷 🚀

Este projeto  gerencia grupos do WhatsApp, gera resumos de mensagens e envia notificações. Ele é composto por vários módulos que interagem com a API Evolution para buscar dados dos grupos, processar mensagens e agendar tarefas.

### Funcionalidades Principais 🚀
- **Gerenciamento de Grupos** 🗂: Busca e armazena informações dos grupos.
- **Geração de Resumos** 📝: Cria resumos diários das mensagens dos grupos.
- **Envio de Mensagens** 💬: Envia mensagens de texto, áudio, imagem, vídeo e documentos para os grupos.
- **Agendamento de Tarefas** ⏰: Agendamento de tarefas para execução automática de scripts.

### Estrutura do Projeto
- `app.py`: Interface principal usando Streamlit para interação com os grupos.
- `group_controller.py`: Controlador para gerenciar grupos e interagir com a API Evolution.
- `group.py`: Definição da classe Group.
- `groups_util.py`: Utilitários para manipulação de dados dos grupos.
- `message_sandeco.py`: Processamento de mensagens recebidas.
- `summary.py`: Script para gerar e enviar resumos.
- `task_scheduler.py`: Agendamento de tarefas no sistema operacional.
- `send_sandeco.py`: Envio de mensagens para os grupos.
- `summary_crew.py`: Configuração e execução de resumos usando CrewAI.
- `save_groups_to_csv.py`: Salva informações dos grupos em um arquivo CSV.

### Como Executar
1. **Instalar Dependências**:
    ```sh
    uv venv
    source .venv/bin/activate
    uv lock
    uv sync 
    ```

2. **Configurar Variáveis de Ambiente**:
    Crie um arquivo `.env` com as seguintes variáveis:
    ```env
    EVO_BASE_URL=<sua_base_url>
    EVO_API_TOKEN=<seu_api_token>
    EVO_INSTANCE_NAME=<seu_instance_name>
    EVO_INSTANCE_TOKEN=<seu_instance_token>
    ```

3. **Executar a Interface Principal**:
    ```sh
    uv run streamlit run app.py
    ```

4. **Agendar Tarefas**:
    Utilize o módulo `task_scheduler.py` para criar, listar e deletar tarefas agendadas.

## Como Contribuir 🤝🇧🇷
Se quiser contribuir, faça um fork deste repositório, crie uma nova branch com suas modificações e abra um pull request para análise.

## Project Description 🇺🇸 🚀

This project manage WhatsApp groups, generate message summaries, and send notifications. It consists of several modules that interact with the Evolution API to fetch group data, process messages, and schedule tasks.

### Main Features 🚀
- **Group Management** 🗂: Fetch and store group information.
- **Summary Generation** 📝: Create daily summaries of group messages.
- **Message Sending** 💬: Send text, audio, image, video, and document messages to groups.
- **Task Scheduling** ⏰: Schedule tasks for automatic script execution.

### Project Structure
- `app.py`: Main interface using Streamlit for group interaction.
- `group_controller.py`: Controller to manage groups and interact with the Evolution API.
- `group.py`: Definition of the Group class.
- `groups_util.py`: Utilities for handling group data.
- `message_sandeco.py`: Processing of received messages.
- `summary.py`: Script to generate and send summaries.
- `task_scheduler.py`: Task scheduling on the operating system.
- `send_sandeco.py`: Sending messages to groups.
- `summary_crew.py`: Configuration and execution of summaries using CrewAI.
- `save_groups_to_csv.py`: Save group information to a CSV file.

### How to Run
1. **Install Dependencies**:
    ```sh
    uv venv
    source .venv/bin/activate
    uv lock
    uv sync   
    ```

2. **Set Environment Variables**:
    Create a `.env` file with the following variables:
    ```env
    EVO_BASE_URL=<your_base_url>
    EVO_API_TOKEN=<your_api_token>
    EVO_INSTANCE_NAME=<your_instance_name>
    EVO_INSTANCE_TOKEN=<your_instance_token>
    ```

3. **Run the Main Interface**:
    ```sh
    uv run streamlit run app.py
    ```

4. **Schedule Tasks**:
    Use the `task_scheduler.py` module to create, list, and delete scheduled tasks.

## How to Contribute 🤝🇺🇸
If you want to contribute, fork this repository, create a new branch with your changes, and open a pull request for review.
=======
# groups_evo_crewai
>>>>>>> de09f1804cd2cc86595c9cf6ff5c3350b0ad888d
