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
from contextlib import contextmanager

from .francais import quantite
from . import agendas
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
        engagements = agendas.en_cours(monde, a)
        if not any(x["condition"] == condition for x in engagements):
            agendas.prendre(monde, a, {"condition": condition, "pour": de, "minute": monde.data["minutes"]})


def clore(monde, objet, destination):
    """L'objet arrive à ``destination`` : s'il revient à son propriétaire, le prêt est clos."""
    liste = monde.data.get("permissions")
    if liste and any(p["objet"] == objet and p["de"] == destination for p in liste):
        rendus = [p for p in liste if p["objet"] == objet and p["de"] == destination]
        liste[:] = [p for p in liste if not (p["objet"] == objet and p["de"] == destination)]
        from .esprits import constater_possession
        for p in rendus:
            for participant in (p["a"], destination):
                constater_possession(monde, participant, objet, "essai", remis_par=p["a"])
            retenir_restitution(monde, p["a"], destination, objet)


def entrees_reemprunt(monde, id, autre, objet):
    """Entrées utiles d'un emprunt, sans date, déplacement ni bénéfice social du retour.

    Une perte de moyen ne donne aucune raison de répéter un emprunt terminé.
    Les besoins sont leurs épisodes urgents, pas leur croissance à chaque minute.
    """
    from .deliberation import urgents
    from .esprits import lire
    from .spatial import porte_par
    croyances = lire(monde, id)["croyances"]
    return {
        "besoins": sorted(urgents(monde, id)) if monde.objets.get(id, {}).get("profil") else [],
        "moyens": sorted(k for k in croyances if k != objet and k in monde.objets
                         and porte_par(monde, k, id)),
        "pieces": bourse(monde, id),
        "contenu": (croyances.get(objet, {}).get("pieces") or {}).get("valeur", 0),
        "proprietaire": proprietaire(monde, objet),
        "prix": prix(monde, objet),
    }


def retenir_restitution(monde, id, autre, objet):
    """Le retour est appris par son emprunteur, même si le propriétaire l'impose."""
    retours = monde.data.setdefault("restitutions", {}).setdefault(id, {})
    retours[objet] = {"a": autre, "entrees": entrees_reemprunt(monde, id, autre, objet)}


def restitution_retenue(monde, id, autre, objet):
    """Un emprunt rendu n'est pas réessayé sans besoin ou moyen nouveau.

    Un achat ou un don reste une autre réponse : ce contrôle porte sur le prêt.
    La mémoire est durable et commune au joueur et aux personnages.
    """
    retour = monde.data.get("restitutions", {}).get(id, {}).get(objet)
    if not retour or retour["a"] != autre:
        return False
    avant, apres = retour["entrees"], entrees_reemprunt(monde, id, autre, objet)
    return (all(b in avant["besoins"] for b in apres["besoins"])
            and all(k in avant["moyens"] for k in apres["moyens"])
            and apres["pieces"] <= avant["pieces"]
            and apres["contenu"] <= avant["contenu"]
            and apres["proprietaire"] == avant["proprietaire"]
            and not (apres["prix"] is not None and
                     (avant["prix"] is None or apres["prix"] < avant["prix"])))


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
        for x in agendas.en_cours(monde, id):
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


