"""Biens : ce qu'on peut faire du bien d'autrui (prêt, garde confiée, don), et l'argent.

Les mêmes règles valent pour le joueur et pour les PNJ.

**Permissions.** User du bien d'autrui est une faute, sauf permission que le moteur connaît :

- un **prêt** (``data["permissions"]``) : son propriétaire le remet à quelqu'un, qui en use sans
  faute jusqu'à ce que l'objet revienne entre les mains de son propriétaire (``deplacer`` clôt le
  prêt) ; le prêteur s'attend à le récupérer (souvenir ``pret``), l'emprunteur s'engage à le
  rendre quand il n'en a plus besoin (engagement ``rendre``) ;
- une **garde confiée** : une tâche qu'il a acceptée sur un bien de celui qui la lui confie
  (engagement ``pour`` son propriétaire), ou une pulsion que le propriétaire lui délègue
  (``delegue_a``) ; le délégué agit sans faute sur ce bien et sur les clés de son propriétaire
  qui l'ouvrent, tant que dure la tâche ;
- un **don** transfère la propriété (``proprietaire``) : ce qui se consomme se donne, ne se prête
  pas.

Aucune permission ne couvre ce qui consomme le bien (``CONSOMMER`` : le manger, en servir une
part) : ce qui se mange se donne ou se vend par parts.

**L'argent.** Chaque personnage a une bourse : ``data["finances_pnj"][id]`` pour un PNJ (absente :
``BOURSE``), ``joueur["or"]`` pour le joueur. Un objet peut contenir des pièces (``pieces`` : une
bourse, une paie) : qui le porte peut les dépenser. Une part d'une ressource comptée a un prix
(``prix_part``, sinon ``PRIX_PART``), un objet le sien s'il est déclaré (``prix``). Ce que vaut une
pièce pour chacun vient de ses besoins et de ses valeurs (``caractere.valeur_piece``).
"""
BOURSE = 5             # pièces d'un PNJ dont rien ne déclare la bourse
PRIX_PART = 2          # prix d'une part d'une ressource comptée qui n'en déclare pas
CONSOMMER = ("manger", "servir")   # gestes qui consomment le bien : aucune permission ne les couvre
BRISER = ("frapper",)              # gestes qui l'abîment (``force``) : aucune permission non plus
# Ce qu'il rechigne à donner sans être payé : un point de DD par GENEROSITE minutes de ce que vaut,
# pour lui, le prix qu'il n'est pas payé, au-delà de ce qu'il vaut pour qui vit modestement.
GENEROSITE = 2


# --- Permissions ------------------------------------------------------------------------

def proprietaire(monde, objet):
    from .vol import proprietaire as possesseur
    return possesseur(monde, monde.objets[objet])


def prets(monde):
    return monde.data.setdefault("permissions", [])


def prete_a(monde, objet):
    """À qui l'objet est prêté par son propriétaire, ou None."""
    p = next((p for p in prets(monde) if p["objet"] == objet), None)
    return p["a"] if p else None


def preter(monde, objet, a):
    """Son propriétaire remet l'objet à ``a`` : un prêt, que ``deplacer`` clôt quand l'objet lui
    revient. L'emprunteur PNJ s'engage à le rendre quand il n'en aura plus besoin."""
    de = proprietaire(monde, objet)
    liste = prets(monde)
    liste[:] = [p for p in liste if p["objet"] != objet]
    liste.append({"objet": objet, "a": a, "de": de, "minute": monde.data["minutes"]})
    if a != "joueur" and a in monde.objets and monde.objets[a].get("profil"):
        from .esprits import esprit
        condition = {"objet": objet, "rendre": de}
        engagements = esprit(monde, a)["engagements"]
        if not any(x["condition"] == condition for x in engagements):
            engagements.append({"condition": condition, "pour": de, "minute": monde.data["minutes"]})


def clore(monde, objet, destination):
    """L'objet arrive à ``destination`` : s'il revient à son propriétaire, le prêt est clos."""
    liste = monde.data.get("permissions")
    if liste and any(p["objet"] == objet and p["de"] == destination for p in liste):
        liste[:] = [p for p in liste if not (p["objet"] == objet and p["de"] == destination)]


def donner(monde, objet, a):
    """Le propriétaire le donne : ``a`` le possède désormais."""
    o = monde.objets[objet]
    o["proprietaire"] = a
    o.pop("vole_par", None)
    o.pop("vole_a", None)
    liste = monde.data.get("permissions")
    if liste:
        liste[:] = [p for p in liste if p["objet"] != objet]


def _cles(monde, objet, de):
    """L'objet et les clés de son propriétaire qui l'ouvrent : le périmètre d'une garde."""
    from .vol import proprietaire as possesseur
    return {objet} | {k for k, o in monde.objets.items() if objet in o.get("ouvre", []) and possesseur(monde, o) == de}


