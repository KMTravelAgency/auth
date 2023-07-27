from fastapi import FastApi

app = FastApi()

@app.post("/login")
def login():
    pass

@app.post("/validate")
def validate():
    pass