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

def reply(text): return brain.process(text)

@app.get("/healthz")
def health(): return jsonify({"ok":True,"service":"neural-dictionary-ai","hf":brain.semantic.status() if brain.semantic else {"enabled":False}})

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
    response=requests.post(f"https://api.telegram.org/bot{token}/sendMessage",json={"chat_id":chat_id,"text":result["response"]},timeout=15)
    response.raise_for_status(); return jsonify({"ok":True,"sent":True})

if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.getenv("PORT","5000")))
