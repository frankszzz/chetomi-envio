FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos los archivos del proyecto
COPY . .

# Crear directorio para la base de datos
RUN mkdir -p instance

# Crear base de datos y poblar datos iniciales
RUN python seed_data.py

# Exponer puerto
EXPOSE 5010

# Comando de inicio con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5010", "--workers", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
