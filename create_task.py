import os
from task_scheduler import TaskScheduled

# Nome da tarefa agendada
TASK_NAME = "SummaryTask"

# Caminho para o script summary.py
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), "summary.py")

# Cria a tarefa agendada para executar diariamente às 22:00
try:
    TaskScheduled.create_task(TASK_NAME, SCRIPT_PATH, schedule_type='DAILY', time='23:55' )
    print(f"Tarefa '{TASK_NAME}' criada com sucesso.")
except Exception as e:
    print(f"Erro ao criar a tarefa: {e}")
