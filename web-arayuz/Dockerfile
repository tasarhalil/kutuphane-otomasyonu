# Aşama 1: derleme
FROM node:20-alpine AS derleme
WORKDIR /uygulama
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

# Aşama 2: Nginx ile sunum
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=derleme /uygulama/dist /usr/share/nginx/html
EXPOSE 80
