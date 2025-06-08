"""Bot pro získání a aktualizaci zákazníků"""

import sys
import time
import logging
import re
import requests
from rich.console import Console
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException
from datetime import datetime

# Nastavení logování
logging.basicConfig(filename='automation.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

cons: Console = Console()

def safe_click(driver, locator, max_attempts=120, sleep_time=0.1):
    """
    Bezpečně klikne na prvek definovaný locatorem s retry mechanismem.
    Vrací nalezený prvek, nebo vyhodí výjimku, pokud prvek není nalezen.
    """
    attempts = 0
    while attempts < max_attempts:
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(locator)
            )
            time.sleep(sleep_time)  # Pauza, aby se stránka stabilizovala
            element.click()
            return element
        except StaleElementReferenceException:
            attempts += 1
            logging.info("Stale element při safe_click na locator %s, pokus %s",
                         locator, attempts)
            time.sleep(sleep_time)
        except WebDriverException as wde:
            # Pokud se objeví jiná chyba (např. Node with given id does not belong to the document)
            attempts += 1
            logging.info(
                "WebDriverException při safe_click na locator %s, pokus %s: %s",
                locator, attempts, str(wde))
            time.sleep(sleep_time)
    raise Exception(
        f"safe_click: Nelze bezpečně kliknout na prvek {locator} po {max_attempts} pokusech.")

TOKEN = "c88580a252b9cb58d091af7603c27ed3609cb1d9"

# Adresa API
API_URL_GET = "http://localhost:8000/api/incomplete-customers/"
API_URL_UPDATE = "http://localhost:8000/api/update-customers/"

# Hlavičky s autorizací
headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json",
}

# --- 1. Získání dat ---
response = requests.get(API_URL_GET, headers=headers, timeout=5)

data = []
if response.status_code == 200:
    cons.log("Získávám data", style="blue bold")
    data = response.json()
    cons.log("Počet záznamů:", len(data))
    for item in data:
        cons.log("Objednávka:", item, style="green")
else:
    cons.log("Chyba:", response.status_code, style="red")
    cons.log(response.text, style="red")
    sys.exit()

if not data:
    cons.log("Žádná data k aktualizaci", style="yellow")
    sys.exit()


