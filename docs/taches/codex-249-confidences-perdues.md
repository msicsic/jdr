# Tâche Codex 249 (diagnostic) : les confidences que perd le lot 235 à la mine et au Relais

Le lot 235 (branche `codex-sait-observations-c`, `942a3c2`, base `adb52c4`, **non fusionnée**) retire la lecture du
savoir réel de l'auditeur dans `social.bavarder` (`_sait`) : le locuteur ne dit que ce qu'il croit nouveau **et**
pertinent pour l'auditeur (`social._utile` : biens, portages, intentions perçues, engagements et supports crus). Rapport :
`docs/taches/rapport-codex-235-sait-observations-c.md` sur cette branche. Confidences Relais/mine/auberge/crue/hameau
**25/101/47/65/62 → 5/10/7/50/47** : la crue et le hameau gardent l'essentiel, **la mine et le Relais perdent 80 à 90 %**.

Décision de l'utilisateur (2026-10-28) : **diagnostiquer avant de choisir** entre une nouvelle reprise ciblée, la fusion de
235 après correction de ses tests, ou la mise de côté. **Aucun code du jeu dans ce lot.**

## Ce que le rapport doit établir
1. **L'inventaire des confidences perdues** à la mine et au Relais (quatre graines, 4 h), base contre 235 : par
   famille (guet, constat matériel, ressource, lieu d'un bien, intention lue, avertissement…), avec locuteur, auditeur,
   contenu et minute ; et ce qui est gardé.
2. **Pour chaque famille perdue, leur utilité** : l'auditeur s'en est-il servi dans la référence (décision changée,
   but, demande, garde, évitement, dans l'heure qui suit) ? Une confidence utile perdue est un défaut du critère ;
   une confidence que personne n'emploie est une perte légitime (bavardage redondant ou hors sujet).
3. **Pourquoi `_utile` écarte chaque famille utile** : la condition qui manque (fonction, croyance lue), sans proposer
   de lecture privée de l'auditeur.
4. **Les huit écarts de tests non résolus et les deux suspects nouveaux** (Aubin/Ilse Relais 2024, Mireille/Mathurine
   auberge 2024) : pour chacun, en une ligne, attente périmée ou défaut réel, et à quelle famille il se rattache.
5. **Une recommandation** parmi : élargir le critère (dire précisément quoi, en un invariant), fusionner 235 tel quel
   après correction des tests, ou mettre de côté.

## Sources et moyens
Bruts du lot 235 recopiés dans `C:\Users\msics\donjon\artifacts\sait-235\` (bancs `banc.json`/`banc-final.json`,
témoins `temoins-adb52c4.json`, `synthese.json`, `diagnostic.md`, suite). Rejoue des nuits seulement si les bruts ne
suffisent pas, sur des worktrees détachés de `adb52c4` et `942a3c2`, une nuit à la fois.

Lot de 30 à 45 minutes. **Poste : le laptop** (l'utilisateur y travaille) : un processus, priorité réduite. Pas de Luna,
pas de suite complète, pas de banc long.

## Livraison
- Branche `codex-confidences-perdues` : seulement `docs/taches/rapport-codex-249-confidences-perdues.md` (une à deux
  pages) et une entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans
  `C:\Users\msics\donjon\artifacts\confidences-249\`. Poussée (pas `main`). Termine par `LOT TERMINÉ` (résumé d'une
  ligne) ou `QUESTION : …`.
