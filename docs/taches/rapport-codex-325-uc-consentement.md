# Lot 325 — U-C, consentement du texte libre

29 octobre 2026. Branche `codex-uc-consentement`, **non fusionnée**, base
initiale `origin/codex-up-recapitulatif`, commit `865aff3`.
Intégrations `9f261f9`, `ad0e5a8`, puis `60c476a` (G6/G17), sans rebase.
Documents conservés des deux côtés ; conflit `jeu.py` résolu au 30 octobre :
perceptions immédiates, consentement lourd et comptes parlés coexistent.

`donjon/consentement.py` prépare sur copie les transactions, admissions et
plans entiers. La gravité porte sur les effets typés de toutes les branches
et sous-plans, paroles et accords compris. Un nouvel effet est lourd par
défaut ; une étape lourde retient toute la composition.

G6 répond immédiatement selon `PERCEPTIONS` ; les autres questions de
faisabilité gardent leur fiche. G17 publie les comptes du registre réellement
admis, aussi avant le résultat d'un plan composé. Après revalidation, mots
et sceaux sont recalculés ; les autorisations non formulées ne deviennent
pas des paroles entendues et une réplique libre périmée est écartée.

`jeu.py` montre la fiche U-P avant effet lourd. Annuler n'exécute rien.
Tenter revalide sans modèle : changement, même sans nouvelle révision,
impose un nouvel aperçu ; un plan impossible reste indisponible. Résultats,
paroles et faits recalculés sont sauvegardés avant affichage. Actes légers
et gestes directs gardent leur politique.

## Vérification

MJ simulé, console/web/vraie TUI : paiement, offre réelle G1/U-P, avis,
enfermement de Rémy, fermeture/verrouillage et offre/dépôt léger. Aperçu,
annulation et confirmation contrôlent monde entier, paroles, ressources,
sauvegarde et rendu après recharge. Prix changé et cible partie sans nouvelle
révision ; acte léger et consommation par clic/menu. Oracles U-P inchangés.

**Fusion précédente (`ad0e5a8`) : 110 tests distincts validés** : 101
résultats verts conservés, neuf tests web rejoués verts en **13,296 s**.
La passe initiale (**881,138 s**) comptait 109 verts et une erreur TCP
`WinError 10053` dans le contrôle HTTP 403 d'un hôte externe. Le fichier web
repasse inchangé ; cause exacte de l'interruption non établie. Aucun échec
d'assertion ni saut. Les 9 tests U-C, 28 TUI, 9 perceptions et 7 questions sur
absents passent. Les **18 parcours lourds**, les paroles et les recharges
restent verts avec G15/G5 ; code/tests inchangés depuis validation.

**Reprise G6/G17 en cours** : deux précontrôles / quatre parcours verts
(35,023 s), onze tests des comptes parlés verts (96,683 s). Les tests
comptables confirment explicitement par `tenter`, sans changer leurs oracles
de mots, ressources ou recharge ; U-P conserve ses nouveaux oracles G6.
La revalidation couvre un décalage réel des identifiants d'émission et
conserve toute l'action composée. Campagne ciblée des chemins de `jeu.py`
préparée sous `fusion-60c476a/`, sans suite complète ni Luna.

Demander les termes reste léger ; accepter et offrir restent lourds.
Quatre parcours Gorm/second donneur × console/web le vérifient. Aucun oracle
affaibli. Première fusion : 94/94 verts, archivés séparément.

Mesures de la dernière fusion, six cas par interface, secondes min–max :

| Interface | Saisie → aperçu | Confirmation → effet |
|---|---:|---:|
| Console | 0,024–5,185 | 0,019–10,540 |
| Web | 0,032–3,167 | 0,032–4,732 |
| TUI | 0,343–3,971 | 2,356–7,451 |

Temps humain simulé séparé : zéro. **Zéro appel après les 18 confirmations**.
Mesures avec interface, sans latence Luna réelle. Bruts dans
`C:/Users/msics/donjon/artifacts/uc-325/fusion-ad0e5a8/` :
`tests.json`, `reprise-web.json`, `mesures.jsonl`, `analyse-cloture.json` et
`fin-cloture.json`. `fin.json` initial avec `ok=false` conservé ; autres
passes archivées dans le dossier parent.

## Limites et intégration

Tout changement d'état hors historique peut redemander un aperçu, même
sans conséquence sur l'acte. Une fiche relue ne réactive pas le consentement.
Fidélité au français imparfaite ; aucune revue retirée ni consigne modifiée
par U-C. Pas de Luna, banc ou suite complète ; un travailleur réduit.
Recouvrement **321/323 : `jeu.py`**, apports d'intégration conservés.
Reprise précédente poussée ; `fusion-ad0e5a8/fin-cloture.json` vert.
Nouvelle reprise non poussée avant validation, résultat `fusion-60c476a/fin.json`.
