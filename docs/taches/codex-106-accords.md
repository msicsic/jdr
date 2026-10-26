# Tâche Codex 106 : l'accord en nombre des textes générés (« l'outils », « 1 pièces »)

Petit lot (`AGENTS.md`, « Rythme des lots »). Pas de Luna. Python : `C:\Users\msics\donjon\.venv\Scripts\python.exe`. **Un seul
poste** : priorité réduite, au plus 2 processus de calcul ; d'autres lots tournent (planificateur, garde-manger). Ce lot touche
`francais.py` et les fonctions qui composent les textes des échanges et du récit des PNJ, pas `planification.py` ni
`deliberation.py`. Termine ton dernier message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

## Le constat (vérifications d'intégration 5c2ce81 et 47d4d25, persistant)
Mine 7, Odon, minutes 0 et 13 : « l'outils de serrurier » ; auberge 7, Lucien, minute 142 : « 1 pièces ». Bruts :
`C:\Users\msics\donjon\artifacts\verif-integ-47d4d25\` (chroniques et récits), rapport `docs/taches/rapport-codex-94-verif-integ.md`.
Le lot 54 (`francais.groupe_nominal`, élision avec de/à) a réglé les liaisons, pas le nombre.

## L'invariant
**Un nom et son déterminant s'accordent en nombre avec ce qu'ils désignent, partout où le moteur compose un texte** : un objet au
nom pluriel (« outils de serrurier », « planches ») prend un déterminant pluriel ou partitif juste (« les outils », « des
planches »), jamais « l'outils » ; une quantité accorde son nom (« 1 pièce », « 2 pièces »), quantité d'objets, de parts ou de
pièces d'argent comprises. Une seule fonction commune dans `francais` (nombre déclaré par la donnée de l'objet si elle existe,
sinon déduit de son nom), employée par tous les textes composés (échanges, propositions, chroniques, récit, rendu) ; pas de
correction au cas par cas.

## Vérification
- Tests : les deux cas réels et d'autres de même nature (un nom au pluriel déclaré, un nom en -x, une quantité 0/1/2 de pièces et
  de parts), dans la chronique, le récit et le rendu du joueur, après rechargement.
- Empreintes 2 h, Relais et mine × quatre graines (référence en cache) : seules les chaînes accordées diffèrent, aucune mesure ni
  état de jeu (dis exactement lesquelles).
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits signés, branche poussée (pas `main`). `docs/etat-dev.md` (« Branche `codex-accords`, non fusionnée »). Rapport d'une
demi-page : `docs/taches/rapport-codex-106-accords.md`.
