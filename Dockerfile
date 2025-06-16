# Utilise une image Python officielle comme base
FROM python:3.9

# Définir le répertoire de travail
WORKDIR /app

# Copier et installer les dépendances avant le reste (pour optimiser le cache)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste de l’application
COPY . .

# Exposer le port de l'API
EXPOSE 8025

# Lancer l’API avec Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8025"]
