FROM python:3.11-slim

# Recibir build args
ARG ORS_API_KEY
ARG SECRET_KEY
ARG TIMEZONE=America/Santiago
ARG MAX_DELIVERY_DISTANCE_KM=7

# Convertir a variables de entorno
ENV ORS_API_KEY=${ORS_API_KEY}
ENV SECRET_KEY=${SECRET_KEY}
ENV TIMEZONE=${TIMEZONE}
ENV MAX_DELIVERY_DISTANCE_KM=${MAX_DELIVERY_DISTANCE_KM}
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

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
EXPOSE 4010

# Comando de inicio con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:4010", "--workers", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
