# Tâche Codex 189 : une sortie extérieure n'est jamais l'étape d'un but dans les lieux

Régression du lot 181, trouvée par la revue vierge 187 (`docs/taches/rapport-codex-187-revue-vierge-pnj.md`, § 1.4) et
confirmée dans les bruts `C:\Users\msics\donjon\artifacts\revue-187\crue_hameau_g1.txt` : **hameau, graine 1, Brune affamée
cherche Gorm, hèle « Gorm ? » au refuge sans réponse, puis passe la digue (`exterieur: true`) en visitant la salle suivante :
« [120 min] Brune, batelière évacuée quitte les lieux » ; même sort pour Ilse à 177 min.** Le banc du lot 181 (graines
1985/7/42/2024) ne l'avait pas montré.

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le laptop** (`C:\Users\msics\donjon`, l'utilisateur y travaille ;
un lot de données y calcule) : au plus 2 processus de calcul, priorité réduite. Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`, `PYTHONIOENCODING=utf-8`. Fichiers : `presence.py`, `planification.py`
(voisinage, `_chercher`, routes, `Vue`), `pnj.py` (marche) et leurs tests ; **pas** `agendas.py`, `deliberation.py` (lot 184 b),
`narration.py`, `mj.py` (lot 180 b), ni les scénarios (lot 186). **Bruts dans `C:\Users\msics\donjon\artifacts\sortie-189\`.**
Termine par `LOT TERMINÉ` (résumé d'une ligne) ou `QUESTION : …`.

Lis `AGENTS.md`, le rapport 181 et le rapport 187 (§ 1.4, P1), puis `presence.franchir`, les routes et salles de `Vue`,
`planification._chercher` et la marche de `pnj`.

## L'invariant
**Franchir une sortie `exterieur: true` change la présence (`parti`) : ce n'est jamais une transition admissible d'un plan dont
le but est dans les lieux (chercher quelqu'un, aller, garder, se nourrir, s'abriter, rondes) ;
seul un but explicite de départ pourrait l'emprunter (aucun n'existe encore).** Même règle pour la recherche,
la marche, l'estimation des trajets et la clé de recherche (`_entrees`) ; une salle extérieure n'est ni « non visitée » à
explorer, ni abri, ni lieu de rendez-vous. Le joueur garde son départ volontaire du lot 181.

## Vérification
- Tests après rechargement : la capture réelle (hameau graine 1, Brune juste avant 120, puis Ilse avant 177) reste dans les
  lieux et poursuit sa recherche ou son recours ; un autre cas de même nature (autre PNJ, autre but : ronde ou abri) ; le
  départ du joueur par la digue reste possible ; même laps d'un bloc ou découpé ; monde et rendu rechargés identiques.
- Banc rapide 4 h, hameau × graines 1, 1985, 7, 42, 2024 : zéro PNJ `parti`, aucune usurpation, plantage ni boucle nouvelle ;
  empreintes 2 h Relais/mine/auberge/crue identiques (aucune sortie extérieure dans ces scénarios).
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
Commits (signés si une clé est configurée, sinon le dire), branche `codex-sortie-exterieure` poussée (pas `main`) ;
`docs/etat-dev.md` (« Branche `codex-sortie-exterieure`, non fusionnée ») ; rapport d'une page
`docs/taches/rapport-codex-189-sortie-exterieure.md`.
