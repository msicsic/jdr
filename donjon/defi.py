"""Défi autonome : retrouver la cloche du Relais des crues et la ramener."""
from __future__ import annotations

from .monde import nouveau_monde, objet
from .geometrie import placer


REFUGE = "antichambre"
BEFFROI = "chambre_cloche"
PIED_BEFFROI = "beffroi"
OBJECTIF = "Ramener la cloche d'alarme du beffroi au refuge du relais."
ANCIENNE_LIGNE_CONSIGNE = ".... ...."
LIGNE_CONSIGNE_MURALE = "...  ...."


def installer_consigne(m):
    """Raccorde la consigne au mur dans les parties antérieures à cette correction."""
    if not m.data.get("defi_relais"):
        return
    refuge = m.data["salles"][REFUGE]
    plan = refuge["plan"]["sol"]
    consigne = m.objets.get("gravure")
    cloison = m.objets.get("antichambre_murs")
    if not consigne or not cloison:
        return
    if (plan[3] == ANCIENNE_LIGNE_CONSIGNE
            and consigne.get("lieu") == REFUGE and consigne.get("position") == [2, 3]
            and cloison.get("position_salle") == REFUGE and cloison.get("position") == [3, 3]
            and not (m.joueur["salle"] == REFUGE and m.joueur["position"] == [3, 3])
            and not any(o is not cloison and o.get("position_salle") == REFUGE
                        and o.get("position") == [3, 3] for o in m.objets.values())):
        plan[3] = LIGNE_CONSIGNE_MURALE
        placer(cloison, REFUGE, [2, 3])
        memoire = m.data.get("exploration", {}).get(REFUGE, [])
        if [3, 3] in memoire:
            memoire.remove([3, 3])
    if plan[3] == LIGNE_CONSIGNE_MURALE and consigne.get("position") == [2, 3]:
        consigne.setdefault("fixee_sur", "la face ouest de la cloison de pierre")


