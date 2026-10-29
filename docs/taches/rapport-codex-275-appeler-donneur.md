# Lot 275 — Appeler un interlocuteur inaccessible

Branche **`codex-appeler-donneur`, non fusionnée**, base `7b58eb0` (intégration
`ac63223`). Aucune donnée de scénario modifiée, ni Luna, ni suite complète.

**Invariant et code.** Une étape sociale admissible peut préparer le contact par
l'appel négocié si l'interlocuteur est localisé, inaccessible et cru à portée de
voix. `planification._appeler`, `_chercher` et `rejoindre` raccordent demandes,
achats et négociations à l'inspection/appel existants. Propagation sur les portes
et positions crues, sans position réelle du tiers ; `_couper` arrête le préfixe
avant toute présence ou acquisition supposée. L'appelé garde son libre choix ;
les appels vains restent dans le registre commun, sans rappel par délai. La
remise de nourriture déjà prévue par le moteur supplée le service inaccessible.
Raccord de `pnj_propositions.recours`, sans modification de `deliberation.py`,
`agendas.py` ou `signes.py`.

**Scènes.** Capture exacte crue 7/270 : Ilse hèle, Gorm ne promet pas de venir,
appel retenu. Variante où seul Gorm sait la porte déverrouillée : venue,
retrouvailles, demande, achat, repas, dans cet ordre. Auberge : achat d'une
lanterne portée, silence par méfiance, aucune acquisition supposée. Contrôles de
portée, lieu inconnu, position cachée, délai, négociation ; mondes/rendus/scènes
rechargés et cinq minutes entières/découpées identiques.

**Échecs instruits.** Les 227 tests ciblés distincts sont passés après correction
de trois scènes/oracles : refus indexé par objet, cible explicitement perdue de
vue dans l'épreuve de coût, rappel d'Hugues exigeant une réouverture positive
(bruit nouveau à 16 min, appel à 18). Le complément : **748 tests, 745 verts,
2 échecs, 1 ignoré** (dépendance MiMo facultative absente), 1 732,113 s.
Les deux épreuves en échec **passent sur `7b58eb0`**, preuves archivées ; elles
sont causées par le lot, non préexistantes :

- Rémy appelle Bram sans contrepartie admissible ; sa venue empêche ensuite le
  vol de la paie. `recours` valide désormais l'existence d'une offre avant de
  préparer le contact, par le jugement commun, sans présumer son acceptation.
- Le graphe faim d'auberge/480 gagne 36 successeurs superflus, malgré un service
  accessible. La remise pour soi est proposée seulement si le service est
  inaccessible, ou déjà promise. **Aucun hash ni oracle remplacé** ; les six
  graphes historiques et l'acquisition effective de la paie restent exigés.

Les dix fichiers directement concernés passent : **77 tests verts, 209,391 s**,
dont les sept régressions nouvelles et les oracles intacts des deux échecs.
Traces base/branche avant et après correction de Rémy : six états chacune,
mondes/rendus/scènes identiques après recharge ; la paie est reprise à 1 min.

**Banc acquis avant ces deux corrections, code `a04090c`.** Vingt paires 4 h,
cinq scénarios × graines 1985/7/42/2024, sonde 265/271. **Critère « aucune hausse
de suspects 219 par nuit » tenu sur 20/20** : Relais/2024 **1 → 1**, les dix-neuf
autres nuits **0 → 0** ; zéro plantage. Appels nommés **22 → 37**, retrouvailles
**8 → 19**, à expliquer **21 → 34**, cycles accomplis **503 → 506**. S/F/D selon
la fonction `cats` exacte du 183 : épisodes distincts, familles, diversité
moyenne par PNJ ; moyennes sur quatre nuits :

| Scénario | S avant → après | F avant → après | D avant → après |
|---|---:|---:|---:|
| Relais | 15,25 → 15,25 | 4,25 → 4,25 | 1,75 → 1,75 |
| Mine | 25,75 → 30,75 | 5 → 4,5 | 1,964 → 1,964 |
| Auberge | 9,25 → 9,25 | 4 → 4 | 1 → 1 |
| Crue | 23,5 → 23,75 | 6,75 → 7 | 3,063 → 3,063 |
| Hameau | 22,75 → 26,5 | 7,25 → 7,5 | 2,167 → 2,292 |

**Ces chiffres ne valident pas encore le code corrigé.** La correction du moteur
exige une nouvelle passe de branche détachée, deux travailleurs réduits ; les
vingt références `7b58eb0` seront lues en cache, sans rejeu. Ni complément entier
ni autre campagne relancés. Bruts : `C:/Users/msics/donjon/artifacts/appeler-275/` ;
attendre **`correction/fin.json`**, écrit en dernier. L'ancien `fin.json` reste
`ok=false` et conserve fidèlement les deux échecs de sa version.

Limites : portée estimée sur les croyances (sans cases si position inconnue),
venue et accord incertains ; richesse descriptive sans preuve universelle de
bénéfice. Aucun calcul long à surveiller par l'agent.
