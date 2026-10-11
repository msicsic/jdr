"""Aides de contexte et traces locales ; aucun appel LLM supplémentaire."""
from datetime import datetime, timezone
import copy
import json
from pathlib import Path
import uuid
import time


CONSIGNES_ATELIER = """Tu es le MJ d'un jeu de rôle en français. Tutoie le joueur.
Tu arbitres une intention dans une fiction ; ne réponds pas comme un conseiller de bricolage réel.
Faits fournis = état établi. Conversation = aide pour comprendre les pronoms, jamais une preuve.
Une question de faisabilité appelle dialogue avec proposition null ; elle ne consomme rien.
Une volonté d'agir appelle action, texte vide, proposition structurée. Ne raconte pas sa réussite.
Utilise les identifiants exacts. Ne remplace pas un objectif par une autre action sans l'expliquer.
Les inconnues restent inconnues : pose une question utile si elle dépend du joueur.
L'objectif du scénario est un but, pas une méthode obligatoire. Les suggestions du dossier
sont facultatives. Examine l'idée du joueur avant de proposer la solution déjà décrite.
Sépare fabrication, installation et franchissement. Ne garantis pas qu'un objet fabriqué convient
à tous les obstacles. Ne crée aucun matériau, appui ni mesure manquante dans le texte.
Une réponse dialogue contient 2 à 4 phrases naturelles avec articles, sans détails informatiques.
Une proposition invalide peut être corrigée une seule fois d'après retour_moteur : conserve
l'intention ; explique l'obstacle si tu ne peux pas le résoudre sans changer les faits.
faits contient uniquement les clés publiques utilisées. Appelle repondre_au_joueur une fois.
"""


REGLES_REPRISE = """
La derniere_tentative est le dernier essai réellement résolu, pas une proposition.
« Je retente », « je réessaie » reprend cette tentative lorsqu'elle vient d'échouer :
ne demande pas de la nommer à nouveau. Conserve sa méthode et son rythme, sauf demande
explicite de changement (par exemple prendre son temps). Pour une séquence, les étapes
déjà réussies ne doivent pas être rejouées ; la reprise proposée part de l'étape échouée.
Si aucune tentative n'est identifiable, pose une question. Vérifie les ressources actuelles.
Un échec n'implique pas une pénurie : compare les quantités restantes aux besoins calculés.
Ne dis pas que la ficelle manque quand le dossier montre qu'il en reste suffisamment.
"""


def derniere_tentative(monde):
    for e in reversed(monde.data["journal"]):
        if e.get("jet") is None and e["action"]["action"] != "fabriquer":
            continue
        p = copy.deepcopy(e["action"])
        if not e["reussite"] and e.get("etapes"):
            echouee = next((s["numero"] for s in e["etapes"] if not s["reussite"]), 1)
            p["etapes"] = p["etapes"][echouee - 1:]
        return {"tour": e["tour"], "reussite": e["reussite"], "faits": e["faits"],
                "proposition_pour_reprise": p,
                "consigne": "À revalider sur les ressources actuelles ; ne pas exécuter sans demande."}
    return None


class JournalMJ:
    """Trace mono-modèle hors chronique, sans clé ni jeton de connexion."""
    def __init__(self, dossier, publier=None, effort="medium"):
        self.chemin = Path(dossier) / (datetime.now().strftime("mj-%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8] + ".jsonl")
        self.publier, self.effort = publier, effort
        self.numero, self.session = 0, time.time_ns()
        self.erreur = None

    def __call__(self, trace):
        try:
            self.chemin.parent.mkdir(parents=True, exist_ok=True)
            with self.chemin.open("a", encoding="utf-8") as f:
                f.write(json.dumps({"date": datetime.now(timezone.utc).isoformat(), **trace}, ensure_ascii=False) + "\n")
        except OSError:
            self.erreur = "Le journal local ne peut pas être écrit ; les traces restent affichées ici."
        if self.publier:
            self.numero += 1
            self.publier({"mono_modele": True, "numero": self.numero, "session": self.session,
                          "revision": trace["revision"], "question": trace["intention"],
                          "erreur_journal": self.erreur,
                          "principal": {"modele": trace["modele"], "effort": self.effort,
                                        "statut": trace["etape"], "appels": [trace],
                                        "secondes": trace.get("secondes", 0),
                                        "validation": trace.get("obstacle", ""),
                                        "reponse": trace.get("reponse", {})}})
