from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def root_url():
    return {"msg":"hello" }

@app.get('/sub')
def internal_url():
    return {"msg":"hello" }