# --- Этап 1: Сборка приложения ---
FROM node:18-alpine as builder

WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальной код
COPY . .

# Сборка приложения (создание production-ready файлов)
RUN npm run build

# --- Этап 2: Запуск через Nginx ---
FROM nginx:alpine

# Копируем собранные файлы из этапа builder в директорию Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Копируем кастомный конфиг Nginx (если нужно)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Nginx по умолчанию слушает порт 80
EXPOSE 80

# Запуск Nginx
CMD ["nginx", "-g", "daemon off;"]
