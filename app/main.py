from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def test():
    return {"Message": "Just Testing it"}