# --- 2. Funkce pro vyplnění dat pomocí Selenium ---
def selenium_foo(data) -> dict[str, list[dict]]:
    """
    Funkce pro získání údajů zákazníků pomocí Selenium.
    Přijímá data z API (seznam čísel zakázek) a vrací slovník s údaji zákazníků.
    """
    driver = None
    order_list = []

    try:
        # Inicializace Edge WebDriveru
        try:
            options = webdriver.EdgeOptions()
            # Můžete přidat další options, pokud je potřeba
            # options.add_argument('--headless') # Pro běh bez viditelného okna prohlížeče
            # options.add_argument('--disable-gpu')
            driver = webdriver.Edge(options=options)
        except WebDriverException as e:
            logging.error(f"Chyba při inicializaci WebDriveru: {e}", exc_info=True)
            cons.log(f"Chyba: Nepodařilo se spustit Microsoft Edge WebDriver. Ujistěte se, že je nainstalován a v systémové cestě (PATH). Chyba: {e}", style="red")
            return {"updates": []}
        except Exception as e:
            logging.error(f"Neočekávaná chyba při inicializaci WebDriveru: {e}", exc_info=True)
            cons.log(f"Neočekávaná chyba při startu WebDriveru: {e}", style="red")
            return {"updates": []}

        # Maximalizace okna
        driver.maximize_window()

        # Přihlášení na stránku
        try:
            driver.get('https://tms.rhenus-hd.de/Login.aspx')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'inputlogin')))

            # Zadejte své uživatelské jméno a heslo zde - POUŽIJTE PLACEHOLDERY NEBO NAČÍTÁNÍ Z KONFIGURACE
            username = 'Dalibor.Zalesak'  # <-- Zde vložte vaše uživatelské jméno nebo použijte bezpečnější metodu
            password = 'Dalzal626Z'       # <-- Zde vložte vaše heslo nebo použijte bezpečnější metodu

            if username == 'VASE_UZIVATELSKE_JMENO' or password == 'VASE_HESLO':
                cons.log("Varování: Ve skriptu nejsou nastaveny přihlašovací údaje!", style="yellow")
                logging.warning("Přihlašovací údaje nejsou ve skriptu nastaveny.")
                return {"updates": []}

            user_field = driver.find_element(By.ID, 'inputlogin')
            pass_field = driver.find_element(By.ID, 'inputpassword')

            user_field.send_keys(username)
            pass_field.send_keys(password)
            pass_field.send_keys(Keys.RETURN)

            # Čekání na přesměrování po přihlášení
            WebDriverWait(driver, 10).until(EC.url_contains("Default.aspx?c=Start&interface=new"))
            logging.info("Úspěšné přihlášení.")
            cons.log("Úspěšné přihlášení do systému", style="green")

        except Exception as e:
            logging.error(f"Chyba při přihlašování: {e}", exc_info=True)
            cons.log(f"Chyba při přihlašování: {e}", style="red")
            if driver: driver.quit()
            return {"updates": []}

        first_run = True  # Abychom ošetřili otevírání filtru při prvním běhu
        total_items = len(data)
        cons.log(f"Zpracovávám {total_items} zakázek", style="blue bold")

        for index, item in enumerate(data):
            try:
                cislo_zasilky = str(item)  # Předpokládáme, že data z API jsou čísla zakázek
                cislo_zasilky_s_hvezdickou = f"{cislo_zasilky}"
                logging.info(f"Číslo zásilky: {cislo_zasilky}")
                cons.log(f"Zpracovávám zakázku {index+1}/{total_items}: {cislo_zasilky}", style="blue")

                # Najetí myší na záložku "zakázky"
                menu_item = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//li[contains(@onmouseover, \"Menu.open('TMS', this, 'Zakázky')\")]"))
                )
                actions = webdriver.ActionChains(driver)
                actions.move_to_element(menu_item).perform()

                # Kliknutí na položku "zakázky" - POUŽITO SAFE_CLICK
                logging.info("Klikám na záložku 'Zakázky'")
                safe_click(driver, (By.XPATH, "//li[contains(@onclick, 'location.href') and contains(text(), 'Zakázky')]"))

                WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, 'body'))) # Počkat na načtení těla stránky

                if first_run:
                    # Otevření filtru při prvním průchodu - POUŽITO SAFE_CLICK
                    logging.info("Otevírám filtr (první spuštění).")
                    try:
                        safe_click(driver, (By.ID, 'iwartikelverwaltungAuftraegeAuftraegeFilterOrderByPagingLabel'))
                        logging.info("Filtr otevřen.")
                    except Exception as e:
                        logging.error(f"Nepodařilo se kliknout na tlačítko filtru: {e}", exc_info=True)
                        cons.log(f"Chyba: Nepodařilo se otevřít filtr. Pokračuji bez filtru? (Chyba: {e})", style="yellow")
                    first_run = False

                # Vyplnění čísla zakázky
                logging.info(f"Vyplňuji číslo zásilky do filtru: {cislo_zasilky_s_hvezdickou}")
                order_input = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.ID, 'iwartikelverwaltungAuftraegeAuftraegeFilterString,0')) # Čekat na viditelnost
                )
                # Použití JavaScriptu pro jistotu vyčištění a zadání hodnoty
                driver.execute_script("arguments[0].value = '';", order_input) # Vyčistit pole
                order_input.send_keys(cislo_zasilky_s_hvezdickou)

                # Stisknutí tlačítka "aktualizovat" - POUŽITO SAFE_CLICK
                logging.info("Klikám na 'Aktualizovat'")
                safe_click(driver, (By.ID, 'iwartikelverwaltungAuftraegeAuftraegeSubmitChanges'))
                # Přidat krátké čekání nebo čekání na zmizení/objevení nějakého elementu po aktualizaci
                time.sleep(1) # Jednoduché čekání, lepší je explicitní čekání na výsledek

                # Kliknutí na "detailní náhled" - POUŽITO SAFE_CLICK
                logging.info("Klikám na 'Detailní náhled'")
                safe_click(driver, (By.ID, 'iwartikelverwaltungAuftraegeAuftraegeBearbeitenDetail'))

                # Kliknutí na záložku "Adresa" - POUŽITO SAFE_CLICK
                logging.info("Klikám na záložku 'Adresa'")
                safe_click(driver, (By.XPATH, "//a[contains(text(), 'Adresa')]"))

                # Extrakce dat z elementu s id "AuftragDetailansicht_AuftragsanschriftLabel"
                logging.info("Extrahuji adresu.")
                adresa_element = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.ID, "AuftragDetailansicht_AuftragsanschriftLabel"))
                )
                adresa_html = adresa_element.get_attribute('innerHTML')
                lines = adresa_html.split('<br>')
                fields = {}
                for line in lines:
                    match = re.match(r'<b>([^<]+):</b>\s*(.*)', line)
                    if match:
                        field_name = match.group(1).strip().replace('&nbsp;', ' ') # Nahradit &nbsp;
                        value = match.group(2).strip().replace('&nbsp;', ' ')
                        fields[field_name] = value
                logging.info(f"Extrahovaná data: {fields}")

                # Vytvoření slovníku s daty pro danou zakázku ve formátu, který očekává API
                customer_data = {
                    cislo_zasilky: {
                        "name": fields.get('Jméno zákazníka', ''),
                        "street": fields.get('Ulice', ''),
                        "zip_code": fields.get('PSČ', ''),
                        "city": fields.get('Obec', ''),
                        "phone": fields.get('Telefon1', ''),
                        "email": fields.get('E-mail', '')
                    }
                }
                order_list.append(customer_data)
                cons.log(f"Data pro zakázku {cislo_zasilky} získána", style="green")

            except Exception as e:
                logging.error(f"Chyba při zpracování zásilky {cislo_zasilky} (index {index}): {e}", exc_info=True)
                cons.log(f"Chyba při zpracování zakázky {cislo_zasilky}: {e}", style="red")
                # Zde můžu implementovat logiku pro opakování pokusu pro daný řádek
                # nebo jednoduše pokračovat dalším řádkem (aktuální chování)
                # Pokud chyba nastane před navigací zpět, je potřeba zajistit návrat na správné místo
                try:
                    # Pokus o návrat na stránku se zakázkami pro další iteraci
                    driver.get("https://tms.rhenus-hd.de/Default.aspx?c=TMS&interface=new&page=Auftrag") # URL stránky se zakázkami
                except Exception as nav_err:
                    logging.error(f"Nepodařilo se navigovat zpět po chybě: {nav_err}")
                    cons.log("Kritická chyba: Nepodařilo se obnovit stav po chybě.", style="red")
                    break # Ukončí smyčku

        cons.log(f"Zpracování dokončeno. Získáno {len(order_list)} záznamů z {total_items} zakázek.", style="green bold")

    except Exception as e:
        # Zachytí chyby, které nastaly mimo hlavní smyčku (např. při inicializaci, přihlášení)
        logging.error(f"Závažná chyba ve skriptu mimo hlavní smyčku: {e}", exc_info=True)
        cons.log(f"Závažná chyba ve skriptu: {e}", style="red")

    finally:
        # Ukončení WebDriveru
        if driver:
            try:
                driver.quit()
                logging.info("WebDriver úspěšně ukončen.")
            except Exception as qe:
                logging.error(f"Chyba při ukončování WebDriveru: {qe}", exc_info=True)

    return {"updates": order_list}


# --- 3. Odeslání aktualizací ---
payload = selenium_foo(data)
cons.log("Odesílám payload:", payload)

try:
    response = requests.post(API_URL_UPDATE, json=payload, headers=headers, timeout=5)
    cons.log("Status code:", response.status_code)
    cons.log("Odpověď serveru:", response.json())
except Exception as e:
    cons.log(f"Chyba při POST: {e}", style="red")
