# Lot 172 — Pas composés et porte d'enfermement

Branche `codex-force-contre-revue`, **non fusionnée**, base `79594e4`
(avance rapide depuis `integration`). PC fixe partagé avec les lots 167 c et
173 ; deux travailleurs de tests au plus, priorité réduite. Aucun fichier réservé
aux autres lots, geste physique, audit narratif ou instruction de contre-revue modifié.

**Invariant.** Le dossier d'un geste composé doit décrire tous les déplacements
que son exécution établit, ainsi que l'état produit par chaque opération de porte.
`tenir.preparer` construit les deux déplacements depuis `valider_trajet` : Corvus
avance et le corps rejoint sa case de départ. Le titre et l'information présentent
ces déplacements comme un seul pas de traînage. `couverture_action` transmet leurs
acteurs, départs et arrivées ; une position dans un lieu non visité est masquée,
sans nom ni coordonnées. Le dossier de porte situe Corvus par rapport aux présences
déjà connues et indique l'état après l'opération : fermée ou verrouillée. Il ne
déplace personne et ne prédit pas une captivité à partir d'issues inconnues.
`consignes` décrit enfermer comme fermer/verrouiller derrière une personne déjà
dans le lieu, et traîner comme les deux pas solidaires. Aucun cas lié à un nom,
une salle ou une formulation particulière.

**Tests.** Les tests de force couvrent le seuil Brune/crypte du banc réel et un
autre seuil, ainsi que Bram/bureau et Rémy/réserve. Les dossiers restent sans
mutation ; coordonnées des deux acteurs vérifiées contre l'exécution, porte
fermée/verrouillée et personne conservée dans son lieu, console avec MJ simulé,
monde et rendu relus après sauvegarde. Un verdict réellement non conforme reste
refusé. Les tests simulés contrôlent le contrat transmis et son exécution, pas
le jugement sémantique de Luna. Première reprise : 27/28 verts ; projection de
verrouillage corrigée (`None` interne signifie l'opération verrouiller, donc
`verrouillee=True`). Reprise : **28/28 verts**. Compléments finaux : **29/29 verts,
39,174 s**, un travailleur, dont le cas réel de traînage dans la console et les
mauvais gestes effectivement présentés à la contre-revue simulée puis refusés.
**Suite complète unique : 2 249 tests, 259 fichiers, 1 279,825 s, aucune erreur
ni test ignoré ; deux échecs MiMo historiques `6 != 5`**, déjà documentés sur la
base, sans rejeu. La suite a précédé les derniers compléments du test force,
repris dans les 29 ciblés finaux ; aucune seconde suite.
**16/16 empreintes moteur 2 h identiques** à `79594e4`, chronique, mesures et
état final complet : Relais, mine, auberge, rixe × graines 1985/7/42/2024.
Les seize références absentes ont été jouées une fois et rangées dans le cache,
puis la branche courante jouée, sans comparaison de temps. Un travailleur réduit,
chevauchant seulement le dernier travailleur de la suite (deux calculs au plus).

**Luna non validée.** Les deux exécutions demandées ont été tentées séquentiellement
sur copies temporaires des scénarios du dépôt : onze scripts, puis traîner et
enfermer. Les treize parties ont échoué avant tout appel réseau au modèle avec
« Coffre ChatGPT illisible ». Aucun changement du coffre, aucune substitution API.
Les compteurs d'appels tentés du harnais ne sont pas des mesures du modèle.
La commande exacte de reprise et le lanceur à priorité réduite sont dans
`C:/Users/msics/donjon/artifacts/force-172/luna-a-jouer.txt` et `jouer_luna.py`.
Le lanceur conserve aussi monde complet et rendu à chaque sauvegarde/recharge.
**Critère des trois appels et amélioration sémantique non certifiés ; aucune
garantie générale d'absence de faux refus ou d'état corporel inventé annoncée.**

Bruts exclusivement `C:/Users/msics/donjon/artifacts/force-172/`. Aucune clé Git de
signature configurée : livraison non signée. `main` intacte ; branche seule poussée.
