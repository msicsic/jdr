# Lot 325 — U-C, consentement du texte libre

29 octobre 2026. Branche `codex-uc-consentement`, **non fusionnée**, base
initiale `origin/codex-up-recapitulatif`, commit `865aff3`.
Reprise : intégration `9f261f9` fusionnée sans rebase après fusion d'U-P ;
seul conflit documentaire, deux côtés conservés. Fabrication terminal
conservée, tests U-C portés sur le registre G15 sans changer leurs oracles.

`donjon/consentement.py` prépare sur copie les transactions, admissions et
plans entiers. La gravité porte sur les effets typés de toutes les branches
et sous-plans, paroles et accords compris. Un nouvel effet est lourd par
défaut ; une étape lourde retient toute la composition.

`jeu.py` montre la fiche U-P avant effet lourd. Annuler ne publie aucune
conséquence. Tenter revalide sans modèle : état, plan ou rapport changé,
même sans nouvelle révision, impose un nouvel aperçu ; un plan impossible
reste indisponible. Une narration périmée cède aux faits publics recalculés.
Résultats et paroles sont sauvegardés avant affichage. Actes légers et
gestes directs gardent leur politique.

## Vérification

MJ simulé, console/web/vraie TUI : paiement, offre réelle G1/U-P, avis,
enfermement de Rémy, fermeture/verrouillage et offre/dépôt léger. Aperçu,
annulation et confirmation contrôlent monde entier, paroles, ressources,
sauvegarde et rendu après recharge. Prix changé et cible partie sans nouvelle
révision ; acte léger et consommation par clic/menu. Oracles U-P inchangés.

**Après fusion : 94/94 tests verts, sept fichiers, 782,847 s**, zéro échec,
erreur ou saut : consentement 9, compréhension 5, TUI 28, fabrication terminal
10, narration 31, transactions 2 et web 9. Tous rejoués, aucun résultat conservé
pour ce bilan. Les **18 parcours lourds** et le rejet d'une ancienne réplique
restent verts avec G15 ; code/tests inchangés depuis cette validation.

Avant fusion, une passe de 83 tests avait révélé une classification trop
large, corrigée puis vérifiée par 37 tests. Demander les termes d'une
récompense reste léger ; accepter et faire une offre engagée restent lourds.
Quatre parcours Gorm/second donneur × console/web vérifient cette distinction,
ressources, monde et rendu rechargés. Aucun oracle existant affaibli.

Mesures après fusion, six cas par interface, secondes min–max :

| Interface | Saisie → aperçu | Confirmation → effet |
|---|---:|---:|
| Console | 0,025–2,412 | 0,014–6,916 |
| Web | 0,028–2,926 | 0,024–4,983 |
| TUI | 0,531–6,433 | 2,134–8,070 |

Temps humain simulé séparé : zéro. **Zéro appel au modèle après confirmation**
sur les 18 parcours. Ces mesures incluent l'interface, pas la latence de
Luna réelle. Bruts dans `C:/Users/msics/donjon/artifacts/uc-325/` :
`fusion-ciblee.json`, `mesures-fusion.jsonl`, `fin-tests-fusion.json` et
`fin-fusion.json`. Les passes antérieures, dont `fin.json` avec `ok=false`,
restent archivées.

## Limites et intégration

La revalidation est conservatrice : tout changement d'état hors historique
d'affichage peut redemander un aperçu, même sans conséquence sur l'acte.
Une fiche relue après recharge ne réactive pas le consentement. La fidélité
au français reste imparfaite. Aucune revue retirée ni consigne Luna modifiée.
Pas de Luna, banc ou suite complète ; un travailleur à priorité réduite.
Recouvrement **321/323 : `jeu.py`** ; aucun changement U-C de la TUI, du
rendu ou du pont web ; leurs apports d'intégration sont conservés.
Reprise terminée, branche poussée, aucun calcul actif ; `fin-fusion.json` vert.
G5 `49608db`, arrivé ensuite dans l'intégration partagée, n'est pas inclus
dans cette fusion de `9f261f9`.
