# Используем легкий образ nginx для максимальной скорости
FROM nginx:alpine

# Устанавливаем рабочую директорию
WORKDIR /usr/share/nginx/html

# Удаляем стандартные файлы nginx
RUN rm -rf /usr/share/nginx/html/*

# Копируем файлы сайта
COPY ./src/ /usr/share/nginx/html/

# Настраиваем права для безопасности
# Не меняем владельца, так как nginx:alpine уже создан правильно
# Пользователь nginx (UID 101) уже существует в образе
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Переключаемся на непривилегированного пользователя
USER nginx

# Открываем порт 80
EXPOSE 80

# Команда запуска nginx
CMD ["nginx", "-g", "daemon off;"]