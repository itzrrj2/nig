# Base image with Python
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot files
COPY . .

# Set environment variables if needed (recommended to use .env or Docker secrets in production)
# ENV API_ID=your_api_id
# ENV API_HASH=your_api_hash
# ENV BOT_TOKEN=your_bot_token

# Run the bot
CMD ["python", "bot.py"]
