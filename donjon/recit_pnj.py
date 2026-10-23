"""Récit du banc sans joueur : ce que chaque PNJ a voulu, tenté et obtenu, et ce qui s'est
passé entre eux.

La chronique dit chaque pas ; le récit en tire l'histoire. Pour chaque PNJ : ses buts
successifs avec les gestes faits pour eux, les rondes résumées, les besoins qui l'ont pressé
et les minutes où rien ne s'offrait à lui. Entre eux : les échanges et leur issue, les gestes
illicites vus, ce qu'ils pensent les uns des autres à la fin. Le banc observe chaque PNJ
après sa délibération de la minute, sans rien changer au monde.
"""
from collections import Counter
from contextlib import contextmanager
import json
from unittest.mock import patch

from . import relations
from .esprits import lire, pnjs
from .temps import instant
from .francais import accorder, de, designer

MOTIFS = {"devoir": "devoir", "biens": "biens", "securite": "sécurité", "faim": "faim", "repos": "fatigue",
          "chaleur": "froid", "engagement": "parole donnée", "alerte": "alerte", "menager": "ménager la flamme",
          "argent": "argent"}
BESOINS = {"securite": "sécurité", "repos": "fatigue", "chaleur": "froid"}
GESTES = {"prendre": "prendre", "ouvrir": "ouvrir", "crocheter": "crocheter", "manger": "manger",
          "deverrouiller": "déverrouiller", "poser": "poser", "pousser": "pousser", "frapper": "frapper", "assommer": "assommer", "dans_le_dos": "approcher dans le dos",
          "briser": "forcer"}


def court(monde, id):
    if id == "joueur":
        return "le joueur"
    return monde.objets[id]["nom"].split(",")[0] if id in monde.objets else id


def _salle(monde, id):
    return monde.data["salles"][id]["nom"] if id in monde.data["salles"] else str(id)


def _objet(monde, id):
    if id == "joueur":
        return court(monde, id)
    return designer(monde.objets[id]) if id in monde.objets else str(id)


def but_en_mots(monde, but):
    mots = _but(monde, but)
    return mots.replace(" à le ", " au ").replace(" à les ", " aux ")


def _but(monde, but):
    t, o = but.get("type"), but.get("objet")
    if t in ("fuir", "riposter", "proteger", "reddition"):
        return {"fuir": "fuir ", "riposter": "riposter contre ", "proteger": "protéger ",
                "reddition": "se rendre à "}[t] + court(monde, but["qui"])
    if t == "degager":
        return "se dégager"
    if t == "ranimer":
        return "ranimer " + court(monde, but["qui"])
    if t == "manger":
        return "manger " + _objet(monde, o)
    if t == "part":
        return f"obtenir une part ({_objet(monde, o)}) {de(court(monde, but['de']))}"
    if t == "chaleur":
        return "se chauffer à " + _objet(monde, o)
    if t == "repos":
        return "se reposer"
    if t == "abri":
        return "se mettre à l'abri : " + _salle(monde, but["lieu"])
    if t == "lumiere":
        return "avoir de la lumière"
    if t == "garder":
        return "garder ses biens : " + _salle(monde, but["lieu"])
    if t == "prevenir":
        return "prévenir " + court(monde, but["qui"])
    if t == "attendre":
        return "attendre que " + court(monde, but["qui"]) + " le rejoigne"
    if t == "rejoindre":
        return "accourir : " + _salle(monde, but["lieu"])
    if t == "voir":
        return "aller voir d'où venait un bruit : " + _salle(monde, but["lieu"])
    if t == "strategie":
        return "stratégie : " + but.get("resume", "")
    if t == "menager":
        return "éteindre " + _objet(monde, o)
    if t == "argent":
        return "prendre des pièces : " + _objet(monde, o)
    if t == "reclamer":
        return "réclamer son dû à " + court(monde, but["qui"])
    if t == "pulsion":
        if "periode" in but:
            return "ronde : " + _salle(monde, but["lieu"])
        if "servir" in but:
            return f"servir {_objet(monde, o)} à {court(monde, but['servir'])}"
        if "allume" in but:
            return "entretenir " + _objet(monde, o)
        if "rendre" in but:
            return f"rendre {_objet(monde, o)} à {court(monde, but['rendre'])}"
        if "verrouillee" in but:
            return f"garder {_objet(monde, o)} sous clé"
        if "lieu" in but:
            return f"mettre {_objet(monde, o)} : {_salle(monde, but['lieu'])}"
    return json.dumps(but, ensure_ascii=False)


