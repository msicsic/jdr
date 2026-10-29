# Lot 315 — réclamations et contact du débiteur

Branche `codex-reclamations-repetees`, base intégration **c4f6d46**.
**Reprise de vérification détachée ; lot non déclaré terminé.**

**Cause établie.** Les sept retours de Sève en 2024 ne suivent aucun
refus de remboursement. La capture 306 t=22057, rejouée sur le moteur de
base jusqu’à la minute 82, porte deux dettes (Gorm 2 pièces, Brune 1),
aucun souvenir `dette_niee`/`creance_vaine`. Le plan `reclamer` ne contient
que `aller` : arrivé dans la salle sans avoir établi la parole, le PNJ
écarte ce débiteur et repart vers l’autre. Les deux recours se relancent.
La mémoire des réponses aux dettes était en outre bornée et temporisée.

**Contrat corrigé.** `planification.reclamer` termine le trajet par une
demande typée, exécutée par `echanges.executer` avec le contact et la parole
communs. Entrer dans une salle n’est plus une restitution accomplie.
`biens.regler` enregistre la réponse dans les refus durables ;
`deliberation.retenir_refus/tient/moyens_crus` et
`biens.reponse_creance_retenue/entrees_creance` servent au choix, au
règlement automatique et aux anciens plans. Aucun délai : changement
d’obligation ou fonds positivement appris ; ni nouvelle position, ni date,
ni diminution des fonds connus, ni bourse privée. Le débiteur conserve le
règlement spontané. Aucune donnée de scénario ni consigne MJ modifiée.

**Preuves déjà obtenues.** Cinq nouveaux tests verts (9,683 s), dont la
capture réelle avant 83 : les deux dettes sont rendues aux minutes **83 et
84**, quatre déplacements de Sève dans le rejeu de seize minutes. État
complet et textes identiques pour un laps entier et seize tranches ; monde,
rendu et scène identiques après sauvegarde/recharge. Refus réels dans le
Relais et l’auberge : réponse conservée après deux fois REDEMANDE et
éviction des souvenirs, ancien plan neutralisé, bourse cachée sans effet,
nouvelle obligation/fonds appris admis, règlement spontané conservé.

**Premier calcul, 890,531 s.** Neuf fichiers : **124/126 tests verts**.
Deux régressions corrigées sans changer les tests existants : `retenir_refus`
créait un second souvenir social après `dette_niee` ; la nouvelle demande
déclarait absent un débiteur passé dans une autre salle mais encore audible.
Mémoire de décision sans événement social supplémentaire (`souvenir=False`)
et même portée de parole que `solder`. Les deux tests existants repassent ;
un sixième test vérifie la parole par le passage et la recharge du témoin.

**Hameau validé sur b05bb80**, données 306 inchangées, worktree retiré :
quatre nuits de 4 h, zéro plantage/usurpation ; suspects **0/0/0/7 → 0/0/0/0**,
à expliquer **7/5/0/10 → 2/5/0/4**. Aucun refus de créance dans ces nuits.
Monde/rendu/scène rechargés identiques pour chaque graine. Résultats conservés,
sans rejouer ce banc réussi ; aucune absence universelle de boucle déduite.

**Empreintes : 13/16 paires 2 h identiques.** Relais 7, auberge 1985 et
crue 1985 diffèrent : premières réclamations nouvelles aux minutes 2, 62,
3, contre 3, 63, 8 sur la base. Le nouveau geste rend possible une demande
avant le règlement automatique à la minute ronde : identité stricte non
atteinte. La sortie d’échec est conservée, aucun oracle modifié. Le détail
des trois nuits corrigées reste à relire avant qualification finale.

**Reprise lancée :** uniquement les deux fichiers en échec et le fichier
de régression (42 tests attendus), puis les trois nuits divergentes.
Références déjà calculées réutilisées, treize autres paires et hameau non
rejoués. Deux travailleurs réduits, aucune suite complète ni Luna.
`C:/Users/msics/donjon/artifacts/reclamations-315/fin.json` (échec initial)
et `fin-reprise.json` (dernier fichier du nouveau calcul).

**Limites et intégration.** Le cas réel est un contact jamais accompli,
pas un refus : aucune fausse cause de refus n’est créée pour le masquer.
Les anciennes sauvegardes sans refus durable peuvent refaire une demande
avant de retenir sa réponse ; pas de migration inventant les moyens jadis
connus. Les prêts et les autres demandes gardent leurs contrôles existants.
Pas de preuve universelle d’absence de boucle. Recouvrement avec 314 :
`echanges.py`, fonctions distinctes (`executer` ici, `_remettre_part` pour
314 au relevé de travail) ; aucune reprise du correctif d’achat promis.