def responsable_cru(monde, objet, id):
    """Responsable connu d'une installation, sans lire les projets privés d'autrui.

    La propriété conserve sa priorité. À défaut : porteur cru d'une clé,
    garde lue, ou charge propre (pulsion/agendas, par leur lecture commune).
    Une garde supposée peut être fausse ; sa vérité n'est pas consultée.
    """
    o = monde.objets[objet]
    de = proprietaire(monde, objet)
    if de or o['type'] not in ('porte', 'contenant') or o.get('mobile'):
        return de
    from .deliberation import _lieu_cru, charges_gardees, salle_crue
    from .signes import actives
    lieux = set(o.get('relie', ())) | {salle_crue(monde, id, objet)}
    lieux.discard(None)
    # Les attaches des clés sont des propriétés structurelles ; leur porteur
    # est exclusivement celui enregistré dans les croyances de l'observateur.
    candidats = set()
    for k, cle in monde.objets.items():
        if objet not in cle.get('ouvre', ()):
            continue
        porteur, vus = _lieu_cru(monde, id, k), set()
        while porteur in monde.objets and porteur not in vus:
            vus.add(porteur)
            if monde.objets[porteur]['type'] == 'personnage':
                candidats.add(porteur)
                break
            porteur = _lieu_cru(monde, id, porteur)
        if porteur == 'joueur':
            candidats.add(porteur)
    if candidats:
        return sorted(candidats)[0]
    gardiens = {x for x, a, c in actives(monde, id)
                if a == 'intention' and c['valeur'] == 'garde'
                and (c.get('envers') == objet or c.get('envers') in lieux
                     or salle_crue(monde, id, c.get('envers')) in lieux)}
    charges = charges_gardees(monde, id) if monde.objets.get(id, {}).get('profil') else ()
    for c in charges:
        if c.get('objet') == objet or c.get('lieu') in lieux or (
                'objet' in c and salle_crue(monde, id, c['objet']) in lieux):
            gardiens.add(id)
    return sorted(gardiens)[0] if gardiens else None


def lese_par(monde, objet, id, operation):
    """Victime crue du geste : propriété habituelle, responsabilité pour le bris."""
    return responsable_cru(monde, objet, id) if operation in (*BRISER, 'briser') else proprietaire(monde, objet)


def a_autrui(monde, objet, id="joueur", operation=None, confies=None):
    """La personne lésée : propriétaire, ou responsable cru pour le bris d'une installation.

    None pour son propre bien, un bien sans responsable connu, ce que le joueur
    a déjà dérobé ou ce qu'une permission couvre (``confies`` : ``permis``).
    """
    o = monde.objets[objet]
    de = lese_par(monde, objet, id, operation)
    if de in (None, id) or id == "joueur" and o.get("vole_par") == "joueur":
        return None
    return None if permis(monde, id, objet, operation, confies) else de


def leses(monde, objet, id, confies=None):
    """(prendre, consommer, abîmer) : la personne que lèse chacun de ces gestes d'``id`` sur
    ``objet``, ou None — ``a_autrui`` sans opération, avec « manger », avec « frapper », jugés en
    une fois : rien ne permet de consommer ni d'abîmer le bien d'autrui (``permis``)."""
    brise = a_autrui(monde, objet, id, 'frapper', confies)
    o = monde.objets[objet]
    de = proprietaire(monde, objet)
    if de in (None, id) or id == "joueur" and o.get("vole_par") == "joueur":
        return None, None, brise
    return (None if permis(monde, id, objet, None, confies) else de), de, brise


def disponible_en_main(monde, objet, acteur):
    """Bien porté, ou atteignable hors d'un contenant fermé et des mains d'autrui."""
    from .spatial import porte_par, proche, position_acteur
    if porte_par(monde, objet, acteur):
        return True
    lieu, vus = monde.objets[objet]["lieu"], set()
    while lieu in monde.objets and lieu not in vus:
        vus.add(lieu)
        contenant = monde.objets[lieu]
        if contenant["type"] != "contenant" or not contenant.get("ouverte", True):
            return False
        lieu = contenant["lieu"]
    return lieu == position_acteur(monde, acteur)[0] and proche(monde, objet, acteur)


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
    noter_compte(monde, compte(de, a, montant=montant, etat="rendu"))


def prix(monde, objet, part=False):
    """Le prix d'une part d'une ressource comptée, ou d'un objet qui en déclare un ; None sinon."""
    o = monde.objets[objet]
    if part:
        return o.get("prix_part", PRIX_PART)
    return o.get("prix")


