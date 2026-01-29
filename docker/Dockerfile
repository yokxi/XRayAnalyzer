# 1. Base Ubuntu
FROM ubuntu:noble

# Evita prompt interattivi durante la build
ENV DEBIAN_FRONTEND=noninteractive

# 2. Tool di base e Python 3.12 (nativo in Ubuntu Noble)
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
    python3.12 \
    python3.12-venv \
    python3-pip \
    && \
    rm -rf /var/lib/apt/lists/*

# 3. Virtual environment globale per il container
ENV VENV_PATH=/opt/venv
RUN python3.12 -m venv $VENV_PATH

# 4. Aggiunta di VENV al PATH, i comandi 'python' e 'pip' useranno automaticamente questo venv
ENV PATH="$VENV_PATH/bin:$PATH"

# 5. Preparazione della cartella di lavoro e installazione dipendenze
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Se si specifica DEVICE=gpu durante la build, si installerà PyTorch con supporto CUDA
# Se non viene specificato, si installerà la versione CPU
ARG DEVICE=cpu
RUN if [ "$DEVICE" = "gpu" ]; then \
        echo "Installazione versione GPU (CUDA 13.0)..." && \
        pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130; \
    else \
        echo "Installazione versione CPU..." && \
        pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu; \
    fi

# 6. Creazione un utente 'dev' con lo stesso ID dell'utente host
ARG USER_ID=1000
ARG USERNAME=dev

# Controlla se l'ID utente (passato come ${USER_ID}) è già in uso.
# Se sì, cancella l'utente esistente prima di creare quello nuovo. Questo evita l'errore "UID not unique".
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