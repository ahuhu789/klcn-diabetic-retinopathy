FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MPLCONFIGDIR=/tmp/matplotlib \
    OMP_NUM_THREADS=2

RUN apt-get update && apt-get install -y --no-install-recommends libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Hugging Face Spaces run the container as uid 1000.
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

RUN pip install --index-url https://download.pytorch.org/whl/cpu torch==2.14.1 torchvision==0.29.1
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=user app ./app
COPY --chown=user models ./models
COPY --chown=user samples ./samples

USER user
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
