# استخدم صورة تحتوي على Python + Playwright
FROM mcr.microsoft.com/playwright/python:v1.53.0

# إعداد مجلد العمل
WORKDIR /app

# نسخ ملفات المشروع
COPY . .

# تثبيت المتطلبات
RUN pip install -r requirements.txt

# نسخ المتصفحات إذا مو موجودة
RUN playwright install --with-deps

# أمر التشغيل
CMD ["python", "main.py"]
