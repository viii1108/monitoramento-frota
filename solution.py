import os
import requests
from dotenv import load_dotenv
from folium import Map, Marker, Icon

# 1. Carregar variáveis do .env
load_dotenv(".env")
token = os.getenv("SPTRANS_TOKEN") or "19bae450e1b94bcde8dc02f671b19716d57c338e100131fe4b1ddee2c8a2206a"

s = requests.Session()

# 2. Autenticação na API SPTrans
res = s.post(
    f"http://api.olhovivo.sptrans.com.br/v2.1/Login/Autenticar?token={token}"
)
print("Status Autenticação:", res.text)

# 3. Buscar linhas relacionadas a Pinheiros
termo_busca = "Pinheiros"
linhas = s.get(
    f"http://api.olhovivo.sptrans.com.br/v2.1/Linha/Buscar?termosBusca={termo_busca}"
).json()

if not linhas:
    print("❌ Nenhuma linha encontrada com esse termo.")
    exit()

paradas = []
linha_encontrada = None

for linha in linhas:
    codigo = linha["cl"]
    res_paradas = s.get(
        f"http://api.olhovivo.sptrans.com.br/v2.1/Parada/BuscarParadasPorLinha?codigoLinha={codigo}"
    ).json()

    if res_paradas:
        paradas = res_paradas
        linha_encontrada = linha
        break

if not paradas:
    print("❌ Nenhuma parada encontrada para as linhas retornadas.")
    exit()

print(f"✅ Linha selecionada: {linha_encontrada['tp']} - {linha_encontrada['ts']} (Código: {linha_encontrada['cl']})")

# 4. Buscar posições dos veículos em tempo real para essa linha
res_posicao = s.get(
    f"http://api.olhovivo.sptrans.com.br/v2.1/Posicao/Linha?codigoLinha={linha_encontrada['cl']}"
).json()

veiculos = res_posicao.get("vs", [])
print(f"✅ Encontrados {len(paradas)} paradas e {len(veiculos)} veículos em circulação.")

# 5. Criar o mapa centralizado na primeira parada usando Esri Street Map (com nomes de ruas)
indice_inicial = 0
m = Map(
    location=[paradas[indice_inicial]["py"], paradas[indice_inicial]["px"]], 
    zoom_start=14,
    tiles="Esri.WorldStreetMap"
)

# 6. Adicionar os marcadores de paradas (Azul)
for i in paradas:
    Marker(
        location=[i["py"], i["px"]], 
        popup=f"Parada: {i['np']}",
        icon=Icon(color="blue", icon="info-sign")
    ).add_to(m)

# 7. Adicionar os marcadores dos ônibus em tempo real (Vermelho com ícone de ônibus)
for v in veiculos:
    Marker(
        location=[v["py"], v["px"]], 
        popup=f"Ônibus Pref: {v['p']}",
        icon=Icon(color="red", icon="bus", prefix="fa")
    ).add_to(m)

# 8. Salvar o arquivo unasp.html
m.save("unasp.html")
print("✅ Arquivo 'unasp.html' atualizado com sucesso!")