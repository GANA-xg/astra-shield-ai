# Use Node.js LTS
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Expose Next.js port
EXPOSE 3000

# Start Next.js development server
CMD ["npm", "run", "dev"]