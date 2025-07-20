# Start from Node base with full Debian
FROM node:20-bullseye

# Set working directory
WORKDIR /app

# Install Python, pip, and dependencies safely
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-distutils && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip (cleanly)
RUN python3 -m pip install --upgrade pip

# Copy Node.js dependencies first
COPY package*.json ./
RUN npm install

# Copy Python requirements and install them
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the full app
COPY . .

# Set environment variables
ENV MONGO_URI=replace_me

# Expose app port
EXPOSE 3000

# Run backend
CMD ["node", "server.js"]
