FROM python:3.12-slim

RUN pip install --upgrade pip && pip install uv

WORKDIR /app

# requirements.txt se copia desde el contexto de build (directorio padre)
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

RUN mkdir -p /home/notebooks
WORKDIR /home/notebooks

EXPOSE 8888

CMD ["jupyter", "lab", \
     "--ip=0.0.0.0", \
     "--port=8888", \
     "--no-browser", \
     "--allow-root", \
     "--notebook-dir=/home/notebooks", \
     "--NotebookApp.token=", \
     "--NotebookApp.password="]
