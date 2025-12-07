from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "CRIS API is running successfully!"}
