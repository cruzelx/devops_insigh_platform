FROM python:3.12-slim

WORDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

# just a placeholder to keep the container running
CMD ["tail","-f","/dev/null"]