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
from .vol import proprietaire as _possesseur

BOURSE = 5             # pièces d'un PNJ dont rien ne déclare la bourse
PRIX_PART = 2          # prix d'une part d'une ressource comptée qui n'en déclare pas
VALEUR_OBJET = 5       # ce que vaut, pour qui l'a prêté, un objet qui ne déclare pas de prix (``planification.reclamer``)
CONSOMMER = ("manger", "servir")   # gestes qui consomment le bien : aucune permission ne les couvre
BRISER = ("frapper",)              # gestes qui l'abîment (``force``) : aucune permission non plus
# Ce qu'il rechigne à donner sans être payé : un point de DD par GENEROSITE minutes de ce que vaut,
# pour lui, le prix qu'il n'est pas payé, au-delà de ce qu'il vaut pour qui vit modestement.
GENEROSITE = 2


# --- Permissions ------------------------------------------------------------------------

def proprietaire(monde, objet):
    return _possesseur(monde, monde.objets[objet])


def prets(monde):
    """Les prêts en cours ; les lire ne change rien à l'état."""
    return monde.data.get("permissions", [])


def prete_a(monde, objet):
    """À qui l'objet est prêté par son propriétaire, ou None."""
    p = next((p for p in prets(monde) if p["objet"] == objet), None)
    return p["a"] if p else None


def preter(monde, objet, a):
    """Son propriétaire remet l'objet à ``a`` : un prêt, que ``deplacer`` clôt quand l'objet lui
    revient. L'emprunteur PNJ s'engage à le rendre quand il n'en aura plus besoin."""
    de = proprietaire(monde, objet)
    liste = monde.data.setdefault("permissions", [])
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
            if not x.get("annule") and x["pour"] == de and o in monde.objets and "rendre" not in x["condition"] \
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


def leses(monde, objet, id, confies=None):
    """(prendre, consommer, abîmer) : le propriétaire que lèse chacun de ces gestes d'``id`` sur
    ``objet``, ou None — ``a_autrui`` sans opération, avec « manger », avec « frapper », jugés en
    une fois : rien ne permet de consommer ni d'abîmer le bien d'autrui (``permis``)."""
    o = monde.objets[objet]
    de = proprietaire(monde, objet)
    if de in (None, id) or id == "joueur" and o.get("vole_par") == "joueur":
        return None, None, None
    return (None if permis(monde, id, objet, None, confies) else de), de, de


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
    """Les dettes en cours ; les lire ne change rien à l'état."""
    return monde.data.get("dettes", [])


# Ce qu'une dette paie et qui n'a pas été livré : une part, un objet, une tâche (``echanges.engagements_echus``).
QUOI = ("part", "objet", "tache")


def rembourser(monde, de, a, montant, objet, quoi="part"):
    """Une contrepartie payée d'avance que ``de`` n'a pas livrée à l'échéance (``echanges.engagements_echus``) :
    une part non servie, un objet non remis, une tâche non faite. Il doit le prix à ``a``. La dette
    est connue des deux (souvenirs ``dette`` et ``creance``) et se règle quand ils se retrouvent
    (``solder``) : tout de suite s'ils le peuvent déjà."""
    from .esprits import memoriser
    monde.data.setdefault("dettes", []).append({"de": de, "a": a, "montant": montant, "objet": objet, "quoi": quoi,
                                                "minute": monde.data["minutes"]})
    memoriser(monde, de, {"type": "dette", "a": a, "montant": montant, "objet": objet, "quoi": quoi})
    from .pnj import _chroniquer
    from .social import _qui
    ce = _ce_qui(monde, {"objet": objet, "quoi": quoi})
    _chroniquer(monde, de, f"{_qui(monde, de)} doit désormais {_pieces(montant)} à {_qui(monde, a)}"
                + (f" : {ce}." if ce else "."), "compte")
    if a != "joueur":
        memoriser(monde, a, {"type": "creance", "de": de, "montant": montant, "objet": objet, "quoi": quoi})


