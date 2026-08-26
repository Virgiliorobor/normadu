FROM nginx:alpine

# Visor autocontenido: se sirve en / y en /normativa.html
COPY normativa.html /usr/share/nginx/html/index.html
COPY normativa.html /usr/share/nginx/html/normativa.html

# JSON estructurado para consumo por agentes: /data/index.json, /data/rgce.json, ...
COPY data /usr/share/nginx/html/data

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
