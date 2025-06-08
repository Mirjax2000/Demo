import logging
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException
import customtkinter as ctk
from tkinter import Tk, StringVar, filedialog
from threading import Thread
from datetime import datetime
import queue
from threading import Event
from openpyxl import Workbook
import re

# Nastavení logování – chyby se zapíší do souboru automation.log
logging.basicConfig(filename='automation.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')


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


ctk.set_default_color_theme("dark-blue")
default_font_color = "Goldenrod"
default_hover_color = "grey21"
border_width = 1
border_color = "DarkRed"
font: tuple = ("Century Gothic", 22, "bold")

# Funkce pro výpočet zbývajícího času
def calculate_remaining_time(start_time, processed, total):
    elapsed_time = datetime.now() - start_time
    avg_time_per_item = elapsed_time / (processed if processed > 0 else 1)
    remaining_items = total - processed
    remaining_time = avg_time_per_item * remaining_items
    return remaining_time

# Vytvoření GUI
def create_gui(total_items, on_close):
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")
    root = ctk.CTk()
    root.title("Progress Tracker")

    # Umístění GUI do pravého horního rohu
    root.geometry("+1200+100")
    root.attributes("-topmost", True)  # GUI bude vždy navrchu
    # root.iconbitmap("CustomTkinter_icon_Windows.ico")  # Pokud máš ikonu, můžeš ji zde přidat

    # Počítadlo
    progress_var = StringVar(value=f"0/{total_items} Completed")
    progress_label = ctk.CTkLabel(master=root, textvariable=progress_var, font=font)
    progress_label.pack(pady=10)

    # Procenta
    percent_var = StringVar(value="0%")
    percent_label = ctk.CTkLabel(master=root, textvariable=percent_var, font=font)
    percent_label.pack(pady=10)

    # Procentní progress bar
    progress_bar = ctk.CTkProgressBar(master=root, width=300)
    progress_bar.pack(pady=10)
    progress_bar.set(0)

    # Zbývající čas
    remaining_time_var = StringVar(value="Calculating...")
    remaining_time_label = ctk.CTkLabel(master=root, textvariable=remaining_time_var, font=font)
    remaining_time_label.pack(pady=10)

    # Tlačítko pro ukončení skriptu (deaktivováno do dokončení)
    exit_button = ctk.CTkButton(master=root, text="Ukončit skript", state='disabled', font=font, text_color=default_font_color, border_width=border_width, border_color=border_color, hover_color=default_hover_color, command=on_close, width=250, height=50)
    exit_button.pack(pady=10)

    return root, progress_var, percent_var, progress_bar, remaining_time_var, exit_button

# Aktualizace GUI během zpracovávání
def update_gui(processed, total, start_time, progress_var, percent_var, progress_bar, remaining_time_var):
    progress_var.set(f"{processed}/{total} Completed")
    percent = int((processed / total) * 100)
    percent_var.set(f"{percent}%")
    progress_bar.set(percent / 100)
    remaining_time = calculate_remaining_time(start_time, processed, total)
    remaining_time_var.set(f"Remaining Time: {str(remaining_time).split('.')[0]}")

# Funkce pro zapisování do Excelu ve druhém vlákně
def excel_writer(data_queue, stop_event, output_file):
    # Inicializace Excel souboru
    wb = Workbook()
    ws = wb.active
    ws.title = "Výsledky"
    ws.append(["CisloZasilky", "JmenoZakaznika", "Ulice", "PSC", "Mesto", "Stat", "Telefon1", "E-Mail"])  # Upravené hlavičky sloupců
    try:
        wb.save(output_file)
    except Exception as e:
        logging.error(f"Chyba při úvodním uložení Excel souboru '{output_file}': {e}", exc_info=True)
        print(f"Chyba při úvodním uložení Excel souboru: {e}")
        stop_event.set() # Signalizuj chybu ostatním vláknům
        return # Ukonči funkci, pokud nelze soubor vytvořit/uložit

    while not stop_event.is_set() or not data_queue.empty():
        try:
            data = data_queue.get(timeout=1)
            cislo_zasilky = data.get('CisloZasilky', '')
            jmeno_zakaznika = data.get('JmenoZakaznika', '')
            ulice = data.get('Ulice', '')
            psc = data.get('PSC', '')
            mesto = data.get('Mesto', '')
            stat = data.get('Stat', '')
            telefon1 = data.get('Telefon1', '')
            email = data.get('E-Mail', '')
            ws.append([cislo_zasilky, jmeno_zakaznika, ulice, psc, mesto, stat, telefon1, email])
            # Ukládej méně často, např. po každých 10 záznamech nebo po určitém čase
            # Časté ukládání může zpomalovat a zvyšovat riziko konfliktu
            # Pro jednoduchost necháme původní logiku, ale zvažte optimalizaci
            wb.save(output_file)
            data_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            logging.error(f"Chyba při zápisu do Excelu '{output_file}': {e}", exc_info=True)
            print(f"Chyba při zápisu do Excelu: {e}")
            # Můžete zvážit logiku opakování zápisu nebo přeskočení záznamu

