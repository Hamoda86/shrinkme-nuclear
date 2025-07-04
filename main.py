import time
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from twocaptcha import TwoCaptcha

TARGET_URL = "https://shrinkme.ink/KUZP"
TWO_CAPTCHA_API = "0a88f59668933a935f01996bd1624450"
VISITS = 10000
DELAY_RANGE = (10, 20)

def stealth_sync(page):
    page.evaluate("""
        () => {
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
            Intl.DateTimeFormat = () => ({resolvedOptions: () => ({timeZone: 'America/New_York'})});
        }
    """)
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    page.set_user_agent(ua)
    page.set_viewport_size({"width": 1366, "height": 768})

def solve_recaptcha(solver, site_key, url):
    try:
        print("🧩 حل reCAPTCHA...")
        captcha_id = solver.recaptcha(sitekey=site_key, url=url)
        result = solver.get_result(captcha_id)
        return result.get("code")
    except Exception as e:
        print("❌ فشل حل الكابتشا:", e)
        return None

def close_popups(page):
    selectors = ["div.popup-close", "button.close", ".modal-close", "div#popup-ad"]
    for sel in selectors:
        try:
            for el in page.query_selector_all(sel):
                el.click()
                page.wait_for_timeout(1000)
        except:
            continue

def main():
    solver = TwoCaptcha(TWO_CAPTCHA_API)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        stealth_sync(page)

        for i in range(1, VISITS + 1):
            print(f"\n🔁 زيارة رقم {i}")
            try:
                page.goto(TARGET_URL, timeout=60000)
                page.wait_for_timeout(5000)
                close_popups(page)

                recaptcha_frame = next((f for f in page.frames if "google.com/recaptcha" in f.url), None)
                if recaptcha_frame:
                    try:
                        site_key = page.eval_on_selector(".g-recaptcha", "el => el.getAttribute('data-sitekey')")
                        if site_key:
                            code = solve_recaptcha(solver, site_key, TARGET_URL)
                            if code:
                                page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML="{code}";')
                                page.evaluate("""
                                    var el = document.getElementById('g-recaptcha-response');
                                    if (el) { el.dispatchEvent(new Event('change')); }
                                """)
                                page.wait_for_timeout(5000)
                    except:
                        print("⚠️ لم يتم العثور على reCAPTCHA")

                close_popups(page)

                clicked = False
                for btn in page.query_selector_all("a, button"):
                    try:
                        text = btn.inner_text().lower()
                        if any(k in text for k in ["skip", "get link", "continue", "تخطي", "التالي", "اذهب"]):
                            btn.click()
                            print("✅ تم الضغط على زر المتابعة")
                            clicked = True
                            break
                    except:
                        continue

                if not clicked:
                    print("⚠️ لم يتم العثور على زر متابعة")

                page.wait_for_timeout(5000)
                print("✅ تمت زيارة ناجحة")

            except PlaywrightTimeoutError:
                print("⌛ مهلة منتهية")
            except Exception as e:
                print(f"❌ خطأ:", e)

            wait_time = random.randint(*DELAY_RANGE)
            print(f"⏳ انتظار {wait_time} ثانية...")
            time.sleep(wait_time)

        browser.close()

if __name__ == "__main__":
    main()
