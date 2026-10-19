"""Interface Textual ; un seul thread possède la boucle de jeu et l'état mutable."""
from queue import Queue

import pyperclip
from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Footer, Header, Input, Static, TabbedContent, TabPane

from .rendu import carte, fiche, regarder
from .comparaison import texte_resultat, texte_comparaison


# Deux nuances discrètes par terrain gardent le pas d'un mètre lisible sans ponctuation.
SOL_VISIBLE = ("#35594d", "#395e50")
SOL_MEMORISE = ("#293942", "#2c3d46")
SOL_PENOMBRE = ("#22392f", "#253d33")  # visible dans la pénombre : vue courte
SOUVENIR_OBJET = "#aebbc3"


def _ligne_de_cases(ligne):
    """Les lignes du plan métrique commencent par une ordonnée sur quatre colonnes."""
    return len(ligne) >= 5 and ligne[4] == " " and ligne[:4].strip().lstrip("-").isdigit()


def coloriser_plan(dessin):
    """Rend le plan métrique en couleurs, sans modifier la carte ASCII du moteur."""
    rendu = Text(no_wrap=True, overflow="ignore")
    for numero, ligne in enumerate(dessin.splitlines()):
        if numero:
            rendu.append("\n")
        if not _ligne_de_cases(ligne):
            rendu.append(ligne)
            continue
        rendu.append(ligne[:5])
        y = int(ligne[:4])
        for colonne in range(5, len(ligne), 2):
            case = ligne[colonne:colonne + 2]
            case_complete = case.ljust(2)
            nuance = ((colonne - 5) // 2 + y) % 2
            if case_complete == ". ":
                rendu.append(" " * len(case), style=f"on {SOL_VISIBLE[nuance]}")
            elif case_complete == ", ":
                rendu.append(" " * len(case), style=f"on {SOL_PENOMBRE[nuance]}")
            elif case_complete == ": ":
                rendu.append(" " * len(case), style=f"on {SOL_MEMORISE[nuance]}")
            elif case_complete == "##":
                rendu.append(case, style="bold #a6b8ae")
            elif case_complete.endswith("#"):
                rendu.append(case[0], style="bold #efc477")
                rendu.append("#", style="bold #a6b8ae")
            elif case_complete.endswith("~"):
                rendu.append(case[0], style=SOUVENIR_OBJET)
                rendu.append("#", style="bold #a6b8ae")
            elif case_complete.startswith("@"):
                rendu.append(case, style=f"bold #ffe19a on {SOL_VISIBLE[nuance]}")
            elif case_complete.startswith("~"):
                rendu.append(case[1:] + " ", style=f"{SOUVENIR_OBJET} on {SOL_MEMORISE[nuance]}")
            elif (case_complete.startswith(("X", "+", "/", "x"))
                  or case_complete[0] == "H" and case_complete[1:].isdigit()):
                rendu.append(case, style="bold #80d5d0")
            elif case_complete.strip():
                rendu.append(case, style=f"bold #efc477 on {SOL_VISIBLE[nuance]}")
            else:
                rendu.append(case)
    return rendu


def coloriser_legende(legende):
    """Remplace les repères techniques par les couleurs affichées sur le plan."""
    rendu = Text()
    for numero, ligne in enumerate(legende.splitlines()):
        if numero:
            rendu.append("\n")
        if ligne == "~ : dernier aperçu, présence ou état actuels non confirmés":
            rendu.append("  ", style=f"on {SOUVENIR_OBJET}")
            rendu.append(" dernier aperçu, présence ou état actuels non confirmés")
            continue
        if ligne.startswith("~"):
            for index, morceau in enumerate(ligne.split("   ")):
                if index:
                    rendu.append("   ")
                if morceau.startswith("~") and len(morceau) > 1:
                    rendu.append(morceau[1], style=SOUVENIR_OBJET)
                    rendu.append(morceau[2:])
                else:
                    rendu.append(morceau)
            continue
        if not ligne.startswith("@ toi   ## mur"):
            rendu.append(ligne)
            continue
        rendu.append("@ toi   ## mur   ")
        rendu.append("  ", style=f"on {SOL_VISIBLE[0]}")
        rendu.append(" visible, éclairé   ")
        if "pénombre" in ligne:
            rendu.append("  ", style=f"on {SOL_PENOMBRE[0]}")
            rendu.append(" visible dans la pénombre (vue courte)   ")
        rendu.append("  ", style=f"on {SOL_MEMORISE[0]}")
        rendu.append(" exploré hors de vue   cases vides : inconnues")
    return rendu


class PontTerminal:
    def __init__(self, app):
        self.app = app
        self.commandes = Queue()

    def envoyer(self, fonction, *args):
        if self.app.is_running:
            self.app.call_from_thread(fonction, *args)

    def ecrire(self, *args, sep=" ", end="\n", **kwargs):
        texte = sep.join(str(a) for a in args)
        if texte.strip():
            self.envoyer(self.app.ecrire, texte)

    def lire(self, prompt):
        return self.commandes.get()

    def montrer(self, vue):
        self.envoyer(self.app.montrer, vue)

    def comparaison(self, fiche):
        self.envoyer(self.app.recevoir_comparaison, fiche)

    def rafraichir(self, monde, pending, mj):
        # La UI reçoit des valeurs déjà rendues, jamais une référence au monde mutable.
        self.envoyer(self.app.actualiser, {
            "carte": carte(monde), "fiche": fiche(monde), "scene": regarder(monde),
            "mode_cases": self._mode_cases(monde),
            "salle": monde.data["salles"][monde.joueur["salle"]]["nom"],
            "pv": f'{monde.joueur["pv"]}/{monde.joueur["pv_max"]}',
            "or": monde.joueur["or"], "minutes": monde.data["minutes"],
            "proposition": pending.resume(monde) if pending else "",
            "connexion": "hors ligne" if mj is None else "déconnecté" if mj.erreur_auth else mj.connexion,
        })

    @staticmethod
    def _mode_cases(monde):
        try:
            from .spatial import active
            return active(monde)
        except ImportError:
            return False


class SeuilApp(App[int]):
    TITLE = "LE SEUIL"
    CSS_PATH = "tui.tcss"
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        Binding("f1", "aide", "Aide"),
        Binding("f2", "carte", "Carte"),
        Binding("f3", "fiche", "Personnage"),
        Binding("f4", "copier_echange", "Copier échange"),
        Binding("f5", "debug", "Debug MJ"),
        Binding("f6", "focus_carte", "Déplacement carte"),
        Binding("ctrl+s", "sauver", "Sauver", priority=True),
        Binding("ctrl+q", "quitter", "Quitter", priority=True),
        Binding("ctrl+c", "copier_selection", "Copier", show=False, priority=True),
    ]

    def __init__(self, argv=None):
        super().__init__()
        self.argv = [a for a in (argv or []) if a not in ("--tui", "--console")]
        self.pont = PontTerminal(self)
        self.occupe = True
        self.fermeture_demandee = False
        self.derniere_vue = {}
        self.historique = []
        self.indice_historique = 0
        self.brouillon = ""
        self.sorties = []
        self.journal_entrees = []
        self.dernier_echange = []
        self.comparaisons = {}
        self.comparaison_selectionnee = None
        self.debug_visible = False
        self.mode_cases = False
        self.focus_carte = False
        self.saisie_a_restaurer = None
        self.mouvement_local_en_cours = False
        self.session_comparaison = 0

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="corps"):
            with TabbedContent(id="etat", initial="onglet-carte"):
                with TabPane("Carte", id="onglet-carte"):
                    with VerticalScroll(id="vue-carte"):
                        yield Static(id="plan", markup=False)
                        yield Static(id="legende", markup=False)
                with TabPane("Personnage", id="onglet-fiche"):
                    with VerticalScroll():
                        yield Static(id="fiche", markup=False)
            with Vertical(id="recit"):
                with VerticalScroll(id="scene-cadre"):
                    yield Static(id="scene", markup=False)
                with VerticalScroll(id="journal"):
                    yield Static(id="journal-texte", markup=False)
        with Vertical(id="debug-cadre"):
            with Horizontal(id="debug-navigation"):
                yield Button("Précédente", id="debug-precedente")
                yield Button("Suivante", id="debug-suivante")
                yield Button("Dernière", id="debug-derniere")
                yield Button("Retour (F5)", id="debug-retour")
            yield Static(id="debug-question", markup=False)
            with Horizontal(id="debug-resultats"):
                with VerticalScroll(id="debug-principal-cadre"):
                    yield Static(id="debug-principal", markup=False)
                with VerticalScroll(id="debug-secondaire-cadre"):
                    yield Static(id="debug-secondaire", markup=False)
        with Vertical(id="proposition-cadre"):
            yield Static("Les boutons portent sur toute la tentative. Annuler n'exécute rien.", id="portee-tentative", markup=False)
            with VerticalScroll(id="risques"):
                yield Static(id="proposition", markup=False)
            with Horizontal(id="choix"):
                yield Button("Lancer la tentative", variant="primary", id="tenter")
                yield Button("Tout annuler", id="annuler")
        yield Static("Chargement de la partie…", id="statut", markup=False)
        yield Input(placeholder="Corvus > Que fais-tu ?", id="commande", disabled=True)
        yield Footer()

    def on_mount(self):
        self.query_one("#plan", Static).can_focus = True
        self.query_one("#journal").border_title = "Chronique"
        self.query_one("#proposition-cadre").display = False
        self.query_one("#proposition-cadre").border_title = "Une seule tentative"
        self.query_one("#debug-cadre").display = False
        self.query_one("#debug-principal-cadre").border_title = "Principal — pilote la partie"
        self.query_one("#debug-secondaire-cadre").border_title = "Secondaire — jamais appliqué"
        self.rendre_comparaison()
        self.screen.set_class(self.size.width < 76, "etroit")
        self.boucle_jeu()

    def on_resize(self, event):
        self.screen.set_class(event.size.width < 76, "etroit")

    @work(thread=True, exit_on_error=False)
    def boucle_jeu(self):
        from jeu import main
        try:
            code = main([*self.argv, "--console"], interface=self.pont)
        except Exception as exc:
            self.pont.ecrire("Erreur du jeu : " + str(exc))
            code = 1
        self.pont.envoyer(self.terminer, code)

    def terminer(self, code):
        if code:
            self.occupe = False
            self.query_one("#statut", Static).update("Le jeu s'est arrêté. Ctrl+Q pour fermer.")
            self.fermeture_demandee = False
            self.jeu_termine = True
        else:
            self.exit(0)

    def actualiser(self, vue):
        self.derniere_vue = vue
        self.mouvement_local_en_cours = False
        self.mode_cases = bool(vue.get("mode_cases"))
        if not self.mode_cases:
            self.focus_carte = False
        if "\n\n=== LEGENDE ===\n" in vue["carte"]:
            dessin, legende = vue["carte"].split("\n\n=== LEGENDE ===\n", 1)
            prefixe_legende = ""
        else:
            dessin, _, legende = vue["carte"].partition("\n\n")
            dessin = dessin.partition("\n")[2]  # L'échelle reste dans la légende, qui peut se replier.
            prefixe_legende = "1 case = 1 m\n\n"
        plan = coloriser_plan(dessin) if vue.get("mode_cases") else Text(dessin, no_wrap=True, overflow="ignore")
        self.query_one("#plan", Static).update(plan)
        self.query_one("#plan").styles.width = max(map(len, dessin.splitlines()), default=1)
        texte_legende = prefixe_legende + legende.strip()
        self.query_one("#legende", Static).update(
            coloriser_legende(texte_legende) if vue.get("mode_cases") else texte_legende)
        self.query_one("#fiche", Static).update(vue["fiche"].strip())
        scene = vue["scene"].strip().split("\n\n", 1)[-1]
        # Le terminal gère le repli selon la largeur du panneau.
        scene = "\n\n".join(" ".join(p.splitlines()) for p in scene.split("\n\n"))
        self.query_one("#scene", Static).update(scene)
        self.query_one("#scene-cadre").border_title = vue["salle"]
        self.sub_title = f'PV {vue["pv"]} · {vue["or"]} pièces · {vue["minutes"]} min'
        self.query_one("#proposition", Static).update(vue["proposition"])
        self.query_one("#proposition-cadre").display = bool(vue["proposition"])
        self.occupe = False
        saisie = self.query_one("#commande", Input)
        saisie.disabled = False
        for bouton in self.query("#choix Button"):
            bouton.disabled = False
        self.query_one("#statut", Static).update("MJ : " + vue["connexion"] + " · À toi de jouer")
        if self.focus_carte and self.mode_cases:
            self.query_one("#plan", Static).focus()
            self.query_one("#statut", Static).update("Carte active · flèches pour marcher · Échap/Entrée : commande")
        else:
            self.query_one("#commande", Input).focus()
        if self.saisie_a_restaurer is not None:
            self.set_timer(0.05, self._restaurer_saisie_deplacement)
        if self.fermeture_demandee:
            self.soumettre("quitter")

    def ecrire(self, texte):
        self.sorties.append(texte)
        self.sorties = self.sorties[-200:]
        if self.dernier_echange and not self.mouvement_local_en_cours and not texte.startswith("Le MJ réfléchit"):
            self.dernier_echange.append(texte)
        self.ajouter_journal(texte)
        if texte.startswith("Le MJ réfléchit") or "dans le navigateur" in texte:
            self.query_one("#statut", Static).update(texte)
        if texte.startswith("Ecriture de sauvegarde impossible"):
            self.fermeture_demandee = False

    def ajouter_journal(self, texte, style=""):
        entree = Text(texte + "\n", style=style)
        self.journal_entrees.append(entree)
        self.journal_entrees = self.journal_entrees[-400:]
        journal = self.query_one("#journal", VerticalScroll)
        suivre = journal.is_vertical_scroll_end and not self.screen.selections
        self.recomposer_journal()
        if suivre:
            journal.call_after_refresh(journal.scroll_end, animate=False)

    def recomposer_journal(self):
        self.query_one("#journal-texte", Static).update(Text("\n").join(self.journal_entrees))

    def montrer(self, vue):
        if vue == "fiche":
            self.action_fiche()
        elif vue == "carte":
            self.action_carte()
        elif vue == "debug":
            if not self.debug_visible:
                self.action_debug()

    def soumettre(self, texte, enregistrer_historique=True):
        texte = texte.strip()
        if not texte or self.occupe:
            return
        self.occupe = True
        if enregistrer_historique:
            self.historique.append(texte)
            self.historique = self.historique[-100:]
            self.indice_historique = len(self.historique)
            self.brouillon = ""
        else:
            self.mouvement_local_en_cours = True
        saisie = self.query_one("#commande", Input)
        if enregistrer_historique:
            saisie.value = ""
        saisie.disabled = True
        for bouton in self.query("#choix Button"):
            bouton.disabled = True
        self.query_one("#statut", Static).update("En cours…")
        if enregistrer_historique:
            self.dernier_echange = ["Corvus > " + texte]
            self.ajouter_journal("Corvus > " + texte, style="bold #ddc694")
        self.pont.commandes.put(texte)

    @on(Input.Submitted, "#commande")
    def commande(self, event):
        self.soumettre(event.value)

    @on(Button.Pressed)
    def choisir(self, event):
        id = event.button.id
        if id == "debug-retour":
            self.action_debug()
        elif id and id.startswith("debug-"):
            numeros = sorted(self.comparaisons)
            if not numeros:
                return
            index = numeros.index(self.comparaison_selectionnee)
            index = (len(numeros) - 1 if id == "debug-derniere" else
                     max(0, min(len(numeros) - 1, index + (-1 if id == "debug-precedente" else 1))))
            self.comparaison_selectionnee = numeros[index]
            self.rendre_comparaison()
        else:
            self.soumettre(id)

    def on_key(self, event):
        saisie = self.query_one("#commande", Input)
        directions_ctrl = {"ctrl+up": "nord", "ctrl+down": "sud",
                           "ctrl+right": "est", "ctrl+left": "ouest"}
        if self.mode_cases and not self.occupe and event.key in directions_ctrl:
            self._marcher(directions_ctrl[event.key])
            event.prevent_default()
            event.stop()
            return
        if self.mode_cases and not self.occupe and self.focus_carte:
            directions = {"up": "nord", "down": "sud", "right": "est", "left": "ouest"}
            if event.key in directions:
                self._marcher(directions[event.key])
                event.prevent_default()
                event.stop()
                return
            if event.key in ("escape", "enter"):
                self.focus_carte = False
                saisie.focus()
                event.prevent_default()
                event.stop()
                return
        if self.focused is saisie and not self.occupe and event.key in ("up", "down"):
            if self.indice_historique == len(self.historique):
                self.brouillon = saisie.value
            self.indice_historique = max(0, min(len(self.historique), self.indice_historique + (-1 if event.key == "up" else 1)))
            saisie.value = self.historique[self.indice_historique] if self.indice_historique < len(self.historique) else self.brouillon
            saisie.cursor_position = len(saisie.value)
            event.prevent_default()
            event.stop()

    def action_aide(self):
        self.soumettre("aide")

    def action_carte(self):
        self.fermer_debug()
        self.query_one("#etat", TabbedContent).active = "onglet-carte"

    def action_focus_carte(self):
        if not self.mode_cases or self.occupe:
            return
        self.query_one("#etat", TabbedContent).active = "onglet-carte"
        self.focus_carte = not self.focus_carte
        (self.query_one("#plan", Static) if self.focus_carte else self.query_one("#commande", Input)).focus()
        self.query_one("#statut", Static).update(
            "Carte active · flèches pour marcher · Échap/Entrée : commande" if self.focus_carte
            else "Commande active · F6 pour déplacer sur la carte")

    def _marcher(self, direction):
        if not self.mode_cases or self.occupe:
            return
        saisie = self.query_one("#commande", Input)
        brouillon, curseur = saisie.value, saisie.cursor_position
        self.saisie_a_restaurer = (brouillon, curseur)
        self.soumettre("pas " + direction, enregistrer_historique=False)
        saisie.value = brouillon
        saisie.cursor_position = min(curseur, len(brouillon))

    def _restaurer_saisie_deplacement(self):
        if self.saisie_a_restaurer is None or not self.is_mounted:
            return
        texte, curseur = self.saisie_a_restaurer
        saisie = self.query_one("#commande", Input)
        saisie.value = texte
        saisie.cursor_position = min(curseur, len(texte))
        self.saisie_a_restaurer = None

    def action_marcher_nord(self): self._marcher("nord")
    def action_marcher_sud(self): self._marcher("sud")
    def action_marcher_est(self): self._marcher("est")
    def action_marcher_ouest(self): self._marcher("ouest")

    def action_fiche(self):
        self.fermer_debug()
        self.focus_carte = False
        self.query_one("#etat", TabbedContent).active = "onglet-fiche"

    def fermer_debug(self):
        self.debug_visible = False
        self.query_one("#debug-cadre").display = False
        self.query_one("#corps").display = True

    def action_debug(self):
        self.focus_carte = False
        self.debug_visible = not self.debug_visible
        self.query_one("#corps").display = not self.debug_visible
        self.query_one("#debug-cadre").display = self.debug_visible

    def recevoir_comparaison(self, fiche):
        session = fiche.get("session", 0)
        if session < self.session_comparaison:
            return
        if session > self.session_comparaison:
            self.comparaisons.clear()
            self.comparaison_selectionnee = None
            self.session_comparaison = session
        numero = fiche["numero"]
        ancienne = self.comparaisons.get(numero)
        if ancienne and ancienne.get("version", 0) > fiche.get("version", 0):
            return
        suivre = not self.comparaisons or self.comparaison_selectionnee == max(self.comparaisons)
        self.comparaisons[numero] = fiche
        if suivre:
            self.comparaison_selectionnee = max(self.comparaisons)
        while len(self.comparaisons) > 100:
            del self.comparaisons[min(self.comparaisons)]
        if self.comparaison_selectionnee not in self.comparaisons:
            self.comparaison_selectionnee = min(self.comparaisons)
        if numero == self.comparaison_selectionnee:
            self.rendre_comparaison()

    def rendre_comparaison(self):
        if self.comparaison_selectionnee is None:
            self.query_one("#debug-question", Static).update(
                "Comparaison désactivée. Un second modèle exige l'option explicite --compare-model MODELE.\n"
                "Avec --debug, les traces de Luna apparaissent ici. Les commandes locales ne sollicitent aucun modèle.")
            return
        fiche = self.comparaisons[self.comparaison_selectionnee]
        texte = (f'#{fiche["numero"]} · révision {fiche["revision"]} · Corvus > {fiche["question"]}\n'
                 + ("Journal du MJ : un seul modèle. F4 : copier cette trace." if fiche.get("mono_modele") else
                    "Même situation initiale ; chaque modèle enrichit sa copie. F4 : copier les deux résultats."))
        if fiche.get("erreur_journal"):
            texte += "\n" + fiche["erreur_journal"]
        self.query_one("#debug-question", Static).update(texte)
        self.query_one("#debug-principal", Static).update(texte_resultat(fiche["principal"]))
        self.query_one("#debug-secondaire-cadre").display = not fiche.get("mono_modele")
        if not fiche.get("mono_modele"):
            self.query_one("#debug-secondaire", Static).update(texte_resultat(fiche["secondaire"]))

    def action_sauver(self):
        self.soumettre("sauver")

    def copy_to_clipboard(self, text):
        # La copie native fonctionne aussi dans les consoles Windows sans OSC 52.
        try:
            pyperclip.copy(text)
        except pyperclip.PyperclipException:
            self.notify("Presse-papiers indisponible. Réessaie la copie.", severity="error")
            return
        self._clipboard = text
        self.notify("Texte copié dans le presse-papiers.", timeout=2)

    def action_copier_selection(self):
        texte = self.screen.get_selected_text()
        if not texte and isinstance(self.focused, Input):
            texte = self.focused.selected_text
        if texte:
            self.copy_to_clipboard(texte)
        else:
            self.notify("Sélectionne du texte à la souris, ou utilise F4 pour copier le dernier échange.")

    def action_copier_echange(self):
        if self.debug_visible and self.comparaison_selectionnee is not None:
            self.copy_to_clipboard(texte_comparaison(self.comparaisons[self.comparaison_selectionnee]))
        elif self.dernier_echange:
            self.copy_to_clipboard("\n\n".join(self.dernier_echange))
        else:
            self.notify("Aucun échange à copier pour le moment.")

    def action_quitter(self):
        if getattr(self, "jeu_termine", False):
            self.exit(1)
        elif self.occupe:
            self.fermeture_demandee = True
            self.query_one("#statut", Static).update("Fin de l'action en cours, puis sauvegarde et fermeture…")
        else:
            self.soumettre("quitter")

    def on_unmount(self):
        # Libère aussi une boucle en attente lors des tests ou d'une fermeture externe.
        self.pont.commandes.put("quitter")
