# Tâche Codex 234 : une attitude de placement périmée ne bloque pas un recours

Le lot 195 (annexe `docs/taches/rapport-codex-195-arbitrage.md` sur la branche `codex-pas-compagnons`, section « Lot de
placement à créer ») a révélé un défaut latent : sur sa trajectoire, le test
`tests.test_securite.AbriTests.test_inquiete_dans_le_noir_elle_rejoint_la_lumiere_et_la_compagnie` échoue. Ilse finit en
`[2,1]`, Aubin en `[1,5]`, Gorm en `[4,5]`. La croyance du lieu de Gorm est devenue nulle, mais l'intention garde
`attitude.place` proche de Gorm. `signes.place` n'efface cette attitude que dans certaines sorties ; des liens sociaux
encore présents permettent d'en sortir sans la renouveler. `pnj.agir` saute alors `_rejoindre_un_proche` dès que cette
attitude existe, même si aucun pas social valable n'a été produit. Une correction essayée en mémoire par 195 faisait
passer 21 tests mais laissait rouge une assertion sur Aubin : ce n'est pas une correction validée.

Sur l'intégration, ce test passe : le défaut est latent. Il faut le reproduire par une scène (état où l'attitude
`place` vise quelqu'un dont le lieu cru est inconnu ou démenti).

Lot de 30 à 45 minutes (`AGENTS.md`). Pas de Luna.

**Poste : le laptop** (l'utilisateur y travaille) : au plus 2 processus, priorité réduite.

**Fichiers** : `signes.place`, le raccord de `pnj.agir` qui consulte l'attitude de place, et leurs tests. **Pas** :
`ouie.py` et `echanges.tenu` (lot 233), `biens.py` (lot 232), `social.py` (lot 235), `deliberation.py` et `esprits.py`
(lot 229), `planification.py`, le MJ.

**Bruts dans `C:\Users\msics\donjon\artifacts\place-234\`.** Termine par `LOT TERMINÉ` (résumé d'une ligne) ou
`QUESTION : …`.

## L'invariant
**Une attitude de placement ne vaut que tant que sa cible est crue localisable et qu'elle produit un pas valable.** Si le
lieu cru de la cible est inconnu, démenti ou hors d'atteinte, ou si l'attitude ne produit aucun pas, elle cède : le
recours ordinaire (rejoindre un proche, s'abriter, la lumière) reprend dans la même minute. Même règle pour toute
attitude de place, quel que soit le lien ou le besoin ; aucune règle propre à Ilse, Gorm ou au Relais.

## Vérification
- Scène reproduisant le défaut sur l'intégration avant correction (échoue avec l'ancien code), puis verte : Ilse rejoint
  la lumière et la compagnie. Un autre cas de même nature (autre PNJ, autre scénario). L'assertion sur Aubin du test
  historique reste exigée ; si elle reste rouge, dis pourquoi, sans l'assouplir.
- Après rechargement : monde et rendu identiques, même laps d'un bloc ou découpé.
- Banc rapide 4 h, cinq scénarios × quatre graines, références du cache, compteur 219 : aucune hausse de suspects ni
  boucle nouvelle.
- Suite complète une fois à la fin (`tools/tests.py --processus 2`).

## Livraison
- Branche `codex-place-perimee` poussée (pas `main`). Si la poussée est bloquée par la revue, laisse le commit local
  et dis-le.
- `docs/etat-dev.md` : « Branche `codex-place-perimee`, non fusionnée ».
- Rapport d'une page `docs/taches/rapport-codex-234-place-perimee.md`.
