"""Deux MJ sur des copies identiques ; seul le résultat principal rejoint le jeu."""
import copy
from datetime import datetime, timezone
import json
from pathlib import Path
from queue import Queue, Empty, Full
from threading import RLock, Thread
import time
from uuid import uuid4

from .monde import ErreurMonde
from .moteur import Moteur


def texte_resultat(resultat):
    lignes = [f'{resultat["modele"]} · raisonnement {resultat["effort"]}', resultat["statut"]]
    if "secondes" in resultat:
        lignes.append(f'{resultat["secondes"]:.2f} s · {len(resultat["appels"])} appel(s)')
    usages = [a["usage"] for a in resultat["appels"] if isinstance(a.get("usage"), dict)]
    if usages:
        entree = sum(u.get("input_tokens", 0) for u in usages)
        sortie = sum(u.get("output_tokens", 0) for u in usages)
        lignes.append(f'Tokens : {entree} entrée / {sortie} sortie (raisonnement inclus)')
    if resultat.get("erreur"):
        lignes += ["", "ERREUR", resultat["erreur"]]
    texte_final = resultat.get("reponse", {}).get("texte", "")
    if not texte_final:
        texte_final = next((a.get("reponse", {}).get("texte") for a in reversed(resultat["appels"])
                            if a.get("reponse", {}).get("texte")), "")
    if texte_final:
        lignes += ["", "TEXTE", texte_final]
    if resultat.get("validation"):
        lignes += ["", "VALIDATION DU MOTEUR", resultat["validation"]]
    if resultat.get("resultat_applique"):
        lignes += ["", "RÉSULTAT DANS LA PARTIE", resultat["resultat_applique"]]
    if resultat.get("engagement_applique"):
        lignes += ["ENGAGEMENT ENREGISTRÉ", json.dumps(resultat["engagement_applique"], ensure_ascii=False, indent=2)]
    if resultat.get("savoirs_appliques"):
        lignes += ["CONNAISSANCES ENREGISTRÉES", json.dumps(resultat["savoirs_appliques"], ensure_ascii=False, indent=2)]
    for i, appel in enumerate(resultat["appels"], 1):
        r = appel.get("reponse", {})
        lignes += ["", f'APPEL {i} — {appel["etape"]}']
        if r.get("texte") and r["texte"] != texte_final:
            lignes += ["TEXTE", r["texte"]]
        if r.get("mode") == "enrichir":
            lignes += ["FAITS PROPOSÉS", json.dumps(r.get("proposition"), ensure_ascii=False, indent=2)]
        elif r.get("mode") == "conversation_pnj":
            lignes += ["ÉCHANGE / ENGAGEMENT PROPOSÉ", json.dumps(r.get("proposition"), ensure_ascii=False, indent=2)]
        elif r.get("mode") == "enrichir_savoirs":
            lignes += ["CONNAISSANCES PROPOSÉES", json.dumps(r.get("proposition"), ensure_ascii=False, indent=2)]
        elif r.get("mode") == "enrichir_espace":
            lignes += ["ABORDS PROPOSÉS", json.dumps(r.get("proposition"), ensure_ascii=False, indent=2)]
        elif r.get("mode") == "enrichir_joueur":
            lignes += ["DÉTAILS DU PERSONNAGE PROPOSÉS", json.dumps(r.get("proposition"), ensure_ascii=False, indent=2)]
        elif r.get("proposition"):
            titre = "OPÉRATIONS PROPOSÉES" if r["proposition"].get("action") == "composer" else "ACTION PROPOSÉE"
            lignes += [titre, json.dumps(r["proposition"], ensure_ascii=False, indent=2)]
        if r.get("faits"):
            lignes.append("Sources : " + ", ".join(str(f) for f in r["faits"]))
        if appel.get("erreur"):
            lignes.append(appel["erreur"])
    # Utile aussi pour les tests ou connecteurs qui n'émettent pas de traces d'appels.
    if not resultat["appels"] and resultat.get("reponse"):
        lignes += ["", json.dumps(resultat["reponse"], ensure_ascii=False, indent=2)]
    return "\n".join(lignes)


def texte_comparaison(fiche):
    if fiche.get("mono_modele"):
        return (f'JOURNAL MJ #{fiche["numero"]} · révision {fiche["revision"]}\n'
                f'Corvus > {fiche["question"]}\n\n' + texte_resultat(fiche["principal"]))
    return (f'COMPARAISON #{fiche["numero"]} · révision {fiche["revision"]}\n'
            f'Corvus > {fiche["question"]}\n\nPRINCIPAL — pilote la partie\n'
            + texte_resultat(fiche["principal"]) + "\n\nSECONDAIRE — jamais appliqué\n"
            + texte_resultat(fiche["secondaire"]))