def garde_du(monde, de, montant):
    """Rendre ce qu'il doit est un choix pesé comme le reste : garder l'argent dû est une faute au
    prix de son honnêteté, sans que rien ne l'use (l'argent ne presse pas : ``caractere.ARGENT``),
    contre ce que valent pour lui ces pièces (``caractere.valeur_pieces``, dépensées). L'honnêteté
    entière, ou une faute qui passe l'enjeu, le fait rendre. Le joueur décide pour lui-même."""
    from .caractere import ARGENT, prix_faute, valeur_pieces
    if de == "joueur" or not (monde.objets.get(de) or {}).get("profil"):
        return False
    faute = prix_faute(monde, de, ARGENT)
    return faute is not None and valeur_pieces(monde, de, montant, depense=True) > faute


def _ce_qui(monde, d, joueur=False):
    """Ce que la dette paie et qui n'a pas été livré, dit au joueur (« que tu avais payée ») ou non."""
    from .francais import accorder, complement_de, designer
    o = monde.objets.get(d["objet"])
    if d["quoi"] == "tache":
        return "le travail que tu avais payé n'a pas été fait" if joueur else "le travail payé n'a pas été fait"
    if o is None:
        return ""
    if d["quoi"] == "part":
        return "la part " + complement_de(o) + (" que tu avais payée ne t'a pas été servie" if joueur
                                                  else " n'a pas été servie")
    return (designer(o) + (" que tu avais " + accorder(o, "payé") + " ne t'a pas été " if joueur else " n'a pas été ")
            + accorder(o, "remis"))


def _pieces(n):
    return f"{n} pièce{'s' if n > 1 else ''}"


def nie_recemment(monde, a, de):
    """``a`` a réclamé son dû à ``de``, qui a refusé de le lui rendre, il y a moins de ``REDEMANDE``
    minutes : il ne le lui redemande pas de sitôt."""
    from .deliberation import REDEMANDE
    from .esprits import lire
    return a != "joueur" and any(s["type"] == "dette_niee" and s["auteur"] == de
                                 and monde.data["minutes"] - s["minute"] < REDEMANDE for s in lire(monde, a)["memoire"])


def regler(monde, d, reclamee, lignes):
    """``de`` et ``a`` se retrouvent : le débiteur rend ce qu'il peut, s'il le veut (``garde_du``).
    ``reclamee`` : son créancier le lui réclame (un PNJ qui le sait là, ou le joueur par la parole) ;
    sinon il le rendrait de lui-même, ou garde l'argent sans rien dire. Renvoie l'issue : « rendu »
    (tout), « partiel », « sans_le_sou », « garde » (il refuse de rendre ce qu'on lui réclame) ou
    « silence » (il garde ce qu'on ne lui a pas réclamé). Le reste demeure dû.

    Un refus se voit : le créancier PNJ cesse de le croire fiable et s'en souvient comme d'une
    nouvelle qu'il peut confier (``social``, « dette_niee »). Retrouvé sans le sou, il ne le relance
    pas de sitôt (``creance_vaine``)."""
    from .deliberation import REDEMANDE
    from .esprits import esprit, memoriser
    from .francais import designer
    from .pnj import _chroniquer
    from .social import _qui
    from .voix import personne_pour_joueur
    de, a = d["de"], d["a"]
    possible = min(d["montant"], richesse(monde, de))
    if not possible:
        if reclamee and a != "joueur" and not any(
                s["type"] == "creance_vaine" and s["de"] == de and monde.data["minutes"] - s["minute"] < REDEMANDE
                for s in esprit(monde, a)["memoire"]):
            memoriser(monde, a, {"type": "creance_vaine", "de": de})
        return "sans_le_sou"
    if reclamee and a != "joueur":
        _chroniquer(monde, a, f"{_qui(monde, a)} réclame à {_qui(monde, de)} les {_pieces(d['montant'])} qu'on lui doit.",
                    "compte")
    if garde_du(monde, de, possible):
        if not reclamee:
            return "silence"
        dues_ = _pieces(d["montant"])
        memoriser(monde, de, {"type": "refus_rembourser", "a": a, "montant": d["montant"]})
        il = "elle" if monde.objets[de].get("genre") == "f" else "il"
        _chroniquer(monde, de, f"{_qui(monde, de)} refuse de rendre à {_qui(monde, a)} les {dues_} qu'{il} lui doit.",
                    "social")
        if a == "joueur":
            nom, il, _ = personne_pour_joueur(monde, de, court=True)
            lignes.append(f"{nom} refuse de te rendre les {dues_} qu'{il} te doit.")
        else:
            # Le créancier le constate : il ne s'y fie plus, et peut le dire (``social.NOUVELLES``).
            memoriser(monde, a, {"type": "dette_niee", "auteur": de, "victime": a, "montant": d["montant"]})
            if monde.visible(de) or monde.visible(a):
                lignes.append(f"{designer(monde.objets[de], debut=True)} refuse de rendre à "
                              f"{designer(monde.objets[a])} ce qu'{il} lui doit.")
        return "garde"
    payer(monde, de, a, possible)
    d["montant"] -= possible
    pieces = _pieces(possible)
    pour = _ce_qui(monde, d)
    _chroniquer(monde, de, f"{_qui(monde, de)} rend {pieces} à {_qui(monde, a)}" + (f" : {pour}." if pour else "."),
                "social")
    memoriser(monde, de, {"type": "rembourse", "a": a, "montant": possible})
    if a == "joueur":
        nom, pronom, _ = personne_pour_joueur(monde, de, court=True)
        payee = _ce_qui(monde, d, joueur=True)
        lignes.append(f"{nom} te rend {pieces}" + (f" : {payee}." if payee else ".")
                      + (f" {pronom.capitalize()} t'en doit encore {d['montant']}." if d["montant"] else ""))
    else:
        memoriser(monde, a, {"type": "rembourse_par", "de": de, "montant": possible})
        if monde.visible(de) or monde.visible(a):
            lignes.append(f"{designer(monde.objets[de], debut=True)} rend {pieces} à {designer(monde.objets[a])}.")
    return "partiel" if d["montant"] else "rendu"


