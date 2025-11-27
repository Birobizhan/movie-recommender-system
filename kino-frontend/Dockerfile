# movie-recommender-system/kino-frontend/Dockerfile

FROM node:20-alpine

WORKDIR /app

# Копируем package.json из папки kino-frontend
COPY package.json package-lock.json ./

RUN npm install

# Копируем исходный код фронта
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]