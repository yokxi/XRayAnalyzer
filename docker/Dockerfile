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
    libgl1 \
    libglib2.0-0 \
    && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    # 
    apt-get install -y python3.13 python3.13-venv python3-pip

# 3. Creiamo un virtual environment globale per il container
ENV VENV_PATH=/opt/venv
RUN python3.13 -m venv $VENV_PATH

# 4. AGGIUNGIAMO IL VENV AL PATH
# I comandi 'python' e 'pip' useranno automaticamente questo venv, senza 'source activate'
ENV PATH="$VENV_PATH/bin:$PATH"

# 5. Prepariamo la cartella di lavoro e installiamo le dipendenze
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# NUOVO STEP: Installazione specifica per PyTorch con CUDA 13.0
# Questo usa l'indice di pacchetti specifico per la versione CUDA
#DA COMMENTARE SE IL PROPRIO COMPUTER NON HA UNA GPU NVIDIA
RUN pip install --no-cache-dir torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cu130

# 6. Creiamo un utente 'dev' con lo stesso ID del tuo utente host
ARG USER_ID=1000
ARG USERNAME=dev

# Controlla se l'ID utente (passato come ${USER_ID}) è già in uso.
# Se sì, cancella l'utente esistente
# prima di creare quello nuovo. Questo evita l'errore "UID not unique".
RUN \
  ( \
    if getent passwd ${USER_ID} > /dev/null 2>&1; then \
      EXISTING_USER=$(getent passwd ${USER_ID} | cut -d: -f1); \
      echo "Trovato utente in conflitto '${EXISTING_USER}' con UID ${USER_ID}. Rimozione..."; \
      deluser --remove-home ${EXISTING_USER}; \
    fi \
  ) && \
  useradd --create-home --shell /bin/bash --uid ${USER_ID} ${USERNAME}

# Assegna la proprietà della cartella venv all'utente 'dev'
RUN chown -R ${USERNAME}:${USERNAME} $VENV_PATH

USER ${USERNAME}

RUN echo 'PS1="\[\033[01;34m\](docker-dev)\[\033[00m\] \[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;36m\]\w\[\033[00m\]\$ "' >> /home/${USERNAME}/.bashrc