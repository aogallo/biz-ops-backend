from fastapi import FastAPI

app = FastAPI(title="API")


@app.get("/")
async def health_check():
    return {"message": "It's fine"}
