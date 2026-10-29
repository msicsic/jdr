# Lot 325 — U-C, consentement du texte libre

29 octobre 2026. Branche `codex-uc-consentement`, **non fusionnée**, base
`origin/codex-up-recapitulatif`, commit `865aff3`. Aucune fusion d'integration.

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

**Passe groupée : 83 tests, 82 verts, un échec, 557,117 s**, sans erreur ni
saut. Les huit tests U-C passent, dont les **18 parcours lourds** et le rejet
d'une ancienne réplique. L'échec TUI révèle une classification trop large :
`conversation_pnj.proposer` demande les termes d'une récompense, sans
engagement de Corvus. Il reste léger ; l'acceptation et les offres engagées
restent lourdes. Quatre nouveaux parcours Gorm/second donneur × console/web
vérifient l'offre à accepter, les ressources, le monde et le rendu rechargés.
**Reprise verte : 37/37 tests, 468,682 s**, dont les 9 tests U-C et les
28 TUI inchangés, sans échec, erreur ni saut. Les 47 autres tests verts,
sans transaction du type corrigé, sont conservés : **84 tests distincts
couverts**. Aucun oracle existant affaibli ; passes imparfaites archivées.

Mesures de clôture, six cas par interface, secondes min–max :

| Interface | Saisie → aperçu | Confirmation → effet |
|---|---:|---:|
| Console | 0,023–1,951 | 0,018–4,539 |
| Web | 0,036–3,503 | 0,033–3,097 |
| TUI | 0,280–5,913 | 2,522–6,938 |

Temps humain simulé séparé : zéro. **Zéro appel au modèle après confirmation**
sur les 18 parcours. Ces mesures incluent l'interface, pas la latence de
Luna réelle. Bruts dans `C:/Users/msics/donjon/artifacts/uc-325/` :
`tests-finaux.json`, `mesures-cloture.jsonl`, `cloture-37.json` et
`fin-cloture.json`. `fin.json` initial reste conservé avec `ok=false`.

## Limites et intégration

La revalidation est conservatrice : tout changement d'état hors historique
d'affichage peut redemander un aperçu, même sans conséquence sur l'acte.
Une fiche relue après recharge ne réactive pas le consentement. La fidélité
au français reste imparfaite. Aucune revue retirée ni consigne Luna modifiée.
Pas de Luna, banc ou suite complète ; un travailleur à priorité réduite.
Recouvrement **321/323 : `jeu.py`** ; TUI, rendu et pont web inchangés.
Lot terminé, branche poussée, aucun calcul actif ; `fin-cloture.json` vert.
