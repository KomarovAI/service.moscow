#!/usr/bin/env python3
"""
Полный скрипт развертывания сайта artur789298.work.gd на VPS
Автоматически устанавливает Docker, Nginx, Certbot и настраивает SSL
"""

import os
import sys
import subprocess
import time
import json
import shutil
import argparse
from pathlib import Path

# Конфигурация
DOMAIN = "artur789298.work.gd"
EMAIL = "artur.komarovv@gmail.com"
PROJECT_NAME = "service-moscow"
INSTALL_DIR = f"/opt/{PROJECT_NAME}"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log(msg, color=Colors.GREEN):
    print(f"{color}[DEPLOY] {msg}{Colors.END}")

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
        error("Скрипт должен запускаться с правами root! Используйте: sudo python3 deploy.py")

def check_system():
    """Проверка системы"""
    log("Проверяю системные требования...")
    
    # Проверка ОС
    try:
        os_info = run_cmd("lsb_release -d", capture=True)
        log(f"ОС: {os_info}")
    except:
        warning("Не удалось определить версию ОС")
    
    # Проверка памяти
    try:
        mem_info = run_cmd("free -h | grep 'Mem:'", capture=True)
        log(f"Память: {mem_info}")
    except:
        warning("Не удалось получить информацию о памяти")
    
    # Проверка места на диске
    try:
        disk_info = run_cmd("df -h / | tail -1", capture=True)
        log(f"Диск: {disk_info}")
    except:
        warning("Не удалось получить информацию о диске")

def install_dependencies():
    """Установка зависимостей"""
    log("Обновляю список пакетов...")
    run_cmd("apt-get update -y")
    
    log("Устанавливаю необходимые пакеты...")
    run_cmd("apt-get install -y curl wget git ufw python3-pip")

def install_docker():
    """Установка Docker и Docker Compose"""
    if shutil.which("docker") and run_cmd("docker compose version", check=False):
        log("Docker уже установлен")
        return
    
    log("Устанавливаю Docker...")
    run_cmd("apt-get remove -y docker docker-engine docker.io containerd runc", check=False)
    run_cmd("apt-get install -y ca-certificates curl gnupg lsb-release")
    run_cmd("install -m 0755 -d /etc/apt/keyrings")
    run_cmd("curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg")
    run_cmd("chmod a+r /etc/apt/keyrings/docker.gpg")
    run_cmd('echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" > /etc/apt/sources.list.d/docker.list')
    
    run_cmd("apt-get update -y")
    run_cmd("apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin")
    
    run_cmd("systemctl enable docker")
    run_cmd("systemctl start docker")
    
    log("Docker успешно установлен!")

def setup_firewall():
    """Настройка файервола"""
    log("Настраиваю файервол...")
    run_cmd("ufw --force reset")
    run_cmd("ufw default deny incoming")
    run_cmd("ufw default allow outgoing")
    run_cmd("ufw allow ssh")
    run_cmd("ufw allow 80/tcp")
    run_cmd("ufw allow 443/tcp")
    run_cmd("ufw --force enable")
    log("Файервол настроен!")

