# Rapport 161 — consignes d'interprétation invariantes (L3)

27 octobre 2026 — branche `codex-consignes-invariantes`, **non fusionnée**, base
`c22541b`. **Vérification Luna confiée à l’orchestrateur.** `main` intacte.

**Invariant.** `MJ._echanger` assemble toujours les mêmes règles d'interprétation,
quel que soit le dossier disponible, la parole attendue ou le refus courant.
Les quatre `REGLES` techniques renvoient au dossier présent sans en déduire de
ressource ni de possibilité quand il manque. L'exemple matériel du franchissement
est remplacé par la séquence générale prise de l'outil puis franchissement.
Les règles de déplacement sont permanentes, avec leur condition `mode_cases`
explicite. `consignes.RETOUR_INTERPRETATION` et `RETOUR_REFUSE` passent dans
`entree.consigne_retour_moteur`, jamais dans les consignes. Les relances narratives
conservent leur révision en entrée. Aucun schéma, fournisseur, `sources.py`,
`narration.py`, coût, action ou sauvegarde changé ; Luna reste `gpt-6-luna`.

**Preuves sans modèle.** Tests ciblés : première passe, **27 tests verts**,
43,82 s. Suite complète unique : **2 214 tests, 253 fichiers, 16 ignorés,
zéro échec ni erreur, 2 060,44 s**, deux travailleurs réduits. Les deux nouveaux
tests L3 et les neuf tests cache/local sont verts dans cette suite.
Deux scènes console réelles, Relais avec obstacle et atelier avec matériau,
chacune proche puis éloignée : consignes identiques entre scènes et tours,
fiche de faisabilité au contact, invitation à s'approcher à distance, aucune
consommation ni déplacement. État et rendu après recharge vérifiés. Les tests
existants couvrent aussi la relance narrative, la voie locale et les refus.

**Mesure isolée**, huit requêtes sur les quatre mêmes placements, avec/sans retour
moteur : `tools.mesure_prompt.mesurer`, base et branche, aucun réseau. Consignes
moyennes **34 259,75 → 39 910 caractères**, variations **7/7 → 0/7** ; schéma stable
sur les deux côtés. Ces captures ne sont pas les 113 transitions historiques du
lot 149 (42 variations). Comparaison séparée au `_echanger` de `c22541b` : **4/4
états complets et sorties console identiques**, rendus rechargés identiques.
Le volume augmente avec les règles permanentes ; le dégraissage étendu reste L6.
Les préfixes simulés ne prouvent aucun cache ni gain de secondes.

**Luna — « passe Luna faite par l'orchestrateur, à compléter ».** Rubrique
réservée à l'orchestrateur : aucune passe n'a été exécutée par cet agent.
L'orchestrateur prend en charge les deux passes et la poussée, après les rejets
de revue automatique. Commande exacte : `luna-a-jouer.txt` dans les bruts.
Sept scripts distincts : Relais/crypte/atelier/échanges, noms-dialogue, soir-appel,
passage dessous (`sous-obstacle-relais`, car `sous-obstacle-dessous` n'existe pas).
Référence `cdaf371` à relire du cache. Appels et secondes par tour, cache par voie,
`usage.attribution`, variations des consignes, refus/relances/replis et critère du
lot 95 restent **à compléter**. Aucun gain de vitesse ni garantie sémantique nouvelle.

**Charge et livraison.** Suite complète unique différée jusqu'à la fin de la suite
d'intégration, puis deux travailleurs réduits. Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/consignes-161/` (`avant.json`, `apres.json`,
`mesures.json`, tests et journaux). Pas de clé Git de signature configurée.
Commits locaux non signés, aucune clé configurée ; aucune poussée par cet agent.
La reprise finale a corrigé une assertion de test qui attendait le résultat exécuté
alors que le parcours prépare seulement la fiche : attente « Ramper sous ».
Suite complète achevée après le calcul d’intégration, sans chevauchement des suites
ni deuxième lancement. Aucun brut produit dans le worktree.
