import paramiko
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed

# Функция для подключения к устройству и выполнения команды
def change_eoip_tunnel_id(ip, tunnel_id, tunnel_id_new, username, password):
    try:
        # Устанавливаем SSH-соединение с таймаутом
        with paramiko.SSHClient() as ssh:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # Таймаут подключения: 5 секунд
            ssh.connect(hostname=ip, username=username, password=password, timeout=5)

            # Команда для изменения ID туннеля
            command = f"/interface eoip set [find tunnel-id={tunnel_id}] tunnel-id={tunnel_id_new}"
            # Таймаут выполнения команды: 5 секунд
            stdin, stdout, stderr = ssh.exec_command(command, timeout=5)

            # Читаем результаты выполнения команды
            output = stdout.read().decode()
            error = stderr.read().decode()

            if error:
                print(f"[Ошибка] {ip}: {error}")
            else:
                print(f"[Успешно] {ip}: ID туннеля изменен с {tunnel_id} на {tunnel_id_new}")
    except paramiko.SSHException as e:
        print(f"[Ошибка SSH] {ip}: {e}")
    except Exception as e:
        print(f"[Ошибка подключения] {ip}: {e}")

# Чтение данных из файла CSV
def process_devices_from_csv(csv_file, username, password):
    try:
        # Открываем CSV-файл с использованием контекстного менеджера
        with open(csv_file, newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=';')
            # Используем ThreadPoolExecutor для параллельного выполнения
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for row in reader:
                    ip = row.get('remote_address')
                    tunnel_id = row.get('tunnel')
                    tunnel_id_new = row.get('tunnel_new')
                    if ip and tunnel_id and tunnel_id_new:
                        # Запускаем выполнение функции в отдельном потоке
                        futures.append(executor.submit(change_eoip_tunnel_id, ip, tunnel_id, tunnel_id_new, username, password))
                    else:
                        print(f"[Ошибка данных] Пропущена строка: {row}")

                # Ожидаем завершения всех задач
                for future in as_completed(futures):
                    future.result()  # Обработка исключений, если они возникли
    except Exception as e:
        print(f"[Ошибка при обработке CSV] {e}")

# Основной блок
if __name__ == "__main__":
    username = "username"
    password = "password"

    # Путь к файлу CSV
    csv_file_path = "file.csv"  # Замените на ваш путь

    # Выполняем процесс
    process_devices_from_csv(csv_file_path, username, password)
