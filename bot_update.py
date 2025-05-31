import requests

from rich.console import Console

cons: Console = Console()

TOKEN = "40ecc9e490d45b6523c549aacae86acfe29bd5da"

# Adresa API
API_URL = "http://localhost:8000/api/update-customers/"

# Hlavičky s autorizací
headers = {"Authorization": f"Token {TOKEN}"}

# Testovací data ve správném tvaru
payload = {
    "updates": [
        {
            "709809544700494450-O": {
                "name": "Zakordonets Kateryna",
                "zip_code": "30100",
                "city": "Praha",
                "street": "Konvalinkova 15",
                "phone": "234234234",
                "email": "katerina@seznam.cz",
            },
        },
        {
            "708807379000495388-R": {
                "name": "Pepa",
                "zip_code": "54321",
                "city": "Brno",
                "street": "Jabloňová 3",
                "phone": "777888999",
                "email": "pepa@centrum.cz",
            },
        },
        {
            "708806960800494870-R": {
                "name": "Lucie",
                "zip_code": "10000",
                "city": "Ostrava",
                "street": "Školní 22",
                "phone": "602123456",
                "email": "lucie@volny.cz",
            },
        },
        {
            "708804205600494935-O": {
                "name": "Karel",
                "zip_code": "11000",
                "city": "Plzeň",
                "street": "Hlavní 5",
                "phone": "601987654",
                "email": "karel@email.cz",
            },
        },
    ]
}

# Odeslání požadavku
response = requests.post(API_URL, json=payload,headers=headers, timeout=5)

# Výsledek
cons.log("Status code:", response.status_code)
cons.log("Odpověď serveru:", response.json())
