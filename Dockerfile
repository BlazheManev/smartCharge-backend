# Start from Node with OS-level tools (not alpine, because it lacks apt)
FROM node:20-slim

# Set working directory
WORKDIR /app

# Install Python and pip
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install --upgrade pip

# Copy Node dependencies first
COPY package*.json ./
RUN npm install

# Copy Python requirements and install them
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the source code
COPY . .

# Set environment variables
ENV MONGO_URI=replace_me

# Expose backend port
EXPOSE 3000

# Run your Node app
CMD ["node", "server.js"]
