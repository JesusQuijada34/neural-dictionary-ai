from __future__ import annotations
import os
from pathlib import Path
import requests
from flask import Flask, jsonify, request
from neural_dictionary_ai.brain import Brain
from neural_dictionary_ai.memory import LexicalMemory
from neural_dictionary_ai.trainer import Trainer

DB=Path(os.getenv("NDA_DB","data/web.sqlite3")); NEURONS=Path(os.getenv("NDA_NEURONS","neurons/default.yml"))
app=Flask(__name__); memory=LexicalMemory(DB); brain=Brain(memory,NEURONS)
if os.getenv("NDA_SEED_ON_START","1")=="1" and not memory.all(): Trainer(memory,brain).teach_once()

@app.get("/")
def index():
    return """<!doctype html><html lang='es'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
    <title>Neural Dictionary AI</title><style>body{margin:0;background:#101318;color:#edf2f7;font:16px system-ui;display:flex;justify-content:center}main{width:min(850px,94vw);padding:28px}h1{font-size:24px}.chat{min-height:60vh;border:1px solid #303846;border-radius:14px;padding:18px;background:#171c24}.msg{white-space:pre-wrap;margin:12px 0;padding:12px 14px;border-radius:12px;max-width:85%}.user{margin-left:auto;background:#245b9e}.bot{background:#242b36}form{display:flex;gap:10px;margin-top:14px}input{flex:1;padding:14px;border-radius:10px;border:1px solid #46505f;background:#0f1319;color:white}button{padding:0 20px;border:0;border-radius:10px;background:#52b788;color:#07130d;font-weight:700}</style>
    <main><h1>Neural Dictionary AI</h1><div id='chat' class='chat'><div class='msg bot'>Hola. ¿En qué puedo ayudarte hoy?</div></div><form><input id='text' autocomplete='off' placeholder='Escribe un mensaje...'><button>Enviar</button></form><p id='status'></p></main><script>const c=document.querySelector('#chat'),f=document.querySelector('form'),i=document.querySelector('#text'),s=document.querySelector('#status');function add(t,k){const e=document.createElement('div');e.className='msg '+k;e.textContent=t;c.append(e);c.scrollTop=c.scrollHeight}f.onsubmit=async e=>{e.preventDefault();const t=i.value.trim();if(!t)return;add(t,'user');i.value='';s.textContent='Pensando...';try{const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:t})});const j=await r.json();add(j.response||j.error,'bot')}catch(x){add('No se pudo conectar con el servidor.','bot')}s.textContent=''};</script></html>"""

def reply(text): return brain.process(text)

@app.get("/healthz")
def health(): return jsonify({"ok":True,"service":os.getenv("NDA_SERVICE_ROLE","web"),"telegram_configured":bool(os.getenv("TELEGRAM_BOT_TOKEN")),"hf":brain.semantic.status() if brain.semantic else {"enabled":False}})

@app.post("/chat")
def chat():
    body=request.get_json(silent=True) or {}; text=body.get("text","")
    if not isinstance(text,str) or not text.strip(): return jsonify({"error":"text debe ser una cadena no vacía"}),400
    return jsonify(reply(text))

@app.post("/telegram/webhook")
def telegram_webhook():
    expected=os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if expected and request.headers.get("X-Telegram-Bot-Api-Secret-Token") != expected:return jsonify({"error":"unauthorized"}),401
    update=request.get_json(silent=True) or {}; message=update.get("message",{}); text=message.get("text"); chat_id=message.get("chat",{}).get("id")
    if not text or chat_id is None:return jsonify({"ok":True,"ignored":True})
    result=reply(text); token=os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:return jsonify({"ok":True,"response":result,"sent":False})
    try:
        response=requests.post(f"https://api.telegram.org/bot{token}/sendMessage",json={"chat_id":chat_id,"text":result["response"]},timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        app.logger.exception("Telegram sendMessage failed")
        return jsonify({"ok":False,"sent":False,"error":str(exc)}),502
    return jsonify({"ok":True,"sent":True,"chat_id":chat_id})

if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.getenv("PORT","5000")))