def gardes(monde, id, de):
    """Les biens de ``de`` dont la garde est confiée à ``id`` : une tâche qu'il a acceptée pour
    lui sur un de ses biens, ou une pulsion que ``de`` lui délègue (et qu'il lui confie encore)."""
    from .vol import proprietaire as possesseur
    confies = set()
    if id != "joueur" and id in monde.objets and monde.objets[id].get("profil"):
        from .esprits import lire
        for x in lire(monde, id)["engagements"]:
            o = x["condition"].get("objet")
            if x["pour"] == de and o in monde.objets and "rendre" not in x["condition"] \
                    and possesseur(monde, monde.objets[o]) == de:
                confies |= _cles(monde, o, de)
    p = (monde.objets.get(de) or {}).get("profil") or {}
    for x in p.get("pulsions", []):
        o = x["condition"].get("objet")
        if x.get("delegue_a") == id and o in monde.objets and possesseur(monde, monde.objets[o]) == de:
            from .deliberation import _delegue
            if _delegue(monde, de, x):
                confies |= _cles(monde, o, de)
    return confies


def permis(monde, id, objet, operation=None, confies=None):
    """``id`` peut-il, sans faute, faire ce geste sur le bien d'un autre ? Un prêt ou une garde
    confiée par son propriétaire, hors ce qui le consomme. User d'une clé prêtée, c'est ouvrir et
    fermer ce qu'elle ouvre (pas en prendre le contenu, qui n'est pas prêté). ``confies`` : les
    gardes confiées par propriétaire (un dictionnaire), quand on juge plusieurs objets à la fois."""
    if operation in CONSOMMER or operation in BRISER:
        return False
    de = proprietaire(monde, objet)
    for p in monde.data.get("permissions", ()):
        if p["a"] == id and p["de"] == de and p["objet"] in monde.objets and (
                p["objet"] == objet or objet in monde.objets[p["objet"]].get("ouvre", [])):
            return True
    if confies is None:
        return objet in gardes(monde, id, de)
    if de not in confies:
        confies[de] = gardes(monde, id, de)
    return objet in confies[de]


def a_autrui(monde, objet, id="joueur", operation=None, confies=None):
    """Le propriétaire dont ``id`` lèse le bien par ce geste, ou None : sans propriétaire, le sien,
    ce que le joueur a déjà dérobé, ou ce qu'une permission couvre (``confies`` : ``permis``)."""
    o = monde.objets[objet]
    de = proprietaire(monde, objet)
    if de in (None, id) or id == "joueur" and o.get("vole_par") == "joueur":
        return None
    return None if permis(monde, id, objet, operation, confies) else de


# --- Argent -------------------------------------------------------------------------------

def bourse(monde, id):
    """Sa bourse : l'or du joueur ; celle que le scénario déclare à un PNJ, sinon ``BOURSE``."""
    return monde.joueur["or"] if id == "joueur" else monde.data["finances_pnj"].get(id, BOURSE)


def bourses_portees(monde, id):
    """Les objets à pièces qu'il porte, dans un ordre stable."""
    from .spatial import porte_par
    return sorted(k for k, o in monde.objets.items() if o.get("pieces") and porte_par(monde, k, id))


def richesse(monde, id):
    """Ce qu'il peut dépenser : sa bourse et les pièces de ce qu'il porte."""
    return bourse(monde, id) + sum(monde.objets[k]["pieces"] for k in bourses_portees(monde, id))


def payer(monde, de, a, montant):
    """``de`` paie ``montant`` pièces à ``a`` : de sa bourse d'abord, puis de ce qu'il porte."""
    assert 0 < montant <= richesse(monde, de), "Paiement sans les moyens"
    reste = montant
    if de == "joueur":
        pris = min(reste, monde.joueur["or"])
        monde.joueur["or"] -= pris
    else:
        pris = min(reste, bourse(monde, de))
        monde.data["finances_pnj"][de] = bourse(monde, de) - pris
    reste -= pris
    for k in bourses_portees(monde, de):
        if reste <= 0:
            break
        pris = min(reste, monde.objets[k]["pieces"])
        monde.objets[k]["pieces"] -= pris
        reste -= pris
    if a == "joueur":
        monde.joueur["or"] += montant
    else:
        monde.data["finances_pnj"][a] = bourse(monde, a) + montant


def prix(monde, objet, part=False):
    """Le prix d'une part d'une ressource comptée, ou d'un objet qui en déclare un ; None sinon."""
    o = monde.objets[objet]
    if part:
        return o.get("prix_part", PRIX_PART)
    return o.get("prix")


def dettes(monde):
    return monde.data.setdefault("dettes", [])


def rembourser(monde, de, a, montant, objet):
    """Une part payée d'avance que ``de`` n'a pas servie à l'échéance (``echanges.engagements_echus``) :
    il doit rendre le prix à ``a``. La dette est connue des deux (souvenirs ``dette`` et ``creance``)
    et soldée dès qu'ils peuvent se parler (``solder``) : tout de suite s'ils le peuvent déjà."""
    from .esprits import memoriser
    dettes(monde).append({"de": de, "a": a, "montant": montant, "objet": objet, "minute": monde.data["minutes"]})
    memoriser(monde, de, {"type": "dette", "a": a, "montant": montant, "objet": objet})
    if a != "joueur":
        memoriser(monde, a, {"type": "creance", "de": de, "montant": montant, "objet": objet})


