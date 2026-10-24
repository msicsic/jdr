# Lot 43 — les recours sur place d'un gardien en détresse

24 octobre 2026. Branche `codex-gardien-detresse`, **non fusionnée**, base moteur
`dd36155`, fiche `97c82fd`. Aucun MJ ni scénario modifié ; aucun appel à Luna.

**Les trois constats, rejoués sur la base (mine 42, 12 h).** L'appel existe :
Bram appelle à 369 puis à **462** ; `secours={minute:462, apaise:false}` empêche de
répéter le même désarroi. Ce n'est donc plus une absence d'appel. Odon est cru au
bureau à 470 (entendu à 462), puis au baraquement à 600 (entendu à 500), à l'entrée
à 650 et 720 (vu à 637). Le noir ne donne aucune absence certaine ; ici les indices
révisent effectivement son lieu. La garde à 100 n'établit pas sa présence : le
besoin de biens reste pressant. Enfin Bram connaît l'emplacement des biscuits,
mais aussi leur **épuisement vu à 139**. Sa faim à 71 puis 78 n'a donc pas de remède
local. Mathe refuse les vivres nécessaires à elle-même. Capture réelle à 470 :
`tests/data/mine_42_minute_470.json.gz` ; bruts dans `artifacts/codex-43/`.

**Invariant et fonctions.** Après l'échec des recours ordinaires, un gardien peut
chercher l'assistance sans quitter sa charge. `planification._aide_sur_place`
ajoute aux gestes communs `confier` l'allumage d'une source locale ou la remise
d'un moyen utile connu, pour tout besoin qui l'emploie. Aucun effet avant le geste
réel : la projection s'arrête à la demande ; la promesse acceptée s'attend.
`echanges.confier` enregistre chez le demandeur les `aides_attendues` ; refus et
échéance communs comptent, sans lire l'agenda privé de l'aidant. `Vue` et `_entrees`
portent ces entrées, le poste et la détresse ; la méthode d'aide en cours survit au
reclassement du besoin en « presse ». `appeler_a_l_aide` ouvre également un appel
par épisode des autres besoins bloqués ; `detresses_appelees` survit à l'oubli des
souvenirs et à la recharge. Prix de garde, profils, seuils et `REPIT` inchangés.

**Preuves.** Cinq tests nouveaux : capture réelle sans répétition de l'appel ;
scène dérivée où Josse accepte, recharge et allume la lampe de Bram ; nourriture
remise en main propre puis mangée ; autre gardien (Lucien, auberge), faim sans
réponse et un seul appel ; promesse conservée sans effet anticipé et sans lecture
d'un abandon privé, contrôle de mémoire avec `VERIFIER`. Même monde complet,
actes utiles rendus et contexte final après recharge, d'un bloc ou par minutes.
Les aperçus et entrées/sorties intermédiaires dépendent de l'échantillonnage de la
saisie et ne sont pas revendiqués identiques.

**Mesures finales.** Rapide 4 h, mine/auberge × 1985, 7, 42, 2024 contre `dd36155` :
zéro plantage, usurpation ou violation ; mine, mêmes gestes et boucles, une recherche
neuve supplémentaire en 7. Auberge : une recherche supplémentaire en 1985 et 42 ;
en 2024, un appel et un échange de plus, noir 165 → 170 min·PNJ ; aucune nouvelle
bascule ni alerte d'audit, passages/h maximum inchangés. CPU moyen des nuits finales
de branche : mine **10,84 s**, auberge **12,61 s** ; la référence finale vient du
cache et la charge a varié : aucun pourcentage de surcoût fiable déduit.
`VERIFIER` + `spatial.VERIFICATION=1`, mine 42 sur 2 h : **aucun écart ni borne**.
Audit final mine 42, 12 h : demande d'allumage à **500** (Gaspard ne peut pas),
appel de faim à **638**, tous deux au bureau. Les excursions déjà présentes à
583–584 et 636–637 demeurent ; Bram finit au bureau, sécurité 100, faim 78,
toujours en attente. Nuit : appels 3 → 4, échanges 78 → 80, attente 1 250 → 1 245
min·PNJ, mêmes bascules (0) et avertissements redits (2), zéro usurpation/écart.
Suite complète finale, une seule exécution (`tools/tests.py --processus 3`, priorité
réduite) : **1 720 tests, quatre ignorés, aucun échec ni erreur**, 636,9 s. Les cinq
tests du lot et douze tests d'échanges repassent sur le code final.

**Limites.** Chercher un recours ne garantit pas un secours effectif. La demande
exige un interlocuteur cru sur place ; le moteur revalide la parole, les moyens
et l'exécution. Aucun appel périodique ajouté si personne ne répond. Les remises
et allumages n'épuisent pas toutes les formes possibles d'assistance. Ni disparition
générale des besoins en attente, ni immobilité absolue d'un gardien devant tout
autre but garantie : les coûts et priorités existants restent souverains.
