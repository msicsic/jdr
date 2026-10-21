"""Le rejeu d'une nuit du banc : où est chacun, vers où il regarde, ce qu'il veut, ce qu'il voit
et ce qu'il croit, instant par instant.

L'enregistreur observe la nuit sans la changer : après chaque geste et à chaque délibération, il
note ce qui a bougé depuis la fois précédente. C'est une vue d'atelier, omnisciente, pas celle
du joueur. ``page`` en tire une page autonome qui rejoue la nuit (``web/rejeu.html``).

Pistes (suites de [instant en dixièmes, changements]) : ``etats``, ``vues``, ``esprits`` et
``lumiere`` (le degré de chaque case, comme la page de jeu : 0 noire, 1 diffuse, 2 directe,
3 pleine). Événements datés : ``bruits`` (chaque bruit émis, avec ce que chacun qui l'a entendu en
a fait), ``gestes`` (les gestes illicites : qui était là, qui en a été témoin et quand) et
``evenements`` (les « aller voir »). Rien de tout cela n'est lu par le jeu.
"""
from contextlib import ExitStack, contextmanager
import json
from pathlib import Path
from unittest.mock import patch

from .esprits import lire, pnjs
from .francais import designer
from .temps import MINUTE

MODELE = Path(__file__).with_name("web") / "rejeu.html"


def _plan(monde):
    """La géométrie de toutes les salles, en cases numérotées dans le repère de leur niveau."""
    from .geometrie import cases
    salles, liste, index = {}, [], {}
    for id, piece in monde.data["salles"].items():
        if "plan" not in piece:
            continue
        ox, oy = piece["plan"]["origine"]
        niveau = piece.get("niveau") or 0
        for x, y in sorted(cases(piece)):
            index[(id, x, y)] = len(liste)
            liste.append([niveau, ox + x, oy + y, id])
        salles[id] = {"nom": piece["nom"], "niveau": niveau, "origine": [ox, oy],
                      "sorties": [{"globale": [ox + s["case"][0], oy + s["case"][1]], "vers": s.get("vers"),
                                   "porte": s.get("porte"), "escalier": bool(s.get("escalier"))}
                                  for s in piece["sorties"].values() if "case" in s]}
    return salles, liste, index