def capacites_crues(monde, id, objet):
    """Services matériels connus, sans lire charge, flamme ou contenu cachés.

    Les usages et attaches sont structurels ; l'état d'une source est cru.
    Une clé n'apporte que les accès que son porteur connaît.
    """
    from .esprits import croyance, lire
    from .force import COUPE
    o = monde.objets[objet]
    if (croyance(monde, id, objet, "fin") or {}).get("valeur"):
        return set()
    usages = set(o.get("usages", ()))
    profil = monde.objets.get(id, {}).get("profil") or {}
    resultat = usages & {"allumage"}
    if usages.intersection(COUPE):
        resultat.add("coupe")
    if "crochetage" in profil.get("capacites", ()) and "crochetage" in usages:
        resultat.add("crochetage")
    connus = lire(monde, id)["croyances"]
    resultat.update("cle:" + cible for cible in o.get("ouvre", ()) if cible in connus)
    etat = croyance(monde, id, objet, "etat")
    etat = etat["valeur"] if etat else {}
    if "allume" in o and (etat.get("allume") or etat.get("charge")):
        resultat.add("lumiere")
    if etat.get("allume"):
        resultat.add("allumage")
    return resultat


def valeur_capacites(monde, id, objet, *, sans=None):
    """Valeur marginale des capacités connues, distincte du prix du bien.

    Même estimation à l'acquisition et à la cession ; ``sans`` retire le bien
    simultanément cédé des moyens qu'il croit conserver.
    """
    from .caractere import valeur
    from .deliberation import _connus, _lieu_cru
    propres = set()
    for k in _connus(monde, id):
        if k in (objet, sans):
            continue
        lieu, vus = _lieu_cru(monde, id, k), {k}
        while lieu in monde.objets and lieu != id and lieu not in vus:
            vus.add(lieu)
            lieu = _lieu_cru(monde, id, lieu)
        if lieu == id:
            propres.update(capacites_crues(monde, id, k))
    nouvelles = capacites_crues(monde, id, objet) - propres
    return 12 * len(nouvelles) * (0.5 + valeur(monde, id, "ambition") / 100)


def valeur_bien(monde, id, objet, part=False, *, sans=None):
    """Estimation commune en minutes : prix/contenu connu ou capacité marginale.

    Un outil porté coûte la capacité perdue ; acquis, il vaut la capacité
    ajoutée. Un doublon porté la conserve ; ``sans`` exclut le bien cédé
    simultanément, pour compter son remplacement parmi les gains. Le désespoir valorise le remède
    utilisable, pas n'importe quelle contrepartie. Aucun devis ni mutation.
    """
    from .caractere import valeur_pieces, ENJEU
    from .deliberation import besoin_de_part, part_pour, parts, DESESPOIR
    from .esprits import croyance, lire
    o = monde.objets[objet]
    montant = prix(monde, objet, part)
    if not part and "pieces" in o:
        c = croyance(monde, id, objet, "pieces")
        montant = (montant or 1) + (c["valeur"] if c else 0)
    if montant is None and not part and besoin_de_part(o) is not None:
        # Le propriétaire compte sa réserve ; aucune quantité distante cachée.
        n = parts(o) if proprietaire(monde, objet) == id else 1
        montant = n * (prix(monde, objet, True) or 1)
    marchande = valeur_pieces(monde, id, montant if montant is not None else 1)
    besoin = besoin_de_part(o)
    remede = 0
    if besoin and part_pour(monde, id, objet, besoin):
        pression = lire(monde, id)["besoins"].get(besoin, 0)
        remede = ENJEU * max(0, pression - DESESPOIR) / (100 - DESESPOIR)
    if part:
        return max(marchande, remede)
    # Même échelle que la peine et la faute. L'ambition pèse l'avenir ;
    # seul un remède effectif peut passer cette capacité au désespoir.
    usage = valeur_capacites(monde, id, objet, sans=sans)
    return max(marchande, usage, remede)


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
    return quantite(n, "pièce")


