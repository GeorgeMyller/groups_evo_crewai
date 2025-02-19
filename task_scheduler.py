import os
import subprocess
import platform


class TaskScheduled:
    @staticmethod
    def validate_python_script(python_script_path):
        # Verifica se o script Python existe. Isso evita que o programa tente agendar uma tarefa para um arquivo inexistente.
        if not os.path.exists(python_script_path):
            raise FileNotFoundError(f"O script Python '{python_script_path}' não foi encontrado.")

    @staticmethod
    def get_python_executable():
        """Obtém o caminho absoluto do executável Python.
        Isso é importante para garantir que o script seja executado com o interpretador correto.
        """
        try:
            if platform.system() == "Windows":
                # 'where' é utilizado em Windows para localizar o executável
                python_executable = subprocess.check_output(['where', 'python'], text=True).strip().split('\n')[0]
            else:
                # 'which' é utilizado em sistemas baseados em Unix para localizar o python3
                python_executable = subprocess.check_output(['which', 'python3'], text=True).strip()
            return os.path.abspath(python_executable)
        except Exception as e:
            raise EnvironmentError("Não foi possível localizar o executável do Python no sistema.") from e

    @staticmethod
    def create_task(task_name, python_script_path, schedule_type='DAILY', time='22:00'):
        """Cria uma tarefa agendada de acordo com o sistema operacional.
        Para cada sistema, constrói o comando ou arquivo de configuração necessário.
        """
        TaskScheduled.validate_python_script(python_script_path)

        python_executable = TaskScheduled.get_python_executable()
        os_name = platform.system()

        if os_name == "Windows":
            # Em Windows, utiliza o comando 'schtasks' para criar a tarefa. O parâmetro /TR define a ação.
            command = [
                'schtasks',
                '/Create',
                '/TN', task_name,
                '/TR', f'"{python_executable}" "{python_script_path}" --task_name {task_name}',
                '/SC', schedule_type.upper(),
                '/ST', time,
            ]
        elif os_name == "Linux":
            # Em Linux, adiciona uma entrada no crontab. O comando concatena entradas existentes com a nova.
            command = f'(crontab -l 2>/dev/null ; echo "{time.split(":")[1]} {time.split(":")[0]} * * * {python_executable} {python_script_path} --task_name {task_name}") | crontab -'
        elif os_name == "Darwin":  
            # Em macOS, cria um arquivo plist para agendar a tarefa pelo launchctl
            safe_task_name = task_name.replace('@', '_').replace('.', '_')
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{safe_task_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/osascript</string>
        <string>-e</string>
        <string>tell application "Terminal" to do script "{python_executable} {python_script_path} --task_name {task_name}" </string>
        <string>{python_executable}</string>
        <string>{python_script_path}</string>
        <string>--task_name</string>
        <string>{task_name}</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>{int(time.split(':')[0])}</integer>
        <key>Minute</key>
        <integer>{int(time.split(':')[1])}</integer>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/{safe_task_name}.out.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/{safe_task_name}.err.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>LANG</key>
        <string>en_US.UTF-8</string>
    </dict>
</dict>
</plist>
"""
            plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{safe_task_name}.plist")
            uid = os.getuid()
            domain_target = f"gui/{uid}"
            # Procedimentos de remoção e criação do serviço são feitos para evitar conflitos
            try:
                try:
                    subprocess.run(["launchctl", "stop", safe_task_name], check=False)
                except:
                    pass
                try:
                    subprocess.run(["launchctl", "remove", safe_task_name], check=False)
                except:
                    pass
                try:
                    os.remove(plist_path)
                except FileNotFoundError:
                    pass

                # Escreve o arquivo plist que define a tarefa
                with open(plist_path, "w") as plist_file:
                    plist_file.write(plist_content)

                try:
                    subprocess.run(["launchctl", "bootstrap", domain_target, plist_path], check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Bootstrap failed: {e}. Falling back to launchctl load.")
                    subprocess.run(["launchctl", "load", plist_path], check=True)

                subprocess.run(["launchctl", "enable", f"{domain_target}/{safe_task_name}"], check=True)
                try:
                    subprocess.run(["launchctl", "kickstart", "-k", f"{domain_target}/{safe_task_name}"], check=True)
                except subprocess.CalledProcessError as e:
                    if e.returncode == 113:
                        print(f"kickstart failed with code 113, falling back to launchctl start")
                        try:
                            subprocess.run(["launchctl", "start", safe_task_name], check=True)
                        except subprocess.CalledProcessError as start_e:
                            if start_e.returncode == 3:
                                print(f"launchctl start failed with code 3, reloading service...")
                                subprocess.run(["launchctl", "load", plist_path], check=True)
                                subprocess.run(["launchctl", "start", safe_task_name], check=True)
                            else:
                                raise
                    else:
                        raise
                
                print(f"Service {task_name} configured and started successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"Error configuring service: {str(e)}")
                try:
                    os.remove(plist_path)
                except:
                    pass
                raise Exception(f"Falha ao configurar o serviço: {str(e)}")
        else:
            raise NotImplementedError("Sistema operacional não suportado para agendamento.")

        try:
            # Executa o comando construído para criar a tarefa conforme o sistema operacional
            if os_name == "Windows":
                subprocess.run(command, check=True, text=True)
            elif os_name in ["Linux", "Darwin"]:
                subprocess.run(command, shell=(os_name != "Windows"), check=True)
            print(f"Tarefa '{task_name}' criada com sucesso no sistema operacional {os_name}!")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao criar a tarefa: {e}")
            raise

    @staticmethod
    def delete_task(task_name):
        """Remove a tarefa agendada de acordo com o sistema operacional.
        Cada sistema possui seu próprio método de remoção da tarefa.
        """
        os_name = platform.system()
        if os_name == "Windows":
            command = [
                'schtasks',
                '/Delete',
                '/TN', task_name,
                '/F'
            ]
        elif os_name == "Linux":
            # Remove a tarefa do crontab filtrando entradas que não contenham task_name
            command = f"crontab -l 2>/dev/null | grep -v '{task_name}' | crontab -"
        elif os_name == "Darwin":  
            safe_task_name = task_name.replace('@', '_').replace('.', '_')
            plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{safe_task_name}.plist")
            uid = os.getuid()
            domain_target = f"gui/{uid}"
            
            try:
                # Primeiro tenta parar o serviço
                subprocess.run(["launchctl", "stop", safe_task_name], check=False)
                
                # Tenta remover o serviço do launchd
                subprocess.run(["launchctl", "unload", plist_path], check=False)
                subprocess.run(["launchctl", "remove", safe_task_name], check=False)
                
                # Remove o arquivo plist
                try:
                    if os.path.exists(plist_path):
                        os.remove(plist_path)
                except FileNotFoundError:
                    pass
                except PermissionError:
                    subprocess.run(["sudo", "rm", plist_path], check=False)
                
                print(f"Service {task_name} stopped and removed successfully")
                return True
            except Exception as e:
                print(f"Error removing service: {str(e)}")
                try:
                    if os.path.exists(plist_path):
                        os.remove(plist_path)
                except:
                    pass
                raise Exception(f"Falha ao remover o serviço: {str(e)}")
        else:
            raise NotImplementedError("Sistema operacional não suportado para remoção de agendamento.")

        try:
            if os_name == "Windows":
                subprocess.run(command, check=True, text=True)
            elif os_name in ["Linux", "Darwin"]:
                subprocess.run(command, shell=(os_name != "Windows"), check=True)
            print(f"Tarefa '{task_name}' removida com sucesso no sistema operacional {os_name}!")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao remover a tarefa: {e}")
            raise

    @staticmethod
    def list_tasks():
        """Lista todas as tarefas agendadas conforme o sistema operacional.
        Essa função utiliza comandos específicos para cada ambiente.
        """
        os_name = platform.system()

        if os_name == "Windows":
            command = [
                'schtasks',
                '/Query',
                '/FO', 'TABLE'
            ]
        elif os_name == "Linux":
            command = "crontab -l 2>/dev/null"
        elif os_name == "Darwin":  
            uid = os.getuid()
            domain_target = f"gui/{uid}"
            command = ["launchctl", "print", domain_target]
        else:
            raise NotImplementedError("Sistema operacional não suportado para listagem de agendamentos.")

        try:
            # Executa o comando de listagem e mostra o resultado ao usuário
            if os_name == "Windows":
                result = subprocess.check_output(command, text=True)
            elif os_name in ["Linux", "Darwin"]:
                result = subprocess.check_output(command, shell=(os_name != "Darwin"), text=True)
            print(f"Tarefas agendadas no sistema operacional {os_name}:")
            print(result)
        except subprocess.CalledProcessError as e:
            print(f"Erro ao listar as tarefas: {e}")
            raise

    @staticmethod
    def open_in_terminal(task_name, python_script_path):
        """Abre uma nova janela do terminal para executar o script especificado.
        Essa função utiliza comandos específicos para cada sistema operacional.
        """
        python_executable = TaskScheduled.get_python_executable()
        command_line = f'"{python_executable}" "{python_script_path}" --task_name {task_name}'
        os_name = platform.system()

        try:
            if os_name == "Windows":
                # Abre o prompt do Windows e mantém a janela aberta
                subprocess.Popen(f'start cmd /k {command_line}', shell=True)
            elif os_name == "Linux":
                # Abre o terminal do GNOME; se usar outro, ajuste aqui
                subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f'{command_line}; exec bash'])
            elif os_name == "Darwin":
                # Usa AppleScript para abrir o Terminal no macOS
                subprocess.Popen(["osascript", "-e", f'tell application "Terminal" to do script "{command_line}"'])
            print("Terminal aberto para exibir a execução do script.")
        except Exception as e:
            print(f"Erro ao abrir o terminal: {e}")

'''
if __name__ == "__main__":
    task_name = "MinhaTarefa"
    # Ajuste o caminho do script conforme necessário
    if platform.system() == "Windows":
        python_script = os.path.join("D:\\GOOGLE DRIVE\\Python-Projects\\crewai_2\\groups\\", "poema.py")
    else:
        python_script = os.path.join(os.path.expanduser("~"), "path", "para", "seu", "script", "poema.py")

    # Cria a tarefa agendada
    try:
        TaskScheduled.create_task(task_name, python_script, schedule_type='DAILY', time='11:13')
    except Exception as e:
        print(f"Erro ao criar a tarefa: {e}")

    # Abre uma janela do terminal para exibir a execução do script
    try:
        TaskScheduled.open_in_terminal(task_name, python_script)
    except Exception as e:
        print(f"Erro ao abrir o terminal: {e}")

    # Exemplo de remoção e listagem de tarefas
    try:
        TaskScheduled.delete_task(task_name)
    except Exception as e:
        print(f"Erro ao deletar a tarefa: {e}")

    try:
        TaskScheduled.list_tasks()
    except Exception as e:
        print(f"Erro ao listar as tarefas: {e}")'''