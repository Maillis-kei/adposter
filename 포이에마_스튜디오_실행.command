#!/bin/bash
# 🕊️ 포이에마성령교회 말씀카드 & 전도지 스튜디오 원클릭 실행기
cd "$(dirname "$0")"

# Activate or create virtual environment
if [ -f ".venv/bin/python3" ]; then
    .venv/bin/python3 gui_app.py
else
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
    .venv/bin/pip install customtkinter
    .venv/bin/python3 gui_app.py
fi
