FROM node:18 AS builder

# for prod
RUN git clone --branch nextjs https://github.com/danionescu0/docker-flask-mongodb-example.git app

WORKDIR /app/docker-nextjs

# Copy package files separately for better caching for dev
#COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the project only for dev env
#COPY . .


# Expose the port and start the development server
EXPOSE 3000

CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0"]