# Tâche Codex 105 (coût) : générer les suites d'un nœud moins cher, mêmes nœuds

Lot de 30 à 45 minutes (`AGENTS.md`, « Rythme des lots »). Pas de Luna. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`.
**Un seul poste** : priorité réduite, au plus 2 processus de calcul ; le lot 103 (boucle de garde-manger, `deliberation`) et un
lot MJ tournent en même temps. Ce lot touche `planification.py` (génération des suites), pas `deliberation.py`. Termine ton
dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

**Contexte.** Seuil de l'utilisateur pour avancer `main` : auberge 12 h ≤ ×1,5 contre `42bb9c0`, fixe et tiré ; après le lot 98 b :
**×1,93 / ×2,85**. Le profil du lot 98 (`docs/taches/rapport-codex-98-profil-compare.md`) attribue 58 % du surcoût à la
fréquence des recherches (décision de l'utilisateur en attente, **hors de ce lot**) et 42 % au coût moyen d'une recherche. Ce lot
attaque le coût moyen, à nœuds identiques. Hausses propres relevées 8–12 h (Δ fixe / tiré) : `_normaliser_suites` +16,7 / +41,6 s,
`Etat.apres` +13,0 / +33,5 s, `gestes` −11,6 / +55,2 s, `Vue.arrivee` +11,1 / +19,3 s, `Vue.mesure_aller` +9,0 / +16,9 s,
`_mesurer` +8,4 / +16,0 s, `Vue.prix_route` +5,0 / +12,5 s, `dict.get` +26,8 / +70,1 s.

## L'invariant
**La génération des suites d'un état coûte moins, sans changer un seul successeur** : mêmes gestes, mêmes états suivants, mêmes
coûts (bit à bit), même ordre, mêmes nœuds. Leviers exacts dans l'ordre que le profil désigne : la normalisation des suites faite
une fois par geste et non par état quand elle ne lit que le geste ; `Etat.apres` sans reconstruire ce qui ne change pas (ensembles
portés et faits partagés, ou bitsets si le profil le justifie) ; le trajet d'un `aller` (`arrivee`, `mesure_aller`, `_mesurer`,
`prix_route`) calculé une fois par (salle, contexte de route) dans la `Vue`. Chaque levier mesuré seul ; garder seulement ceux qui
rapportent. Aucune lecture nouvelle hors `_entrees` ; reprises contrôlées par `VERIFIER` / `spatial.VERIFICATION`.

## Vérification
- Captures auberge et mine à 480 (lots 81/86/98 b) : mêmes états/successeurs ordonnés et coûts hexadécimaux que la base, µs par
  nœud avant/après ; monde et rendu identiques après recharge.
- Empreintes 2 h quatre scénarios × quatre graines (référence en cache) ; `VERIFIER` + spatial 1, auberge 42, 2 h.
- CPU 12 h auberge 1985 fixe et tiré, mine 1985 fixe, par paires lancées ensemble (`42bb9c0`/branche, base/branche), deux
  processus, tranche 8–12 h ; `comparer --calcul` mêmes résultats. Dis où cela place l'auberge contre ×1,5.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md` si une règle change, `docs/etat-dev.md` (« Branche
`codex-suites-par-noeud`, non fusionnée »). Rapport d'une page : `docs/taches/rapport-codex-105-suites-par-noeud.md`.
