from fastapi import FastAPI, Body #链接fastapi
from fastapi.middleware.cors import CORSMiddleware #前端网页能连上后端
from pipeline import run 

app = FastAPI(title="Excuse Machine API", version="1.0") #创建一个“服务”Excuse Machine API

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 允许任何网站访问
    allow_methods=["*"],          # 允许所有 HTTP 方法
    allow_headers=["*"],          # 允许所有请求头
) #任何人、任何网站都能访问我的接口

@app.get("/") #GET 接口
def health_check():
    return {"status": "ok", "message": "Excuse Machine API running."}

@app.post("/excuse")
def generate_excuse(
    data: dict = Body(...)
): #前端发一个 POST 请求，路径是 /excuse
    user_input = data.get("text", "").strip() 
    style = data.get("style", "sarcastic").strip().lower() #从前端传的 JSON 中取出字段

    if not user_input:
        return {"error": "Missing input text."}

    result = run(user_input, style)
    return result
