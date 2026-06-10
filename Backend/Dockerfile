FROM python:3.9-slim

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias para mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements.txt primero (para aprovechar caché de Docker)
COPY requirements.txt /app/

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del proyecto
COPY . /app/

# Exponer puerto (el default de Django)
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["gunicorn", "API_recommendme.wsgi:application", "--chdir", "/app/API_recommendme", "--bind", "0.0.0.0:8000", "--workers", "3"]