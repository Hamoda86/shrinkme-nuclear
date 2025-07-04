#!/bin/bash

# تثبيت المتطلبات
pip install -r requirements.txt

# تثبيت المتصفحات (كروميوم، فايرفوكس، إلخ)
playwright install chromium

# تشغيل السكربت
python main.py

