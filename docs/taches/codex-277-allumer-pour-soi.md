# Tâche Codex 277 : demander à qui porte une flamme d'allumer un foyer fixe pour soi

Le diagnostic 269 (`docs/taches/rapport-codex-269-coup-torche.md`, fusionné ; bruts et captures
`C:\Users\msics\donjon\artifacts\coup-269\`) montre Aubin (hameau 1985, sur `c870c8b`), chaleur 100, sans aucun plan
pacifique : Gorm porte une torche allumée (bien de Maël, portée avec permission), le brasero et le poêle sont des foyers
fixes. `echanges.demander_feu` n'allume qu'une source **portée par le demandeur** (il la tend au porteur de la flamme) ;
pour un foyer fixe, aucun recours ne demande au porteur de venir l'allumer. « Aucun service de rechange ni aide
attendue », dit le rapport. Aubin finit par assommer Gorm pour prendre la torche.

## L'invariant
**Quand le moyen d'un besoin est d'allumer (ou de rallumer) un foyer fixe que l'acteur ne peut allumer faute de flamme,
et qu'un autre est cru porter une flamme, lui demander de venir l'allumer est un moyen ordinaire : une tâche demandée
par la voie commune existante (`confier` gratuite, `engager` payée), condition d'état `allume` sur ce foyer, jugée par le
devis et le jet communs du destinataire.** Le destinataire décide selon ses propres priorités et relations ; aucun
accord présumé, aucun effet à l'acceptation (il doit réellement venir et allumer) ; le refus est retenu selon sa cause
comme les autres refus. Même voie pour le joueur s'il le demande en parole. Aucune exception par personnage, objet,
foyer ou scénario ; aucune lecture de position réelle.

**Commence par vérifier sur une scène** si `confier`/`engager` avec la condition `allume` sur un foyer est déjà offert
au recours d'un besoin de chaleur (ou de lumière) et pourquoi il ne l'est pas pour Aubin : catalogue des recours,
admission de la condition, devis du destinataire, refus retenu. Si c'est déjà possible et que seul un refus tenant ou un
coût l'écarte, arrête-toi et rapporte-le (`QUESTION : …`) au lieu d'ajouter un mécanisme.

Lot de 30 à 45 minutes. Pas de Luna, pas de suite complète (le superviseur la lance). **Poste : le laptop**, deux
processus au plus, priorité réduite.

**Fichiers attendus** : `donjon/planification.py` (recours et gestes sociaux), `donjon/echanges.py` en raccord. Le lot
266, non fusionné, modifie aussi `planification.py`, `deliberation.py`, `pnj.py`, `signes.py` : raccords minimaux, dis
dans le rapport chaque fonction touchée. Ne touche pas `agendas.py`, `signes.py`.

## Vérification
- Scène construite depuis la capture 269 la plus proche (ou scène d'auteur équivalente au hameau) : Aubin demande à Gorm
  d'allumer le brasero ; Gorm accepte ou refuse selon ses priorités ; s'il accepte, il vient et l'allume réellement, et
  Aubin se chauffe. Autre cas de même nature : autre scénario ou autre foyer (poêle, âtre, fourneau). Contre-épreuves :
  porteur cru sans flamme (aucune demande), refus retenu sans redemande par délai, foyer sous l'eau ou sans combustible.
  Monde, rendu et scène identiques après recharge et laps entier/découpé.
- Tous les fichiers de tests qui exercent les fonctions modifiées (trouve-les par recherche des appelants).
- Banc rapide 4 h, cinq scénarios (`relais`, `mine`, `auberge`, `crue`, `crue_hameau`) × quatre graines, référence de
  l'intégration à ta base (en cache si présente, sinon calculée une fois), sonde actuelle (lots 265, 271, 276) : suspects
  219 par nuit sans hausse, coups, richesse S/F/D (fonction `cats` du lot 183). Calcul long détaché.

## Livraison
- Branche `codex-allumer-pour-soi` poussée (sinon commit local, et dis-le). Rapport d'une page
  `docs/taches/rapport-codex-277-allumer-pour-soi.md` ; entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans
  `C:\Users\msics\donjon\artifacts\allumer-277\`. Termine par `LOT TERMINÉ` (résumé d'une ligne),
  `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
