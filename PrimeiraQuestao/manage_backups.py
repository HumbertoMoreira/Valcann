import os
import shutil
import time
import logging
from datetime import datetime

BACKUPSFROM = "/mnt/efs-simulada/backupsFrom"
BACKUPSTO = "/mnt/efs-simulada/backupsTo"
LOGFROM = "/mnt/efs-simulada/backupsFrom.log"
LOGTO = "/mnt/efs-simulada/backupsTo.log"
THREE_DAYS_IN_SECONDS = 3 * 24 * 60 * 60

# Configuração do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Helper function to get file metadata
def get_file_metadata(file_path):
    stats = os.stat(file_path)
    creation_time = time.ctime(stats.st_ctime)
    modification_time = time.ctime(stats.st_mtime)
    size = stats.st_size
    return creation_time, modification_time, size

# 1) Listar arquivos em backupsFrom e salvar no log
def log_files(directory, log_file):
    logging.info(f"Gerando log de arquivos em {directory}...")
    with open(log_file, 'w') as log:
        log.write(f"=== LISTA DE ARQUIVOS EM {directory} ({datetime.now()}) ===\n")
        for file_name in os.listdir(directory):
            file_path = os.path.join(directory, file_name)
            if os.path.isfile(file_path):
                creation_time, modification_time, size = get_file_metadata(file_path)
                log.write(f"Nome: {file_name} | Tamanho: {size} bytes | Criado: {creation_time} | Modificado: {modification_time}\n")
    logging.info(f"Log de arquivos em {directory} concluído.")

# 2) Remover arquivos "com data de criação superior a 3 dias"
def remove_old_files(directory, threshold_seconds):
    logging.info(f"Removendo arquivos mais antigos que {threshold_seconds / (24 * 60 * 60)} dias em {directory}...")
    current_time = time.time()
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            file_creation_time = os.stat(file_path).st_ctime
            if current_time - file_creation_time > threshold_seconds:
                os.remove(file_path)
                logging.info(f"Arquivo removido: {file_name}")
    logging.info(f"Remoção de arquivos antigos em {directory} concluída.")

# 3) Copiar arquivos "com 3 dias ou menos" para backupsTo
def copy_recent_files(source_dir, destination_dir, threshold_seconds):
    logging.info(f"Copiando arquivos recentes de {source_dir} para {destination_dir}...")
    current_time = time.time()
    os.makedirs(destination_dir, exist_ok=True)
    for file_name in os.listdir(source_dir):
        source_path = os.path.join(source_dir, file_name)
        if os.path.isfile(source_path):
            file_creation_time = os.stat(source_path).st_ctime
            if current_time - file_creation_time <= threshold_seconds:
                shutil.copy2(source_path, destination_dir)
                logging.info(f"Arquivo copiado: {file_name}")
    logging.info(f"Cópia de arquivos recentes concluída.")

# 4) Gerar log de backupsTo
def main():
    logging.info("Iniciando script de gerenciamento de backups...")

    # Step 1: Log files in backupsFrom
    log_files(BACKUPSFROM, LOGFROM)

    # Step 2: Remove old files from backupsFrom
    remove_old_files(BACKUPSFROM, THREE_DAYS_IN_SECONDS)

    # Step 3: Copy recent files to backupsTo
    copy_recent_files(BACKUPSFROM, BACKUPSTO, THREE_DAYS_IN_SECONDS)

    # Step 4: Log files in backupsTo
    log_files(BACKUPSTO, LOGTO)

    logging.info("Script finalizado com sucesso.")

if __name__ == "__main__":
    main()