# Funkce pro přihlášení na web, extrakci dat z tabulky a jejich uložení do Excelu
def run_script(progress_var, percent_var, progress_bar, remaining_time_var, exit_button, data_queue, stop_event, excel_file):
    driver = None
    try:
        # Načtení dat z Excelu
        try:
            df = pd.read_excel(excel_file)
            print("Názvy sloupců ve vašem Excel souboru:", df.columns.tolist())
        except FileNotFoundError:
            logging.error(f"Vstupní Excel soubor nebyl nalezen: {excel_file}")
            print(f"Chyba: Vstupní Excel soubor nebyl nalezen: {excel_file}")
            stop_event.set()
            return
        except Exception as e:
            logging.error(f"Chyba při čtení Excel souboru '{excel_file}': {e}", exc_info=True)
            print(f"Chyba při čtení vstupního Excel souboru: {e}")
            stop_event.set()
            return

        # Inicializace Edge WebDriveru
        try:
            options = webdriver.EdgeOptions()
            # Můžete přidat další options, pokud je potřeba
            # options.add_argument('--headless') # Pro běh bez viditelného okna prohlížeče
            # options.add_argument('--disable-gpu')
            driver = webdriver.Edge(options=options)
        except WebDriverException as e:
             logging.error(f"Chyba při inicializaci WebDriveru: {e}", exc_info=True)
             print(f"Chyba: Nepodařilo se spustit Microsoft Edge WebDriver. Ujistěte se, že je nainstalován a v systémové cestě (PATH). Chyba: {e}")
             stop_event.set()
             return
        except Exception as e:
             logging.error(f"Neočekávaná chyba při inicializaci WebDriveru: {e}", exc_info=True)
             print(f"Neočekávaná chyba při startu WebDriveru: {e}")
             stop_event.set()
             return

        # Maximalizace okna
        driver.maximize_window()

        # Přihlášení na stránku
        try:
            driver.get('https://tms.rhenus-hd.de/Login.aspx')
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'inputlogin')))

            # Zadejte své uživatelské jméno a heslo zde - POUŽIJTE PLACEHOLDERY NEBO NAČÍTÁNÍ Z KONFIGURACE
            username = 'Dalibor.Zalesak'  # <-- Zde vložte vaše uživatelské jméno nebo použijte bezpečnější metodu
            password = 'Dalzal626Z'              # <-- Zde vložte vaše heslo nebo použijte bezpečnější metodu

            if username == 'VASE_UZIVATELSKE_JMENO' or password == 'VASE_HESLO':
                 print("Varování: Ve skriptu nejsou nastaveny přihlašovací údaje!")
                 logging.warning("Přihlašovací údaje nejsou ve skriptu nastaveny.")
                 # Můžete zde skript ukončit nebo pokračovat, pokud je to žádoucí

            user_field = driver.find_element(By.ID, 'inputlogin')
            pass_field = driver.find_element(By.ID, 'inputpassword')

            user_field.send_keys(username)
            pass_field.send_keys(password)
            pass_field.send_keys(Keys.RETURN)

            # Čekání na přesměrování po přihlášení
            WebDriverWait(driver, 10).until(EC.url_contains("Default.aspx?c=Start&interface=new"))
            logging.info("Úspěšné přihlášení.")

        except Exception as e:
            logging.error(f"Chyba při přihlašování: {e}", exc_info=True)
            print(f"Chyba při přihlašování: {e}")
            stop_event.set()
            if driver: driver.quit()
            return

        first_run = True  # Abychom ošetřili otevírání filtru při prvním běhu

        total_items = len(df)
        start_time = datetime.now()

        for index, row in df.iterrows():
            if stop_event.is_set():
                logging.info("Skript byl externě zastaven.")
                break  # Umožňuje bezpečné ukončení

            processed_items = index + 1
            logging.info(f"Zpracovávám položku {processed_items}/{total_items}.")

            try:
                cislo_zasilky = str(row['CisloZasilky'])  # Ujistěte se, že název sloupce odpovídá vašemu Excelu
                cislo_zasilky_s_hvezdickou = f"{cislo_zasilky}"
                logging.info(f"Číslo zásilky: {cislo_zasilky}")

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
                         print(f"Chyba: Nepodařilo se otevřít filtr. Pokračuji bez filtru? (Chyba: {e})")
                         # Zvážit, zda pokračovat nebo ukončit skript, pokud je filtr kritický
                         # stop_event.set(); break # Příklad ukončení
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

                # Vložení dat do fronty pro zápis do Excelu
                data_to_write = {
                    'CisloZasilky': cislo_zasilky,
                    'JmenoZakaznika': fields.get('Jméno zákazníka', ''), # Použití přesných názvů polí z HTML
                    'Ulice': fields.get('Ulice', ''),
                    'PSC': fields.get('PSČ', ''),
                    'Mesto': fields.get('Obec', ''),
                    'Stat': fields.get('Stát', ''),
                    'Telefon1': fields.get('Telefon1', ''),
                    'E-Mail': fields.get('E-mail', '')
                }
                data_queue.put(data_to_write)
                logging.info(f"Data pro {cislo_zasilky} vložena do fronty.")

                # Aktualizace GUI
                update_gui(processed_items, total_items, start_time, progress_var, percent_var, progress_bar, remaining_time_var)

            except Exception as e:
                 logging.error(f"Chyba při zpracování zásilky {cislo_zasilky} (index {index}): {e}", exc_info=True)
                 print(f"Chyba při zpracování řádku {index + 1} (Zásilka: {cislo_zasilky}): {e}. Pokračuji dalším řádkem.")
                 # Zde můžu implementovat logiku pro opakování pokusu pro daný řádek
                 # nebo jednoduše pokračovat dalším řádkem (aktuální chování)
                 # Pokud chyba nastane před navigací zpět, je potřeba zajistit návrat na správné místo
                 try:
                     # Pokus o návrat na stránku se zakázkami pro další iteraci
                     driver.get("URL_STRANKY_SE_ZAKAZKAMI") # Nahraďte skutečnou URL, pokud je známa
                     # nebo zkuste navigovat zpět pomocí tlačítek, pokud existují
                 except Exception as nav_err:
                     logging.error(f"Nepodařilo se navigovat zpět po chybě: {nav_err}")
                     print("Kritická chyba: Nepodařilo se obnovit stav po chybě. Ukončuji skript.")
                     stop_event.set()
                     break # Ukončí smyčku


        # Po zpracování všech zakázek aktivuj tlačítko pro ukončení
        if not stop_event.is_set(): # Aktivuj jen pokud skript nebyl zastaven chybou nebo uživatelem
             exit_button.configure(state='normal')
             logging.info("Zpracování dokončeno.")
        else:
             logging.warning("Skript byl ukončen před dokončením všech položek.")


    except Exception as e:
        # Zachytí chyby, které nastaly mimo hlavní smyčku (např. při inicializaci, přihlášení)
        logging.error(f"Závažná chyba ve skriptu mimo hlavní smyčku: {e}", exc_info=True)
        print(f"Závažná chyba ve skriptu: {e}")
        stop_event.set() # Signalizuj chybu ostatním vláknům


    finally:
        # Ukončení WebDriveru
        if driver:
            try:
                driver.quit()
                logging.info("WebDriver úspěšně ukončen.")
            except Exception as qe:
                logging.error(f"Chyba při ukončování WebDriveru: {qe}", exc_info=True)
        # Signalizace, že hlavní vlákno skončilo (i v případě chyby)
        stop_event.set()
        logging.info("Hlavní vlákno (run_script) bylo ukončeno.")

