RISO = {"nome": "Riso", "kcal": 350, "proteine": 8, "carboidrati": 77, "grassi": 0.6}
POLLO = {"nome": "Pollo", "kcal": 110, "proteine": 23, "carboidrati": 0, "grassi": 1.2}


def _alimenti(client):
    riso = client.post("/alimenti", json=RISO).json()["id"]
    pollo = client.post("/alimenti", json=POLLO).json()["id"]
    return riso, pollo


def _crea_ricetta(client, riso, pollo, nome="Riso e pollo"):
    return client.post(
        "/ricette",
        json={
            "nome": nome,
            "istruzioni": "Cuoci tutto.",
            "ingredienti": [
                {"alimento_id": riso, "grammi": 80},
                {"alimento_id": pollo, "grammi": 150},
            ],
        },
    )


def test_crea_con_macro_totali(client):
    riso, pollo = _alimenti(client)
    r = _crea_ricetta(client, riso, pollo)
    assert r.status_code == 201
    dati = r.json()
    assert len(dati["ingredienti"]) == 2
    # 80 g riso + 150 g pollo
    assert dati["macro"]["kcal"] == 445.0
    assert dati["macro"]["proteine"] == 40.9
    assert dati["macro"]["carboidrati"] == 61.6
    assert dati["macro"]["grassi"] == 2.3


def test_leggi_e_lista(client):
    riso, pollo = _alimenti(client)
    id_ = _crea_ricetta(client, riso, pollo).json()["id"]
    assert client.get(f"/ricette/{id_}").status_code == 200
    assert len(client.get("/ricette").json()) == 1
    assert client.get("/ricette", params={"q": "zzz"}).json() == []


def test_non_trovata_404(client):
    assert client.get("/ricette/999").status_code == 404


def test_alimento_inesistente_404(client):
    r = client.post(
        "/ricette",
        json={"nome": "X", "ingredienti": [{"alimento_id": 999, "grammi": 50}]},
    )
    assert r.status_code == 404


def test_alimento_ripetuto_422(client):
    riso, _ = _alimenti(client)
    r = client.post(
        "/ricette",
        json={
            "nome": "X",
            "ingredienti": [
                {"alimento_id": riso, "grammi": 50},
                {"alimento_id": riso, "grammi": 30},
            ],
        },
    )
    assert r.status_code == 422


def test_senza_ingredienti_422(client):
    r = client.post("/ricette", json={"nome": "X", "ingredienti": []})
    assert r.status_code == 422


def test_nome_duplicato_409(client):
    riso, pollo = _alimenti(client)
    _crea_ricetta(client, riso, pollo)
    assert _crea_ricetta(client, riso, pollo).status_code == 409


def test_modifica_solo_nome(client):
    riso, pollo = _alimenti(client)
    id_ = _crea_ricetta(client, riso, pollo).json()["id"]
    r = client.patch(f"/ricette/{id_}", json={"nome": "Nuovo nome"})
    assert r.status_code == 200
    assert r.json()["nome"] == "Nuovo nome"
    assert len(r.json()["ingredienti"]) == 2


def test_modifica_ingredienti_sostituisce(client):
    riso, pollo = _alimenti(client)
    id_ = _crea_ricetta(client, riso, pollo).json()["id"]
    # il riso resta (stessa coppia ricetta/alimento) con grammi diversi, il pollo sparisce
    r = client.patch(
        f"/ricette/{id_}",
        json={"ingredienti": [{"alimento_id": riso, "grammi": 200}]},
    )
    assert r.status_code == 200
    ingredienti = r.json()["ingredienti"]
    assert len(ingredienti) == 1
    assert ingredienti[0]["grammi"] == 200
    assert r.json()["macro"]["kcal"] == 700.0


def test_elimina(client):
    riso, pollo = _alimenti(client)
    id_ = _crea_ricetta(client, riso, pollo).json()["id"]
    assert client.delete(f"/ricette/{id_}").status_code == 204
    assert client.get(f"/ricette/{id_}").status_code == 404
    # gli alimenti restano
    assert len(client.get("/alimenti").json()) == 2
