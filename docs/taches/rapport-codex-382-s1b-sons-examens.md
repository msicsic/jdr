# Lot 382 — S1b, sons et examens

30 octobre 2026 · `codex-s1b-sons-examens` · base exacte `integration 06895c7d`.
Code mesuré `ff467a7b`. `origin/integration` revérifiée à la conclusion : encore à cette base.

**Invariant et code.** Les consultations sonores passent par `memoire.bruits_retenus`
et `examen_couvrant`, qui renvoient des copies profondes sans créer d'esprit.
`rafraichir_examen_sonore` modifie la date de l'occurrence couverte dans la porte,
sans nouvelle preuve, déplacement ni crochet. `retenir_examen_sonore`, `retirer_bruits`
et `retenir_bruit_sans_profil` conservent les remplacements, maximums, ordre et identité
des survivants historiques. `ouie.parcouru`, `couvert` et `_retenir_seulement` restent
des façades ; `couvert` ne renvoie plus un alias du stockage. L'orchestration de
`_bruit_inconnu` garde sa séquence : couverture, attente, réveil, retrait, inquiétude,
indice de recherche, chronique et insertion par la porte avec les mêmes crochets.
Les politiques de délibération et de réception des causes restent chez leurs lecteurs.
Liste, plafond 40, clés et sérialisation inchangés ; aucun nouveau registre.

**Contrôle AST.** Douze expressions retirées de la fixture S1a (102 → 90) : les cinq d'`ouie`,
trois de `deliberation`, deux de `causes` et celle du rejeu ; celle de `dernier_son`
est également portée. Les autres lecteurs généraux,
migrations et validations restent pour les lots suivants. Le contrôle détecte aussi
les mutations de champs d'un épisode filtré comme bruit/examen dans une boucle sur
le stock brut, y compris alias local, champ imbriqué et méthode détachée ; six
contre-épreuves ajoutées. Il ne prouve pas tous les flux interprocéduraux de Python.

**Tests.** **158/158 passent dans les douze fichiers ciblés**, sans échec, erreur ni
test ignoré (791,9 s écoulées, deux processus, priorité réduite). Sont couverts :
ouïe, appels restants, demande de cause, socle, esprits, délibération, temps/état,
rejeu, défense et relations. Les six nouveaux tests comprennent le contrôle AST,
quatre tests de porte sonore et le parcours de chaîne. Celui-ci reprend Mathe
(mine 18, appel répété du bureau noir),
puis Bram : voix anonyme et émetteur occupé sur place pour isoler la couverture des
autres motifs. Examen vain, deux appels répétés et bruit mieux situé ; quatre minutes
d'un bloc par intervalles de deux minutes ou découpées en minutes avec recharges.
État complet et ordre JSON identiques, rendu/scène/paroles identiques après recharge.
Les tests de porte contrôlent copie imbriquée, pureté, borne de trente minutes,
examen récent incompatible, maximums, identité et crochets réentrants.

**Empreintes.** **16/16 nuits identiques** : 2 h × graines 1985/7/42/2024 ×
Relais/mine/auberge/crue, chronique, mesures et empreinte de l'état final complet,
sans exclusion ni plantage. Comparaison contre la base exacte `06895c7d` ; les seize
références manquantes ont été calculées une fois puis rangées dans le cache partagé.
Branche mesurée propre, aucun changement de code depuis. Les avis auxiliaires sont
les mêmes des deux côtés (neuf « à expliquer », aucun « non justifié ») ; ils ne sont
pas présentés comme corrigés. Aucune conclusion de coût tirée de ces nuits séquentielles.
Deux processus au plus, priorité réduite ; aucune suite complète ni Luna.
Bruts : `C:/Users/msics/donjon/artifacts/s1b-382/` : `tests.json`,
`empreintes-base.json`, journaux, `fin.json` et `conclusion.json`.

**Recouvrements et limites.** Avec 374 : seul `esprits.dernier_son`, aucune modification
de localisation ni de `planification.py`. Aucun fichier de 380/381 touché. L'oubli
âge/importance et les autres familles de mémoire restent hors lot. Les vérifications
de sauvegarde ont nécessité de sortir de la restriction Windows sur les répertoires
temporaires ; aucun contournement dans le moteur. Aucun contrôle requis du lot en attente.