def reponse_creance_retenue(monde, a, de):
    """La dernière réponse à cette créance tient selon sa cause, sans délai."""
    from .deliberation import refus_retenu
    return a != "joueur" and refus_retenu(monde, a, de, ("reclamer_dette",)) is not None


def entrees_creance(monde, a, de):
    """Obligations connues et fonds identifiés par le créancier, sans bourse privée.

    Une autre position, une date de regard ou une diminution des moyens ne
    lèvent pas la réponse. Un remboursement ou une nouvelle obligation, oui.
    Le débiteur reste libre de rembourser spontanément (``solder``).
    """
    from .esprits import lire
    from .deliberation import _lieu_cru
    faits = [["dette", d["objet"], d["quoi"], d["montant"]] for d in dues(monde, de, a)]
    for k, c in lire(monde, a)["croyances"].items():
        if k in monde.objets and _lieu_cru(monde, a, k) == de:
            pieces = c.get("pieces", {}).get("valeur", 0)
            if pieces:
                faits.append(["pieces", k, de, pieces])
    return sorted(faits, key=str)


def regler(monde, d, reclamee, lignes):
    """``de`` et ``a`` se retrouvent : le débiteur rend ce qu'il peut, s'il le veut (``garde_du``).
    ``reclamee`` : son créancier le lui réclame (un PNJ qui le sait là, ou le joueur par la parole) ;
    sinon il le rendrait de lui-même, ou garde l'argent sans rien dire. Renvoie l'issue : « rendu »
    (tout), « partiel », « sans_le_sou », « garde » (il refuse de rendre ce qu'on lui réclame) ou
    « silence » (il garde ce qu'on ne lui a pas réclamé). Le reste demeure dû.

    Un refus se voit : le créancier PNJ cesse de le croire fiable et s'en souvient comme d'une
    nouvelle qu'il peut confier (``social``, « dette_niee »). La réponse est aussi retenue hors
    mémoire bornée, jusqu'à une obligation ou un moyen connu nouveau."""
    from .deliberation import retenir_refus, oublier_refus
    from .esprits import memoriser
    from .francais import designer, groupe_nominal
    from .pnj import _chroniquer
    from .social import _qui
    from .voix import personne_pour_joueur
    de, a = d["de"], d["a"]
    # Le règlement automatique et un ancien plan lisent la même réponse.
    reclamee = reclamee and not reponse_creance_retenue(monde, a, de)
    possible = min(d["montant"], richesse(monde, de))
    if reclamee and a != "joueur":
        _chroniquer(monde, a, f"{_qui(monde, a)} réclame à {_qui(monde, de)} les {_pieces(d['montant'])} qu'on lui doit.",
                    "compte")
    if not possible:
        if reclamee and a != "joueur":
            memoriser(monde, a, {"type": "creance_vaine", "de": de})
            retenir_refus(monde, a, de, "reclamer_dette", "sans_le_sou", souvenir=False)
        return "sans_le_sou"
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
            # dette_niee porte déjà l'effet social ; la mémoire de décision
            # ne doit pas créer un deuxième événement de refus.
            retenir_refus(monde, a, de, "reclamer_dette", "garde", souvenir=False)
            if monde.visible(de) or monde.visible(a):
                lignes.append(f"{designer(monde.objets[de], debut=True)} refuse de rendre à "
                              f"{designer(monde.objets[a])} ce qu'{il} lui doit.")
        return "garde"
    payer(monde, de, a, possible)
    d["montant"] -= possible
    if a != "joueur":
        oublier_refus(monde, a, de, "reclamer_dette")
        if d["montant"]:
            retenir_refus(monde, a, de, "reclamer_dette", "sans_le_sou", souvenir=False)
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
            lignes.append(f"{designer(monde.objets[de], debut=True)} rend {pieces} {groupe_nominal(designer(monde.objets[a]), 'à')}.")
    return "partiel" if d["montant"] else "rendu"


