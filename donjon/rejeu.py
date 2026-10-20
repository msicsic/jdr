"""Le rejeu d'une nuit du banc : où est chacun, vers où il regarde, ce qu'il veut, ce qu'il voit
et ce qu'il croit, instant par instant.

L'enregistreur observe la nuit sans la changer : après chaque geste et à chaque délibération, il
note ce qui a bougé depuis la fois précédente. C'est une vue d'atelier, omnisciente, pas celle
du joueur. ``page`` en tire une page autonome qui rejoue la nuit (``web/rejeu.html``).
"""
from contextlib import contextmanager
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
        self.etats, self.vues, self.esprits = [], [], []
        self._etat, self._vue, self._esprit = {}, {}, {}
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
        for id in self.personnages:
            self._penser(monde, id)  # Ce qu'il vient de voir change ce qu'il croit.

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
        autres = {k: v for k, v in self._esprit.items() if not k.startswith(id + "|")}
        self._piste(self.esprits, self._esprit, self._instant(monde), {**autres, **esprit})

    @contextmanager
    def observer(self):
        from . import deliberation, pnj
        deliberer, temoigner = deliberation.deliberer, pnj.temoigner_en_cours

        def _deliberer(monde, id, minute):
            resultat = deliberer(monde, id, minute)
            if id in self.personnages:
                self._penser(monde, id)
            return resultat

        def _temoigner(monde):
            resultat = temoigner(monde)
            self._noter(monde)
            return resultat
        with patch.object(deliberation, "deliberer", _deliberer), patch.object(pnj, "temoigner_en_cours", _temoigner):
            yield self

    def donnees(self, monde, chronique, titre=""):
        return {"titre": titre, "fin": self._instant(monde), "minute": MINUTE,
                "salles": self.salles, "cases": self.cases, "objets": self.objets,
                "personnages": self.personnages, "joueur": self.joueur,
                "etats": self.etats, "vues": self.vues, "esprits": self.esprits,
                "chronique": [{"minute": c["minute"], "pnj": c.get("pnj"), "texte": c["texte"]} for c in chronique]}


def page(donnees):
    """La page de rejeu, autonome : les données y sont incluses."""
    contenu = json.dumps(donnees, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return MODELE.read_text(encoding="utf-8").replace("/*DONNEES*/null", contenu)
