# Tâche Codex 139 (données) : la crue étendue aux évacués du hameau

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna. **Poste : le PC fixe** (`C:\Users\msics\donjon`). Python :
`C:\Users\msics\donjon\.venv\Scripts\python.exe`. Deux autres lots tournent sur ce poste : au plus 2 processus de calcul,
priorité réduite. **Données d'abord** : un scénario dérivé nouveau, sans changer `scenario_crue.json` ni aucun autre scénario
existant, ni le moteur. Touche seulement le nouveau JSON, son chargeur (sur le modèle de `rixe.py`), l'enregistrement du
scénario dans `banc_pnj.py` (choix `--scenario`, une ligne) et `jeu.py` si une option de jeu est simple à ajouter ; **pas**
`narration.py`, `mj.py`, `paroles.py` (lot 138), ni `tenir.py`, `pnj.py`, `moteur.py`, `commandes.py`, `planification.py`
(lot 136). Si l'enregistrement dans `banc_pnj.py` entre en conflit avec le lot 136, garde-le minimal. Termine ton dernier
message par `LOT TERMINÉ` (résumé d'une ligne) ou par `QUESTION : …`.

Lis `AGENTS.md`, `docs/plan-crue.md` (cadre : vallée, hameau, évacués, cloche, barque), `docs/plan-agendas.md` (§ 9, A5 ;
§ 10, décision 5 : « la crue étendue aux évacués du hameau, six à huit PNJ »), le rapport du lot 125
(`docs/taches/rapport-codex-125-adoption-avis.md` : avis inutiles car chacun a déjà vu l'eau ; il faut une asymétrie des
preuves), puis `donjon/scenario_crue.json` et `donjon/rixe.py`.

## Décision de l'utilisateur (2026-10-26)
Les avis de menace d'eau deviennent utiles **par la crue étendue** (évacués du hameau), pas en retouchant la crue actuelle.

## Ce qu'il faut faire
- Un scénario dérivé `crue_hameau` (nom à garder court) : la crue actuelle plus **deux à quatre évacués** du hameau, pour six à
  huit PNJ en tout, arrivés par la digue avant le début de la nuit, au refuge ou à la galerie. Ils ont vu le hameau noyé, **pas**
  l'eau des salles basses du Relais : leurs croyances initiales ne contiennent aucune mesure d'eau de la conduite ni des vannes,
  alors que Gorm et Aubin en ont. Profils complets (caractéristiques, valeurs, besoins, liens de départ avec un ou deux PNJ du
  Relais, biens modestes), écrits dans l'esprit du cadre du plan, sans règle de comportement propre : uniquement des données.
- Ressources : assez de vivres et de chaleur pour que l'arrivée de bouches supplémentaires crée de la tension sans tout bloquer
  (mesurer, ne pas deviner).
- Vérifier sur le banc ce qu'on attend : des avis de menace exprimés **et adoptés** par des évacués qui n'avaient pas la preuve.

## Vérification
- Le scénario se charge (validation du lot 137 comprise si elle est déjà dans ta base, sinon contrôle `lieu`/`relie` à la main),
  se sauvegarde et se recharge ; une scène courte jouée d'un bloc et découpée donne le même monde.
- Banc 4 h, `crue_hameau` × quatre graines, et la crue × les mêmes graines lue du cache comme témoin : avis exprimés/adoptés,
  disputes, échanges, sans recours, attente, noir, eau, passages par heure ; aucun plantage, violation, usurpation ni boucle
  nouvelle. Les scénarios existants ne changent pas (empreintes 2 h de la crue contre la base : identiques).
- Pas de suite complète si aucun fichier de `donjon/` hors du nouveau scénario et de son chargeur n'est modifié ; sinon une fois.

## Livraison
Commits signés si une clé est configurée (sinon le dire), branche `codex-crue-hameau` poussée (pas `main`).
`docs/plan-crue.md` (le scénario dérivé et ses personnages), `docs/etat-dev.md` (« Branche `codex-crue-hameau`, non fusionnée »).
Rapport d'une page avec la liste des personnages proposés (l'utilisateur pourra les retoucher) :
`docs/taches/rapport-codex-139-crue-hameau.md`.
