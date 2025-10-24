# Используем легкий образ nginx для максимальной скорости
FROM nginx:alpine

# Устанавливаем рабочую директорию
WORKDIR /usr/share/nginx/html

# Удаляем стандартные файлы nginx
RUN rm -rf /usr/share/nginx/html/*

# Копируем файлы сайта
COPY ./src/ /usr/share/nginx/html/

# Копируем кастомную конфигурацию nginx для оптимизации
COPY nginx.conf /etc/nginx/nginx.conf

# Открываем порт 80
EXPOSE 80

# Команда запуска nginx
CMD ["nginx", "-g", "daemon off;"]