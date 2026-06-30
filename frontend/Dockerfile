FROM nginx:1.27-alpine

# Default config-i öz proxy konfiqimizlə əvəz et
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Static fayllar
COPY index.html styles.css app.js /usr/share/nginx/html/

EXPOSE 80
