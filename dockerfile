# Base image olarak Python 3.11 kullan
FROM python:3.11

# Çalışma dizinini ayarla
WORKDIR /app

# PostgreSQL ve gerekli paketleri yükle
RUN apt-get update && apt-get install -y \
    postgresql postgresql-contrib wget

# PostgreSQL hizmetini başlat
RUN service postgresql start

# PostgreSQL için gerekli dosyaları ve Northwind SQL dosyasını indir
RUN wget https://raw.githubusercontent.com/pthom/northwind_psql/master/northwind.sql -O /app/northwind.sql

# PostgreSQL kullanıcı ayarlarını yap
USER postgres
RUN /etc/init.d/postgresql start && \
    psql --command "CREATE USER myuser WITH SUPERUSER PASSWORD 'mypassword';" && \
    createdb -O myuser northwind && \
    psql -U myuser -d northwind -f /app/northwind.sql

# PostgreSQL hizmetini başlat ve arka planda çalıştır
CMD service postgresql start && tail -f /dev/null

# Ana kullanıcıya geri dön
USER root

# Gerekli Python kütüphanelerini yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Çalışma komutunu ayarla
CMD ["python", "app.py"]