def solder(monde, lignes):
    """Chaque débiteur qui sait son créancier là et peut lui parler (``pnj.pourraient_se_parler``)
    lui rend ce qu'il doit, s'il le veut ; un créancier PNJ qui le sait là le lui réclame, sauf s'il
    vient d'essuyer un refus (``reponse_creance_retenue``). Le débiteur rend autant qu'il le peut ; le reste
    demeure dû (``regler``)."""
    from .pnj import pourraient_se_parler
    for d in list(dettes(monde)):
        de, a = d["de"], d["a"]
        if de not in monde.objets or not (a == "joueur" or a in monde.objets):
            continue
        reclamee = a != "joueur" and not reponse_creance_retenue(monde, a, de) and pourraient_se_parler(monde, a, de)
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
    from .francais import complement_de
    for c in livraisons_dues(monde):
        o = monde.objets.get(c["objet"])
        if o is None:
            continue
        servir = any(x["condition"].get("servir") == "joueur" and
                     x["condition"]["objet"] == c["objet"]
                     for x in agendas.en_cours(monde, c["debiteur"]))
        bien = "une part " + complement_de(o) if servir else designer(o)
        nom = personne_pour_joueur(monde, c["debiteur"], court=True)[0]
        lignes.append(f"{nom} doit encore te {'servir' if servir else 'remettre'} {bien}.")
    return lignes


def compte(debiteur, creancier, objet="", montant=0, etat="du"):
    """Un sens unique, commun aux comptes et aux issues : qui doit/rend quoi à qui.

    Un objet vide désigne les pièces ; sinon l'identité du bien remis ou à livrer.
    Pour un prêt, le débiteur est l'emprunteur, indépendamment du sens historique
    des champs de/a de la permission.
    """
    return {"debiteur": debiteur, "creancier": creancier, "objet": objet,
            "montant": montant, "etat": etat}


def noter_compte(monde, c):
    """Journal transactionnel ouvert par la conversation, copié avec ses essais.

    Il n'existe que dans la copie de travail et est retiré avant publication.
    Un essai abandonné ne publie donc aucun transfert ; aucun compte PNJ privé.
    """
    journal = monde.data.get("_comptes_echange")
    if journal is not None and "joueur" in (c["debiteur"], c["creancier"]):
        precedent = next((a for a in journal if all(a[k] == c[k] for k in
                         ("debiteur", "creancier", "objet", "etat"))), None)
        if precedent is None:
            journal.append(c)
        else:
            precedent["montant"] += c["montant"]


def livraisons_dues(monde):
    """Biens effectivement promis au joueur, depuis les engagements du moteur.

    Une part détachée porte sa propre identité ; un service de part à servir
    garde le lot et une quantité, sans transformer le lot entier en prêt.
    """
    comptes = []
    for id, o in monde.objets.items():
        if not o.get("profil"):
            continue
        for x in agendas.en_cours(monde, id):
            c = x["condition"]
            if not x.get("annule") and x["pour"] == "joueur" and (
                    c.get("remettre") == "joueur" or c.get("servir") == "joueur"):
                comptes.append(compte(id, "joueur", c["objet"], 1))
    return comptes


def etat_comptes_joueur(monde, interlocuteurs=()):
    """Comptes connus du joueur seulement ; aucune dette privée entre PNJ.

    Les zéros sont bornés aux pièces et aux interlocuteurs fournis, dans les deux
    sens. L'absence de dette monétaire ne dit rien d'un objet prêté.
    """
    from .voix import reel
    personnes = {reel(monde, x) for x in interlocuteurs}
    personnes.update(d["de"] if d["a"] == "joueur" else d["a"] for d in dettes(monde)
                      if "joueur" in (d["de"], d["a"]))
    comptes = []
    for personne in sorted(personnes - {"joueur"}):
        for de, a in ((personne, "joueur"), ("joueur", personne)):
            montant = sum(d["montant"] for d in dues(monde, de, a))
            comptes.append(compte(de, a, montant=montant, etat="du" if montant else "absent"))
    comptes.extend(compte(p["a"], p["de"], p["objet"], 1) for p in prets(monde)
                   if "joueur" in (p["de"], p["a"]))
    return comptes + livraisons_dues(monde)


