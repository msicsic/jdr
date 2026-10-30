# Lot 359 — E5, accord par choix direct

Branche `codex-e5-choix-direct`, base `origin/integration 6d046070`, laptop.

**Invariant.** Le formulaire web et la commande terminal `accord` figent une
prestation ponctuelle publique, un prix couvert par l'or de Corvus et une limite
facultative. Le délai relatif en minutes est résolu une seule fois en dixièmes
absolus ; le résumé montre aussi la minute de jeu. Corriger un champ ou annuler
le brouillon ne parle, ne paie et n'engage pas. La date reste identique jusqu'à
la validation U-C ; T reste inclus, une offre dépassée n'est pas émise.

**Raccord.** `accords_publics` construit les prestations du vocabulaire E4
(part, allumage ponctuel, verrouillage, objet en un lieu connu, nourriture servie)
sur les seuls biens et interlocuteurs publics. `AccordTerminal` sert à la console
et à la TUI ; le web reçoit la même projection. L'adresse structurée est
revalidée par `parole_directe`, entrée commune extraite du raccord information.
Le seul changement de `paroles.py` branche cette validation dans `_adresse` ;
aucune analyse de texte ni interprétation du clic. Le récapitulatif des termes
datés précise le paiement présent. U-C prépare sur copie, demande « tenter »,
revalide et sauvegarde les effets et les mots avant affichage.
Les règles d'agendas, d'échanges et de propositions sont inchangées.

**Épreuves et mesures.** Neuf méthodes E5 vertes, dont quatre parcours de la vraie
TUI. Six résultats conservés de la passe à 138,669 s ; revalidation/correction
complétées en 39,276 s, parité renforcée rejouée en 30,948 s et durée indéterminée
verte dans `revalidation.json`. Huile d'Odile à l'auberge et
verrou du garde-manger : mêmes termes typés E4, accord, paiement, paroles, scène
et fiche après recharge ; correction prix/date, annulation locale et U-C,
paramètres injectés, délai impossible et accord sans limite. Revalidation réelle
(temps, départ, or changé sans révision), durée indéterminée et borne inclusive.
La parité E4 compare tout l'état hors traces de saisie, avec la même mémoire
perceptive d'ouverture et le même enregistrement du rendu moteur.
E1 et information : 21 tests verts ; autres voisins en cours de clôture.
**Deux parcours mesurés : 9 clics web ou 7 saisies terminal**, confirmation
comprise, lecture et défilement exclus ; **zéro appel au modèle**.
Le contrôle du schéma JSON E4 est sauté : dépendance facultative `jsonschema`
absente du venv de ce poste. Les autres épreuves E2/E3/E4 sont vertes.

**Reprises conservées.** La première passe signale un nom JavaScript réservé
(`public`), corrigé en `projection`. Le harnais d'huile plaçait Corvus à deux
cases d'Odile : le refus de portée était correct ; la rencontre de paiement
est maintenant au contact. Aucune assertion mécanique affaiblie. Les premiers
imports de classes de tests élargissaient involontairement la découverte ; le
fichier final importe les modules de support. Un lanceur voisin a d'abord
masqué le namespace `tests` par `tools/tests.py` : corrigé avant sa reprise.
Le départ simulé choisit une case libre ; le témoin E4 installe la mémoire
perceptive comme la boucle réelle, sans exclure de champ mécanique.
Bruts, mesures et bilans dans `C:/Users/msics/donjon/artifacts/e5-359/`.

**Limites.** Délai saisi en minutes entières ; zéro signifie explicitement
« sans limite négociée ». « Demain » exige un repère et n'est pas converti en
calendrier. Une durée indéterminée est rendue par le refus moteur, sans retirer
la date ; un nouveau brouillon sans limite reste possible. Les listes de tâches
peuvent être longues. Un choix ne promet ni acceptation ni réussite.
Ni prêt daté, maintien continu, paiement futur, offre PNJ durable, renégociation
d'un accord conclu ou compilation libre E6 ajoutés. Pas de Luna, de banc,
de suite complète ni de changement d'autonomie PNJ ; deux travailleurs réduits
au plus. Fusion laissée au superviseur.
