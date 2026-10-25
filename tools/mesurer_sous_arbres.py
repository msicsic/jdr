"""Lot 92 b : ascendance des expansions, clôture des moyens et réveils de faim.

Observation seule : aucun filtre appliqué au moteur. Les préfixes de moindre
coût retenus par la recherche définissent l'ascendance (le graphe fusionne
plusieurs chemins). Les sous-arbres peuvent se recouper ; leur union est séparée.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import inspect
import json
from pathlib import Path
import time

import empreintes_nuits as empreintes


def fermeture(p, v, e, but, vises):
    """Sur-approximation transitive, sans lire de vérité à la place d'une croyance.

    Les prédicats arbitraires et les franchissements dépendant de l'équipement
    gardent tout. Les trois prédicats moteurs déclarent ici leurs feuilles ;
    la lumière reste requise par la pression, le but ou une capacité de
    crochetage (même sans serrure utile démontrée : sur-approximation).
    """
    if but not in (p.a_mange, p.rechauffe, p.eclaire) or any(v.metrique(a) for a in (15, 30)):
        return set(v.connus), {o: "but_opaque_ou_passage" for o in v.connus}, set(v.rechargeables)
    objets = v.objets
    raisons = {}
    lumiere = (v.peur or v.eclairer or v._lumiere_lue or but in (p.rechauffe, p.eclaire)
               or "crochetage" in p.profil(v.monde, v.id)["capacites"])
    from donjon.combat import arme, prix_violence
    violence = prix_violence(v.monde, v.id, v.motif) is not None
    # Une charge ne s'épuise pas dans le graphe. Pour ces trois prédicats,
    # charger ne sert qu'à permettre un allumage : une source déjà allumée
    # ne gagne ni flamme ni lumière en recevant le seul fait charge=True.
    charges = {o for o in v.rechargeables if lumiere and v.feu(e, o)[0] is not True and not v.feu(e, o)[1]}

    def ajouter(o, pourquoi):
        if o in objets and o not in raisons:
            raisons[o] = pourquoi

    for o in v.connus:
        x = objets[o]
        if but is p.a_mange and x["type"] == "nourriture" and v.disponible(o):
            ajouter(o, "vivre_ou_part")
        if but is p.rechauffe and (x.get("foyer") or v.besoin[o] == "chaleur"):
            ajouter(o, "foyer_ou_part")
        if lumiere and ("allume" in x or "allumage" in x.get("usages", ())):
            ajouter(o, "lumiere_flamme_pression")
        if x["type"] == "porte":
            ajouter(o, "route_conservatrice_toutes_portes")
        # Une arme peut diminuer le coût d'acquisition d'un moyen porté par autrui.
        if violence and x.get("mobile") and v.utile[o] and arme(x):
            ajouter(o, "arme_acquisition")
    for valeur in (vises or {}).values():
        for o in valeur:
            ajouter(o, "vise")
    precedent = -1
    while precedent != len(raisons):
        precedent = len(raisons)
        for o in list(raisons):
            # Tous les ancêtres de contenant/porteur, jusqu'au point fixe.
            parent = v._lieu(e, o)
            if parent in objets:
                ajouter(parent, "acces:" + o)
            x = objets[o]
            if o in charges:
                for k in v.connus:
                    if p.recharge(x, objets[k]):
                        ajouter(k, "combustible:" + o)
            if x["type"] in ("porte", "contenant") and v.verrouille(e, o):
                for k in v.connus:
                    y = objets[k]
                    if o in y.get("ouvre", ()) or "crochetage" in y.get("usages", ()) or p.force.adapte(x, y):
                        ajouter(k, "serrure:" + o)
    return set(raisons), raisons, charges


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scenario", default="auberge")
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--causes-seules", action="store_true", help="Clé complète sans observer les sous-arbres")
    args = ap.parse_args()
    empreintes._preparer(".", False, 0)
    from donjon import banc_pnj, planification as p
    from donjon.monde import Monde
    from donjon.rendu import regarder
    from donjon.scene import scene_percue
    banc_pnj.ceder()
    sortie = Path(args.sortie)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    pile, lignes, precedents, sauvegardees, capture = [], [], {}, set(), {}
    chercher, entrees, creer = p.chercher, p._entrees, banc_pnj.creer
    heure = [0]

    def observer_entrees(v, *a):
        cle = entrees(v, *a)
        if pile and pile[-1]["minute"] >= 480:
            r = pile[-1]
            valeurs = json.loads(cle[0])
            ancien = precedents.get((r["pnj"], r["but"]))
            r["entrees"] = hashlib.sha256(repr(cle).encode()).hexdigest()
            r["changements"] = ([] if ancien is None else [i for i, (x, y) in enumerate(zip(ancien, valeurs)) if x != y])
            avant = {} if ancien is None else {(x[0], x[1]): x[2] for x in ancien[3]}
            apres = {(x[0], x[1]): x[2] for x in valeurs[3]}
            r["croyances_changees"] = [list(k) for k in avant.keys() | apres.keys() if avant.get(k) != apres.get(k)]
            precedents[r["pnj"], r["but"]] = valeurs
        return cle

    def expansion(v, e, etapes, but, vises, n):
        if not pile or pile[-1]["minute"] < 480:
            return
        r = pile[-1]
        r["expansions"] += 1
        r["vus"].add(e)
        r["profondeurs"][str(n)] += 1
        cle = id(v)
        if cle not in r["fermetures"]:
            utiles, raisons, charges = fermeture(p, v, e, but, vises)
            r["fermetures"][cle] = (v, utiles, charges)
            r["dependances"] = raisons
            r["charges_utiles"] = sorted(charges)
            r["feux_depart"] = {o: v.feu(e, o) for o in v.rechargeables}
        utiles = r["fermetures"][cle][1]
        charges = r["fermetures"][cle][2]
        prepares = set()
        while etapes:
            etapes, ajout = etapes
            for x in ajout:
                operation = x["operation"]
                if operation != "aller":
                    prepares.add((operation, x.get("cible", ""), x.get("outil", "")))
        sans = []
        for operation, cible, outil in prepares:
            nom = "/".join((operation, cible, outil))
            r["descendants"][nom] += 1
            inutile = (operation in ("prendre", "ouvrir") and cible not in utiles
                       or operation == "alimenter" and cible not in charges)
            if inutile:
                sans.append(nom)
                r["descendants_sans_rapport"][nom] += 1
        if sans:
            r["union_sans_rapport"] += 1
        if any(x[0] in ("prendre", "ouvrir", "alimenter") for x in prepares):
            r["union_preparatifs"] += 1

    if not args.causes_seules:
        source = inspect.getsource(p._explorer_etats)
        point = "        examines += 1\n"
        assert source.count(point) == 1
        source = source.replace(point, point + "        _p2_expansion(v, e, etapes, but, vises, n)\n")
        p.__dict__["_p2_expansion"] = expansion
        exec(compile(source, "<diagnostic-p2>", "exec"), p.__dict__)

    def observer(monde, qui, *a, **k):
        r = {"minute": monde.data["minutes"], "pnj": qui, "but": k.get("nom", ""),
             "expansions": 0, "union_preparatifs": 0, "union_sans_rapport": 0,
             "descendants": Counter(), "descendants_sans_rapport": Counter(),
             "profondeurs": Counter(), "vus": set(), "fermetures": {}}
        from donjon.caractere import prix_faute
        r["prix"] = [prix_faute(monde, qui, k.get("motif"), n) for n in ("honnetete", "douceur")]
        pile.append(r)
        avant, debut = len(p.DIAGNOSTIC or []), time.process_time()
        try:
            resultat = chercher(monde, qui, *a, **k)
        finally:
            r["cpu_instrumente"] = time.process_time() - debut
            pile.pop()
        r["distincts"] = len(r.pop("vus"))
        r.pop("fermetures")
        if not pile and 480 <= r["minute"] < 720:
            if p.DIAGNOSTIC is not None and len(p.DIAGNOSTIC) > avant:
                r["diagnostic"] = p.DIAGNOSTIC[-1]
            if k.get("memo") is not None and k.get("depuis") is None:
                place = (qui, json.dumps(k["memo"], ensure_ascii=False))
                retenue = p._MEMOIRE.get(place)
                if (retenue is not None and hashlib.sha256(repr(retenue[0][0][0]).encode()).hexdigest()
                        == r.get("entrees")):
                    r["signature_complete"] = hashlib.sha256(repr(retenue[0][0]).encode()).hexdigest()
            lignes.append(r)
            diag = r.get("diagnostic", {})
            cle = (qui, r["but"], diag.get("issue"))
            if qui in ("joss", "tilo") and r["but"] == "faim" and diag.get("noeuds") and cle not in sauvegardees:
                nom = f"{args.scenario}-{qui}-{diag['issue']}-{r['minute']:g}.json.gz"
                (sortie.parent / nom).write_bytes(gzip.compress(json.dumps(monde.data, ensure_ascii=False).encode()))
                r["capture"] = nom
                sauvegardees.add(cle)
        if int(monde.data["minutes"] // 60) > heure[0]:
            heure[0] = int(monde.data["minutes"] // 60)
            print(f"{args.scenario} {heure[0]} h", flush=True)
        return resultat

    def creer_observe(*a, **k):
        capture["monde"] = creer(*a, **k)
        return capture["monde"]

    p.chercher, p._entrees, banc_pnj.creer = observer, observer_entrees, creer_observe
    resume = empreintes.nuit(".", args.scenario, 1985, 12, "tire")
    monde = capture["monde"]
    monde.sauver(sortie.with_suffix(".monde.json"))
    recharge = Monde.charger(sortie.with_suffix(".monde.json"))
    controles = {"monde": monde.data == recharge.data, "regarder": regarder(monde) == regarder(recharge),
                 "scene": scene_percue(monde) == scene_percue(recharge)}
    assert all(controles.values()), controles
    sortie.write_text(json.dumps({"resume": resume, "recharge": controles, "recherches": lignes},
                                ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps({"noeuds": resume["noeuds"], "sortie": str(sortie), "recharge": controles}), flush=True)


if __name__ == "__main__":
    main()