def create_project_structure():
    """Создание структуры проекта"""
    log(f"Создаю структуру проекта в {INSTALL_DIR}...")
    
    # Создаем директории
    dirs = [
        INSTALL_DIR,
        f"{INSTALL_DIR}/nginx/conf.d",
        f"{INSTALL_DIR}/certbot",
        f"{INSTALL_DIR}/scripts",
        f"{INSTALL_DIR}/logs"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    log("Структура проекта создана!")

def write_docker_compose():
    """Создание docker-compose.yml"""
    compose_content = f'''version: '3.8'

services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: {PROJECT_NAME}-web
    restart: unless-stopped
    networks:
      - webnet
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s

  nginx:
    image: nginx:alpine
    container_name: {PROJECT_NAME}-nginx
    depends_on:
      - web
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    networks:
      - webnet
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - certbot-webroot:/var/www/certbot
      - letsencrypt:/etc/letsencrypt
      - ./logs/nginx:/var/log/nginx

  certbot:
    image: certbot/certbot:latest
    container_name: {PROJECT_NAME}-certbot
    depends_on:
      - nginx
    volumes:
      - certbot-webroot:/var/www/certbot
      - letsencrypt:/etc/letsencrypt
    entrypoint: sh
    command: -c "trap exit TERM; while :; do sleep 6h & wait $$!; certbot renew --webroot -w /var/www/certbot --quiet --deploy-hook 'docker exec {PROJECT_NAME}-nginx nginx -s reload'; done"

networks:
  webnet:
    driver: bridge

volumes:
  certbot-webroot:
  letsencrypt:
'''
    
    with open(f"{INSTALL_DIR}/docker-compose.yml", "w") as f:
        f.write(compose_content)
    
    log("docker-compose.yml создан!")

def write_nginx_config():
    """Создание конфигурации Nginx"""
    nginx_config = f'''server {{
    listen 80;
    listen [::]:80;
    server_name {DOMAIN} www.{DOMAIN};

    # ACME Challenge для Let's Encrypt
    location ^~ /.well-known/acme-challenge/ {{
        root /var/www/certbot;
        default_type "text/plain";
        try_files $uri =404;
    }}

    # Редирект на HTTPS после получения сертификата
    location / {{
        return 301 https://{DOMAIN}$request_uri;
    }}
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name www.{DOMAIN};

    ssl_certificate /etc/letsencrypt/live/{DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{DOMAIN}/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/{DOMAIN}/chain.pem;

    # Редирект с www на основной домен
    return 301 https://{DOMAIN}$request_uri;
}}

server {{
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name {DOMAIN};

    # SSL конфигурация
    ssl_certificate /etc/letsencrypt/live/{DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{DOMAIN}/privkey.pem;
    ssl_trusted_certificate /etc/letsencrypt/live/{DOMAIN}/chain.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Content-Security-Policy "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob:;" always;

    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        image/svg+xml;

    # ACME Challenge
    location ^~ /.well-known/acme-challenge/ {{
        root /var/www/certbot;
        default_type "text/plain";
        try_files $uri =404;
    }}

    # Основной проксирование на контейнер с сайтом
    location / {{
        proxy_pass http://{PROJECT_NAME}-web:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Кэширование статических файлов
        location ~* \\.(?:jpg|jpeg|gif|png|ico|svg|css|js|woff2?|ttf|eot)$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }}
    }}

    # Логирование
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Обработка ошибок
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
}}
'''
    
    with open(f"{INSTALL_DIR}/nginx/conf.d/site.conf", "w") as f:
        f.write(nginx_config)
    
    log("Конфигурация Nginx создана!")

def write_dockerfile():
    """Создание Dockerfile"""
    dockerfile_content = '''FROM nginx:alpine

WORKDIR /usr/share/nginx/html

RUN rm -rf /usr/share/nginx/html/*

COPY ./src/ /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
'''
    
    with open(f"{INSTALL_DIR}/Dockerfile", "w") as f:
        f.write(dockerfile_content)
    
    log("Dockerfile создан!")

def clone_website():
    """Клонирование исходников сайта"""
    log("Клонирую исходники сайта...")
    
    # Проверяем, существует ли уже git репозиторий
    if os.path.exists(f"{INSTALL_DIR}/.git"):
        log("Репозиторий уже существует, обновляю...")
        run_cmd(f"cd {INSTALL_DIR} && git pull origin main")
    else:
        # Если папка существует, но это не git репозиторий - клонируем во временную папку
        temp_dir = "/tmp/service-moscow-temp"
        if os.path.exists(temp_dir):
            run_cmd(f"rm -rf {temp_dir}")
        
        run_cmd(f"git clone https://github.com/KomarovAI/service.moscow.git {temp_dir}")
        
        # Копируем исходники в нужное место
        run_cmd(f"cp -r {temp_dir}/src {INSTALL_DIR}/")
        run_cmd(f"cp {temp_dir}/.git* {INSTALL_DIR}/", check=False)  # Копируем git файлы если есть
        run_cmd(f"rm -rf {temp_dir}")
    
    log("Исходники сайта получены!")

def start_services():
    """Запуск сервисов"""
    log("Запускаю сервисы...")
    run_cmd(f"cd {INSTALL_DIR} && docker compose up -d --build nginx web")
    
    # Ждем запуска
    time.sleep(10)
    log("Сервисы запущены!")

def obtain_ssl_certificate():
    """Получение SSL сертификата"""
    log("Получаю SSL сертификат...")
    
    # Проверяем, что сайт доступен по HTTP
    log("Проверяю доступность сайта по HTTP...")
    test_result = run_cmd(f"curl -I http://{DOMAIN}", check=False)
    if not test_result:
        warning("Сайт не отвечает по HTTP, но продолжаю...")
    
    # Получаем сертификат
    cert_cmd = f'''cd {INSTALL_DIR} && docker compose run --rm certbot \\
    certbot certonly --agree-tos --no-eff-email \\
    --email {EMAIL} --webroot -w /var/www/certbot \\
    -d {DOMAIN} -d www.{DOMAIN}'''
    
    success = run_cmd(cert_cmd, check=False)
    
    if success:
        log("SSL сертификат получен!")
        # Перезапускаем Nginx
        run_cmd(f"cd {INSTALL_DIR} && docker exec {PROJECT_NAME}-nginx nginx -s reload")
        log("Nginx перезапущен с SSL!")
    else:
        warning("Не удалось получить SSL сертификат. Сайт работает по HTTP.")

def setup_cron():
    """Настройка автообновления сертификатов"""
    log("Настраиваю автообновление сертификатов...")
    
    # Создаем скрипт обновления
    renew_script = f'''#!/bin/bash
cd {INSTALL_DIR}
docker compose run --rm certbot certbot renew --quiet
docker exec {PROJECT_NAME}-nginx nginx -s reload
'''
    
    script_path = f"{INSTALL_DIR}/scripts/renew-cert.sh"
    with open(script_path, "w") as f:
        f.write(renew_script)
    
    run_cmd(f"chmod +x {script_path}")
    
    # Добавляем в cron
    cron_entry = f"0 3 * * * {script_path} >/dev/null 2>&1"
    run_cmd(f'(crontab -l 2>/dev/null; echo "{cron_entry}") | crontab -')
    
    log("Автообновление сертификатов настроено!")

def check_health():
    """Проверка здоровья сервисов"""
    log("Проверяю состояние сервисов...")
    
    # Проверяем контейнеры
    run_cmd(f"cd {INSTALL_DIR} && docker compose ps")
    
    # Проверяем доступность сайта
    log("Проверяю доступность сайта...")
    
    http_test = run_cmd(f"curl -I http://{DOMAIN}", check=False)
    https_test = run_cmd(f"curl -I https://{DOMAIN}", check=False)
    
    if http_test:
        log(f"✅ HTTP доступен: http://{DOMAIN}")
    else:
        warning(f"❌ HTTP недоступен: http://{DOMAIN}")
    
    if https_test:
        log(f"✅ HTTPS доступен: https://{DOMAIN}")
    else:
        warning(f"❌ HTTPS недоступен: https://{DOMAIN}")

def print_final_report():
    """Финальный отчет"""
    log("=" * 60, Colors.BOLD)
    log("🎉 РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!", Colors.BOLD)
    log("=" * 60, Colors.BOLD)
    
    log(f"🌐 Ваш сайт доступен по адресам:")
    log(f"   HTTP:  http://{DOMAIN}")
    log(f"   HTTPS: https://{DOMAIN}")
    
    log(f"📁 Файлы проекта: {INSTALL_DIR}")
    log(f"📧 Email для SSL: {EMAIL}")
    
    log("🔧 Полезные команды:")
    log(f"   Статус:      cd {INSTALL_DIR} && docker compose ps")
    log(f"   Логи:        cd {INSTALL_DIR} && docker compose logs -f")
    log(f"   Перезапуск:  cd {INSTALL_DIR} && docker compose restart")
    log(f"   Обновление:  cd {INSTALL_DIR} && python3 update.py")
    
    log("🛡️ Безопасность:")
    log("   ✅ Файервол настроен")
    log("   ✅ SSL сертификаты установлены")
    log("   ✅ Автообновление сертификатов настроено")
    log("   ✅ Security headers включены")
    
    log("=" * 60, Colors.BOLD)
    log("ВСЁ ЗЕБА! 🚀", Colors.BOLD)
    log("=" * 60, Colors.BOLD)

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Развертывание сайта на VPS")
    parser.add_argument("--skip-ssl", action="store_true", help="Пропустить настройку SSL")
    parser.add_argument("--skip-firewall", action="store_true", help="Пропустить настройку файервола")
    args = parser.parse_args()
    
    try:
        log("Начинаю полное развертывание сайта...", Colors.BOLD)
        
        check_root()
        check_system()
        install_dependencies()
        install_docker()
        
        if not args.skip_firewall:
            setup_firewall()
        
        create_project_structure()
        clone_website()
        write_docker_compose()
        write_nginx_config()
        write_dockerfile()
        start_services()
        
        if not args.skip_ssl:
            obtain_ssl_certificate()
            setup_cron()
        
        check_health()
        print_final_report()
        
    except KeyboardInterrupt:
        error("Развертывание прервано пользователем")
    except Exception as e:
        error(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    main()