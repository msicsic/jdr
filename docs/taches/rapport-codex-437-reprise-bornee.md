# Lot 437 — reprise exacte et contrôle d'une recherche bornée

31 octobre 2026, laptop · branche `codex-reprise-bornee`, base `integration 693200b4`.
**Correction réalisée ; vérifications ciblées et campagne détachée en cours.**
Bruts : `C:/Users/msics/donjon/artifacts/reprise-bornee-437/`.

**Cause établie sur le cas réel.** L'archive renforcée du 402 et son état commis à
360 minutes ont été récupérés du PC fixe. L'avance réelle retrouve la recherche de
Lucien `garder:chambre_chaude` à 364 minutes, dans la transaction 360 → 365.
Sa photographie est versionnée avec celle de 360 dans `tests/data/reprise-bornee-437/`.
Sur les mêmes entrées, sans mémoire ni graphe, le résultat est exactement celui
qui faisait arrêter le contrôle : **82,72039452358611**, **285 nœuds**.
Le témoin uniforme plafonne à **4 000** sans plan ; la référence uniforme complète
plafonne aussi à **60 000** sans plan. Son `None` n'était pas une preuve d'absence.
La complète avec la borne admissible de séjour trouve le même résultat, également
en **285 nœuds**, sans report des devis ni découverte paresseuse de discrétion.
Mesures : `comparaisons.json`, captures et scripts de diagnostic dans les bruts.
L'écart étudié vient du contrôle, pas d'une entrée omise de reprise. Les portages
S1k/S1m et les positions datées ont été relus ; aucune clé n'est modifiée.

**Contrat commun corrigé.** `_verifier` vérifie séparément une reprise mémoire ou
graphe par une recherche jouée neuve : même résultat intégral, même plafond.
Une égalité de coût devant un témoin uniforme borné ne peut plus excuser une
reprise différente. Le témoin historique à 4 000 reste uniforme ; la complète
à `REFERENCE` conserve désormais le minorant admissible de séjour du lot 48.
Gestes, prix, ordre du jeu, plafonds, mémoire sauvegardée et choix restent inchangés.
Si cette complète ne trouve toujours rien, le contrat strict continue de refuser
un résultat différent ; aucun relèvement de plafond ni dispense n'est ajouté.

**Vérification.** Deux contre-épreuves locales passent : rejet d'une reprise
différente même à coût égal, et distinction entre borne sans plan et certificat
d'impossibilité. Six fichiers ciblés sont lancés à deux travailleurs, priorité
réduite : nouveaux tests, borne de séjour, coût des suites, complétion des preuves,
attente bornée et coût de planification. Ils comprennent les captures mine/crue,
les reprises et le monde/rendu après recharge, ainsi que l'avance réelle 360 → 365
avec `VERIFIER` et spatial à 1. Premier lancement confiné inutilisable à cause
des droits des fichiers temporaires Windows ; arrêté puis relancé avec les droits nécessaires.

**Campagne et limites.** `tools/verifier_reprise_437.py` enchaîne les empreintes
2 h, auberge/Relais, graines 1985/7/42/2024, référence exacte en cache, puis
l'auberge 42 sur **8 h**, `VERIFIER`, spatial **0,2**, sans Luna ni suite complète.
Il conserve le cas `placer:ballot` à 303 minutes et contrôle la recharge finale.
Une borne jouée sans plan alors que la complète en trouve reste permise quand
le témoin uniforme rend le même résultat borné : absence de plan trouvable dans
l'effort joué, pas impossibilité du but. Les 29 observations du 402 relèvent de
cette catégorie ; la capture ciblée du nouveau passage reste à lire.
Le verdict des tests et de la campagne reste à reporter après leur achèvement :
**`FIN.json`**, écrit en dernier, porte le succès ou l'erreur. Aucune certification
des 8 h ni des empreintes n'est annoncée avant ce fichier.