def nouveau_defi(seed=1985):
    """Construit la partie; le launcher installe ensuite le mode cases."""
    m = nouveau_monde(seed)

    # Les seuils opposés partagent la même coordonnée globale. Les salles
    # forment une boucle : refuge → conduite → vannes → pied → beffroi.
    # La chambre haute touche aussi le refuge par un rebord extérieur.
    m.data["salles"].update({
        "antichambre": {"nom": "Refuge du relais", "sorties": {
            "ouest": {"vers": "echoppe", "porte": None, "case": [-1, 3]}},
            "fenetres": 0, "lumiere_naturelle": 0, "altitude_cm": 0,
            "plan": {"origine": [0, 0], "sol": [" ....... ", ".........", ".... ....",
                     LIGNE_CONSIGNE_MURALE, ".... ....", ".........", " ....... "], "repere": "R"}},
        "echoppe": {"nom": "Conduite basse", "sorties": {
            "est": {"vers": "antichambre", "porte": None, "case": [9, 3]},
            "sud": {"vers": "crypte", "porte": None, "case": [4, 7]}},
            "fenetres": 0, "lumiere_naturelle": 0, "altitude_cm": 0,
            "plan": {"origine": [-10, 0], "sol": [".........", ".........", ".. ......",
                     ".. ......", ".. ......", ".........", "........."], "repere": "C"}},
        "crypte": {"nom": "Salle des vannes", "sorties": {
            "nord": {"vers": "echoppe", "porte": None, "case": [4, -1]},
            "est": {"vers": PIED_BEFFROI, "porte": "porte", "case": [9, 3]}},
            "fenetres": 0, "lumiere_naturelle": 0, "altitude_cm": 0,
            "plan": {"origine": [-10, 8], "sol": ["  .....  ", ".........", ".........",
                     ".........", ".........", ".........", "  .....  "], "repere": "V"}},
        PIED_BEFFROI: {"nom": "Palier des vannes", "sorties": {
            "ouest": {"vers": "crypte", "porte": "porte", "case": [-1, 3]},
            "est": {"vers": BEFFROI, "porte": None, "case": [9, 3], "escalier": True}},
            "fenetres": 0, "lumiere_naturelle": 0, "altitude_cm": 0,
            "plan": {"origine": [0, 8], "sol": ["         ", "         ", ".........", ".........",
                     ".........", "         ", "         "], "repere": "P"}},
        BEFFROI: {"nom": "Galerie de ronde", "sorties": {
            "ouest": {"vers": PIED_BEFFROI, "porte": None, "case": [-1, 11], "escalier": True}},
            "fenetres": 1, "lumiere_naturelle": 1, "altitude_cm": 240, "niveau": 1,
            "plan": {"origine": [10, 0], "sol": ["......."] * 15, "repere": "H"}},
    })
    m.joueur.update(salle=REFUGE, position=[1, 3], masse_kg=70)
    m.data["visitees"] = [REFUGE]
    m.data["scenario"] = {
        "version": 1,
        "debut": (
            "Après la rupture du pont, tu as rejoint à pied le Relais des crues par la digue. "
            "Gorm y prépare l'accueil des habitants évacués. Il t'a demandé de rapporter la petite "
            "cloche de réserve, rangée dans la galerie du vieux beffroi : elle servira à donner "
            "le signal depuis le refuge. Une consigne émaillée est fixée près de l'entrée. "
            "À l'ouest, une conduite mène aux locaux du relais."
        ),
        "objectif": OBJECTIF,
        "liberte_personnage": "Le joueur choisit son itinéraire et ses moyens. Aucun compte à rebours ne s'écoule.",
    }

    # Identifiants historiques utilisés par plusieurs mécaniques, réhabillés
    # pour le relais et conservés dans des états ordinaires.
    porte = m.objets["porte"]
    porte.update(nom="porte étanche du beffroi", aliases=["porte", "porte du beffroi", "battant"],
                 materiau="chêne", integrite=30, maximum=30,
                 relie=["crypte", PIED_BEFFROI], ouverte=False, verrouillee=True,
                 detachee=False, bloque_par=None)
    for axe_id, nom in (("axe_haut", "axe du gond supérieur"), ("axe_bas", "axe du gond inférieur")):
        m.objets[axe_id].update(nom=nom, cote="crypte", attache=True, amovible=True,
                                integrite=12, maximum=12, lieu="porte")
    m.objets["serrure"].update(nom="serrure de la porte étanche", lieu="porte", aliases=["serrure"])
    m.objets["gravure"].update(
        nom="consigne émaillée", genre="f", materiau="fer émaillé", lieu=REFUGE, aliases=["plaque", "consigne", "inscription", "gravure"],
        fixee_sur="la face ouest de la cloison de pierre",
        motif="Un croissant gravé derrière un épaulement de pierre, une petite clé et une cloche.",
        inscription=("Le veilleur cachait la clé au pied de l'épaulement fissuré. On ne la voit qu'en "
                     "contournant le mur par son ouverture basse. La porte étanche mène au beffroi."),
        sens="Cherche derrière l'épaulement de pierre; l'ouverture basse permet d'en contourner l'angle.")
    placer(m.objets["gravure"], REFUGE, [2, 3])
    m.objets["antichambre_murs"].update(aliases=["murs", "mur", "cloison", "épaulement"],
        description_visuelle="Une cloison de pierre fissurée coupe le centre du refuge. On peut la contourner par ses deux extrémités.")
    placer(m.objets["antichambre_murs"], REFUGE, [2, 3])
    m.objets["cle"].update(nom="clé du relais", aliases=["clé", "cle", "clé du relais"],
                            lieu=REFUGE, proprietaire=None, ouvre=["porte"])
    placer(m.objets["cle"], REFUGE, [7, 5])
    m.objets["coffre"].update(nom="coffre d'entretien ouvert", lieu=BEFFROI,
                               aliases=["coffre", "coffre du beffroi"], ouverte=True,
                               verrouillee=False, integrite=40, maximum=40)
    placer(m.objets["coffre"], BEFFROI, [4, 3])
    m.objets["anneau"].update(nom="anneau de tirage", lieu="porte", mobile=False,
                               aliases=["anneau"], masse=0.02)

    gardienne = m.objets["marchand"]
    gardienne.update(nom="Gorm, gardien du relais", lieu="echoppe",
                     aliases=["gorm", "gardien", "marchand"], humeur="préoccupé",
                     portrait="Gorm est trapu, d'une cinquantaine d'années, au visage large.",
                     maniere_de_parler="Gorm parle peu et va droit au but, d'une voix grave.")
    m.data["dialogues_pnj"]["marchand"] = {
        "intentions": "Gorm veut que la cloche du relais revienne au refuge avant la crue.",
        "ton": "Il parle clairement et s'en tient à ce qu'il sait du relais.",
    }
    m.data["missions"] = {}
    m.data["engagements"] = {}
    m.data["savoirs_pnj"]["marchand"] = {
        "itineraire_relais": {"texte": "La conduite rejoint la salle des vannes, puis le palier du beffroi.",
                              "origine": "jeu", "revision": m.data["revision"]}}
    m.data["sujets_savoirs_pnj"]["marchand"] = {}
    m.data["souvenirs_personnages"]["marchand"].update(
        nom="Gorm, gardien du relais", portrait=gardienne["portrait"],
        maniere_de_parler=gardienne["maniere_de_parler"], source="Gorm veille sur le Relais des crues.")

    # Les outils de secours sont disponibles dans la conduite, loin du spawn.
    m.objets["crochets"].update(nom="trousse de crochets", lieu="echoppe", proprietaire=None, en_vente=False)
    placer(m.objets["crochets"], "echoppe", [8, 5])
    for id in ("pied_de_biche", "marteau"):
        m.objets[id].update(lieu="echoppe", en_vente=False, proprietaire=None)
        placer(m.objets[id], "echoppe", [7, 5] if id == "pied_de_biche" else [8, 5])
    m.objets["torche"].update(lieu=REFUGE, allume=True)
    placer(m.objets["torche"], REFUGE, [1, 2])
    m.objets["brasero"].update(lieu="echoppe", allume=True)

    # Le détour par l'échelle requiert d'explorer le côté est de l'épaulement.
    echelle = objet("echelle_relais", "échelle du relais", "assemblage", REFUGE,
                    aliases=["échelle", "echelle", "échelle du relais"], genre="f", mobile=True,
                    masse=3.3, materiau="bois et corde", integrite=10, maximum=10,
                    assemblage="barreaux", longueur_cm=300, largeur_cm=35, barreaux=7,
                    charge_jeu_kg=110, composants={})
    m.objets[echelle["id"]] = echelle
    placer(echelle, REFUGE, [7, 3])
    cloche = objet("cloche", "cloche d'alarme", "tresor", BEFFROI,
                   aliases=["cloche", "cloche d'alarme"], genre="f", materiau="bronze",
                   masse=1.2, mobile=True)
    m.objets[cloche["id"]] = cloche
    placer(cloche, BEFFROI, [2, 3])

    m.objets["appui_clocher"] = objet(
        "appui_clocher", "rebord extérieur du beffroi", "surface", REFUGE,
        aliases=["rebord", "mur extérieur", "mur exterieur"], materiau="pierre",
        appui_vertical={"bas": REFUGE, "haut": BEFFROI, "hauteur_cm": 240,
                        "recul_cm": 90, "sol_stable": True, "sommet_stable": True,
                        "elan_cm": 400, "reception_stable": True, "prise_sommet": True,
                        "direction": "est", "position_bas": [8, 3], "position_haut": [0, 3]},
    )
    # Réutilise les surfaces de sol de la carte de base, sans doublons.
    for id, salle in (("antichambre_sol", REFUGE), ("echoppe_sol", "echoppe"),
                      ("crypte_sol", "crypte")):
        if id in m.objets:
            m.objets[id].update(nom="sol", lieu=salle)
    for id, salle in (("sol_palier", PIED_BEFFROI), ("sol_galerie", BEFFROI)):
        m.objets[id] = objet(id, "sol", "surface", salle, materiau="pierre")
    m.objets["colonne_vannes"] = objet("colonne_vannes", "pilier de maçonnerie", "meuble", "crypte",
                                      bloque_passage=True, bloque_vue=True)
    placer(m.objets["colonne_vannes"], "crypte", [5, 3])
    m.objets["poutre_conduite"] = objet("poutre_conduite", "poutre effondrée", "meuble", "echoppe",
                                        genre="f", materiau="bois", bloque_passage=True, bloque_vue=True)
    placer(m.objets["poutre_conduite"], "echoppe", [5, 3])
    m.data["defi_relais"] = {"id": "relais_des_crues", "refuge": REFUGE,
                             "objet": "cloche", "objectif": OBJECTIF}
    m.data["defi"] = m.data["defi_relais"]
    m.data.pop("objectif_atteint", None)
    m.verifier()
    return m


def actualiser(m, lignes):
    """Valide la victoire uniquement avec la cloche portée au refuge."""
    defi = m.data.get("defi", {})
    cible = defi.get("objet", "cloche")
    refuge = defi.get("refuge", REFUGE)
    if (m.joueur["salle"] == refuge and cible in m.objets
            and m.objets[cible]["lieu"] == "joueur"):
        if not m.data.get("objectif_atteint"):
            m.data["objectif_atteint"] = True
            lignes.append("OBJECTIF ATTEINT : la cloche est de retour au refuge. Le relais peut donner l'alarme.")
    return bool(m.data.get("objectif_atteint"))
