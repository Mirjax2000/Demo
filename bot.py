"""Bot pro ziskani incomplete customers"""

import requests
from rich.console import Console

cons: Console = Console()

TOKEN = "40ecc9e490d45b6523c549aacae86acfe29bd5da"

# Adresa API
API_URL = "http://localhost:8000/api/incomplete-customers/"

# Hlavičky s autorizací
headers = {"Authorization": f"Token {TOKEN}"}

# Požadavek na endpoint
response = requests.get(API_URL, headers=headers, timeout=5)

# Výpis výsledku
if response.status_code == 200:
    cons.log("Ziskavam data", style="blue bold")

    # --- zde jsou data ---
    data = response.json()
    # ---

    for item in data:
        cons.log("objednavka: ", item, style="green")
    cons.log("Seznam ziskan", style="blue bold")
else:
    cons.log("Chyba:", response.status_code, style="red")
    cons.log(response.text, style="red")
