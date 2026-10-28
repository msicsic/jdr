# Lot 266 — rester près d'un proche effrayé

Branche `codex-rester-pres`, **non fusionnée**, base `7404d2d`.
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

**Anciennes mesures, désormais historiques :** 84 secours, 161,077 min de
sécurité urgente en baisse sous compagnie ; compteur 219 brut 2 → 6.
Gorm hameau 7 : sans but pressé 195 → 195 min aux relevés, confié 75 → 40,
attente 120 → 155 ; ni absence de moyens sûrs vers le brasero ni attente
continue de 155 min imputables à une rupture de `pres`. Le nouveau banc devra
remesurer cette trajectoire ; le précédent diagnostic ne valide plus le lot.

**Banc de continuité détaché en cours : branche seule, vingt nuits 4 h**,
cinq scénarios × 1985/7/42/2024, deux travailleurs réduits. Référence `7404d2d`
exclusivement en cache, aucun calcul de référence autorisé. **Même sonde que
le premier banc** : `0ff727d`, blob `4e2c68d073fcdf71d4996da93527bf3cdd02267b`,
instrumentation `1f6b05da83` ; sonde d'intégration 265/271 non utilisée.
**Critère : aucune hausse de suspects par nuit. Aucune validation avant résultat.**
Bruts `C:/Users/msics/donjon/artifacts/rester-266/` : `continuite-captures/`
(`preuves.json`, `intervalles-complets.json`, mondes/rendus/scènes et
`tests-consolides.json`), fin attendue `continuite-banc/fin.json`.