class Recit:
    def __init__(self, monde):
        ids = [id for id in pnjs(monde) if monde.objets[id].get("profil")]
        self.ids = ids
        self.episodes = {id: [] for id in ids}
        self.souvenirs = {id: [] for id in ids}
        self._vus = {id: set() for id in ids}
        self._derniere = {id: -1 for id in ids}
        self.urgence = {id: Counter() for id in ids}
        self.maximum = {id: Counter() for id in ids}
        self.sans_recours = Counter()
        self.en_attente = Counter()
        self._relations = {(id, x): relations.axes(monde, id, x)["bandes"]
                           for id in ids for x in relations.connus(monde, id)}
        self.changements_relations = []

    @contextmanager
    def observer(self):
        from . import deliberation
        originale, choix = deliberation.deliberer, deliberation.choisir

        def deliberer(monde, id, minute):
            resultat = originale(monde, id, minute)
            if id in self.episodes:
                self._noter(monde, id, minute)
            return resultat

        def choisir(monde, id, minute):
            # Un but choisi entre deux minutes (fin de plan, geste manqué, événement) compte aussi.
            resultat = choix(monde, id, minute)
            if id in self.episodes:
                self._episode(monde, id, minute)
            return resultat
        with patch.object(deliberation, "deliberer", deliberer), patch.object(deliberation, "choisir", choisir):
            yield self

    def _noter(self, monde, id, minute):
        from .deliberation import attentes, seuils, urgents
        e = lire(monde, id)
        for x in relations.connus(monde, id):
            r = relations.axes(monde, id, x)
            cle = (id, x)
            avant = self._relations.get(cle, relations._bandes(relations.ETRANGER))
            if avant != r["bandes"]:
                detail = relations.envers(monde, id, x)
                self.changements_relations.append({"minute": minute, "de": id, "envers": x,
                                                  "bandes": r["bandes"], "resume": relations.resume(detail), "motifs": detail["motifs"]})
            self._relations[cle] = r["bandes"]
        # Souvenirs nouveaux depuis sa dernière délibération (les sons sont le fond du monde).
        for s in e["memoire"]:
            cle = json.dumps(s, sort_keys=True, ensure_ascii=False)
            if s["minute"] >= self._derniere[id] and cle not in self._vus[id] and s["type"] != "son":
                self._vus[id].add(cle)
                self.souvenirs[id].append(dict(s))
        self._vus[id] = {c for c in self._vus[id] if json.loads(c)["minute"] >= minute - 1}
        self._derniere[id] = minute
        limites = seuils(monde, id)
        for nom, valeur in e["besoins"].items():
            self.maximum[id][nom] = max(self.maximum[id][nom], valeur)
            if valeur >= limites.get(nom, 101):
                self.urgence[id][nom] += 1
        i = e["intention"]
        if i is None and urgents(monde, id):
            if set(urgents(monde, id)) <= set(attentes(monde, id)):
                self.en_attente[id] += 1
            else:
                self.sans_recours[id] += 1
        self._episode(monde, id, minute)

    def _episode(self, monde, id, minute):
        """Le but en cours : il prolonge l'épisode courant ou en ouvre un autre."""
        i = lire(monde, id)["intention"]
        cle = (json.dumps(i["but"], sort_keys=True), i["motif"]) if i else None
        episodes = self.episodes[id]
        courant = episodes[-1] if episodes and episodes[-1]["fin"] is None else None
        if courant and courant["cle"] == cle:
            return
        if courant:
            courant["fin"] = minute - 1
            courant["t_fin"] = instant(monde)  # Ses gestes s'arrêtent là, au dixième (``_gestes``).
        if cle is None:
            return
        precedent = episodes[-1] if episodes else None
        if precedent and precedent["cle"] == cle and minute - precedent["fin"] <= 2:
            precedent["fin"] = precedent["t_fin"] = None  # Un battement d'une minute ne coupe pas le même but.
            return
        episodes.append({"cle": cle, "but": dict(i["but"]), "motif": i["motif"], "debut": minute, "fin": None,
                         "t": instant(monde), "t_fin": None})

    def clore(self, monde):
        for id in self.ids:
            for ep in self.episodes[id]:
                if ep["fin"] is None:
                    ep["fin"] = monde.data["minutes"]
                ep["abandon"] = any(s["type"] == "renoncement" and s["but"] == ep["but"]
                                    and ep["debut"] <= s["minute"] <= ep["fin"] + 1 for s in self.souvenirs[id])

    # --- Rendu ------------------------------------------------------------------------------

    def _gestes(self, monde, id, chronique, debut, fin, t=None, t_fin=None):
        """Ses gestes pendant un but : de ``debut`` à ``fin`` (minutes), départagés à l'instant
        (``t`` inclus, ``t_fin`` exclu) quand la chronique le porte."""
        noms = sorted({monde.objets[id]["nom"], court(monde, id)}, key=len, reverse=True)
        gestes = []
        for c in chronique:
            if "instant" in c and t is not None:
                dedans = t <= c["instant"] and (t_fin is None or c["instant"] < t_fin)
            else:
                dedans = debut <= c["minute"] <= fin
            if c["pnj"] != id or not dedans or c.get("nature") in ("deplacement", "ouie", "reponse", "relation"):
                continue
            texte = c["texte"].rstrip(".")
            for nom in noms:
                if texte.startswith(nom + " "):
                    texte = texte[len(nom) + 1:]
                    break
            gestes.append(texte)
        return gestes

    def personnage(self, monde, id, chronique):
        lignes = [f"== {monde.objets[id]['nom']} =="]
        pressants = [f"{BESOINS.get(n, n)} {m} min (max {self.maximum[id][n]:.0f})"
                     for n, m in sorted(self.urgence[id].items(), key=lambda x: -x[1]) if m]
        lignes.append("  Pressé par : " + (", ".join(pressants) if pressants else "rien"))
        if self.sans_recours[id]:
            lignes.append(f"  Pressé sans rien entreprendre : {self.sans_recours[id]} min")
        if self.en_attente[id]:
            lignes.append(f"  Pressé, en attente d'un moyen : {self.en_attente[id]} min")
        rondes, sans_geste, faits = Counter(), {}, []
        for ep in self.episodes[id]:
            mots = but_en_mots(monde, ep["but"])
            gestes = self._gestes(monde, id, chronique, ep["debut"], ep["fin"], ep.get("t"), ep.get("t_fin"))
            if ep["but"].get("periode") and not ep["abandon"] and all(g.startswith("inspecte") for g in gestes):
                rondes[mots.removeprefix("ronde : ")] += 1
                continue
            if not gestes and not ep["abandon"]:
                # Aller voir sans avoir à agir : résumé comme les rondes.
                sans_geste.setdefault(f"{mots} ({MOTIFS.get(ep['motif'], ep['motif'])})", []).append(ep["debut"])
                continue
            mots = f"{mots} ({MOTIFS.get(ep['motif'], ep['motif'])})"
            if faits and faits[-1]["mots"] == mots and not faits[-1]["abandon"] and ep["debut"] - faits[-1]["fin"] <= 3:
                faits[-1].update(fin=ep["fin"], abandon=ep["abandon"], gestes=faits[-1]["gestes"] + gestes)
                continue
            faits.append({"mots": mots, "debut": ep["debut"], "fin": ep["fin"], "abandon": ep["abandon"],
                          "gestes": gestes})
        for f in faits:
            issue = " — abandonné" if f["abandon"] else ""
            detail = " : " + " ; ".join(f["gestes"]) if f["gestes"] else ""
            lignes.append(f"  {f['debut']:>4}–{f['fin']:<4} {f['mots']}{issue}{detail}")
        if rondes:
            lignes.append("  Rondes : " + ", ".join(f"{s} ×{n}" for s, n in rondes.most_common()))
        for mots, debuts in sans_geste.items():
            lignes.append(f"  Sans geste à faire : {mots} ×{len(debuts)} ({', '.join(map(str, debuts))})")
        lignes += self._ouie(id, chronique)
        return lignes

    @staticmethod
    def _ouie(id, chronique):
        """Ce qu'il a entendu : combien de fois il s'est retourné au bruit, les bruits inconnus qu'il
        a retenus, par lieu, et ceux qu'il est allé voir."""
        ouie = [c for c in chronique if c["pnj"] == id and c.get("nature") == "ouie"]
        if not ouie:
            return []
        tours = sum(c["texte"].endswith("se retourne au bruit.") for c in ouie)
        lieux, vus = Counter(), Counter()
        for c in ouie:
            for marque, compte in ((" entend un bruit : ", lieux), (" va voir d'où venait le bruit : ", vus)):
                if marque in c["texte"]:
                    compte[c["texte"].split(marque, 1)[1].rstrip(".")] += 1
        parties = [f"se retourne au bruit ×{tours}"] if tours else []
        parties += [f"bruit inconnu : {s} ×{n}" for s, n in lieux.most_common()]
        parties += [f"va voir : {s} ×{n}" for s, n in vus.most_common()]
        return ["  Ouïe : " + ", ".join(parties)]

    def entre_eux(self, monde, chronique):
        lignes = ["== Entre eux =="]
        sociaux = [c for c in chronique if c.get("nature") in ("social", "reponse")]
        vus = [(s["minute"], f"{court(monde, id)} voit {court(monde, s['auteur'])} "
                f"{GESTES.get(s['operation'], s['operation'])} {_objet(monde, s['objet'])}")
               for id in self.ids for s in self.souvenirs[id] if s["type"] == "vu_agir"]
        tenus = [(s["minute"], f"{court(monde, id)} "
                 f"{'tient' if s['type'] == 'engagement_tenu' else 'abandonne'} sa parole envers {court(monde, s['pour'])}")
                 for id in self.ids for s in self.souvenirs[id]
                 if s["type"] in ("engagement_tenu", "engagement_abandonne") and "pour" in s]
        evenements = sorted([(c["minute"], c["texte"].rstrip(".")) for c in sociaux] + vus + tenus)
        # Une même scène répétée se lit une fois, avec ses minutes.
        groupes = {}
        for minute, texte in evenements:
            if minute not in groupes.get(texte, []):
                groupes.setdefault(texte, []).append(minute)
        for texte, minutes in sorted(groupes.items(), key=lambda x: x[1][0]):
            quand = ", ".join(str(m) for m in minutes)
            lignes.append(f"  {texte}" + (f" ×{len(minutes)} ({quand})" if len(minutes) > 1 else f" ({quand})"))
        if len(lignes) == 1:
            lignes.append("  aucun échange")
        lignes.append("== Ce qu'ils pensent les uns des autres ==")
        avant = len(lignes)
        changements = [c for c in chronique if c.get("nature") == "relation" and c.get("relation")]
        for c in changements:
            lignes.append(f"  {c['minute']} min : {c['texte']}")
        for c in self.changements_relations:
            if not any(x["pnj"] == c["de"] and x.get("relation") == c["envers"] and c["minute"] - 1 <= x["minute"] <= c["minute"] for x in changements):
                lignes.append(f"  {c['minute']} min : {court(monde, c['de'])} envers {court(monde, c['envers'])} : "
                              f"{c['resume']} (estompement ; motifs : {c['motifs']})")
        for id in self.ids:
            for autre in relations.connus(monde, id):
                r = relations.envers(monde, id, autre)
                if autre == id or (autre not in self.ids and autre != "joueur"):
                    continue
                if r["motifs"]:
                    motifs = "; ".join(f"{m['type']} à {m['minute']} ({m['effets']})" for m in r["motifs"])
                    lignes.append(f"  {court(monde, id)} envers {court(monde, autre)} : {relations.resume(r)} ({motifs})")
                    continue
                if relations.confiance(r):
                    if r["minute"] == 0:
                        continue  # La confiance de départ ne raconte rien.
                    avis = "fait confiance à"
                elif relations.mefiance(r):
                    avis = "se méfie de"
                else:
                    continue
                depuis = "depuis le début" if r["minute"] == 0 else f"depuis {r['minute']}, {r['source']}"
                lignes.append(f"  {court(monde, id)} {avis} {court(monde, autre)} ({depuis})")
        if len(lignes) == avant:
            lignes.append("  aucun changement de relation")
        return lignes

    def crue(self, monde):
        """Ce que l'eau a fait : le tirage, les salles gagnées puis noyées, les feux éteints, et où
        chacun se trouve à la fin."""
        from .eau import active, altitude, niveau, profondeur
        if not active(monde):
            return []
        crue = monde.data["crue"]
        x = crue["tirage"]
        lignes = ["== La crue ==",
                  f"  Tirage : montée {x['montee_cm_heure']} cm/h, pic à {x['minute_pic']} min, plafond "
                  f"{x['hauteur_pic_cm']:+d} cm, baisse {x['baisse_cm_heure']} cm/h ; niveau {niveau(monde, 0):+d} cm "
                  f"au départ, {niveau(monde, x['minute_pic']):+d} cm au pic, {niveau(monde):+d} cm à la fin."]
        mots = {"seche": "au sec", "mouillee": "mouillée", "noyee": "noyée"}
        for salle in sorted(monde.data["salles"], key=lambda s: altitude(monde, s)):
            etapes = [f"{mots[h['etat']]} à {h['minute']}" for h in crue["historique"]
                      if h.get("salle") == salle and "etat" in h]
            lignes.append(f"  {_salle(monde, salle)} ({altitude(monde, salle):+d} cm) : "
                          + (", ".join(etapes) if etapes else "au sec"))
        for h in crue["historique"]:
            if "eteint" in h:
                lignes.append(f"  {_objet(monde, h['eteint'])[:1].upper() + _objet(monde, h['eteint'])[1:]} "
                              f"s'éteint sous l'eau à {h['minute']} ({_salle(monde, h['salle'])}).")
        for id in self.ids:
            salle = monde.objets[id]["lieu"]
            p = profondeur(monde, salle)
            trempe = monde.objets[id].get("corps", {}).get("trempe")
            lignes.append(f"  À la fin, {court(monde, id)} : {_salle(monde, salle)}, "
                          + (f"dans {p} cm d'eau" if p else "au sec")
                          + (", " + accorder(monde.objets[id], "trempé") if trempe else ""))
        return lignes

    def texte(self, monde, chronique):
        lignes = []
        for id in self.ids:
            lignes += self.personnage(monde, id, chronique) + [""]
        crue = self.crue(monde)
        if monde.data.get("historique_corps"):
            from .corps import mesures
            lignes += ["== Violences et corps ==", ", ".join(f"{k} : {v:g}" for k, v in mesures(monde).items())]
            for e in monde.data["historique_corps"]:
                if e["type"] == "coup":
                    lignes.append(f"{e['instant'] / 600:.2f} min : {court(monde, e['auteur'])} frappe {court(monde, e['cible'])} : "
                                  f"{'touché' if e['touche'] else 'esquivé'}, {e['degats']} PV perdus"
                                  + (", assommé." if e["assomme"] else "."))
                if e["type"] == "mort_vue":
                    lignes.append(f"{court(monde, e['temoin'])} découvre {court(monde, e['id'])} après {e['delai']} min.")
        return "\n".join((crue + [""] if crue else []) + lignes + self.entre_eux(monde, chronique))

    def donnees(self, monde, chronique):
        return {"episodes": {id: [{k: v for k, v in ep.items() if k != "cle"} | {"mots": but_en_mots(monde, ep["but"])}
                                  for ep in self.episodes[id]] for id in self.ids},
                "urgence": {id: dict(self.urgence[id]) for id in self.ids},
                "sans_recours": dict(self.sans_recours), "en_attente": dict(self.en_attente),
                "souvenirs": self.souvenirs, "relations": self.changements_relations}
