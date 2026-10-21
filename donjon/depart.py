"""Le départ tiré de la graine : la même règle pour tout scénario, sans branche par scénario.

Un scénario déclare un état de départ (le corps de chaque PNJ, ses besoins, ses rondes, les
horloges). Ce départ est une valeur centrale : à la création du monde, le moteur en tire une
variante dans des bornes, par un tirage qui lui est propre (``random.Random(f"{seed}:depart")``),
comme le niveau d'eau (``eau.py``) : les jets de la partie (``Monde.d20``) ne s'en trouvent pas
décalés. Le tirage est fait une fois, quand le monde est créé (minute 0), et vit dans
``data["depart"]`` avec les valeurs appliquées : un rechargement ne tire plus rien.

Ce qui est tiré, pour chaque PNJ qui a un profil, puis pour chaque horloge :

- **le corps** : minutes depuis le dernier repas, de veille, passées trempé, à ``corps`` près
  (écart relatif) de leur valeur déclarée ; un état déclaré nul le reste (qui est au sec y
  reste) ;
- **les besoins du profil** (devoir, biens, sécurité…), à ``besoins`` points près ;
- **les rondes** : chaque période, à ``periodes`` près (écart relatif) ; puis la phase, le temps
  écoulé depuis la dernière ronde, entre 0 et ``rondes`` fois la période (une ronde qui vient
  d'être faite, ou qui est due dès le départ) ;
- **l'échéance d'une horloge**, à ``horloges`` près (écart relatif).

Aucun tirage ne mène un besoin au-delà de ``PLAFOND``, sauf si le scénario l'y a déjà déclaré
(alors au-delà de sa valeur déclarée) : personne n'est à l'extrême dès la première minute. Le
scénario déclare ses bornes (``data["depart"]["bornes"]``) ; celles qu'il ne déclare pas valent
``DEFAUT``. ``data["depart"]["mode"] == "fixe"`` garde le départ déclaré (pour comparer, au banc).
"""
import random

# Écarts par défaut : un repas ou une veille d'une heure ou deux plus tôt ou plus tard, quelques
# points d'inquiétude ou de devoir, des rondes décalées sur toute leur période.
DEFAUT = {"corps": 0.2, "besoins": 10, "rondes": 0.5, "periodes": 0.2, "horloges": 0.25}
PLAFOND = 85           # sous l'extrême du corps (95) et le désespoir (95) : au moins une heure et
                       # demie de faim avant qu'elle ne lève toute précaution
MODES = ("tire", "fixe")


def bornes(monde):
    return {**DEFAUT, **monde.data.get("depart", {}).get("bornes", {})}


def _profils(monde):
    return sorted(id for id, o in monde.objets.items() if o.get("type") == "personnage" and o.get("profil"))


def _ecart(r, valeur, relatif):
    return valeur * (1 + r.uniform(-relatif, relatif))


def installer(monde):
    """À la création du monde, tire et applique le départ ; ensuite, plus rien."""
    d = monde.data.setdefault("depart", {})
    d.setdefault("mode", "tire")
    if d["mode"] == "fixe" or "tirage" in d or monde.data.get("minutes", 0) != 0:
        return
    from .corps import CORPS, FAITS, corps, depart as ressenti
    b, r = bornes(monde), random.Random(f'{monde.data["seed"]}:depart')
    tirage = {"corps": {}, "besoins": {}, "periodes": {}, "visites": {}, "horloges": {}}
    for id in _profils(monde):
        # L'esprit n'est pas encore installé (``esprits.installer`` le complète ensuite) : seuls
        # ses besoins et ses visites reçoivent le tirage, comme un scénario les déclarerait.
        o = monde.objets[id]
        declare_esprit = monde.data.setdefault("esprits", {}).setdefault(id, {})
        e = {"besoins": declare_esprit.setdefault("besoins", {}), "visites": declare_esprit.setdefault("visites", {})}
        # Le corps : chaque état, puis le plafond de ce qu'il fait éprouver.
        faits = corps(monde, id)
        declare = ressenti(faits)
        for nom in FAITS:
            valeur = max(0, round(_ecart(r, faits.get(nom, 0), b["corps"])))
            for besoin in CORPS:
                par_minute = ressenti({nom: 60})[besoin] / 60
                plafond = max(PLAFOND, declare[besoin])
                if par_minute and valeur * par_minute > plafond:
                    valeur = int(plafond / par_minute)
            faits[nom] = valeur
        tirage["corps"][id] = {nom: faits[nom] for nom in FAITS}
        # Les besoins du profil.
        besoins = {}
        for nom, x in sorted(o["profil"]["besoins"].items()):
            valeur = x["depart"] + r.uniform(-b["besoins"], b["besoins"])
            besoins[nom] = round(min(max(PLAFOND, x["depart"]), max(0.0, valeur)), 3)
        e["besoins"].update(besoins)
        tirage["besoins"][id] = besoins
        # Les rondes : la période, puis le temps écoulé depuis la dernière (la plus courte d'un lieu).
        periodes, phases = [], {}
        for x in o["profil"]["pulsions"]:
            c = x["condition"]
            if "periode" not in c:
                periodes.append(None)
                continue
            c["periode"] = max(1, round(_ecart(r, c["periode"], b["periodes"])))
            periodes.append(c["periode"])
            phases[c["lieu"]] = min(phases.get(c["lieu"], c["periode"]), c["periode"])
        tirage["periodes"][id] = periodes
        visites = {}
        for lieu, periode in sorted(phases.items()):
            if lieu not in e["visites"]:
                # La prochaine ronde tombe entre la minute 0 et ``rondes`` fois la période : la
                # dernière a été faite une période plus tôt.
                visites[lieu] = r.randint(0, int(b["rondes"] * periode)) - periode
        e["visites"].update(visites)
        tirage["visites"][id] = visites
    for h in sorted(monde.data.get("horloges", []), key=lambda h: h["id"]):
        h["minute"] = max(0, round(_ecart(r, h["minute"], b["horloges"])))
        tirage["horloges"][h["id"]] = h["minute"]
    d["tirage"] = tirage


def verifier(monde):
    d = monde.data.get("depart", {})
    assert isinstance(d, dict) and d.get("mode", "tire") in MODES, "Départ invalide"
    assert (isinstance(d.get("bornes", {}), dict) and set(d.get("bornes", {})) <= set(DEFAUT)
            and all(isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0
                    for v in d.get("bornes", {}).values())), "Bornes de départ invalides"
    assert "tirage" not in d or (isinstance(d["tirage"], dict)
                                 and set(d["tirage"]) == {"corps", "besoins", "periodes", "visites", "horloges"}), \
        "Tirage de départ invalide"
