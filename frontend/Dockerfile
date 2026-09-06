# --- Этап 1: сборка статики ---
FROM node:20-alpine AS build

WORKDIR /app

# Аналогично backend — сначала зависимости, потом код,
# для эффективного кэширования слоёв
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# --- Этап 2: раздача собранной статики ---
FROM node:20-alpine AS serve

WORKDIR /app

RUN npm install -g serve

COPY --from=build /app/dist ./dist

EXPOSE 5173

CMD ["serve", "-s", "dist", "-l", "5173"]