"""Le pont entre la boucle de jeu (``jeu.main``) et la page du navigateur.

Même contrat que ``tui.PontTerminal`` : la boucle écrit des lignes, lit des commandes, demande
qu'on rafraîchisse l'état ou qu'on montre une vue. Le pont diffuse tout cela aux pages
abonnées et reçoit leurs commandes, une à la fois. La page n'a aucun pouvoir sur l'état : elle
envoie une saisie libre ou un descripteur de geste explicite.
"""
from queue import Empty, Queue
import threading

HISTORIQUE_MAX = 400


def inventaire_public(monde):
    """Les affaires de la besace, sans le contenu caché des contenants portés."""
    from ..francais import designer
    from ..noms import public, PERSONNES
    biens = []
    for id, o in monde.objets.items():
        if o["lieu"] != "joueur" or o["type"] in PERSONNES:
            continue
        bien = {"id": id, "nom": designer(o), "type": o["type"]}
        # La quantité des affaires portées figure déjà dans le nom de la fiche,
        # même dans le noir ; elle ne dépend pas d'un nouvel examen visuel.
        if "physique" in o:
            bien["pieces"] = o["physique"]["pieces"]
        if monde.visible(id):
            if "allume" in o:
                bien["allume"] = bool(o["allume"])
        biens.append(bien)
    return public(monde, biens)


def destinataires_publics(monde):
    """Présence et portée publiques ; aucune acceptation de don présumée."""
    from ..francais import designer
    from ..noms import public
    from ..spatial import proche
    return public(monde, [{"id": id, "nom": designer(o)} for id, o in monde.objets.items()
                         if o["type"] == "personnage" and monde.visible(id)
                         and (not monde.data.get("mode_cases") or proche(monde, id))])


def ressources_publiques(monde):
    """Choix matériels connus, sans capacités, règles ni inventaire d'autrui."""
    from ..francais import designer
    from ..noms import public, PERSONNES
    from ..spatial import proche

    def chez_autrui(o):
        parents = set()
        while o["lieu"] in monde.objets and o["lieu"] not in parents:
            parents.add(o["lieu"])
            o = monde.objets[o["lieu"]]
            if o["type"] in PERSONNES:
                return True
        return False

    biens = []
    for id, o in monde.objets.items():
        if o["type"] in (*PERSONNES, "partie_corps") or chez_autrui(o):
            continue
        porte = o["lieu"] == "joueur" and monde.present_physique(id)
        vu = monde.visible(id)
        if not porte and not (vu and (not monde.data.get("mode_cases") or proche(monde, id))):
            continue
        bien = {"id": id, "nom": designer(o), "type": o["type"]}
        if vu and o.get("foyer"):
            bien["foyer"] = True
        biens.append(bien)
    return public(monde, biens)


class PontWeb:
    def __init__(self):
        self.commandes = Queue()
        self.verrou = threading.Lock()
        self.abonnes = []
        self.historique = []          # les dernières lignes, pour une page ouverte en cours de partie
        self.dernier_etat = None
        self.occupe = True            # tant que la boucle n'attend pas de commande
        self.termine = False

    # --- Diffusion vers les pages ---------------------------------------------------------

    def abonner(self):
        """Une file d'événements pour une page ; elle reçoit d'abord le récit et l'état courants."""
        file = Queue()
        with self.verrou:
            for texte in self.historique:
                file.put({"type": "ligne", "texte": texte})
            if self.dernier_etat:
                file.put(self.dernier_etat)
            file.put({"type": "occupe" if self.occupe else "pret"})
            self.abonnes.append(file)
        return file

    def desabonner(self, file):
        with self.verrou:
            if file in self.abonnes:
                self.abonnes.remove(file)

    def diffuser(self, evenement):
        with self.verrou:
            for file in self.abonnes:
                file.put(evenement)

    # --- Le contrat de la boucle de jeu -----------------------------------------------------

    def ecrire(self, *args, sep=" ", end="\n", **kwargs):
        texte = sep.join(str(a) for a in args).strip("\n")
        if not texte.strip():
            return
        with self.verrou:
            self.historique.append(texte)
            del self.historique[:-HISTORIQUE_MAX]
        self.diffuser({"type": "ligne", "texte": texte})

    def lire(self, prompt=""):
        self.occupe = False
        self.diffuser({"type": "pret"})
        return self.commandes.get()

    def montrer(self, vue):
        self.diffuser({"type": "vue", "nom": vue})

    def comparaison(self, fiche):
        pass  # La comparaison entre modèles reste une affaire du terminal.

    def rafraichir(self, monde, pending, mj):
        from ..carte import carte
        from ..rendu import fiche, regarder
        from ..francais import quantite
        from ..gestes_publics import catalogue_public
        self.termine = bool(monde.data.get("fin"))
        cases = bool(monde.data.get("mode_cases"))
        etat = {"type": "etat", "fin": monde.data.get("fin"),
                "catalogue_gestes": catalogue_public(),
                "scene": None, "carte_texte": "" if cases else carte(monde),
                "fiche": fiche(monde), "regard": regarder(monde),
                "inventaire": inventaire_public(monde), "destinataires": destinataires_publics(monde),
                "ressources": ressources_publiques(monde),
                "salle": monde.data["salles"][monde.joueur["salle"]]["nom"],
                "pv": f'{monde.joueur["pv"]}/{monde.joueur["pv_max"]}', "or": monde.joueur["or"], "or_texte": quantite(monde.joueur["or"], "pièce"),
                "minutes": monde.data["minutes"],
                "proposition": pending.resume(monde) if pending else "",
                "connexion": "hors ligne" if mj is None else "déconnecté" if mj.erreur_auth else mj.connexion}
        if cases:
            from ..scene import scene_percue
            etat["scene"] = scene_percue(monde)
        with self.verrou:
            self.dernier_etat = etat
        self.diffuser(etat)

    # --- Ce que la page envoie --------------------------------------------------------------

    def soumettre(self, texte):
        """Une commande de la page ; refusée si la précédente n'est pas finie."""
        from ..commandes import DescripteurPublic
        direct = isinstance(texte, DescripteurPublic)
        texte = texte if direct else (texte or "").strip()
        if not texte or self.occupe or self.termine:
            return False
        self.occupe = True
        self.diffuser({"type": "occupe"})
        self.ecrire("Corvus > " + ("Geste direct" if direct else texte))
        self.commandes.put(texte)
        return True

    def evenement(self, file, attente=15):
        """Le prochain événement d'une page, ou None après ``attente`` secondes (pour un signe de vie)."""
        try:
            return file.get(timeout=attente)
        except Empty:
            return None
