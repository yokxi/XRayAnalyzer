# 1. Partiamo da una base Ubuntu
FROM ubuntu:noble

# Evita prompt interattivi durante la build
ENV DEBIAN_FRONTEND=noninteractive

# 2. Installiamo i tool di base e Python 3.13
RUN apt-get update && \
    apt-get install -y \
    software-properties-common \
    build-essential \
    cmake \
    git \
    curl \
    wget \
    nano \
    && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.13 python3.13-venv python3-pip

# 3. Creiamo un virtual environment globale per il container
ENV VENV_PATH=/opt/venv
RUN python3.13 -m venv $VENV_PATH

# 4. AGGIUNGIAMO IL VENV AL PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# Aggiungiamo /app al PYTHONPATH così Python trova i moduli 'src' e 'web_app'
ENV PYTHONPATH="${PYTHONPATH}:/app"
# -----------------------------

# 5. Prepariamo la cartella di lavoro
WORKDIR /app

# (A) PRIMA installiamo PyTorch CPU (Veloce e Leggero)
RUN pip install --no-cache-dir --default-timeout=100 \
    torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

# (B) POI copiamo il file dei requisiti e installiamo il resto
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ARG USER_ID=1000 
ARG USERNAME=dev
# -----------------------------

# Controlla se l'ID utente è già in uso e crea l'utente
RUN \
  ( \
    if getent passwd ${USER_ID} > /dev/null 2>&1; then \
      EXISTING_USER=$(getent passwd ${USER_ID} | cut -d: -f1); \
      echo "Trovato utente in conflitto '${EXISTING_USER}' con UID ${USER_ID}. Rimozione..."; \
      deluser --remove-home ${EXISTING_USER}; \
    fi \
  ) && \
  useradd --create-home --shell /bin/bash --uid ${USER_ID} ${USERNAME}

USER ${USERNAME}

RUN echo 'PS1="\[\033[01;34m\](docker-dev)\[\033[00m\] \[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;36m\]\w\[\033[00m\]\$ "' >> /home/${USERNAME}/.bashrc