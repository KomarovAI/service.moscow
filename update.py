#!/usr/bin/env python3
"""
Скрипт быстрого обновления сайта artur789298.work.gd
Обновляет только контент, не затрагивая системные настройки
"""

import os
import sys
import subprocess
import time
import shutil
import argparse
from datetime import datetime
from pathlib import Path

# Конфигурация
DOMAIN = "artur789298.work.gd"
PROJECT_NAME = "service-moscow"
INSTALL_DIR = f"/opt/{PROJECT_NAME}"
BACKUP_DIR = f"{INSTALL_DIR}/backups"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log(msg, color=Colors.GREEN):
    print(f"{color}[UPDATE] {msg}{Colors.END}")

def error(msg):
    print(f"{Colors.RED}[ERROR] {msg}{Colors.END}")
    sys.exit(1)

def warning(msg):
    print(f"{Colors.YELLOW}[WARNING] {msg}{Colors.END}")

def run_cmd(cmd, check=True, capture=False):
    """Выполнить команду с логированием"""
    log(f"Выполняю: {cmd}", Colors.BLUE)
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, check=check, 
                                 capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=check)
            return True
    except subprocess.CalledProcessError as e:
        if check:
            error(f"Команда завершилась с ошибкой: {cmd}")
        return False

def check_root():
    """Проверка root прав"""
    if os.geteuid() != 0:
        error("Скрипт должен запускаться с правами root! Используйте: sudo python3 update.py")

def check_installation():
    """Проверка, что сайт установлен"""
    if not os.path.exists(INSTALL_DIR):
        error(f"Проект не найден в {INSTALL_DIR}. Запустите deploy.py сначала.")
    
    if not os.path.exists(f"{INSTALL_DIR}/docker-compose.yml"):
        error(f"docker-compose.yml не найден в {INSTALL_DIR}. Проект не установлен полностью.")
    
    log("Проверка прошла успешно!")

def create_backup(no_backup=False):
    """Создание резервной копии"""
    if no_backup:
        log("Пропускаю создание резервной копии")
        return
    
    log("Создаю резервную копию...")
    
    # Создаем папку для бэкапов
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Имя бэкапа с таймстампом
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}"
    backup_path = f"{BACKUP_DIR}/{backup_name}"
    
    # Копируем текущие исходники
    if os.path.exists(f"{INSTALL_DIR}/src"):
        shutil.copytree(f"{INSTALL_DIR}/src", backup_path)
        log(f"Резервная копия создана: {backup_path}")
    else:
        warning("Папка src не найдена, резервная копия не создана")

def update_content():
    """Обновление контента сайта"""
    log("Обновляю контент сайта...")
    
    # Клонируем новые исходники
    temp_dir = "/tmp/service-moscow-update"
    run_cmd(f"rm -rf {temp_dir}", check=False)
    run_cmd(f"git clone https://github.com/KomarovAI/service.moscow.git {temp_dir}")
    
    # Удаляем старые исходники
    if os.path.exists(f"{INSTALL_DIR}/src"):
        run_cmd(f"rm -rf {INSTALL_DIR}/src")
    
    # Копируем новые
    run_cmd(f"cp -r {temp_dir}/src {INSTALL_DIR}/")
    
    # Очищаем временную папку
    run_cmd(f"rm -rf {temp_dir}")
    
    log("Контент обновлён!")

def rebuild_containers():
    """Пересборка контейнеров"""
    log("Пересобираю контейнеры...")
    
    # Пересобираем только веб-контейнер
    run_cmd(f"cd {INSTALL_DIR} && docker compose up -d --build web")
    
    # Ждем немного
    time.sleep(5)
    
    log("Контейнеры пересобраны!")

def cleanup_old_images(no_cleanup=False):
    """Очистка старых Docker образов"""
    if no_cleanup:
        log("Пропускаю очистку старых образов")
        return
    
    log("Очищаю старые Docker образы...")
    
    # Удаляем неиспользуемые образы
    run_cmd("docker image prune -f", check=False)
    
    # Удаляем старые контейнеры
    run_cmd("docker container prune -f", check=False)
    
    log("Очистка завершена!")