def solder(monde, lignes):
    """Chaque débiteur qui sait son créancier là et peut lui parler (``pnj.pourraient_se_parler``)
    lui rend ce qu'il doit, s'il le veut ; un créancier PNJ qui le sait là le lui réclame, sauf s'il
    vient d'essuyer un refus (``nie_recemment``). Le débiteur rend autant qu'il le peut ; le reste
    demeure dû (``regler``)."""
    from .pnj import pourraient_se_parler
    for d in list(dettes(monde)):
        de, a = d["de"], d["a"]
        if de not in monde.objets or not (a == "joueur" or a in monde.objets):
            continue
        reclamee = a != "joueur" and not nie_recemment(monde, a, de) and pourraient_se_parler(monde, a, de)
        if reclamee or pourraient_se_parler(monde, de, a):
            regler(monde, d, reclamee, lignes)
    monde.data["dettes"] = [d for d in dettes(monde) if d["montant"] > 0]


def dues(monde, de, a):
    """Les dettes de ``de`` envers ``a``, dans l'ordre où elles sont nées."""
    return [d for d in dettes(monde) if d["de"] == de and d["a"] == a]


def reclamer_dette(monde, a, de, lignes):
    """``a`` réclame à ``de`` ce qu'il lui doit, de vive voix : chaque dette se règle comme quand ils
    se retrouvent (``regler``), réclamée. Renvoie les issues, une par dette ; [] s'il ne lui doit rien."""
    issues = [regler(monde, d, True, lignes) for d in dues(monde, de, a)]
    if issues:
        monde.data["dettes"] = [d for d in dettes(monde) if d["montant"] > 0]
    return issues


# --- Prêts réclamés ------------------------------------------------------------------------

RENDRE = 30   # minutes qu'un prêteur laisse à qui il a réclamé un prêt échu pour le lui rendre


def pret(monde, objet):
    return next((p for p in prets(monde) if p["objet"] == objet), None)


