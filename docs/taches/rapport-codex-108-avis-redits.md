# Lot 108 — valeurs dites par destinataire

Base `a73a35d`, branche `codex-avis-redits`, non fusionnée. Aucun Luna.

**Diagnostic.** Les premières traces sur la base établissent la cause ;
le rejeu exact de `47d4d25` confirme six répétitions crue 2024 justifiées :

| Locuteur → destinataire | Annonces (min) | Rallumage connu entre-temps |
| --- | --- | --- |
| Aubin → Ilse | 0 / 238 | vu à 102 |
| Brune → Aubin | 122 / 258 / 445 | vu à 240 / 381 |
| Brune → Gorm | 146 / 242 / 444 | vu à 241 / 382 |
| Ilse → Gorm | 242 / 445 | Gorm croit encore le rallumage à 382 avant Brune à 444 |

Mine 2024 76/79 et mine 7 76/78 : `lampe_rechange_2` puis
`lampe_rechange_1`, deux objets homonymes. Ces paroles sont des constats,
sans contournement ni saturation (sept entrées au maximum).

**Correction générale.** `reviser_dits` effaçait tous les destinataires
quand le seul locuteur changeait de croyance. Le registre conserve désormais
chaque valeur dite par destinataire. `croire` transmet la croyance précédente :
seul un changement appris par le destinataire rouvre ses suivis ; une
réaffirmation les conserve. Les conclusions dérivées restent suivies même
sans parole. Nouvelles, menaces et `_a_dire` partagent ce contrat.
`esprits.installer` migre les anciennes listes. Moteur limité à
`social.py`/`esprits.py`.

**Preuves.** Captures crue 140/mine 70 : mêmes monde, chronique et rendu
rechargés, laps d'un bloc ou découpé ; annonces justifiées conservées.
Tests complémentaires : aller-retour connu du seul locuteur, changement
connu du destinataire, réaffirmation après refus, valeurs par auditeur,
lieux, menaces et migration. Suite complète unique : **2 007 tests,
16 ignorés, 1 915,93 s**, 214 fichiers, deux processus réduits.
Six empreintes monde actualisées après restitution exacte des six SHA-256
historiques par conversion inverse du seul registre ; plans et rendus
inchangés. **11 tests repris verts en 14,23 s**, dans les deux fichiers concernés.

Banc final **4 h × quatre scénarios × quatre graines** : 16 références
réutilisées du cache, aucun plantage ni usurpation. Relais/mine/auberge/crue :
répétitions textuelles **0/7/0/1 → 0/8/0/1**, constats confiés
**9/83/37/22 → 9/84/37/22** ; mêmes catégories d'audit. Trace typée mine
42 : le supplément textuel à 76/77 concerne aussi les deux lampes distinctes.
Mine 2024 : les retours d'intention suivent des changements chez les auditeurs
(Mathe, fatigue à 117 avant Josse à 137 ; Rémy, fatigue à 11 avant Mathe
à 11). Les anciennes paroles refusées restent notées « connu » et ne
remplacent pas une croyance plus récente. Temps du cache non comparables.

**Limites.** Les valeurs déjà effacées d'une ancienne sauvegarde restent
irrécupérables. Les répétitions textuelles justifiées restent permises.
Le rendu instantané des déplacements varie avec le regroupement des
attentes ; état, chronique et rendu après recharge sont identiques.
Bruts/scripts : `artifacts/avis-108/` ; sources et bruts historiques lus seuls.
