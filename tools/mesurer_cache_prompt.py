"""Mesure les préfixes et les tokens servis en cache dans les fils de bancs JSON.

  python tools/mesurer_cache_prompt.py artifacts/bancs-multi/DATE --sortie artifacts/cache.json

Les pourcentages sont pondérés par les tokens, appels froids compris. Aucun appel au modèle.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path


def mesurer(parties):
    groupes = defaultdict(lambda: {"appels": 0, "prefixes": set(), "instructions": set(),
                                  "schemas": set(), "entree": 0, "cache": 0, "sans_usage": 0})
    for partie in parties:
        for tour in partie.get("tours", []):
            for appel in tour.get("fil", []):
                if appel.get("etape") != "appel":
                    continue
                m = groupes[appel["fonction"]]
                m["appels"] += 1
                def empreinte(objet):
                    # L'ordre des propriétés fait partie du texte envoyé au fournisseur.
                    return hashlib.sha256(json.dumps(objet, ensure_ascii=False).encode()).hexdigest()
                m["prefixes"].add(empreinte([appel["fonction"], appel["schema"], appel["instructions"]]))
                m["schemas"].add(empreinte(appel["schema"]))
                m["instructions"].add(empreinte(appel["instructions"]))
                usage = appel.get("usage") or {}
                tokens = usage.get("input_tokens")
                cache = (usage.get("input_tokens_details") or {}).get("cached_tokens")
                if type(tokens) is not int or type(cache) is not int:
                    m["sans_usage"] += 1
                    continue
                m["entree"] += tokens
                m["cache"] += cache
    resultat = {}
    for fonction, m in sorted(groupes.items()):
        resultat[fonction] = {k: len(v) if isinstance(v, set) else v for k, v in m.items()}
        resultat[fonction]["part_cache"] = m["cache"] / m["entree"] if m["entree"] else None
    total = {k: sum(m[k] for m in resultat.values()) for k in ("appels", "entree", "cache", "sans_usage")}
    total["part_cache"] = total["cache"] / total["entree"] if total["entree"] else None
    return {"fonctions": resultat, "total": total}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("chemins", nargs="+", type=Path)
    p.add_argument("--sortie", type=Path)
    args = p.parse_args()
    fichiers = sorted({f.resolve() for chemin in args.chemins
                       for f in (chemin.rglob("*.json") if chemin.is_dir() else [chemin])})
    parties = []
    sources = []
    for fichier in fichiers:
        contenu = json.loads(fichier.read_text(encoding="utf-8"))
        if isinstance(contenu, dict) and isinstance(contenu.get("tours"), list):
            parties.append(contenu)
            sources.append(str(fichier))
    if not parties:
        p.error("aucune partie de banc trouvée")
    resultat = {**mesurer(parties), "fichiers": sources}
    texte = json.dumps(resultat, ensure_ascii=False, indent=2)
    if args.sortie:
        args.sortie.parent.mkdir(parents=True, exist_ok=True)
        args.sortie.write_text(texte + "\n", encoding="utf-8")
    print(texte)


if __name__ == "__main__":
    main()