class Comparateur:
    def __init__(self, principal, secondaire, publier=None, dossier=None):
        self.principal, self.secondaire = principal, secondaire
        self.publier = publier
        self.verrou = RLock()
        self.fiches = {}
        self.numero = 0
        self.session = time.time_ns()
        self.ferme = False
        self.file = Queue(maxsize=8)
        self.chemin = None
        self.erreur_journal = None
        if dossier is not None:
            self.chemin = Path(dossier) / (datetime.now().strftime("comparaison-%Y%m%d-%H%M%S-") + uuid4().hex[:8] + ".jsonl")
        self.thread = Thread(target=self._secondaire, name="MJ-comparaison", daemon=True)
        self.thread.start()

    def __getattr__(self, nom):
        return getattr(self.principal, nom)

    def _publier(self, numero, role=None, **modifications):
        with self.verrou:
            if self.ferme:
                return
            fiche = self.fiches[numero]
            fiche["version"] = fiche.get("version", 0) + 1
            if role:
                fiche[role].update(modifications)
            fiche["date"] = datetime.now(timezone.utc).isoformat()
            if self.chemin and not self.erreur_journal:
                try:
                    self.chemin.parent.mkdir(parents=True, exist_ok=True)
                    with self.chemin.open("a", encoding="utf-8") as fichier:
                        fichier.write(json.dumps(fiche, ensure_ascii=False) + "\n")
                except OSError:
                    self.erreur_journal = "Journal de comparaison indisponible ; résultats conservés à l'écran."
            if self.erreur_journal:
                fiche["erreur_journal"] = self.erreur_journal
            copie = copy.deepcopy(fiche)
        if self.publier:
            try:
                self.publier(copie)
            except Exception:
                # Une fenêtre de debug fermée ne doit jamais perturber le jeu.
                pass

    def _executer(self, numero, role, mj, monde, intention, pending, resultat=None):
        debut = time.monotonic()
        appels = []
        def observer(trace):
            appels.append(copy.deepcopy(trace))
            self._publier(numero, role, appels=copy.deepcopy(appels))
        ancien = mj.observateur
        mj.observateur = observer
        self._publier(numero, role, statut="En cours")
        try:
            reponse = mj.raconter_resultat(monde, resultat) if resultat is not None else mj.echanger(monde, intention, pending)
            validation = "Dialogue sans action."
            if reponse["mode"] == "action":
                try:
                    validation = Moteur(monde).preparer(reponse["proposition"], origine="comparaison").resume(monde)
                except ErreurMonde as exc:
                    validation = "Refus / avis du moteur : " + str(exc)
            elif "_enrichissement" in reponse:
                validation = "Compléments descriptifs validés sur une copie."
            elif "_savoirs" in reponse:
                validation = "Connaissances narratives validées sur une copie ; aucune propriété physique modifiée."
            elif "_conversation_pnj" in reponse:
                validation = "Conversation validée sur une copie. " + " ".join(reponse["_conversation_pnj"]["rapport"]["faits"])
            self._publier(numero, role, statut="Terminé", reponse=copy.deepcopy(reponse),
                          validation=validation, secondes=round(time.monotonic() - debut, 3))
            return reponse
        except Exception as exc:
            erreur = str(exc) if isinstance(exc, ErreurMonde) else "Erreur interne du comparateur : " + type(exc).__name__
            self._publier(numero, role, statut="Erreur", erreur=erreur,
                          secondes=round(time.monotonic() - debut, 3))
            raise
        finally:
            mj.observateur = ancien

    def echanger(self, monde, intention, proposition_en_attente=None):
        return self._lancer(monde, intention, proposition_en_attente)

    def raconter_resultat(self, monde, resultat):
        return self._lancer(monde, "Récit de la manœuvre résolue", None, resultat)

    def _lancer(self, monde, intention, proposition_en_attente=None, resultat=None):
        # Copies prises AVANT tout appel et avant toute application de la réponse principale.
        principal, secondaire = monde.copier(), monde.copier()
        pending = copy.deepcopy(proposition_en_attente)
        with self.verrou:
            self.numero += 1
            numero = self.numero
            self.fiches[numero] = {
                "numero": numero, "session": self.session, "revision": monde.data["revision"], "question": intention,
                **{role: {"modele": mj.modele, "effort": mj.effort, "statut": "En attente",
                          "appels": []} for role, mj in (("principal", self.principal), ("secondaire", self.secondaire))},
            }
            if resultat is not None:
                self.fiches[numero]["resultat_resolu"] = copy.deepcopy(resultat)
        self._publier(numero)
        try:
            self.file.put_nowait((numero, secondaire, intention, copy.deepcopy(pending), copy.deepcopy(resultat)))
        except Full:
            self._publier(numero, "secondaire", statut="Non lancé : huit comparaisons attendent déjà")
        return self._executer(numero, "principal", self.principal, principal, intention, pending, resultat)

    def _secondaire(self):
        while True:
            tache = self.file.get()
            if tache is None:
                return
            numero, monde, intention, pending, resultat = tache
            if self.ferme:
                return
            try:
                self._executer(numero, "secondaire", self.secondaire, monde, intention, pending, resultat)
            except Exception:
                pass  # L'erreur est déjà visible dans la fiche ; le principal continue.

    def noter_resultat(self, texte, engagement=None, numero=None):
        numero = self.numero if numero is None else numero
        if numero:
            self._publier(numero, "principal", resultat_applique=texte, engagement_applique=engagement)

    def noter_savoirs(self, texte, proposition):
        if self.numero:
            self._publier(self.numero, "principal", resultat_applique=texte, savoirs_appliques=proposition)

    def fermer(self):
        # Ne bloque pas la fermeture sur le réseau. Un appel déjà envoyé peut finir côté serveur.
        with self.verrou:
            if self.ferme:
                return
            incompletes = [(n, r) for n, f in self.fiches.items() for r in ("principal", "secondaire")
                           if f[r]["statut"] in ("En attente", "En cours")]
        for n, r in incompletes:
            self._publier(n, r, statut="Interrompu à la fermeture (requête envoyée éventuellement consommée)")
        with self.verrou:
            self.ferme = True
        while True:
            try:
                self.file.get_nowait()
            except Empty:
                break
        self.file.put_nowait(None)