def check_health(quick=False):
    """Проверка работоспособности"""
    log("Проверяю работоспособность...")
    
    if not quick:
        # Проверяем статус контейнеров
        run_cmd(f"cd {INSTALL_DIR} && docker compose ps")
    
    # Проверяем доступность сайта
    http_test = run_cmd(f"curl -I http://{DOMAIN}", check=False)
    https_test = run_cmd(f"curl -I https://{DOMAIN}", check=False)
    
    if http_test or https_test:
        log(f"✅ Сайт доступен: https://{DOMAIN}")
    else:
        warning(f"❌ Проблемы с доступом к сайту!")

def show_logs():
    """Показ логов"""
    log("Показываю последние логи...")
    run_cmd(f"cd {INSTALL_DIR} && docker compose logs --tail=20")

def cleanup_old_backups():
    """Очистка старых резервных копий (оставляем только 5 последних)"""
    if not os.path.exists(BACKUP_DIR):
        return
    
    backups = []
    for item in os.listdir(BACKUP_DIR):
        backup_path = os.path.join(BACKUP_DIR, item)
        if os.path.isdir(backup_path) and item.startswith("backup_"):
            backups.append((backup_path, os.path.getctime(backup_path)))
    
    # Сортируем по времени (новые впереди)
    backups.sort(key=lambda x: x[1], reverse=True)
    
    # Удаляем старые бэкапы (оставляем 5)
    for backup_path, _ in backups[5:]:
        shutil.rmtree(backup_path)
        log(f"Удалён старый бэкап: {os.path.basename(backup_path)}")

def print_final_report():
    """Финальный отчёт"""
    log("=" * 50, Colors.BOLD)
    log("🎉 ОБНОВЛЕНИЕ ЗАВЕРШЕНО!", Colors.BOLD)
    log("=" * 50, Colors.BOLD)
    
    log(f"🌐 Сайт: https://{DOMAIN}")
    log(f"📁 Проект: {INSTALL_DIR}")
    
    if os.path.exists(BACKUP_DIR):
        backup_count = len([f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_")])
        log(f"💾 Резервных копий: {backup_count}")
    
    log("🔧 Полезные команды:")
    log(f"   Логи:        cd {INSTALL_DIR} && docker compose logs -f")
    log(f"   Статус:      cd {INSTALL_DIR} && docker compose ps")
    log(f"   Перезапуск:  cd {INSTALL_DIR} && docker compose restart")
    
    log("=" * 50, Colors.BOLD)
    log("ОБНОВЛЕНИЕ УСПЕШНО! 🚀", Colors.BOLD)
    log("=" * 50, Colors.BOLD)

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Обновление контента сайта")
    parser.add_argument("--no-backup", action="store_true", help="Не создавать резервную копию")
    parser.add_argument("--no-cleanup", action="store_true", help="Не удалять старые Docker образы")
    parser.add_argument("--show-logs", action="store_true", help="Показать логи после обновления")
    parser.add_argument("--quick", action="store_true", help="Быстрое обновление без лишних проверок")
    args = parser.parse_args()
    
    try:
        log("Начинаю обновление сайта...", Colors.BOLD)
        
        check_root()
        check_installation()
        
        # Создаём резервную копию
        create_backup(args.no_backup)
        
        # Обновляем контент
        update_content()
        
        # Пересобираем контейнеры
        rebuild_containers()
        
        # Очищаем старые образы
        cleanup_old_images(args.no_cleanup)
        
        # Очищаем старые резервные копии
        cleanup_old_backups()
        
        # Проверяем работоспособность
        check_health(args.quick)
        
        # Показываем логи если нужно
        if args.show_logs:
            show_logs()
        
        print_final_report()
        
    except KeyboardInterrupt:
        error("Обновление прервано пользователем")
    except Exception as e:
        error(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    main()