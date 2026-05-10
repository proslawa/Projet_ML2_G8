# Étape 1 : Build de l'application
FROM node:18-alpine AS builder

WORKDIR /app

# Copie des fichiers de configuration NPM
COPY package.json package-lock.json* ./

# Installation des dépendances (npm ci est plus sûr pour la CI/CD)
RUN npm ci

# Copie du reste du code source
COPY . .

# Build de l'application React/Vite (les fichiers iront dans /app/dist)
RUN npm run build

# Étape 2 : Serveur web léger pour la production
FROM nginx:alpine

# Copie de la configuration Nginx customisée (pour le routing de la SPA)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copie des fichiers statiques générés depuis l'étape de build
COPY --from=builder /app/dist /usr/share/nginx/html

# Exposition du port 80
EXPOSE 80

# Lancement de Nginx
CMD ["nginx", "-g", "daemon off;"]
