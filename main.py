import os
from fastapi import FastAPI, Request
import requests

app = FastAPI()

DEEPSEEK_API_URL = "https://api.aiai.by/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.api_route("/", methods=["GET", "HEAD", "POST"])
async def main(request: Request):
    if request.method in ["GET", "HEAD"]:
        return {"status": "ok"}

    try:
        body = await request.json()
        user_text = body["request"]["original_utterance"]
        is_new_session = body["session"]["new"]
    except Exception:
        return {"status": "error"}

    if is_new_session or not user_text.strip():
        return {
            "version": body.get("version", "1.0"),
            "session": body.get("session", {}),
            "response": {
                "end_session": False,
                "text": "Привет! Я готов к общению. Задай свой вопрос."
            }
        }

    try:
        response = requests.post(
            DEEPSEEK_API_URL,
            headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
            json={
                "model": "gpt-4o-mini", # Самая дешевая модель
                "messages": [{"role": "user", "content": user_text}],
                "max_tokens": 200 # Увеличили лимит, чтобы ответы были длиннее
            },
            timeout=4 
        )
        
        data = response.json()
        
        if isinstance(data, list):
            answer = data[0]["choices"][0]["message"]["content"]
        else:
            answer = data["choices"][0]["message"]["content"]
            
    except requests.exceptions.Timeout:
        answer = "Извини, я задумался надолго. Давай попробуем еще раз?"
    except Exception as e:
        print("ОШИБКА:", e)
        answer = "Извини, произошла ошибка при обработке запроса."

    return {
        "version": body.get("version", "1.0"),
        "session": body.get("session", {}),
        "response": {
            "end_session": False,
            "text": answer
        }
    }
