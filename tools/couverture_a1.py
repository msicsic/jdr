"""Relire les requêtes A0 scellées et mesurer A1, sans moteur ni modèle."""
import argparse
from collections import Counter
import hashlib
import gzip
import json
from pathlib import Path
import sys

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
from donjon.projection_publique import projeter, verifier_couverture


def taille(value):
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def requetes(archives, oracle):
    """Référence historique du 318/A0 ; reprises conservées, dénominateur fixe."""
    attendus = {c["id"] for c in oracle["cas"] if c["modele"]}
    vus = set()
    sources = [s for s in oracle["sources"] if s["campagne"] == "230e7b3"]
    if len(sources) != 6:
        raise ValueError("Les six scripts de référence sont requis")
    for source in sources:
        fichier = archives / source["path"]
        brut = fichier.read_bytes()
        if hashlib.sha256(brut).hexdigest() != source["sha256"]:
            raise ValueError(f"Archive modifiée : {fichier}")
        partie = json.loads(brut)
        for n, tour in enumerate(partie["tours"]):
            cle = f"{partie['script']}/{n}"
            if cle not in attendus:
                continue
            appels = [e for e in tour.get("fil", []) if e.get("etape") == "appel"
                      and e.get("fonction") == "repondre_au_joueur"
                      and not {"conversation_validee", "resultat_resolu"}.intersection(
                          e.get("entree", {}).get("faits", {}))]
            if not appels:
                raise ValueError(f"Requête manquante : {cle}")
            vus.add(cle)
            for i, appel in enumerate(appels):
                yield cle, i, appel["entree"], source
    if vus != attendus or len(vus) != 30:
        raise ValueError(f"Corpus incomplet : {attendus - vus}")


def mesurer(archives, oracle):
    lignes, motifs = [], Counter()
    for cle, i, entree, source in requetes(archives, oracle):
        p = projeter(entree)
        nombre = verifier_couverture(entree, p)
        motifs.update(e["motif"] for e in p.exclusions)
        lignes.append({"id": cle, "requete": i, "source_sha256": source["sha256"],
                       "octets_entree": taille(entree), "octets_donnees": taille(p.entree),
                       "octets_projection_avec_provenance": taille(p.publique()),
                       "donnees_couvertes": nombre, "exclusions": p.exclusions})
    return {"reference": "230e7b3", "tours": len({r['id'] for r in lignes}),
            "requetes": len(lignes), "donnees_couvertes": sum(r['donnees_couvertes'] for r in lignes),
            "exclusions_par_motif": dict(motifs),
            "tailles_totales": {k: sum(r[k] for r in lignes) for k in (
                "octets_entree", "octets_donnees", "octets_projection_avec_provenance")},
            "appel_modele": False, "rejeu_moteur": False, "requetes_detail": lignes}


def corpus(archives, oracle):
    from tools.oracle_g1 import empreinte
    return [dict(id=cle, requete=i, entree=e, source=s, entree_sha256=empreinte(e))
            for cle, i, e, s in requetes(archives, oracle)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archives", type=Path, required=True)
    parser.add_argument("--sortie", type=Path, required=True)
    parser.add_argument("--figer-entrees", type=Path,
                        help="Copie reproductible des entrées pour les tests sans archives")
    args = parser.parse_args()
    from tools.priorite import ceder
    ceder()
    oracle = json.loads((RACINE / "tests/data/oracle_g1.json").read_text(encoding="utf-8"))
    result = mesurer(args.archives, oracle)
    extrait = corpus(args.archives, oracle)
    if args.figer_entrees:
        args.figer_entrees.write_bytes(gzip.compress(json.dumps(
            extrait, ensure_ascii=False, separators=(",", ":")).encode("utf-8"), mtime=0))
    fixture = RACINE / "tests/data/projection_a1_entrees.json.gz"
    if json.loads(gzip.decompress(fixture.read_bytes())) != extrait:
        raise ValueError("La copie versionnée diffère des archives scellées")
    result["corpus_versionne_sha256"] = hashlib.sha256(fixture.read_bytes()).hexdigest()
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    args.sortie.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "requetes_detail"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
