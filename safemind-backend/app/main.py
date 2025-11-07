from fastapi import FastAPI

app  = FastAPI(title="Safemind Setup")

@app.get("/")
def root():
    return {"message": "Welcome to Safemind Setup!"}