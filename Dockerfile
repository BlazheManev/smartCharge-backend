# Use official Node image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files separately for better caching
COPY package*.json ./

# Install production dependencies
RUN npm install --production

# Copy all other source code
COPY . .

# Expose the port your backend runs on
EXPOSE 3000

# Default ENV (can override with `-e` when running)
ENV MONGO_URI=replace_me

# Start the app
CMD ["node", "index.js"]