def offres_joueur(monde):
    """Devis de mission publics, distincts des soldes dus et des paiements."""
    from .dialogues import missions_discutables, offre_mission
    from .agendas import contrats
    ids = set(missions_discutables(monde)) | set(contrats(monde))
    return [o for id in sorted(ids) if (o := offre_mission(monde, id))]


def reticence(monde, id, prix_, offre=0):
    """Ce qu'ajoute au DD d'une demande la part du prix qu'on ne lui paie pas : ce qu'elle vaut
    pour lui, au-delà de ce qu'elle vaut pour qui vit modestement. Un riche, pour qui une pièce
    compte peu, donne plus volontiers ; un endetté rechigne."""
    from .caractere import PIECE, valeur_pieces
    if not prix_ or id == "joueur":
        return 0
    manque = max(0, prix_ - offre)
    return round((valeur_pieces(monde, id, manque) - prix_ * PIECE) / GENEROSITE)


# --- Résultats des paroles de service -----------------------------------------------------


def retenir_service(monde, id, engagement):
    """Un résultat promis et constaté, pas une obligation de le maintenir."""
    c = engagement["condition"]
    if set(c) not in ({"objet", "allume"}, {"objet", "verrouillee"}, {"objet", "lieu"}):
        return
    from .deliberation import salle_crue
    trace = {"de": id, "pour": engagement["pour"], "condition": dict(c)}
    services = monde.data.setdefault("services_rendus", [])
    if not any(all(s.get(k) == v for k, v in trace.items()) for s in services):
        # Le prestataire peut déplacer le résultat : cela ne prouve pas que
        # son bénéficiaire est parti. Retenir son lieu au constat de réussite.
        trace["lieu_beneficiaire"] = salle_crue(monde, id, engagement["pour"])
        services.append(trace)


@contextmanager
def clotures_services_du_choix(monde):
    """Clôtures découvertes en lecture, publiées après le choix complet seulement.

    Les choix imbriqués transmettent leurs clôtures au parent. Un devis isolé
    n'ouvre pas ce registre ; une interruption abandonne tout le registre.
    """
    ancien = getattr(monde, "_clotures_services", None)
    clotures = []
    monde._clotures_services = clotures
    try:
        yield
    except BaseException:
        raise
    else:
        if ancien is not None:
            ancien.extend(s for s in clotures if s not in ancien)
        elif clotures:
            services = monde.data.get("services_rendus", [])
            services[:] = [s for s in services if s not in clotures]
    finally:
        monde._clotures_services = ancien


