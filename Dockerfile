# Usar una imagen oficial de Python ligera
FROM python:3.12-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar los requerimientos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn  # Servidor de producción para Flask

# Copiar todo el contenido del proyecto
COPY . .

# Exponer el puerto que usará Flask
EXPOSE 5000

# Comando para ejecutar la aplicación con Gunicorn (Producción)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
