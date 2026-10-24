# Tâche Codex 43 : un gardien en détresse agit sans quitter ce qu'il garde

Branche `codex-gardien-detresse` (elle porte ce fichier, issue de l'intégration **dd36155** : lots 38 à 41
compris), worktree dans `tmp-worktrees/`. **Lot de 30 à 45 minutes** (`AGENTS.md`, « Rythme des lots ») : un
invariant, vérification minimale, rapport d'une page. Pas de Luna sur ce poste (aucun changement du MJ).

Un autre lot tourne sur l'autre poste (42, le MJ : `faits_locaux.py`, `mj.py`, `narration.py`, `consignes.py`).
Ne touche pas à ces fichiers.

Lis `AGENTS.md`, `docs/etat-dev.md` (« Décisions prises le 2026-10-24 » : **un gardien en détresse agit sans
partir** ; entrées `pnj-lumiere-garde`, `codex-garde-pret`, `codex-signalements`, `besoins`), `docs/plan-planificateur.md`
(« Lumière et garde », « Dynamique des besoins »), puis `donjon/deliberation.py` (`menaces`, `appeler_a_l_aide`,
`_candidats`, `attentes`, `_plan_lumiere`), `donjon/planification.py` (`prix_gardes`, `Vue.pression`,
`demander_feu` et la demande d'objet), `donjon/echanges.py` (`demander_feu`), `donjon/esprits.py` (révision des
croyances de lieu d'autrui dans le noir).

## Le constat (audit 12 h, mine graine 42, ffcc295 et 42bb9c0 ; archives sur l'autre poste, chiffres ici)
Bram, payeur, garde la bourse de la paie dans le bureau. À 150, Odon (endetté, but « prendre des pièces : la bourse
de la paie ») entre au bureau : la garde de Bram passe à 100 (un gardien ne laisse pas son bien à qui le menace).
À 450 le bureau tombe dans le noir ; Bram craint le noir, sa sécurité monte à 100 en vingt minutes. De 470 à 720 il
ne fait rien d'autre que garder : sécurité 100 et faim (jusqu'à 78) « en attente », c'est-à-dire sans aucun plan
accepté ; pour la lumière, partir coûte plus que rester. Odon quitte le bureau vers 600, mais la garde reste à 100
jusqu'à la fin. Sur 42bb9c0, même blocage après deux allers vers la lumière (465, 585). Bram croit des biscuits
dans le coffre de la paie, dans son propre bureau.

## La décision de l'utilisateur (2026-10-24)
Il garde son bien : la peur ne lève pas la garde. Mais **une détresse qui dure le fait agir sans partir** : appeler
à l'aide, demander qu'on lui apporte de la lumière ou qu'on la lui allume, demander ce qui lui manque.

## D'abord, établir (rejoue la nuit mine 42 de 12 h sur la base ; joueur passif comme `tools/audit_nuits.py`)
1. Pourquoi l'appel à l'aide existant (« il appelle à l'aide si sa crainte l'emporte sur son courage ») ne part pas.
2. S'il croit encore Odon là après son départ (croyance de lieu non révisée dans le noir), et si c'est juste.
3. Pourquoi la faim n'a aucun plan alors qu'il croit des biscuits à portée.
Si la nuit de la base ne reproduit plus le cas, place la scène d'autorité (capture enregistrée) au plus près.

## L'invariant
**Un PNJ dont un besoin presse sans aucun plan qui ne l'éloigne pas de ce qu'il garde cherche les recours qui le
laissent sur place** : appeler à l'aide (règle existante, débloquée si c'est elle qui manque), demander qu'on lui
apporte ou lui allume une source, demander une part ou l'objet qui lui manque à qui il croit pouvoir l'entendre.
Une règle commune à tout gardien et à tout besoin, pas un cas de Bram, de la paie ou du noir. Ce que lit la règle
entre dans `_entrees` si la recherche le lit ; `VERIFIER` reste sans écart. Ne change ni les profils, ni `REPIT`,
ni les seuils, ni le prix de la garde.

## Vérification (minimale)
- Tests après rechargement, même laps découpé : Bram (capture de la mine 42 au moment du blocage) appelle ou demande
  sans quitter le bureau, et ce qui suit (quelqu'un répond, apporte, ou personne) est sauvegardé et rendu ; un autre
  cas de même nature (un autre gardien, à l'auberge par exemple Lucien au grenier noir, ou une scène d'auteur).
- Banc rapide (`tools/comparer_bancs.py --reference dd36155`, 4 h, 4 graines, mine et auberge) : aucune usurpation,
  violation, plantage ni boucle nouvelle (`tools/audit_nuits.py` : appels à l'aide répétés, bascules) ; écarts lus
  en deux lignes. Puis l'audit 12 h de la seule mine 42, branche seule : ce que fait Bram de 450 à 720.
- `VERIFIER` + `spatial.VERIFICATION` 1 sur 2 h, mine 42 : sans écart.
- Suite complète une fois à la fin (`tools/tests.py --processus 3`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/plan-planificateur.md` (la règle), `docs/etat-dev.md`
(« Branche `codex-gardien-detresse`, non fusionnée »). Rapport d'une page :
`docs/taches/rapport-codex-43-gardien-detresse.md` (réponses aux trois questions, invariant, fonctions, mesures,
coût CPU si la règle pèse, limites).
