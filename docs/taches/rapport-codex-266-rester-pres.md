# Lot 266 — rester près d'un proche effrayé

Branche `codex-rester-pres`, **non fusionnée**, base `7404d2d`.
**Reprise ciblée de la suite de fusion `f637396` terminée : 193 tests /
dix-neuf fichiers verts, consolidés**, assertions existantes conservées.
[Diagnostic des onze échecs et preuves de reprise](rapport-codex-266-suite.md).
Les mesures de vingt nuits ci-dessous portent sur `21d5f5b`, avant cette reprise.
Reprise du 29 octobre 2026. **Le précédent verdict « cinq surplus légitimes »
est retiré : les clignotements étaient un défaut de continuité.**
Ni scénario, Luna, comparaison de modèles ni suite complète. Commit local,
push précédemment refusé par la revue automatique (GitHub non vérifié).

**Invariant corrigé.** Une détresse perçue devient une croyance datée de
l'observateur, conservée après perte de vue, changement de regard ou péremption
de l'affichage d'une impression. `signes.retenir_detresses`, appelé par la
perception commune et les nouvelles lectures, enregistre `croyances.detresse`
avec preuve et confiance. `detresse_retenue` n'a aucune échéance et ne lit
aucun besoin privé d'autrui. Les anciennes impressions/raisons adoptées sont
reprises sans inventer leur disparition. `esprits` valide et sauvegarde la preuve.
Les seuls démentis sont un calme corporel discernable, une nouvelle lecture
contradictoire du même signe encore perçu, ou un état connu (parti, mort,
inconscient). Détresse propre et souci retiré rendent aussi le secours inadmissible.
Une provenance rafraîchie sans changement de croyance ne réveille pas le PNJ.

`deliberation.secours`, `_raison_tient` et `_fin_demande` utilisent cette
croyance retenue. Le parent ne cède plus à une intention vide sur simple
non-perception. Pour les demandes portant une raison, un **moyen manqué**
libère son plan et ses préférences, conserve le parent, puis replanifie ; le
geste encore marqué manqué n'est pas recopié. Un autre moyen réellement
admissible au même palier peut servir **la même raison** ; une attente ne
remplace pas une autre attente. Les autres charges gardent leur arbitrage.
Approche, coûts, positions et apaisement par `autour`/`vecu` restent communs.
`agendas.py`/`echanges.py` inchangés pendant cette reprise (seule validation
`peur` déjà autorisée dans le premier). Aucun délai ni cas de personnage ajouté.

**93 tests ciblés distincts verts / dix fichiers**, bilan consolidé.
Dernière reprise : 37 tests en 79,443 s ; dix tests de proximité en 14,675 s.
Les cinq paires réelles sont rechargées ; état entier, rendu et scène comparés.
Les quatre intervalles courts sont vécus sans interruption/reprise. Le cinquième
est vécu jusqu'à une vraie fin observée, sans renaissance automatique :

| Cas | Ancien clignotement (dixièmes absolus) | Résultat corrigé |
|---|---:|---|
| Brune/Ilse, crue 1985 | 49663 → 49763 | Contrat et `depuis` maintenus malgré le regard NE/SO. |
| Brune/Ilse, même nuit | 49784 → 49900 | Maintien malgré déplacement et regard ; aucun nouveau départ. |
| Aubin/Ilse, hameau 7 | 23408 → 23832 | Maintien ; les rondes ne remplacent plus le secours sur non-perception. |
| Maël/Ilse, hameau 7 | 22905 → 36600 | Tient depuis 38 ; vraie fin à 60 sur nouvelle lecture `mefiance`, preuve fausse retenue. |
| Maël/Gorm, hameau 2024 | 121810 → 121820 | Le pas de Brune et le regard de Gorm ne rompent plus le parent. |

Autres contrôles : calme effectivement vu, lecture contradictoire, souci retiré,
détresse/faim propres, perte de vue/noir, absence de lecture privée, moyen
manqué sans perte du parent, autre moyen disponible, état/rendu/scène après
recharge, laps entier/découpé. L'oracle de garde de Lucien est conservé intact ;
l'ancien oracle qui imposait la clôture de toute demande sur échec d'un moyen
est remplacé par la conservation de sa raison, sans conserver le plan manqué.

**Banc de continuité terminé**, code 0, 374,736 s : code `21d5f5b`, branche
seule, vingt nuits de 4 h, deux travailleurs à priorité réduite. Les vingt
références `7404d2d` viennent du cache, aucune rejouée. **Même sonde que
le premier banc** : `0ff727d`, blob `4e2c68d073fcdf71d4996da93527bf3cdd02267b`,
instrumentation `1f6b05da83` ; sonde d'intégration 265/271 non utilisée.
**Critère « aucune hausse de suspects par nuit » tenu sur 20/20 : 2 → 0.**
Chaque cellule ci-dessous donne référence → branche ; graines dans l'ordre indiqué.

| Scénario | 1985 | 7 | 42 | 2024 | Secours commencés | Minutes apaisées |
|---|---:|---:|---:|---:|---:|---:|
| Relais | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 4 | 36,310 |
| Mine | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 40 | 112,645 |
| Auberge | 0 → 0 | 0 → 0 | 0 → 0 | 1 → 0 | 17 | 1,528 |
| Crue | 0 → 0 | 1 → 0 | 0 → 0 | 0 → 0 | 20 | 29,148 |
| Hameau | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 102 | 22,763 |

**183 départs de secours ; 202,393 min** de sécurité urgente effectivement
en baisse sous compagnie de secours. Ce compteur ne mesure ni un gain causal
contre la référence, ni la réussite de chaque départ. Aucun plantage,
usurpations 0 → 0 ; cycles accomplis 489 → 420, entrées à expliquer 55 → 56,
bascules 3 → 1, appels à l'aide 8 → 3, avertissements redits 3 → 6.

**Gorm, hameau 7 :** l'ancienne attente nouvelle de 155 min appartenait au
premier correctif, désormais remplacé. La référence avait déjà 195 min sans
but sous devoir pressant (75 confiées + 120 en attente) ; la branche corrigée
en a **0** aux relevés de cinq minutes, sans alerte `fige_presse`. Ce résultat
n'établit pas que tout est réglé : Gorm commence 44 secours vers Ilse, sur
les 50 du hameau 7 ; cycles 14 → 50, tous classés accomplis par cette sonde,
aucune minute urgente apaisée mesurée cette nuit. Cette fréquence reste une
limite à examiner, pas une preuve de légitimité de chaque reprise.

**Alertes nouvelles à conserver pour l'intégration :** sans but sous devoir
pressant, marchand relais 7 (155 min, confié) et Josse mine 7 (185 min,
satisfaite) ; Lucien auberge 42, 95 min dans le noir avec `pres Hugues` ;
Brune crue 1985, appel « Gorm ? » répété neuf fois. Avertissements redits
nouveaux : mine 1985 (1), auberge 42 (1), hameau 1985 (3), avec disparition
de deux anciens. Deux nouveaux constats de cessation physique de torche
(Brune, relais 7/hameau 7) sont marqués `violation: false`. Le critère 219
est satisfait ; ces autres écarts ne sont pas déclarés corrigés ni légitimes.

Bruts `C:/Users/msics/donjon/artifacts/rester-266/` : `continuite-captures/`
(`intervalles-complets.json`, mondes/rendus/scènes, `tests-consolides.json`),
`continuite-banc/` (`fin.json`, `bilan.json`, `validation.json`, vingt nuits
et référence). L'ancien 2 → 6 est historique ; il ne décrit plus ce code.
