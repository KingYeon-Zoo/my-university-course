# Step 1: Build the Vue application
FROM node:16-alpine AS build-stage
WORKDIR /app

# Install build dependencies for native node modules (like deasync)
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package*.json ./

# Configure NPM with longer timeout and auto-retry to prevent network drops
RUN npm config set registry https://registry.npmmirror.com \
    && npm config set fetch-retry-maxtimeout 600000 \
    && npm config set fetch-retries 10 \
    && npm config set timeout 600000 \
    && npm install

# Copy all source files and build
COPY . .
RUN npm run build:prod

# Step 2: Serve using Nginx
FROM nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
