from fastapi import FastAPI

app = FastAPI(title="TP MLOps API")

@app.get("/health")
def health():
    return {"status": "ok"}