def echu(monde, objet):
    """Le prêt de cet objet dure depuis l'échéance d'une parole (``echanges.ENGAGEMENT_MAX``) : son
    prêteur peut le réclamer, et l'emprunteur qui ne le rend pas perd sa confiance."""
    from .echanges import ENGAGEMENT_MAX
    p = pret(monde, objet)
    return bool(p) and monde.data["minutes"] - p["minute"] >= ENGAGEMENT_MAX


def pret_garde(monde, preteur, emprunteur, objet, lignes):
    """L'emprunteur ne rend pas un prêt échu qu'on lui réclame : le prêteur ne s'y fie plus, et peut
    le dire (``social``, « pret_garde »). Pour le joueur comme pour un PNJ."""
    from .esprits import memoriser
    from .francais import accorder, designer
    from .pnj import _chroniquer
    from .social import _qui
    memoriser(monde, preteur, {"type": "pret_garde", "auteur": emprunteur, "victime": preteur, "objet": objet})
    o = monde.objets[objet]
    _chroniquer(monde, preteur, f"{_qui(monde, preteur)} reproche à {_qui(monde, emprunteur)} de garder "
                                f"{designer(o)} qu'on lui a {accorder(o, 'prêté')}.", "social")
    if emprunteur == "joueur":
        from .voix import personne_pour_joueur
        nom = personne_pour_joueur(monde, preteur, court=True)[0]
        lignes.append(f"{nom} te reproche de ne pas lui avoir rendu {designer(o)}.")


def prets_reclames(monde, lignes):
    """Le joueur à qui un PNJ a réclamé un prêt échu (souvenir ``pret_reclame``, qui date le prêt) et
    qui ne l'a pas rendu ``RENDRE`` minutes après perd sa confiance (``pret_garde``) : il garde ce
    qu'on lui redemande, comme un PNJ qui refuse (``echanges.demander``)."""
    from .esprits import esprit
    for p in [p for p in prets(monde) if p["a"] == "joueur" and p["de"] in monde.objets]:
        for s in esprit(monde, p["de"])["memoire"]:
            if (s["type"] == "pret_reclame" and s["objet"] == p["objet"] and s["pret"] == p["minute"]
                    and s["echu"] and not s.get("juge") and monde.data["minutes"] - s["minute"] >= RENDRE):
                s["juge"] = True
                pret_garde(monde, p["de"], "joueur", p["objet"], lignes)


def comptes_joueur(monde):
    """Ce que le joueur sait de ses comptes : ce qu'on lui doit (une contrepartie payée et non
    livrée), ce qu'il a prêté, ce qu'on lui a prêté. Il le sait de ce qu'il a payé, prêté et reçu."""
    from .francais import designer
    from .voix import personne_pour_joueur
    lignes = []
    for d in dettes(monde):
        if d["a"] == "joueur" and d["de"] in monde.objets:
            ce = _ce_qui(monde, d, joueur=True)
            lignes.append(f"{personne_pour_joueur(monde, d['de'], court=True)[0]} te doit {_pieces(d['montant'])}"
                          + (f" : {ce}." if ce else "."))
    for p in prets(monde):
        if p["objet"] not in monde.objets:
            continue
        o = designer(monde.objets[p["objet"]])
        if p["de"] == "joueur" and p["a"] in monde.objets:
            lignes.append(f"Tu as prêté {o} à {personne_pour_joueur(monde, p['a'], court=True)[0]}.")
        elif p["a"] == "joueur" and p["de"] in monde.objets:
            lignes.append(f"{personne_pour_joueur(monde, p['de'], court=True)[0]} t'a prêté {o}.")
    return lignes


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
        assert (isinstance(x, dict) and set(x) == {"de", "a", "montant", "objet", "quoi", "minute"}
                and x["de"] in d["objets"] and (x["a"] == "joueur" or x["a"] in d["objets"])
                and type(x["montant"]) is int and x["montant"] > 0 and isinstance(x["objet"], str)
                and x["quoi"] in QUOI and type(x["minute"]) is int), "Dette invalide"
    for o in d["objets"].values():
        for cle in ("pieces", "prix_part"):
            if cle in o:
                assert type(o[cle]) is int and o[cle] >= (0 if cle == "pieces" else 1), "Pièces ou prix invalides"
