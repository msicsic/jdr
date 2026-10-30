# Lot 352 — E3, délai jugé sur les moyens crus

Branche `codex-e3-delai-cru`, base `origin/integration e7ea375`, PC fixe
(`msi-desktop`). Code mesuré : `d03d0d2`.

**Invariant.** `echanges.juger_delai(monde, contractant, condition, pour, limite)`
juge une prestation ponctuelle avec le devis commun du contractant. Le résultat
sépare `cout` pondéré, `duree` en minutes, `estimation` et `limite` en dixièmes
absolus. Il distingue `credible`, `impossible` et `indetermine`. Une limite
atteinte exactement est admissible ; une limite passée, des moyens crus
insuffisants et une durée trop longue ont chacun leur cause. Une incertitude
expose un message et un `attendu` proposant explicitement un accord sans limite ;
elle ne supprime aucune clause. Les formes invalides réemploient les refus E1.
Le jugement se fait sur copie, sans jet, parole, paiement ni nouvel engagement réel.

**Fonctions.** `planification.devis_pulsion(..., duree=...)` conserve son résultat
historique et peut renseigner une durée par `duree_devis`. La mesure intervient
avant la coupe des hypothèses dans `_pulsion` et `_devis_remise` : un préfixe
exécutable ne certifie pas l'achèvement. Recherche du destinataire, fourniture
attendue, geste incertain et recherche bornée ne garantissent aucune date.
Le devis du feu ne lit plus l'état privé cru par le payeur : l'offre établit le
besoin de recharge, l'allumage reste celui cru par le contractant. Cette lecture
propre est déjà couverte par `_entrees` ; aucun cache de jugement supplémentaire.
Chaque appel réutilise la recherche commune et ses invalidations sur croyances.

**Épreuves.** 103 tests distincts validés : 93 voisins dans neuf fichiers
(propositions, répétitions, refus retenus, devis observateur, durée/suivi des
délégations, socle, tâches promises, références et réalisations datées), puis
10 épreuves E3 finales, toutes vertes (8,015 s). La première passe groupée
(101 tests, 191,632 s) avait uniquement un placement invalide dans la nouvelle
épreuve E3 ; sa fixture a été corrigée, ses dix tests finaux rejoués.
Huile Odile → Joss, huile Gaspard → Rémy et feu Brune → Gorm : trois verdicts,
limite inclusive, coût distinct du temps, moyens cachés inchangés, connaissance
nouvelle invalidante puis retour aux mêmes moyens, savoir privé du bénéficiaire
sans effet, préfixe hypothétique et borne de recherche. `planification.VERIFIER`
est actif sur les jugements. Les tests comparent monde, scène perçue, rendu et
promesses visibles après recharge ; la chaîne réelle ajoute achat/engagement,
gestes moteur, livraison ou alimentation du feu, issue datée et comptes sans
second paiement. Laps continu/découpé identiques, limite absolue conservée.
Le jugement sans effet couvre l'abandon du brouillon ; aucune interface datée
n'est encore disponible pour une annulation joueur spécifique.

**Banc rapide en cours.** 4 h de jeu, graines 1985/7/42/2024, Relais/auberge/mine,
deux processus à priorité réduite. Comparaisons successives avec `origin/main`
(`0bad227`, le main publié ; le `main` local `c870c8b` est ancien) et la base
exacte `e7ea375`, sans rejouer les nuits présentes dans le cache commun. Les
nuits de `d03d0d2` sont mises en cache et réutilisées pour la seconde comparaison.
Le lanceur compare aussi chroniques, mesures, empreinte finale et audits nuit
par nuit, sans comparer les temps issus du cache aux temps courants.
Bruts : `C:\Users\msics\donjon\artifacts\e3-352\` ; résultats `banc-main.json`,
`banc-base.json`, `synthese-bancs.json` ; fin écrite en dernier : `fin-bancs.json`.
La neutralité des nuits reste à conclure à la lecture de ces résultats.

**Limites.** Socle interne : E1/E2 n'ont préparé aucun point d'évaluation d'offre
datée. Aucun schéma, rendu, prompt ni appelant de jeu ajouté ; E4–E6 restent
nécessaires. Le devis est une estimation sur les croyances, sans garantie de
réussite ni priorité sur la survie. Les contrôles ordinaires du marché restent
en vigueur ; le jugement temporel ne remplace ni faisabilité réelle à l'exécution,
ni accueil, ni prix, ni accord atomique. Ni suite complète, ni Luna, ni banc long.
