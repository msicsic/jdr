"""Scène d'essai isolée pour fabriquer, installer et emprunter un assemblage."""
from .monde import nouveau_monde, objet
from .geometrie import placer


def nouveau_atelier(seed=1985):
    m = nouveau_monde(seed)
    m.data["salles"].update({
        "cour": {"nom": "Cour de l'atelier", "sorties": {}, "fenetres": 0, "exterieur": True,
                 "lumiere_naturelle": 2, "niveau": 0,
                 "plan": {"origine": [20, 10], "sol": ["......"] * 6, "repere": "A"}},
        "terrasse": {"nom": "Terrasse de l'atelier", "sorties": {}, "fenetres": 0, "exterieur": True,
                     "lumiere_naturelle": 2, "niveau": 1,
                     "plan": {"origine": [20, 10], "sol": ["......"] * 3, "repere": "T"}},
    })
    m.joueur.update(salle="cour", position=[2, 3], masse_kg=70)
    m.data["visitees"] = ["cour"]
    m.data["scenario"] = {
        "version": 1, "debut": "Tu es dans la cour d'un atelier, en plein jour. Trois perches et une bobine de ficelle sont à ta disposition. "
        "Une terrasse borde le sommet d'un mur de 2,4 m. Tu portes une hache : à toi d'imaginer comment atteindre ce palier.",
        "objectif": "Fabriquer un accès à la terrasse, y monter puis redescendre.",
        "liberte_personnage": "Le joueur décide de ses actions. Les dimensions et ressources sont établies, sans création gratuite.",
    }
    for i in range(1, 4):
        id = f"perche_{i}"
        m.objets[id] = objet(id, f"perche de bois {i}", "materiau", "cour", aliases=[f"perche {i}", f"branche {i}", f"tronc {i}"],
                             genre="f", mobile=True, masse=3, materiau="bois", ressource="perche", proprietaire="joueur",
                             longueur_cm=300, diametre_cm=5, charge_jeu_kg=110)
        placer(m.objets[id], "cour", [i, 1])
    m.objets["ficelle"] = objet("ficelle", "bobine de ficelle solide", "materiau", "cour", aliases=["ficelle", "bobine"],
                                genre="f", mobile=True, masse=.3, materiau="fibres", ressource="lien", proprietaire="joueur",
                                longueur_cm=2000, charge_jeu_kg=110)
    placer(m.objets["ficelle"], "cour", [4, 2])
    m.objets["hache"] = objet("hache", "hache", "outil", "joueur", aliases=["hache"], genre="f", elision=False,
                              mobile=True, masse=1.5, materiau="acier et bois", usages=["couper_bois"], proprietaire="joueur")
    m.objets["mur_atelier"] = objet("mur_atelier", "mur de l'atelier", "surface", "cour", aliases=["mur"], materiau="pierre",
                                    appui_vertical={"bas": "cour", "haut": "terrasse", "hauteur_cm": 240,
                                                    "recul_cm": 90, "sol_stable": True, "sommet_stable": True})
    for salle in ("cour", "terrasse"):
        m.objets[salle + "_sol"] = objet(salle + "_sol", "sol", "surface", salle, aliases=["sol"], materiau="pierre")
    m.objets["lanterne"]["allume"] = False
    from .franchissement import installer
    installer(m)
    from .artisanat import installer as installer_artisanat
    installer_artisanat(m)
    from .espace import installer as installer_espace
    installer_espace(m)
    m.verifier()
    return m
