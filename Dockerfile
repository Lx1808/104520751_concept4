# Use an official Python runtime as a parent image
# 使用官方的 python 镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目依赖文件
COPY requirements.txt /app/requirements.txt

# 复制代码
COPY ./Backend /app

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个项目到容器中
COPY . /app

# Make port 8000 available to the world outside this container
EXPOSE 8080

# Set environment variables
ENV MONGO_URI="mongodb+srv://lx941008:lx79112661@cluster0.16uwt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
ENV SECRET_KEY="LINOH=921893u239OIefiowja"

# Run app.py when the container launches
CMD ["uvicorn", "Backend.main:app", "--host", "0.0.0.0", "--port", "8080"]