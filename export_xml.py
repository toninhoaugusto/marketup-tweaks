import requests
import time
from datetime import datetime
import os

#--- CARREGAR TOKENS
def carregar_tokens():

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "auth"))
    token_file = os.path.join(base_dir, "auth.txt")

    with open(token_file, "r") as f:
        linhas = f.read().splitlines()

    if len(linhas) < 2:
        raise ValueError("O arquivo auth.txt deve conter duas linhas: Bearer e X-Auth-Token")

    bearer_token = linhas[0].strip()
    x_auth_token = linhas[1].strip()
    return bearer_token, x_auth_token

# -------------------------
# CONFIGURAÇÕES
# -------------------------
bearer, x_auth = carregar_tokens()

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Authorization": "Bearer " + bearer,
    "Content-Type": "application/json",
    "Referer": "https://dentalvita.marketup.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
    "X-Auth-Token": x_auth
}

USER_ID = 1  # seu UserID no sistema

# Período da exportação (máx. 17 dias)
START_DATE = "2025-07-27T00:00:00.000"
END_DATE   = "2025-08-13T23:59:59.999"

# -------------------------
# 1 Criar tarefa de exportação
# -------------------------
payload = {
    "StartDate": START_DATE,
    "EndDate": END_DATE,
    "UserID": USER_ID,
    "Type": "1",
    "IsImported": False
}

print("Criando tarefa de exportação...")
r = requests.post("https://api-erp.marketup.com/v1/NewInvoice/ExportXmls", json=payload, headers=HEADERS)
resp = r.json()

if not resp.get("success"):
    print("Erro ao criar exportação:", resp.get("errorMessage"))
    exit()

operation_ticket = resp["OperationTicket"]
print("Tarefa criada com OperationTicket:", operation_ticket)

# -------------------------
# 2 Aguardar a conclusão da tarefa
# -------------------------
def check_queue(ticket):
    payload = {"QueueOperationTypeID": 3}  # retorna apenas tarefas de exportação
    r = requests.post(
        "https://api-erp.marketup.com/v1/UserQueue/GetPagedList",
        json=payload,
        headers=HEADERS
    )
    r.raise_for_status()
    data = r.json()
    for item in data.get("Items", []):
        if item["OperationTicket"] == ticket:
            return item
    return None

print("Aguardando a conclusão da exportação...")
while True:
    task = check_queue(operation_ticket)
    if task and task.get("Status") == 3 and task.get("ResponseUrl"):
        download_url = task["ResponseUrl"]
        print("Tarefa concluída! URL de download:", download_url)
        break
    print("Ainda processando... esperando 10 segundos")
    time.sleep(10)

# -------------------------
# 3 Baixar o ZIP
# -------------------------
filename = f"xml_export_{START_DATE[:10]}_a_{END_DATE[:10]}.zip"
print("Baixando arquivo ZIP...")

r = requests.get(download_url, headers={"User-Agent": HEADERS["User-Agent"]}, allow_redirects=True)
r.raise_for_status()  # garante que houve sucesso

with open(filename, "wb") as f:
    f.write(r.content)

print(f"Arquivo salvo como {filename}")

