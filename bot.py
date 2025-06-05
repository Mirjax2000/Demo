"""Bot pro získání a aktualizaci zákazníků"""

import sys
import requests
from rich.console import Console

cons: Console = Console()

TOKEN = "40ecc9e490d45b6523c549aacae86acfe29bd5da"

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


# --- 2. Funkce pro vyplnění dat (nahraď selenium daty později) ---
def selenium_foo(data) -> dict[str, list[dict]]:
    order_list = [
        {
            "708809617500494793-O": {
                "name": "Horakova Magda",
                "zip_code": "51801",
                "city": "Praha",
                "street": "Konvalinkova 15",
                "phone": "234234234",
                "email": "horakova.magda@seznam.cz",
            }
        },
        {
            "709809544700494450-O": {
                "name": "Zakordonets Kateryna",
                "zip_code": "30100",
                "city": "Praha",
                "street": "Konvalinkova 15",
                "phone": "234234234",
                "email": "katerina@seznam.cz",
            }
        },
        {
            "708807379000495388-R": {
                "name": "Pepa",
                "zip_code": "54321",
                "city": "Brno",
                "street": "Jabloňová 3",
                "phone": "777888999",
                "email": "pepa@centrum.cz",
            }
        },
        {
            "708806960800494870-R": {
                "name": "Lucie",
                "zip_code": "10000",
                "city": "Ostrava",
                "street": "Školní 22",
                "phone": "602123456",
                "email": "lucie@volny.cz",
            }
        },
        {
            "708804205600494935-O": {
                "name": "Karel",
                "zip_code": "11000",
                "city": "Plzeň",
                "street": "Hlavní 5",
                "phone": "601987654",
                "email": "karel@email.cz",
            }
        },
    ]
    
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
