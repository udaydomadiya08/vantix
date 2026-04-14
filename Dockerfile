# 🏛️ VANTIX MEDIA ENGINE (v1.0)
FROM python:3.11-slim

# 🛠️ INDUSTRIAL DEPENDENCIES
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    curl \
    git \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# 🎞️ IMAGEMAGICK SECURITY PATCH (Allow# 🔮 MOVIEYP PERMISSIONS FIX (Dynamic Version)
RUN find /etc/ImageMagick* -name policy.xml -exec sed -i 's/policy domain="path" rights="none" pattern="@\*"/policy domain="path" rights="read|write" pattern="@\*"/g' {} +

WORKDIR /app

# 📂 CODE TRANSFER
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🧠 NEURAL MODELS BOOTSTRAP
RUN python -m spacy download en_core_web_sm
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('universal_tagset')"

# 📂 FULL REPOSITORY CLONE (Excluding ignored via .dockerignore)
COPY . .

# 🏗️ INDUSTRIAL INFRASTRUCTURE BOOTSTRAP
RUN mkdir -p checkpoints static/videos audio video_creation api && \
    chmod -R 777 checkpoints static audio video_creation api

# 🛰️ MODEL SYNCHRONIZATION
COPY download_models.sh .
RUN chmod +x download_models.sh && ./download_models.sh

# 🌐 STARTUP
EXPOSE 7860
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
