# Tâche Codex 306 (A5) : la crue du hameau déclare l'agenda d'évacuation de Gorm, comme la crue

Suite du lot 302, fusionné. Lis son rapport `docs/taches/rapport-codex-302-a5-donnees-hameau.md` (section « Limites
établies »), puis les rapports A5 déjà cités dans le brief 302.

## Le constat
Le hameau (`donjon/scenario_crue_hameau.json`) déclare désormais le statut de Gorm et des ascendants, mais aucun agenda
`amener` ni `informer`. Sans charge à déléguer, l'autorité ne sert à rien : sur quatre nuits, zéro mandat. La crue
(`donjon/scenario_crue.json`) déclare pourtant un agenda `evacuer_crue` de Gorm (`amener` Ilse et Brune à la galerie).
Le dérivé du hameau l'a perdu à sa création (lot 139, antérieur aux agendas).

## L'invariant
**Le hameau déclare à Gorm la même responsabilité d'évacuation que la crue, étendue aux personnes que le scénario met
sous sa garde, en données. Toute délégation qui en naît passe par les mécaniques communes :**

- le choix entre faire et confier, d'après le devis vu par le mandant (lots 258 et 260) ;
- le jugement du mandat selon l'autorité perçue (lot 256) ;
- le compte rendu (lot 283) et la réaffectation (lot 297).

Aucune attribution forcée, ni mandat initial, ni changement de coût ou de moteur.

Justifie qui figure dans l'agenda d'après les profils et les liens : Ilse et Brune comme dans la crue ; Maël et Sève,
s'ils sont plausiblement sous la garde du passeur. Garde la même destination que la crue. Une éventuelle seconde charge
(`informer`) doit avoir une raison dans les données ; sinon, n'en ajoute pas. N'ajuste pas les données après mesure
pour obtenir un mandat.

## Fichiers attendus
`donjon/scenario_crue_hameau.json`, tests et scènes. **Aucun fichier du moteur**, ni du MJ.

## Vérification
- Agenda chargé, activé et sauvegardé ; monde et rendu après recharge.
- Crue d'origine inchangée : empreintes 2 h, 4 graines.
- **Banc rapide** : hameau 4 h × quatre graines contre la référence de l'intégration (cache). Compte :
  - les mandats (proposés, acceptés, refusés par cause, comptes rendus, réaffectations) ;
  - les évacuations atteintes ;
  - les suspects 219 par nuit ;
  - les boucles et les usurpations.

  Si aucun mandat ne naît, dis quel devis ou quel jugement l'empêche, chiffres à l'appui, sur une capture rechargée.
- Calcul détaché, fichier de fin écrit même en cas d'échec. Pas de Luna ni de suite complète.

## Contraintes
**Poste : le PC fixe.** D'autres lots y tournent : deux processus au plus, priorité réduite.

## Livraison
- Branche `codex-a5-agenda-hameau`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur :
  la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-306-a5-agenda-hameau.md`.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\agenda-hameau-306\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
