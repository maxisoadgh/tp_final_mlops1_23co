FROM python:3.12-slim

RUN pip install --upgrade pip && pip install uv

WORKDIR /app

COPY dockerfiles/streamlit/requirements.txt .
RUN uv pip install --system -r requirements.txt

COPY streamlit/ .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
