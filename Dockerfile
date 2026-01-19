# Sử dụng image Python chính thức
FROM python:3.10-slim

# Cài đặt dependencies hệ thống cho mysqlclient
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements và install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code dự án vào container
COPY . .

# Expose port 8000 (Django default)
EXPOSE 8000

# Default command (sẽ được override bởi docker-compose.yml)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