def services_proteges(monde, id):
    """Résultats encore utiles d'après les seules observations du prestataire.

    Le besoin est approché par la présence crue du bénéficiaire au lieu
    retenu à la réussite ou auprès du résultat (ou son portage).
    Un départ connu de ces lieux ou un état constaté défait
    termine la protection définitivement ; ni oubli par délai, ni entretien.
    Un bénéficiaire présent qui n'en a plus besoin reste donc protégé.
    La lecture reste pure ; les traces finies sont proposées au registre du
    choix, lorsqu'il existe, sans écriture pour un devis isolé.
    """
    from .deliberation import _cru, _lieu_cru, salle_crue
    from .monde import mobile_par_nature
    actifs = [{"de": id, "pour": x["pour"], "condition": x["condition"]}
              for x in agendas.en_cours(monde, id) if not x.get("annule")
              and set(x["condition"]) in ({"objet", "allume"}, {"objet", "verrouillee"}, {"objet", "lieu"})]
    services = monde.data.get("services_rendus", [])
    proteges, finis = [], []
    for s, actif in [(s, False) for s in services] + [(s, True) for s in actifs]:
        if s["de"] != id:
            continue
        c, pour = s["condition"], s["pour"]
        o = c["objet"]
        etat = _cru(monde, id, o, "etat") or {}
        lieu = salle_crue(monde, id, o)
        beneficiaire = salle_crue(monde, id, pour)
        porteur = _lieu_cru(monde, id, o)
        cesse = (o not in monde.objets or _cru(monde, id, o, "fin") is not None
                 or (_cru(monde, id, pour, "etat") or {}).get("mort")
                 or "allume" in c and etat.get("allume") is False
                 or "verrouillee" in c and (_cru(monde, id, o, "verrouillee") is False
                                              or etat.get("ouverte") is True)
                 or "lieu" in c and lieu is not None and lieu != c["lieu"])
        # Sans ancrage historique, seul un résultat fixe fournit encore un
        # lieu de référence. Le déplacement d'un résultat mobile, porté ou
        # posé ensuite, ne prouve jamais un départ de son bénéficiaire.
        reference = s.get("lieu_beneficiaire",
                          None if mobile_par_nature(monde.objets.get(o, {})) else lieu)
        parti = (porteur != pour and reference is not None and lieu is not None
                 and beneficiaire is not None and reference != beneficiaire and lieu != beneficiaire)
        if cesse and not actif or parti:
            if not actif:
                finis.append(s)
        else:
            # L'absence d'information nouvelle ne dément pas la parole reçue.
            if c not in proteges:
                proteges.append(c)
    clotures = getattr(monde, "_clotures_services", None)
    if clotures is not None:
        clotures.extend(s for s in finis if s not in clotures)
    return proteges


# --- Vérification ------------------------------------------------------------------------


def verifier(monde):
    d = monde.data
    from .deliberation import condition_valide
    assert isinstance(d.get("services_rendus", []), list), "Traces de service invalides"
    for s in d.get("services_rendus", []):
        assert (isinstance(s, dict) and set(s) in ({"de", "pour", "condition"},
                                                {"de", "pour", "condition", "lieu_beneficiaire"})
                and (s.get("lieu_beneficiaire") is None or s["lieu_beneficiaire"] in monde.data["salles"])
                and s["de"] in monde.objets and monde.objets[s["de"]]["type"] in ("personnage", "depouille")
                and (s["pour"] == "joueur" or s["pour"] in monde.objets
                     and monde.objets[s["pour"]]["type"] in ("personnage", "depouille"))
                and condition_valide(monde, s["condition"])
                and set(s["condition"]) in ({"objet", "allume"}, {"objet", "verrouillee"}, {"objet", "lieu"})
                ), "Trace de service invalide"
    for id, retours in d.get("restitutions", {}).items():
        assert id == "joueur" or id in monde.objets, "Emprunteur restituant inconnu"
        for objet, retour in retours.items():
            assert isinstance(objet, str) and set(retour) == {"a", "entrees"}, "Restitution invalide"
            assert isinstance(retour["a"], str), "Destinataire de restitution invalide"
            e = retour["entrees"]
            assert set(e) == {"besoins", "moyens", "pieces", "contenu", "proprietaire", "prix"}, "Entrées de restitution invalides"
            assert all(isinstance(e[k], list) and all(isinstance(x, str) for x in e[k])
                       for k in ("besoins", "moyens")), "Moyens de restitution invalides"
            assert all(type(e[k]) is int and e[k] >= 0 for k in ("pieces", "contenu")), "Fonds de restitution invalides"
            assert e["proprietaire"] is None or isinstance(e["proprietaire"], str), "Propriété de restitution invalide"
            assert e["prix"] is None or type(e["prix"]) is int and e["prix"] >= 0, "Prix de restitution invalide"
    for p in d.get("permissions", []):
        assert (set(p) == {"objet", "a", "de", "minute"} and p["objet"] in d["objets"]
                and (p["a"] == "joueur" or p["a"] in d["objets"] and d["objets"][p["a"]]["type"] in ("personnage", "depouille"))
                and p["de"] in d["objets"] and d["objets"][p["de"]]["type"] in ("personnage", "depouille")
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