# Funkce pro spuštění skriptu ve vlákně
def start_script_thread(progress_var, percent_var, progress_bar, remaining_time_var, exit_button, data_queue, stop_event, excel_file):
    thread = Thread(target=run_script, args=(progress_var, percent_var, progress_bar, remaining_time_var, exit_button, data_queue, stop_event, excel_file))
    thread.daemon = True # Nastavení vlákna jako daemon, aby se ukončilo s hlavním programem, pokud GUI zavřeme
    thread.start()
    logging.info("Spouštěcí vlákno (start_script_thread) bylo spuštěno.")

# Funkce pro spuštění zapisovacího vlákna
def start_writer_thread(data_queue, stop_event, output_file):
    writer_thread = Thread(target=excel_writer, args=(data_queue, stop_event, output_file), daemon=True)
    writer_thread.start()
    logging.info("Zapisovací vlákno (excel_writer) bylo spuštěno.")
    return writer_thread

# Funkce pro bezpečné ukončení
def on_gui_close(root, stop_event, data_queue, writer_thread):
    logging.info("Zavírání GUI iniciováno uživatelem.")
    print("Ukončování skriptu...")
    stop_event.set() # Signalizuj ostatním vláknům, aby skončily
    # Můžete přidat krátké čekání, aby vlákna stihla zareagovat
    # time.sleep(1)
    # Čekání na dokončení zápisu zbývajících dat
    print("Čekání na dokončení zápisu do Excelu...")
    data_queue.join() # Čeká, dokud nejsou všechny položky z fronty zpracovány (task_done())
    if writer_thread and writer_thread.is_alive():
         writer_thread.join(timeout=5) # Počká na ukončení zapisovacího vlákna max 5 sekund
         if writer_thread.is_alive():
             logging.warning("Zapisovací vlákno se neukončilo v časovém limitu.")
    print("Skript ukončen.")
    root.quit() # Ukončí hlavní smyčku Tkinter


