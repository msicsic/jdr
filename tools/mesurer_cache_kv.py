"""Mesure le taux de réutilisation du préfixe KV (1-slot et 4-slots) sur les traces d'appels MJ."""
import argparse
import glob
import json
from pathlib import Path
import sys

RACINE = Path(__file__).resolve().parents[1]
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

from donjon.mj import INSTRUCTIONS_INTERPRETATION, INSTRUCTIONS_NARRATION
from donjon.sources import ordonner_entree, slot_cache, voie_cache

BLOC_TOKENS_CHARS = 512  # ~128 tokens (granularité typique de bloc KV Radix / llama.cpp / vLLM)


def lcp_aligne(a, b, bloc=BLOC_TOKENS_CHARS):
    limite = min(len(a), len(b))
    i = 0
    while i < limite and a[i] == b[i]:
        i += 1
    return (i // bloc) * bloc


def extraire_appels(objet):
    """Extrait récursivement les étapes d'appel d'un fichier de trace MJ."""
    if isinstance(objet, list):
        for element in objet:
            yield from extraire_appels(element)
    elif isinstance(objet, dict):
        if objet.get("etape") == "appel" and "entree" in objet and "fonction" in objet:
            yield objet
        for valeur in objet.values():
            if isinstance(valeur, (dict, list)):
                yield from extraire_appels(valeur)


def simuler_trace(appels, *, reordonner=True):
    """Simule le flux de tokens d'entrée [system(instructions), user(entree)] sur une partie."""
    slots = {}
    slots_entree = {}
    precedent = ""
    total = total_chaud = cache_4slots = cache_1slot = 0
    entree_chaud = entree_cache_chaud = 0
    par_voie = {}

    for appel in appels:
        fonction = appel["fonction"]
        entree = appel["entree"]
        voie = voie_cache(fonction, entree)
        slot = slot_cache(voie) if reordonner else 0
        if reordonner:
            instructions = (INSTRUCTIONS_NARRATION if voie == "raconter"
                            else INSTRUCTIONS_INTERPRETATION if voie == "interpreter"
                            else appel.get("instructions", ""))
            entree_flux = ordonner_entree(entree)
        else:
            instructions = appel.get("instructions", "")
            entree_flux = entree
        schema_str = "" if reordonner else json.dumps(appel.get("schema", {}), ensure_ascii=False)
        entree_str = json.dumps(entree_flux, ensure_ascii=False)
        flux = (schema_str + "\n" if schema_str else "") + instructions + "\n" + entree_str
        longueur = len(flux)
        total += longueur
        stat = par_voie.setdefault(voie, {"appels": 0, "total": 0, "cache": 0})
        stat["appels"] += 1
        stat["total"] += longueur
        if slot in slots:
            hit = lcp_aligne(slots[slot], flux)
            total_chaud += longueur
            cache_4slots += hit
            stat["cache"] += hit
            if slot in slots_entree:
                entree_chaud += len(entree_str)
                entree_cache_chaud += lcp_aligne(slots_entree[slot], entree_str)
        slots[slot] = flux
        slots_entree[slot] = entree_str
        if precedent:
            cache_1slot += lcp_aligne(precedent, flux)
        precedent = flux

    return {
        "appels": len(appels),
        "appels_chauds": max(0, len(appels) - len(slots)),
        "total_chars": total,
        "total_chaud_chars": total_chaud,
        "total_tokens_est": total // 4,
        "cache_1slot_chars": cache_1slot,
        "ratio_1slot": round(100 * cache_1slot / total, 1) if total else 0.0,
        "cache_4slots_chars": cache_4slots,
        "ratio_4slots_total": round(100 * cache_4slots / total, 1) if total else 0.0,
        "ratio_4slots_chaud": round(100 * cache_4slots / total_chaud, 1) if total_chaud else 0.0,
        "entree_chaud_chars": entree_chaud,
        "entree_cache_chaud_chars": entree_cache_chaud,
        "ratio_entree_chaud": round(100 * entree_cache_chaud / entree_chaud, 1) if entree_chaud else 0.0,
        "uncached_tokens_par_appel_chaud": round((total_chaud - cache_4slots) / 4 / max(1, len(appels) - len(slots))),
        "par_voie": par_voie,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chemins", nargs="+", help="Fichiers ou motifs glob de traces JSON")
    args = parser.parse_args(argv)
    fichiers = []
    for motif in args.chemins:
        fichiers.extend(sorted(glob.glob(motif, recursive=True)))
    avant_tot = []
    apres_tot = []
    for f in fichiers:
        try:
            donnees = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue
        appels = list(extraire_appels(donnees))
        if not appels:
            continue
        avant_tot.append(simuler_trace(appels, reordonner=False))
        apres_tot.append(simuler_trace(appels, reordonner=True))

    def agreger(liste):
        appels = sum(x["appels"] for x in liste)
        appels_chauds = sum(x["appels_chauds"] for x in liste)
        tot = sum(x["total_chars"] for x in liste)
        tot_chaud = sum(x["total_chaud_chars"] for x in liste)
        ent_chaud = sum(x["entree_chaud_chars"] for x in liste)
        ent_cache = sum(x["entree_cache_chaud_chars"] for x in liste)
        c1 = sum(x["cache_1slot_chars"] for x in liste)
        c4 = sum(x["cache_4slots_chars"] for x in liste)
        return {
            "parties": len(liste),
            "appels": appels,
            "appels_chauds": appels_chauds,
            "tokens_totaux_est": tot // 4,
            "ratio_1slot_pct": round(100 * c1 / tot, 1) if tot else 0.0,
            "ratio_4slots_total_pct": round(100 * c4 / tot, 1) if tot else 0.0,
            "ratio_4slots_chaud_pct": round(100 * c4 / tot_chaud, 1) if tot_chaud else 0.0,
            "ratio_entree_chaud_pct": round(100 * ent_cache / ent_chaud, 1) if ent_chaud else 0.0,
            "tokens_prefill_non_caches_par_appel_total": round((tot - c4) / 4 / max(1, appels)),
            "tokens_prefill_non_caches_par_appel_chaud": round((tot_chaud - c4) / 4 / max(1, appels_chauds)),
        }

    print(json.dumps({"avant_main": agreger(avant_tot), "apres_cache_kv_local": agreger(apres_tot)},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