def solder(monde, lignes):
    """Chaque débiteur qui sait son créancier là et peut lui parler (``pnj.pourraient_se_parler``),
    ou dont le créancier PNJ le sait là et le lui réclame, lui rend ce qu'il doit, autant qu'il le
    peut ; le reste demeure dû. Le joueur créancier le lit. Un créancier qui le retrouve sans le sou
    s'en souvient (``creance_vaine``)."""
    from .deliberation import REDEMANDE
    from .esprits import esprit, memoriser
    from .francais import complement_de, designer
    from .pnj import _chroniquer, pourraient_se_parler
    from .social import _qui
    restantes = []
    for d in dettes(monde):
        de, a = d["de"], d["a"]
        # Le débiteur rend ce qu'il doit à qui il sait là ; un créancier PNJ qui le sait là le réclame.
        ensemble = de in monde.objets and (a == "joueur" or a in monde.objets) and (
            pourraient_se_parler(monde, de, a) or a != "joueur" and pourraient_se_parler(monde, a, de))
        rendu = min(d["montant"], richesse(monde, de)) if ensemble else 0
        if ensemble and not rendu and a != "joueur" and not any(
                s["type"] == "creance_vaine" and s["de"] == de and monde.data["minutes"] - s["minute"] < REDEMANDE
                for s in esprit(monde, a)["memoire"]):
            # Retrouvé sans le sou : le créancier le sait, et ne le relance pas de sitôt.
            memoriser(monde, a, {"type": "creance_vaine", "de": de})
        if rendu:
            payer(monde, de, a, rendu)
            d["montant"] -= rendu
            o = monde.objets.get(d["objet"])
            pour = (" : la part " + complement_de(o) + " n'a pas été servie.") if o else "."
            pieces = f"{rendu} pièce{'s' if rendu > 1 else ''}"
            _chroniquer(monde, de, f"{_qui(monde, de)} rend {pieces} à {_qui(monde, a)}{pour}", "social")
            memoriser(monde, de, {"type": "rembourse", "a": a, "montant": rendu})
            if a != "joueur":
                memoriser(monde, a, {"type": "rembourse_par", "de": de, "montant": rendu})
            if a == "joueur":
                from .voix import personne_pour_joueur
                nom, pronom, _ = personne_pour_joueur(monde, de, court=True)
                payee = (" : la part " + complement_de(o) + " que tu avais payée ne t'a pas été servie.") if o else "."
                lignes.append(f"{nom} te rend {pieces}{payee}"
                              + (f" {pronom.capitalize()} t'en doit encore {d['montant']}." if d["montant"] else ""))
            elif monde.visible(de) or monde.visible(a):
                lignes.append(f"{designer(monde.objets[de], debut=True)} rend {pieces} à {designer(monde.objets[a])}.")
        if d["montant"] > 0:
            restantes.append(d)
    monde.data["dettes"] = restantes


def reticence(monde, id, prix_, offre=0):
    """Ce qu'ajoute au DD d'une demande la part du prix qu'on ne lui paie pas : ce qu'elle vaut
    pour lui, au-delà de ce qu'elle vaut pour qui vit modestement. Un riche, pour qui une pièce
    compte peu, donne plus volontiers ; un endetté rechigne."""
    from .caractere import PIECE, valeur_pieces
    if not prix_ or id == "joueur":
        return 0
    manque = max(0, prix_ - offre)
    return round((valeur_pieces(monde, id, manque) - prix_ * PIECE) / GENEROSITE)


# --- Vérification ------------------------------------------------------------------------

def verifier(monde):
    d = monde.data
    for p in d.get("permissions", []):
        assert (set(p) == {"objet", "a", "de", "minute"} and p["objet"] in d["objets"]
                and (p["a"] == "joueur" or p["a"] in d["objets"] and d["objets"][p["a"]]["type"] == "personnage")
                and p["de"] in d["objets"] and d["objets"][p["de"]]["type"] == "personnage"
                and type(p["minute"]) is int), "Prêt invalide"
    for x in d.get("dettes", []):
        assert (isinstance(x, dict) and set(x) == {"de", "a", "montant", "objet", "minute"}
                and x["de"] in d["objets"] and (x["a"] == "joueur" or x["a"] in d["objets"])
                and type(x["montant"]) is int and x["montant"] > 0 and isinstance(x["objet"], str)
                and type(x["minute"]) is int), "Dette invalide"
    for o in d["objets"].values():
        for cle in ("pieces", "prix_part"):
            if cle in o:
                assert type(o[cle]) is int and o[cle] >= (0 if cle == "pieces" else 1), "Pièces ou prix invalides"
