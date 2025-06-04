import sys
import pathlib
import base64

import pytest

# Aggiungiamo ai path i moduli vision, bucket e vdb
sys.path.append("packages/rag/loader")
import bucket, vision, vdb, loader


def test_loader_image_flow(tmp_path):
    """
    Questo test verifica il flusso completo di:
    1. Scrittura di `cat.jpg` nel Bucket.
    2. Chiamata a `loader(...)` con input "$" per elencare le immagini.
    3. Chiamata a `loader(...)` con input "$cat" per descrivere e inserire nel VectorDB.
    4. Chiamata a `loader(...)` con input "*cat" per effettuare la ricerca vettoriale.
    """

    args = {}
    collection = "default"

    # 1) Pulizia iniziale del bucket: rimuoviamo ogni oggetto che contenga "cat"
    buc = bucket.Bucket(args)
    existing = buc.find("cat")
    for key in existing:
        buc.remove(key)

    # 2) Scriviamo `cat.jpg` nel bucket a partire dal file di test
    cat_bytes = pathlib.Path("tests/vision/cat.jpg").read_bytes()
    buc.write("cat.jpg", cat_bytes)

    # 3) Pulizia iniziale del VectorDB: distruggiamo la collection di default se esiste
    db = vdb.VectorDB(args, collection)
    db.destroy(collection)

    # --- Fase 1: elenco immagini con input "$" ---
    out1 = loader.loader({"input": "$", "state": ""})
    # Controlliamo che nell'output compaia "cat.jpg"
    assert "cat.jpg" in out1["output"]

    # Recuperiamo lo stato restituito per riutilizzarlo nelle chiamate successive
    state1 = out1["state"]
    assert state1.startswith("default:")

    # --- Fase 2: inserimento immagine con input "$cat" ---
    out2 = loader.loader({"input": "$cat", "state": state1})
    # out2["output"] deve contenere la descrizione dell'immagine: ci aspettiamo almeno la parola "cat"
    assert out2["output"], "L'output non deve essere vuoto"
    assert "cat" in out2["output"].lower()

    # Lo stato non cambia: rimane sulla stessa collection e limit
    state2 = out2["state"]
    assert state2 == state1

    # --- Fase 3: ricerca vettoriale con input "*cat" ---
    out3 = loader.loader({"input": "*cat", "state": state2})
    # L'output dovrebbe iniziare con "Found:" e contenere almeno un risultato
    assert out3["output"].startswith("Found:")
    # Verifichiamo che nell'output appaia di nuovo "cat" (la descrizione salvata)
    assert "cat" in out3["output"].lower()

    # --- Cleanup finale ---
    # Rimuoviamo l'elemento "cat.jpg" dal bucket
    remaining = buc.find("cat")
    for key in remaining:
        buc.remove(key)

    # Distruggiamo la collection "default" nel VectorDB
    db.destroy(collection)
