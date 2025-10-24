from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pipeline import run

app = FastAPI(title="Excuse Machine API", version="1.0")

# —— 跨域设置：允许前端本地调后端 ——
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 可改成你前端的域名
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    """简单健康检查"""
    return {"status": "ok", "message": "Excuse Machine API running."}


@app.post("/excuse")
def generate_excuse(
    data: dict = Body(...)
):
    """
    主接口：
    接收前端传来的 {"text": "...", "style": "creator"}，
    调 pipeline.run()，
    返回生成结果。
    """
    user_input = data.get("text", "").strip()
    style = data.get("style", "sarcastic").strip().lower()

    if not user_input:
        return {"error": "Missing input text."}

    result = run(user_input, style)
    return result