class Enregistreur:
    def __init__(self, monde):
        self.salles, self.cases, self._index = _plan(monde)
        self.objets = {id: {"nom": designer(o), "type": o["type"], **({"foyer": True} if o.get("foyer") else {})}
                       for id, o in monde.objets.items()}
        self.personnages = [id for id in pnjs(monde) if monde.objets[id].get("profil")]
        self.joueur = {"salle": monde.joueur["salle"], "case": monde.joueur.get("position"),
                       "orientation": monde.joueur.get("orientation")}
        # Chaque piste : une suite de [instant en dixièmes, changements].
        self.etats, self.vues, self.esprits, self.lumiere = [], [], [], []
        self._etat, self._vue, self._esprit, self._lum = {}, {}, {}, {}
        self.bruits, self.gestes, self.evenements = [], [], []
        self._signature = self._bruit = self._issue = None
        self._geste_de = {}
        self._noter(monde)

    @staticmethod
    def _instant(monde):
        return monde.data["minutes"] * MINUTE + monde.data.get("dixiemes", 0)

    @staticmethod
    def _piste(piste, memoire, instant, valeurs):
        changes = {k: v for k, v in valeurs.items() if memoire.get(k) != v}
        changes.update({k: None for k in memoire if k not in valeurs})
        if not changes:
            return
        memoire.clear()
        memoire.update(valeurs)
        if piste and piste[-1][0] == instant:
            piste[-1][1].update(changes)
        else:
            piste.append([instant, changes])

    def _noter(self, monde):
        """Positions, regards, portes et flammes ; ce que chaque PNJ voit et croit."""
        from .spatial import champ_visible
        etat = {}
        for id, o in monde.objets.items():
            if o["type"] == "personnage":
                etat[id] = [o["lieu"], o.get("position"), o.get("orientation")]
            elif o["type"] == "porte":
                etat[id] = [bool(o.get("ouverte")), bool(o.get("verrouillee"))]
            else:
                etat[id] = [o.get("lieu"), o.get("position"), o.get("allume")]
        instant = self._instant(monde)
        self._piste(self.etats, self._etat, instant, etat)
        vues = {}
        for id in self.personnages:
            vus = champ_visible(monde, id)
            vus = vus.items() if isinstance(vus, dict) else ((s, (x, y)) for s, x, y in vus)
            vues[id] = sorted(i for i in (self._index.get((s, *p)) for s, p in vus) if i is not None)
        self._piste(self.vues, self._vue, instant, vues)
        self._eclairer(monde, instant)
        for id in self.personnages:
            self._penser(monde, id)  # Ce qu'il vient de voir change ce qu'il croit.

    def _eclairer(self, monde, instant):
        """Le degré de lumière de chaque case, recalculé quand ce dont dépend la lumière change
        (``spatial.signature_vue`` : portes, sources allumées et leur case, obstacles opaques)."""
        from .spatial import signature_vue
        signature = signature_vue(monde)
        if signature == self._signature:
            return
        self._signature = signature
        from .perception import CarteLumiere
        degres, cartes = {}, []
        for id, piece in monde.data["salles"].items():
            if "plan" not in piece:
                continue
            carte = next((c for c in cartes if id in c.salles), None)
            if carte is None:
                carte = CarteLumiere(monde, id)
                cartes.append(carte)
            for (salle, x, y), g in carte.geometrie.sol:
                if salle != id or (salle, x, y) not in self._index:
                    continue
                niveau = carte.niveau(g)
                degres[str(self._index[salle, x, y])] = 3 if niveau == 2 else 2 if carte.directe(g) else 1 if niveau else 0
        self._piste(self.lumiere, self._lum, instant, degres)

    def _penser(self, monde, id):
        """Son but, ses besoins et où il croit chaque chose."""
        from .recit_pnj import but_en_mots
        e = lire(monde, id)
        i = e["intention"]
        # Une clé par chose suivie (« id|:but », « id|objet ») : seul ce qui change est noté.
        esprit = {f"{id}|:but": [but_en_mots(monde, i["but"]), i["motif"]] if i else None,
                  f"{id}|:besoins": {k: round(v) for k, v in e["besoins"].items()}}
        for objet, croyance in e["croyances"].items():
            lieu = croyance.get("lieu")
            if lieu:
                esprit[f"{id}|{objet}"] = [lieu.get("valeur"), lieu.get("salle"), lieu.get("case")]
        salles = monde.data["salles"]
        esprit[f"{id}|:bruits"] = sorted([salles[m["salle"]]["nom"], m["nature"]]
                                         for m in e["memoire"] if m["type"] == "bruit" and m["salle"] in salles) or None
        avant = self._esprit.get(f"{id}|:but")
        if i and i["but"]["type"] == "voir" and (not avant or avant[0] != esprit[f"{id}|:but"][0]):
            self.evenements.append({"t": self._instant(monde), "pnj": id, "nature": "voir",
                                    "texte": f"{designer(monde.objets[id], debut=True)} part {esprit[f'{id}|:but'][0]}"
                                             + (f" ({i['motif']})" if i["motif"] else "") + "."})
        autres = {k: v for k, v in self._esprit.items() if not k.startswith(id + "|")}
        self._piste(self.esprits, self._esprit, self._instant(monde), {**autres, **esprit})

    def _case(self, monde, qui):
        """(salle, case) de ``qui`` et le numéro de sa case dans le plan."""
        from .ouie import _place
        salle, case = _place(monde, qui)
        return salle, case, (self._index.get((salle, *case)) if case is not None else None)

    @contextmanager
    def observer(self):
        from . import deliberation, ouie, pnj, social
        deliberer, temoigner = deliberation.deliberer, pnj.temoigner_en_cours
        retentir, entendre, attribuer = ouie.retentir, ouie.entendre, ouie._attribuer
        se_tourner, bruit_inconnu = ouie._se_tourner, ouie._bruit_inconnu
        retenir, commencer, temoins = social.retenir_parole, pnj.commencer_geste, pnj._temoins

        def _deliberer(monde, id, minute):
            resultat = deliberer(monde, id, minute)
            if id in self.personnages:
                self._penser(monde, id)
            return resultat

        def _temoigner(monde):
            resultat = temoigner(monde)
            self._noter(monde)
            return resultat

        def _retentir(monde, auteur, geste, discret=False, bruit=0, texte="", cites=(), parole=None, vers=()):
            n = ouie.nature(geste, discret, bruit)
            salle, case, numero = self._case(monde, auteur)
            evenement, precedent = None, self._bruit
            if n is not None and salle in monde.data["salles"]:
                evenement = {"t": self._instant(monde), "a": auteur, "n": n, "c": numero, "r": []}
                if texte:
                    evenement["x"] = texte[:160]
            self._bruit = evenement
            try:
                return retentir(monde, auteur, geste, discret, bruit, texte, cites, parole, vers)
            finally:
                self._bruit = precedent
                if evenement is not None:
                    self.bruits.append(evenement)

        def _entendre(monde, id, auteur, salle, case, n, t, niveau=ouie.SEUIL):
            precedent, self._issue = self._issue, []
            try:
                retourne = entendre(monde, id, auteur, salle, case, n, t, niveau)
                if self._bruit is not None and id in self.personnages:
                    self._bruit["r"].append([id, niveau, "+".join(self._issue) or "vu"])
                return retourne
            finally:
                self._issue = precedent

        def _marquer(code, fonction):
            def marque(*arguments, **suite):
                resultat = fonction(*arguments, **suite)
                if self._issue is not None and (code != "tourne" or resultat):
                    self._issue.append(code)
                return resultat
            return marque

        def _retenir(monde, id, locuteur, destinataires, texte, cites, contenu):
            retenir(monde, id, locuteur, destinataires, texte, cites, contenu)
            if self._bruit is not None and id in self.personnages:
                self._bruit["r"].append([id, None, "parole"])

        def _commencer(monde, auteur, operation, objet, fin, exclus=()):
            geste = commencer(monde, auteur, operation, objet, fin, exclus)
            salle, case, numero = self._case(monde, auteur)
            self._noter(monde)
            maintenant = self._instant(monde)
            enregistre = {"t": maintenant, "fin": fin, "a": auteur, "op": operation, "objet": objet, "c": numero,
                          "salle": salle,
                          "voient": [x for x in self.personnages if x != auteur and numero is not None
                                     and numero in self._vue.get(x, ())],
                          "dans_la_salle": [x for x in self.personnages if x != auteur and monde.objets[x]["lieu"] == salle],
                          "temoins": [[x, maintenant] for x in geste["temoins"]]}
            self.gestes.append(enregistre)
            self._geste_de[id(geste)] = (geste, enregistre)
            return geste

        def _temoins(monde, geste, souvenir, victime):
            deja = len(geste["temoins"])
            resultat = temoins(monde, geste, souvenir, victime)
            lie = self._geste_de.get(id(geste))
            if lie is not None and lie[0] is geste:
                lie[1]["temoins"] += [[x, self._instant(monde)] for x in geste["temoins"][deja:]]
            return resultat
        with ExitStack() as pile:
            for module, nom, remplacant in (
                    (deliberation, "deliberer", _deliberer), (pnj, "temoigner_en_cours", _temoigner),
                    (ouie, "retentir", _retentir), (ouie, "entendre", _entendre),
                    (ouie, "_attribuer", _marquer("attribue", attribuer)), (ouie, "_se_tourner", _marquer("tourne", se_tourner)),
                    (ouie, "_bruit_inconnu", _marquer("bruit", bruit_inconnu)), (social, "retenir_parole", _retenir),
                    (pnj, "commencer_geste", _commencer), (pnj, "_temoins", _temoins)):
                pile.enter_context(patch.object(module, nom, remplacant))
            yield self

    def donnees(self, monde, chronique, titre=""):
        return {"titre": titre, "fin": self._instant(monde), "minute": MINUTE,
                "salles": self.salles, "cases": self.cases, "objets": self.objets,
                "personnages": self.personnages, "joueur": self.joueur,
                "etats": self.etats, "vues": self.vues, "esprits": self.esprits, "lumiere": self.lumiere,
                "bruits": self.bruits, "gestes": self.gestes,
                "chronique": sorted([{"minute": c["minute"], "t": c["minute"] * MINUTE, "pnj": c.get("pnj"),
                                      "texte": c["texte"], "nature": c.get("nature", "geste")} for c in chronique]
                                    + [{"minute": e["t"] // MINUTE, **e} for e in self.evenements],
                                    key=lambda c: c["t"])}


def page(donnees):
    """La page de rejeu, autonome : les données y sont incluses."""
    contenu = json.dumps(donnees, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return MODELE.read_text(encoding="utf-8").replace("/*DONNEES*/null", contenu)
