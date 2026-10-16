POLLO = {
    "nome": "Petto di pollo",
    "kcal": 110,
    "proteine": 23,
    "carboidrati": 0,
    "grassi": 1.2,
}


def test_crea_e_leggi(client):
    r = client.post("/alimenti", json=POLLO)
    assert r.status_code == 201
    dati = r.json()
    assert dati["nome"] == "Petto di pollo"

    r = client.get(f"/alimenti/{dati['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == dati["id"]


def test_nome_duplicato_409(client):
    client.post("/alimenti", json=POLLO)
    r = client.post("/alimenti", json=POLLO)
    assert r.status_code == 409


def test_non_trovato_404(client):
    assert client.get("/alimenti/999").status_code == 404


def test_valori_negativi_422(client):
    r = client.post("/alimenti", json={**POLLO, "kcal": -5})
    assert r.status_code == 422


def test_ricerca(client):
    client.post("/alimenti", json=POLLO)
    client.post("/alimenti", json={**POLLO, "nome": "Riso"})
    r = client.get("/alimenti", params={"q": "poll"})
    assert [a["nome"] for a in r.json()] == ["Petto di pollo"]


def test_modifica(client):
    id_ = client.post("/alimenti", json=POLLO).json()["id"]
    r = client.patch(f"/alimenti/{id_}", json={"kcal": 120})
    assert r.status_code == 200
    assert r.json()["kcal"] == 120
    assert r.json()["nome"] == "Petto di pollo"


def test_elimina(client):
    id_ = client.post("/alimenti", json=POLLO).json()["id"]
    assert client.delete(f"/alimenti/{id_}").status_code == 204
    assert client.get(f"/alimenti/{id_}").status_code == 404
