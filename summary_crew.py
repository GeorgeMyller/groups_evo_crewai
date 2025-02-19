from dotenv import load_dotenv          # Importa a função load_dotenv para carregar variáveis de ambiente a partir do arquivo .env
from crewai import Agent, Task, Crew, Process, LLM  # Importa classes necessárias do módulo crewai para gerenciar agente, tarefa, crew, processo e LLM

class SummaryCrew:
    """
    Classe para organizar um agente, tarefa e execução de resumos de mensagens do WhatsApp.
    """

    def __init__(self):
        load_dotenv()                      # Carrega as variáveis de ambiente definidas no arquivo .env
        self.llm = "gemini/gemini-2.0-flash" # Define o modelo LLM a ser utilizado para a geração de resumos
        
        self.create_crew()                 # Chama o método para configurar o agente, tarefa e crew

    def create_crew(self):
        # Configurar o agente responsável por criar os resumos
        self.agent = Agent(
            role="Assistente de Resumos",   # Define o papel do agente como assistente de resumos
            goal="Criar resumos organizados e objetivos de mensagens de WhatsApp.",  
                                             # Define o objetivo do agente: resumos claros e objetivos das mensagens
            backstory=(                     # Define o contexto (backstory) do agente
                "Você é um assistente de IA especializado em analisar e organizar informações "
                "extraídas de mensagens de WhatsApp, garantindo clareza e objetividade."
            ),
            verbose=True,                   # Habilita saídas detalhadas para depuração
            memory=False,                   # Desativa o uso de memória, pois não é necessário para essa tarefa simples
            llm=self.llm                    # Configura o modelo LLM definido anteriormente para gerar os resumos
        )

        # Configurar a tarefa que o agente deve desempenhar
        self.task = Task(
            description=r"""
Você é um assistente de IA especializado 
em criar resumos organizados e objetivos 
de mensagens em grupos de WhatsApp. 
Seu objetivo é apresentar as informações 
de forma clara e segmentada, 
usando o templete delimitado por <template>. 
Para alimentar o resumo use as mensagens
de WhatsApp delimitadas por <msgs>. 

Importante:
- Ignore mensagens que são resumos anteriores.
- Retire os placeholders < > do texto. 
- Deve haver somente um tópico da lista abaixo no resumo:
    - Resumo do Grupo
    - Tópico Principal
    - Dúvidas, Erros e suas Soluções
    - Resumo geral do período
    - Links do Dia
    - Conclusão
- Quando não houver informações sobre um tópico simplesmente não coloque o tópico.

<template>
*Resumo do Grupo📝 - <Data ou Período>*

*<Tópico Principal> <Emoji relacionado> - <Horário>*

- *Participantes:* <Nomes dos usuários envolvidos>  
- *Resumo:* <Descrição do tópico discutido, incluindo detalhes importantes e ações relevantes>  

*Dúvidas, Erros e suas Soluções ❓ - <Horário>*

- *Solicitado por:* <Nome do participante que levantou a dúvida ou relatou o erro>  
- *Respondido por:* <Nome(s) dos participantes que ofereceram soluções ou respostas>
- *Resumo:* <Descrição do problema ou dúvida e as soluções ou respostas apresentadas.> 

*Resumo geral do período 📊:*
- <Resumo curto e objetivo sobre o tom geral das interações ou assuntos discutidos no período.>

*Links do Dia🔗:*
- <Caso sejam compartilhados links importantes, liste-os aqui com data e contexto.>

*Conclusão🔚:*
- <Conclua destacando o ambiente do grupo ou a produtividade das interações.>
</template>

Mensagens do grupo para análise:

<msgs>
{msgs}
</msgs>
            """,  # Descrição detalhada da tarefa, contendo template e instruções para a criação do resumo
            expected_output=(  
                "Um resumo segmentado de acordo com o template fornecido, contendo apenas informações "
                "relevantes extraídas das mensagens fornecidas."
            ),  # Define a saída esperada da tarefa
            agent=self.agent,             # Atribui o agente configurado para executar essa tarefa
        )

        # Configurar o crew com os agentes e tarefas definidos, e o processo de execução
        self.crew = Crew(
            agents=[self.agent],           # Lista de agentes que farão parte do crew; neste caso, apenas um agente
            tasks=[self.task],             # Lista de tarefas a serem executadas pelo crew; neste caso, apenas uma tarefa
            process=Process.sequential,    # Define que as tarefas serão processadas de forma sequencial
        )

    def kickoff(self, inputs):
        """
        Executa o processo de resumo de mensagens.

        Args:
            inputs (str): Mensagens de WhatsApp para processar.

        Returns:
            str: O resumo gerado no formato esperado.
        """
        result = self.crew.kickoff(inputs=inputs).raw  # Executa a tarefa do crew com os inputs fornecidos e obtém o resultado bruto
        return result  # Retorna o resumo gerado pelo processo