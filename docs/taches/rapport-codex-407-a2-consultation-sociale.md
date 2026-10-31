# Lot 407 — A2, consultation sociale

31 octobre 2026 — branche `codex-a2-consultation-sociale`, base `integration`
`b4130dc3412e1a3d384978ef9d78474b0074a3ac`, non fusionnée.

**Invariant.** `donjon/contrats_consultation.py` réunit le sens, les champs
utiles et requis, le schéma, le typage moteur et le rendu public de `qui`,
`localisation`, `ressource` et `reclamer`. `paroles` réemploie ses tables et
ses fonctions ; `comprehension` délègue leur rendu. Le sujet d'une recherche
ne peut être remplacé par un attribut, une valeur ou un interlocuteur voisin.
La réplique seule ne choisit aucun acte. Un sujet vide reste légal pour
réclamer des pièces ; il est requis pour chercher un bien ou une personne.

**Changement.** Les charges mal formées (champ supplémentaire, valeur non
textuelle, sujet requis vide) portent un refus de forme avec champ, reçu et
accepté. Les schémas annoncent les champs neutres et le sujet requis. Le rendu
normalise les codes de besoin comme l'exécution, tout en conservant la
distinction entre recherche lexicale libre et référence exacte du formulaire.
`commandes.consultation_locale` construit le contenu canonique des raccourcis.
Deux raccords limités dans `dialogues` sont nécessaires pour l'employer depuis
les menus information et comptes. `operations.py` reste inchangé : ces actes
sont des contenus de parole, pas des étapes de manœuvre. Aucune nouvelle
opération composée, règle de scénario, revue ni consigne au prompt.

**Mécanique conservée.** Les contrôles de personne connue, d'objet réclamé,
d'adresse et d'audience restent dans les mécanismes actuels. Les réponses
utilisent les croyances du témoin ; la réclamation reste susceptible de
régler un dû même formulée en question. Prix, ressources, refus retenus,
émissions et sauvegardes ne sont pas réécrits. Aucun registre d'esprit ajouté.
Pas de recouvrement identifié avec le code annoncé du 406
(`social.py`/`voix.py`/`memoire.py`) ; `etat-dev.md` reste partagé avec 403/406.

**Preuves ciblées.** Neuf nouvelles méthodes : `ressources/0` (« Aubin, as-tu
du bois ? »), une lampe à l'auberge, deux localisations crues mais fausses,
`ressources/2` et les règlements/refus du banc comptes, question au MJ sans
parole de Corvus et mêmes mots sans acte typé. Vraie boucle console/PontWeb,
« Compris » et réponse sauvés avant affichage, reprise et vues rechargées.
Parité des raccourcis et des charges explicites, refus sans mutation,
schéma effectivement émis ; deux minutes en bloc ou huit tranches avec
recharge, monde complet et vues comparés. Aucune assertion existante modifiée.

**Mesures provisoires — vérification en cours.** Première passe : neuf tests,
219,82 s, huit méthodes vertes et deux sous-cas rouges dans la nouvelle méthode
de localisation. Le montage ne changeait que les coordonnées, sans changer
`lieu` ; corrigé en fixant aussi le lieu, sans changer les attentes ni le jeu.
Rejeu des deux méthodes localisation/biens : **2/2 vertes, 72,35 s**.
La passe finale des **13 fichiers ciblés et voisins**, à un travailleur, est
lancée détachée (`tests.json`, `tests.log`). Empreintes **2 h × quatre graines
1985/7/42/2024 × Relais/auberge**, base exacte puis worktree courant, un
travailleur, `PYTHONHASHSEED=0`, référence mise en cache une seule fois et
branche non cachée : calcul détaché (`empreintes.json`, `empreintes.log`).
Les deux calculs vivent ; priorité réduite, au plus deux travailleurs actifs.
Bruts : `C:/Users/msics/donjon/artifacts/a2-consultation-sociale-407/`.
Le fichier `fin.json` est écrit en dernier après les deux résultats ;
attendre `tests=0`, `empreintes=0`, `erreur=null` avant validation du lot.
Ni suite complète ni Luna. Aucun gain de vitesse revendiqué.

**Limites.** Ce contrat garantit le sens d'une charge typée admise, pas la
fidélité du choix de Luna. Une question au MJ et des propos sans acte typé
restent des faux pendants légaux ; leurs mots ne déclenchent aucune enquête.
Les revues de fidélité actuelles restent en place, A4/A6 hors lot. Les
contraintes de connaissance et d'audience dépendant du monde restent validées
à l'exécution, et ne sont pas déduites du seul schéma. Les mesures finales
sont encore attendues ; ce rapport ne déclare pas l'invariant vérifié.
