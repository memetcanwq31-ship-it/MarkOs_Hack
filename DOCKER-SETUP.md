# Docker ile Tüm Araçlara Sahip Güvenlik Konteyneri

## Docker Kurulumu

### Linux
```bash
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo usermod -aG docker $USER
```

### Mac
```bash
# Homebrew ile
brew install docker
brew install --cask docker

# Docker Desktop açın
```

### Windows
```bash
# WSL2 kurun
wsl --install

# Docker Desktop indir: https://www.docker.com/products/docker-desktop
```

## Dockerfile

```dockerfile
FROM kalilinux/kali-rolling

LABEL maintainer="Security Tools"
LABEL description="Kali Linux tüm güvenlik araçları ile"

# Sistem güncelle
RUN apt-get update && apt-get upgrade -y

# Temel araçlar
RUN apt-get install -y \
    git \
    curl \
    wget \
    nano \
    vim \
    build-essential \
    python3 \
    python3-pip \
    perl \
    ruby

# Güvenlik araçları
RUN apt-get install -y \
    nmap \
    wireshark \
    tcpdump \
    aircrack-ng \
    hashcat \
    john \
    sqlmap \
    nikto \
    hydra \
    netcat \
    metasploit-framework \
    burpsuite \
    gobuster \
    masscan \
    responder

# Python paketleri
RUN pip3 install --no-cache-dir \
    requests \
    beautifulsoup4 \
    paramiko \
    scapy \
    pexpect \
    pycryptodome \
    selenium \
    shodan

# GitHub araçları
RUN mkdir -p /opt/tools && cd /opt/tools && \
    git clone https://github.com/Lucksi/Mr-Holmes.git && \
    git clone https://github.com/laramies/theHarvester.git && \
    git clone https://github.com/aboul3la/Sublist3r.git && \
    git clone https://github.com/enablesecurity/wafw00f.git && \
    git clone https://github.com/maurosoria/dirsearch.git && \
    git clone https://github.com/commixproject/commix.git && \
    git clone https://github.com/lanmaster53/recon-ng.git && \
    git clone https://github.com/BC-SECURITY/Empire.git

# Mr Holmes bağımlılıkları
RUN cd /opt/tools/Mr-Holmes && pip3 install -r requirements.txt

# TheHarvester bağımlılıkları
RUN cd /opt/tools/theHarvester && pip3 install -r requirements.txt

# Wordlists dizini
RUN mkdir -p /wordlists && cd /wordlists && \
    wget -q https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt || true

# Alias ve konfigürasyon
RUN echo 'alias nmap-scan="nmap -sV -A"' >> /root/.bashrc && \
    echo 'alias msfconsole="msfconsole"' >> /root/.bashrc && \
    echo 'alias tools-dir="cd /opt/tools"' >> /root/.bashrc

# Çalışma dizini
WORKDIR /root

# Başlangıç komutu
CMD ["/bin/bash"]
```

## Docker Görüntüsü Oluşturma

```bash
# Dosyayı kaydet: Dockerfile (uzantı olmadan)

# Image oluştur
docker build -t security-tools:latest .

# Image oluştur (no cache)
docker build --no-cache -t security-tools:latest .

# Image listele
docker images
```

## Container Çalıştırma

### Basit başlangıç
```bash
docker run -it security-tools
```

### Yerel dosya bağlama
```bash
docker run -it -v $(pwd):/data security-tools

# Windows
docker run -it -v %cd%:/data security-tools
```

### Port yönlendirmesi (Burp Suite proxy)
```bash
docker run -it -p 8080:8080 -v $(pwd):/data security-tools
```

### Adlandırılmış container
```bash
docker run -it --name security-labs -v $(pwd):/data security-tools

# Tekrar başlat
docker start -i security-labs
```

### Network bağlantısı
```bash
# Host network
docker run -it --network host security-tools

# Belirli network
docker run -it --network my-network security-tools
```

## Docker Compose Dosyası

```yaml
version: '3.8'

services:
  security-tools:
    build:
      context: .
      dockerfile: Dockerfile
    image: security-tools:latest
    container_name: security-labs
    stdin_open: true
    tty: true
    volumes:
      - ./data:/data
      - ./wordlists:/wordlists
    ports:
      - "8080:8080"  # Burp proxy
      - "5432:5432"  # PostgreSQL (Metasploit)
    environment:
      - TERM=xterm-256color
    networks:
      - security-network

  metasploit-db:
    image: postgres:14
    container_name: msfdb
    environment:
      POSTGRES_PASSWORD: password
      POSTGRES_USER: msf
      POSTGRES_DB: msf
    volumes:
      - msf-data:/var/lib/postgresql/data
    networks:
      - security-network

volumes:
  msf-data:

networks:
  security-network:
    driver: bridge
```

## Docker Compose Kullanımı

```bash
# Services başlat
docker-compose up -d

# Container'a bağlan
docker-compose exec security-tools bash

# Logları göster
docker-compose logs -f

# Durdur
docker-compose down

# Restart
docker-compose restart
```

## Container Yönetimi

```bash
# Çalışan containerları listele
docker ps

# Tüm containerları listele
docker ps -a

# Container'e bağlan
docker exec -it container-name bash

# Container'ı durdur
docker stop container-name

# Container'ı kaldır
docker rm container-name

# Image'i kaldır
docker rmi security-tools

# CPU/Memory kullanımı
docker stats
```

## Metasploit İçin PostgreSQL Kurulumu

```bash
# Container içinde
docker exec -it msfdb psql -U msf -d msf

# Veya Metasploit DB init
msfdb init
msfdb status
```

## Örnek Workflow

```bash
# 1. Image oluştur
docker build -t security-tools .

# 2. Container başlat
docker run -it --name sec-lab -v $(pwd)/targets:/data security-tools

# 3. İçinde komut çalıştır
nmap -sV -A 192.168.1.0/24 -oN /data/results.txt

# 4. Container'dan çık
exit

# 5. Dosyaları kontrol et
cat results.txt

# 6. Container'ı temizle
docker rm sec-lab
```

## Private Registry'ye Push

```bash
# Tag oluştur
docker tag security-tools:latest myregistry.com/security-tools:latest

# Push et
docker push myregistry.com/security-tools:latest

# Pull et
docker pull myregistry.com/security-tools:latest
```

## Sorun Giderme

### Docker daemon çalışmıyor
```bash
sudo systemctl start docker
```

### Permission denied
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Disk alanı sorunu
```bash
docker system prune
docker system prune -a
```

### Network sorunu
```bash
docker network ls
docker network create my-network
```

---

⚠️ **YASAL UYARI**: Docker container'ındaki araçlar yalnızca YETKILI testler için kullanılabilir!
