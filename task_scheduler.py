import os
import subprocess
import platform


class TaskScheduled:
    @staticmethod
    def validate_python_script(python_script_path):
        """Valida se o script Python fornecido existe."""
        if not os.path.exists(python_script_path):
            raise FileNotFoundError(f"O script Python '{python_script_path}' não foi encontrado.")

    @staticmethod
    def get_python_executable():
        """Obtém o caminho do executável Python."""
        try:
            if platform.system() == "Windows":
                python_executable = subprocess.check_output(['where', 'python'], text=True).strip().split('\n')[0]
            else:
                python_executable = subprocess.check_output(['which', 'python3'], text=True).strip()
            return os.path.abspath(python_executable)
        except Exception as e:
            raise EnvironmentError("Não foi possível localizar o executável do Python no sistema.") from e

    @staticmethod
    def create_task(task_name, python_script_path, schedule_type='DAILY', time='22:00'):
        """Cria a tarefa agendada no sistema operacional apropriado."""
        TaskScheduled.validate_python_script(python_script_path)

        python_executable = TaskScheduled.get_python_executable()
        os_name = platform.system()

        if os_name == "Windows":
            # Ajustando a formatação do comando /TR
            command = [
                'schtasks',
                '/Create',
                '/TN', task_name,
                '/TR', f'"{python_executable}" "{python_script_path}" --task_name {task_name}',
                '/SC', schedule_type.upper(),
                '/ST', time,
            ]
        elif os_name == "Linux":
            command = f'(crontab -l 2>/dev/null ; echo "{time.split(":")[1]} {time.split(":")[0]} * * * {python_executable} {python_script_path} --task_name {task_name}") | crontab -'
        elif os_name == "Darwin":  # macOS
            # Sanitize the task_name to ensure valid LABEL in plist (replace '@' and '.' with '_')
            safe_task_name = task_name.replace('@', '_').replace('.', '_')
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{safe_task_name}</string>
    <key>ProgramArguments</key>
    <array>
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
            
            try:
                # Stop and remove any existing service using safe name
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

                # Write the new plist file
                with open(plist_path, "w") as plist_file:
                    plist_file.write(plist_content)

                # Try to bootstrap the service
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
        """Remove a tarefa agendada no sistema operacional apropriado."""
        os_name = platform.system()

        if os_name == "Windows":
            command = [
                'schtasks',
                '/Delete',
                '/TN', task_name,
                '/F'
            ]
        elif os_name == "Linux":
            command = f"crontab -l 2>/dev/null | grep -v '{task_name}' | crontab -"
        elif os_name == "Darwin":  # macOS
            # Sanitize the task_name to ensure valid LABEL in plist (replace '@' and '.' with '_')
            safe_task_name = task_name.replace('@', '_').replace('.', '_')
            plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{safe_task_name}.plist")
            uid = os.getuid()
            domain_target = f"gui/{uid}"
            
            try:
                # First stop and disable the service
                try:
                    subprocess.run(["launchctl", "disable", f"{domain_target}/{safe_task_name}"], check=False)
                    subprocess.run(["launchctl", "bootout", domain_target, plist_path], check=False)
                except:
                    pass

                # Remove plist file
                try:
                    os.remove(plist_path)
                except FileNotFoundError:
                    pass

                print(f"Service {task_name} stopped and removed successfully")
                return True
            except Exception as e:
                print(f"Error removing service: {str(e)}")
                try:
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
        """Lista todas as tarefas agendadas no sistema operacional apropriado."""
        os_name = platform.system()

        if os_name == "Windows":
            command = [
                'schtasks',
                '/Query',
                '/FO', 'TABLE'
            ]
        elif os_name == "Linux":
            command = "crontab -l 2>/dev/null"
        elif os_name == "Darwin":  # macOS
            uid = os.getuid()
            domain_target = f"gui/{uid}"
            command = ["launchctl", "print", domain_target]
        else:
            raise NotImplementedError("Sistema operacional não suportado para listagem de agendamentos.")

        try:
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
        """Abre uma nova janela do terminal para executar o script."""
        python_executable = TaskScheduled.get_python_executable()
        command_line = f'"{python_executable}" "{python_script_path}" --task_name {task_name}'
        os_name = platform.system()

        try:
            if os_name == "Windows":
                # Abre o cmd e mantém a janela aberta após a execução
                subprocess.Popen(f'start cmd /k {command_line}', shell=True)
            elif os_name == "Linux":
                # Usa o gnome-terminal; se usar outro terminal, ajuste o comando
                subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f'{command_line}; exec bash'])
            elif os_name == "Darwin":
                # Usa AppleScript para instruir o Terminal a executar o comando
                subprocess.Popen(["osascript", "-e", f'tell application "Terminal" to do script "{command_line}"'])
            print("Terminal aberto para exibir a execução do script.")
        except Exception as e:
            print(f"Erro ao abrir o terminal: {e}")


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
        print(f"Erro ao listar as tarefas: {e}")