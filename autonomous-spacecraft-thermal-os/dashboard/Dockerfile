FROM node:18-alpine

WORKDIR /app

# Install dependencies in cache layer
COPY package.json package-lock.json* ./
RUN npm install

# Copy source code files
COPY . .

# Build production bundle of Next.js app
RUN npm run build

# Expose dashboard web port
EXPOSE 3000

# Start Next.js server
CMD ["npm", "run", "start"]
