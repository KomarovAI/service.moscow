FROM nginx:alpine

# Copy static files
COPY src/ /usr/share/nginx/html/

# Simple nginx config for static files only
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
    \
    # Static file caching \
    location ~* \.(css|js|jpg|jpeg|gif|png|svg|ico|woff|woff2|ttf)$ { \
        expires 1y; \
        add_header Cache-Control "public, immutable"; \
    } \
    \
    # Main location \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    \
    # Enable gzip \
    gzip on; \
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript; \
}' > /etc/nginx/conf.d/default.conf

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf.bak 2>/dev/null || true

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]