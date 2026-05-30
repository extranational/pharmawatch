FROM oven/bun:latest

WORKDIR /app

# Copy dependency files
COPY package.json bun.lockb ./

# Install dependencies
RUN bun install

# Copy the rest of the application
COPY . .

# Set environment
ENV PATH="/app/node_modules/.bin:$PATH"

CMD ["bun", "run", "dev"]