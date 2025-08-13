import requests
import csv
import time
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

# --- CONFIG
bearer, x_auth = carregar_tokens()

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Authorization": "Bearer " + bearer,
    "Content-Type": "application/json",
    "Referer": "https://SUAEMPRESA.marketup.com/", # insira aqui a sua URL no MarketUP
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0",
    "X-Auth-Token": x_auth
}

URL_LISTA = "https://api-erp.marketup.com/v1/StockMovement/GetPagedList"
URL_DETALHE = "https://api-erp.marketup.com/v1/StockMovement/Get"

# --- PERÍODO
start_date = "2025-06-01" # data de início da listagem de movimentações
end_date   = "2025-08-12" # data de fim da listagem de movimentações

def pegar_ids():
    ids = set()
    page = 1
    page_size = 200  # aumentar o page size para reduzir requisições

    while True:
        payload = {
            "Page": page,
            "PageSize": page_size,
            "MovementStartDate": start_date + "T00:00:00",
            "MovementEndDate": end_date + "T23:59:59"
        }
        print(f"\nConsultando página {page} de movimentações...")
        r = requests.post(URL_LISTA, json=payload, headers=HEADERS)
        r.raise_for_status()
        dados = r.json()

        items = dados.get("Items", [])
        print(f"  {len(items)} movimentações encontradas nesta página")

        for item in items:
            ids.add(item["StockMovementID"])

        total_pages = dados.get("TotalPages", 0)
        if page >= total_pages:
            break
        page += 1
        time.sleep(0.1)  # evitar sobrecarga

    return list(ids)

def pegar_detalhes(stock_id):
    payload = {"ID": stock_id}
    r = requests.post(URL_DETALHE, json=payload, headers=HEADERS)
    r.raise_for_status()
    return r.json()

# --- EXECUÇÃO
ids_mov = pegar_ids()
print(f"\nTotal de movimentações únicas encontradas: {len(ids_mov)}\n")

nome_arquivo = f"movimentacoes_{start_date}_a_{end_date}.csv"
with open(nome_arquivo, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)
    writer.writerow([
        "StockMovementID",
        "LocalEstoqueOrigem",
        "DataMovimentacao",
        "CodigoBarras",
        "Produto",
        "Quantidade",
        "Lote",
        "Fabricacao",
        "Validade"
    ])
    
    for idx, mid in enumerate(ids_mov, start=1):
        print(f"\n[{idx}/{len(ids_mov)}] Buscando detalhes da movimentação {mid}...")
        dados = pegar_detalhes(mid)

        movimento = dados.get("Item", {})
        data_mov = movimento.get("MovementDate")
        local_origem = movimento.get("StockLocationOrigin", {}).get("Name")

        stock_items = movimento.get("StockMovementItemList", [])
        if stock_items:
            for item in stock_items:
                produto = item.get("ItemName")
                quantidade = item.get("Amount")
                lote = item.get("Batch")
                fab = item.get("ManufactureDate")
                val = item.get("ExpirationDate")
                barcode = "'" + item.get("Item", {}).get("BarCode", "")  # apóstrofo incluído
                writer.writerow([
                    mid,
                    local_origem,
                    data_mov,
                    barcode,
                    produto,
                    quantidade,
                    lote,
                    fab,
                    val
                ])
        time.sleep(0.2)

print("\nCSV gerado: " + nome_arquivo + ".csv")