# Hlavní část pro spuštění GUI
if __name__ == "__main__":
    logging.info("="*20 + " Spuštění skriptu " + "="*20)

    # Vytvoření dialogového okna pro výběr vstupního Excelu
    root_tk = Tk()
    root_tk.withdraw()  # Skryje hlavní okno Tkinter
    excel_file = filedialog.askopenfilename(title="Vyberte vstupní Excel soubor", filetypes=[("Excel Files", "*.xlsx;*.xls")])
    root_tk.destroy()

    if not excel_file:
        print("Nebyl vybrán žádný vstupní soubor. Skript se ukončí.")
        logging.warning("Nebyl vybrán vstupní Excel soubor.")
        exit()
    logging.info(f"Vybrán vstupní soubor: {excel_file}")

    # Načtení dat z Excelu pro získání počtu položek (pouze pro GUI, hlavní načtení je ve vlákně)
    try:
        df_check = pd.read_excel(excel_file)
        total_items = len(df_check)
        del df_check # Uvolnění paměti
        logging.info(f"Celkový počet položek k zpracování: {total_items}")
    except Exception as e:
        print(f"Chyba při čtení vstupního Excelu pro zjištění počtu položek: {e}")
        logging.error(f"Nepodařilo se načíst Excel pro zjištění počtu položek: {e}", exc_info=True)
        total_items = 0 # Nebo ukončit skript

    ctk.set_default_color_theme("dark-blue")

    # Vytvoření fronty a stop eventu
    data_queue = queue.Queue()
    stop_event = Event()  # Vytvoření eventu pro zastavení

    # Vytvoření dialogového okna pro uložení výstupního Excelu
    root_tk = Tk()
    root_tk.withdraw()
    output_excel = filedialog.asksaveasfilename(title="Uložte výstupní Excel soubor", defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx;*.xls")])
    root_tk.destroy()

    if not output_excel:
        print("Nebyl vybrán žádný výstupní soubor. Skript se ukončí.")
        logging.warning("Nebyl vybrán výstupní Excel soubor.")
        exit()
    logging.info(f"Vybrán výstupní soubor: {output_excel}")

    # Spuštění zapisovacího vlákna
    writer_thread = start_writer_thread(data_queue, stop_event, output_excel)

    # Vytvoření GUI
    # Použití lambda pro on_close, aby se předaly potřebné argumenty
    root_gui, progress_var, percent_var, progress_bar, remaining_time_var, exit_button = create_gui(total_items, lambda: on_gui_close(root_gui, stop_event, data_queue, writer_thread))
    # Připojení on_close i k zavření okna křížkem
    root_gui.protocol("WM_DELETE_WINDOW", lambda: on_gui_close(root_gui, stop_event, data_queue, writer_thread))


    # Spuštění skriptu ve vlákně
    start_script_thread(progress_var, percent_var, progress_bar, remaining_time_var, exit_button, data_queue, stop_event, excel_file)

    # Hlavní smyčka GUI
    logging.info("Spouštím hlavní smyčku GUI.")
    root_gui.mainloop()
    logging.info("Hlavní smyčka GUI byla ukončena.")
    logging.info("="*20 + " Ukončení skriptu " + "="*20)
