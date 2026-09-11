FROM node:20-alpine AS build

WORKDIR /app

ARG VITE_API_URL=/api/v1/
ENV VITE_API_URL=${VITE_API_URL}

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Финальный этап — не запускающийся сервис, просто контейнер,
# из которого docker compose скопирует dist/ в shared volume.
# Используем минимальный alpine, команда ничего не делает — 
# существование контейнера не нужно после копирования файла.
FROM alpine:3.20
COPY --from=build /app/dist /dist
