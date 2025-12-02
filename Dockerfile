# Oficiální Python image
FROM python:3.12

# Nastavení pracovního adresáře
WORKDIR /app

# Zkopíruj requirements
COPY requirements.txt .

# Instalace závislostí
RUN pip install --no-cache-dir -r requirements.txt

# Zkopíruj aplikaci
COPY . .

# Expose port
EXPOSE 8000

# Spouštěcí příkaz
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
