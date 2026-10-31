# Lot 402 — Vérification d'intégration

31 octobre 2026, PC fixe, branche `codex-verif-integ-4`, code **`4539dd68`**.
**49 archives, 48 nuits achevées : intégration non validée pour avancer `main`.**
Campagnes du brief exécutées une fois, en série, détachées à priorité réduite.
Sources inchangées (empreintes et diff), sans pull, Luna ni suite complète ;
49 références `0bad227` relues sans rejeu. Bruts et synthèse `bilan-final.json` :
`C:/Users/msics/donjon/artifacts/verif-integ-4539dd68/`. `FIN.json` confirme
l'achèvement du lanceur, pas un verdict vert.

**Moyennes par nuit, `0bad227` → `4539dd68`**, uniquement les 36 nuits 12 h
complètes : huit graines par scénario, quatre au hameau. Temps en PNJ·min ;
passages = maximum PNJ/heure ; S/F/D = signatures/familles/moyenne par PNJ
inactifs compris, selon 183. Les lignes 219/227 sont des observations de sonde.

| Mesure | Relais | Mine | Auberge | Crue | Hameau |
|---|---:|---:|---:|---:|---:|
| Sans recours / attente | 0/548,12 → 0/355 | 0/1 208,12 → 0/208,12 | 0/338,75 → 0/83,75 | 0,62/1 138,12 → 0/298,75 | 0/1 062,5 → 1,25/403,75 |
| Noir / eau | 323,75/0 → 273,12/0 | 1 043,12/0 → 194,38/0 | 701,88/0 → 860,62/0 | 23,75/94,38 → 163,75/43,12 | 132,5/13,75 → 125/16,25 |
| Appels / aide | 1,88/0,25 → 4,88/0,38 | 16,38/3 → 13,75/2,25 | 17,5/2,25 → 39,5/1,5 | 3,75/1,38 → 18,12/2,88 | 2,25/1,5 → 15,25/2,75 |
| Bascules / passages max | 0,12/9 → 0/12 | 0/27 → 1,12/41 | 1/40 → 0,88/49 | 0,75/32 → 0,25/44 | 0,25/18 → 1/41 |
| Échanges | 54,62 → 85,62 | 159,12 → 227,62 | 197,88 → 280 | 59,62 → 94,62 | 109,5 → 250,75 |
| Propositions / acceptées | 7,75/3 → 9,75/3,5 | 10,38/0 → 6/0 | 8,5/0,38 → 5,62/0,12 | 7,5/1,12 → 8,25/1,62 | 11,25/2,25 → 13,75/1,5 |
| Avis exprimés / changements | 0/0 → 0/0 | 0/0 → 0/0 | 0/0 → 0/0 | 0,75/0,12 → 1,12/0,12 | 2,25/0 → 0,75/0,75 |
| Disputes / pertes (227) | 0/1 → 0/1,12 | 0/0 → 0/0 | 0/0,12 → 0/0,12 | 0/0 → 0/0,38 | 0,5/0 → 0,25/0,75 |
| Constats / avertissements redits | 11,5/1,25 → 31,88/3,12 | 35,62/1,12 → 32,88/0,12 | 51,25/2,5 → 67,75/2,12 | 17,5/0,75 → 14,62/1 | 22,25/1,25 → 41,25/4,75 |
| Suspects / à expliquer (219) | 0,12/1,25 → 0,25/2,25 | 0,5/7,75 → 0,38/24,5 | 0/6,75 → 0,5/16,5 | 0/1,88 → 0,25/7,75 | 0,25/3 → 0/11 |
| S/F/D | 31,62/5,75/3,06 → 40,38/5,88/3,47 | 101,62/7,12/3,5 → 141,75/6,25/3,14 | 107/6,12/3,09 → 158,62/6/3,09 | 31,88/7,5/3,69 → 56,38/6,62/3,75 | 56,25/8,5/3,42 → 132,5/7,5/4,12 |

**Contrôles.** Un arrêt `VERIFIER` décrit ci-dessous, aucun autre plantage,
aucune violation marquée, usurpation ou mort. Frappes/touchées **15/6 → 50/27**,
dont hameau 2024 **35/18** contre zéro ; deux assommés actuels. **49 états finaux
rechargés**, état/rendu stables ; aucun captif final ni volonté brisée finale.
Captivité transitoire non certifiée par l'échantillonnage. Quatre contrôles
spatiaux achevés sur 8 h ; aucun écart spatial enregistré avant l'arrêt de l'auberge.

**219/227**, sur **48 nuits complètes appariées**, auberge renforcée exclue des
deux côtés : suspects **7 → 13**, à expliquer **167 → 475** (274 : 170 sur 49),
cycles 3 829 → 3 042, préemptions 381 → 1 738, moyens 106 → 167, entrées publiées
utilisées 106 → 173, rendez-vous accomplis 0 → 32 ; dérives 1 203 → 2 570.
Le 219 courant ajoute perception/provenance et renouvellement perceptif (un cas) :
ces totaux ne certifient pas autant de boucles fautives. Pertes 227 **19 → 26** :
21 cessations physiques, quatre départs, une clôture antérieure ; aucune fautive.

**Petits lots à ouvrir, sans correction ici.**

- **Reprise et contrôle des recherches bornées** : auberge 42, avance **360 → 365 min**,
  Lucien `garder:chambre_chaude`, assertion « ancienne borne, complète » : coût
  conservé **82,7204**, recalcul `None`, état commis à 360. Invariant : reprise
  et recalcul comparables sous des garanties de bornage explicites ; défaut de
  reprise ou limite du contrôle à départager. **29 bornes sans plan** alors que
  le contrôle en trouve (dès Lucien `placer:ballot`, 303), contre 88 anciennes
  toutes au coût de contrôle sur 8 h achevées. Écart nouveau.
- **Réessai d'un mandat refusé et réveil d'agenda** : hameau 1985, **129–143 min**,
  Gorm propose 14 fois à Maël et 11 fois à Sève d'évacuer Ilse : `impossible`.
  Nuit : 31 activations « mandataire estimé », 32 sommeils « sans plan admissible
  au coût » ; aucune de ces répétitions dans la même nuit ancienne. Invariant à
  vérifier : preuve pertinente nouvelle pour reprendre mandat, devis et agenda
  après refus. Les textes seuls ne certifient pas l'absence de nouvelles entrées.

**Suivis et limites.** Aubin crue 42 : **14 → 24 passages la première heure**,
**2 → 14 appels sur 12 h** ; rappels crypte 41/42 après nouveaux bruits, pas une
preuve de régression de l'expiration (374). Mine 42 : 24 alternances compagnie/feu
de Josse, absentes de l'ancienne alerte ; quatre alimentations conservées,
pas de faute établie par l'alternance seule. Hameau : attente réduite, S accru,
familles **8,5 → 7,5** ; signatures ≠ épisodes causaux. Rixe/douce : huit nuits
achevées sans violation. A5 : **36 mandats, cinq acceptés, 31 refusés, quatre
comptes rendus**. Remboursements **13 → 9**, pièces **19 → 16**, aucune dette
monétaire finale (distincte des dettes relationnelles) ; voie volontaire 388
non certifiée isolément. Neutralité de S1 non attribuable dans ces changements
groupés ; aucun temps de cache comparé. Détails : `cas-a-instruire.json`.
