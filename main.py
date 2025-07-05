# === تفعيل التخفي اليدوي (stealth) ===
def stealth_sync(page):
    page.evaluate("""
        () => {
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
        }
    """)

# === الكود الرئيسي ===
def main():
    solver = TwoCaptcha(TWO_CAPTCHA_API)

    with sync_playwright() as p:
        for i in range(VISITS):
            print(f"\n🔄 زيارة {i+1}/{VISITS} بدون بروكسي")

            try:
                browser = p.chromium.launch(headless=True)

                user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
                context = browser.new_context(user_agent=user_agent)
                page = context.new_page()

                stealth_sync(page)

                page.goto(TARGET_URL, timeout=60000)
                page.wait_for_timeout(5000)

                close_popups(page)

                # التحقق من وجود reCAPTCHA
                recaptcha_frame = next((f for f in page.frames if "google.com/recaptcha" in f.url), None)

                if recaptcha_frame:
                    site_key = None
                    try:
                        site_key = recaptcha_frame.eval_on_selector(
                            ".g-recaptcha", "el => el.getAttribute('data-sitekey')"
                        )
                    except:
                        pass

                    if not site_key:
                        try:
                            site_key = page.eval_on_selector(
                                ".g-recaptcha", "el => el.getAttribute('data-sitekey')"
                            )
                        except:
                            pass

                    if site_key:
                        solution = solve_recaptcha(solver, site_key, TARGET_URL)
                        page.evaluate(
                            f'document.getElementById("g-recaptcha-response").innerHTML="{solution}";'
                        )
                        page.evaluate("""
                            var el = document.getElementById('g-recaptcha-response');
                            if (el) { el.dispatchEvent(new Event('change')); }
                        """)
                        page.wait_for_timeout(5000)
                    else:
                        print("⚠️ لم يتم العثور على sitekey")

                close_popups(page)

                # الضغط على زر "تخطي" أو "استمرار"
                clicked = False
                buttons = page.query_selector_all("a, button")
                for btn in buttons:
                    try:
                        text = btn.inner_text().lower()
                        if any(k in text for k in ["skip", "get link", "continue"]):
                            btn.click()
                            print("✅ تم الضغط على زر المتابعة")
                            clicked = True
                            break
                    except:
                        continue

                if not clicked:
                    print("⚠️ لم يتم العثور على زر المتابعة")

                page.wait_for_timeout(5000)
                print("✅ الزيارة مكتملة")

            except PlaywrightTimeoutError:
                print("❌ انتهاء المهلة")
            except Exception as e:
                print(f"❌ خطأ أثناء الزيارة: {e}")
            finally:
                browser.close()
                print(f"⏳ الانتظار {DELAY_SECONDS} ثانية ...")
                time.sleep(DELAY_SECONDS)

