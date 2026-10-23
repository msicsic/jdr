# Signes : coût, relectures et calibration

Branche `codex-signes-calibration`, non fusionnée. Base du moteur `8855312`,
brief `0ebb31a`. Worktree `tmp-worktrees/codex-signes-calibration` ; le dépôt
principal reste sur `main`. Aucun changement de `planification.py` ou `deliberation.py`.

## 1. Coût à comportement constant

`relations._lecture_pure` conserve le calcul de référence ; `_lecture` mémorise
la lecture par paire orientée, sous la minute, la relation enregistrée et les
valeurs du profil qui règlent l'estompement. `signature_signes` ne retient que
les bandes et seuils que les émissions consomment. `signes.de` dépend de cette
signature, de l'attitude, du guet, du seuil d'attente, du plan, de la fierté,
de la conscience et du seuil de colère ; la minute seule n'invalide plus une
émission inchangée. Pour le joueur : observation et intervalle actif.

`_percus_gardes` garde une entrée par observateur : personnes effectivement
perçues, émissions, lumière et distance, position et regard de l'émetteur,
présence perceptible ou crue de la cible et sa position requise par le geste.
Un esprit éloigné n'invalide plus tous les observateurs. Les mémoires sont
dérivées, hors `data`, et se reconstruisent après rechargement.
`spatial.VERIFICATION` recompare relations, émissions et perceptions au calcul
de référence. Les deux outils de nuits acceptent aussi `rixe`.

Preuve initiale : 20 nuits de 2 h (quatre scénarios et `rixe`, quatre graines),
chronique, mesures et état final complet identiques à `8855312`.
Les mesures définitives et la preuve 8 h seront ajoutées après exécution.

## 2. Relectures

`signes._presence` enregistre les épisodes de perception par observateur dans
`data.suivi_signes` : signes présents, numéro d'épisode, essai, conclusion et
lecture retenue par signe. Une réception partielle de tons ne fait pas disparaître
les autres signes. Une perception complète vide clôt les épisodes, y compris
quand personne n'émet plus rien. Les simples projections restent pures.

`lire` rafraîchit une lecture active équivalente (valeur et cible), sans souvenir
`intention_lue` ni ligne de chronique ; un échec n'écrit pas dans la lecture.
Un épisode nouveau ou une lecture périmée compte de nouveau. La date `apprise`
et l'épisode distinguent une nouvelle impression d'un rafraîchissement ;
`bilan_signes` ne répète que les faits physiques demandés, pas une même impression.
La carte et le contexte conservent l'impression actuelle avec son incertitude.

Tests ciblés : 28 tests des signes et de calibration, dont les guets du Relais et
de l'auberge, retour immédiat d'un signe, péremption, échec préservant la lecture,
deux observations du joueur et 20 minutes d'un bloc ou découpées avec reprise.
Les mesures de nuits avant/après restent à consigner.

## 3. Calibration

La grille sera commune à tous : pénombre 4/3/2, dissimulation 5/4/3,
bande sans interprétation 5/7/9. Le dé, les bonus de familiarité et d'observation,
la distance, le seuil de réussite et les sens des méprises ne changent pas.
L'étude conditionnelle rejugera les jets d'un corpus enregistré ; une nuit libre
avec le réglage retenu vérifiera ensuite les rétroactions sur les décisions.
Ces deux mesures seront distinguées dans les résultats.

## 4. Observer sans voir

En cours de validation. Deux passes Luna de référence terminées sur copies :
`signes-ecart`, `signes-noir`, `signes-guet`. Les refus locaux de `signes-noir`
partent au MJ sur la référence.

## 5. Vols vus, vérifications et limites

Les mesures et constats finaux seront ajoutés après exécution.
