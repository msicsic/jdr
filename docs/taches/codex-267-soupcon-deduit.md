# Tâche Codex 267 : le soupçon déduit (A6)

`docs/plan-agendas.md`, « Soupçon déduit » (revue externe retenue le 2026-10-24, brique des cas 5 et 10) : quand un PNJ
constate une atteinte à un bien qu'il avait vu intact plus tôt, **sans avoir vu ni entendu le geste**, il cherche dans
ses souvenirs qui il a perçu dans ce lieu entre les deux constats ; **un seul suspect** donne une épreuve de soupçon
dosée par la PSY (surveiller, refuser un prêt, interpeller), jamais une certitude ni un nom qu'il ne connaît pas.
Le lot 192 (`docs/taches/rapport-codex-192-naissance-evenement.md`) fait naître `récupérer` sur un portage illégitime
**constaté** ; la disparition attribuée sans portage vu est restée ouverte.

## L'invariant
**Une atteinte constatée (bien disparu, contenant forcé ou vidé, source éteinte d'autrui…) entre deux constats datés
du même PNJ s'attribue, d'après ses seuls souvenirs de présences perçues dans ce lieu pendant l'intervalle :** zéro
suspect, rien ; plusieurs, rien de nominatif (au plus une méfiance diffuse si le mécanisme existe déjà, sinon rien) ;
un seul, une épreuve relationnelle commune nommée (`relations.EPREUVES`, cause distincte de `vol_vu`), plus faible
qu'un témoignage et modulée par la PSY de l'observateur, révisable : démentie si l'auteur réel est appris ou si le
bien revient. Le soupçon peut alimenter la naissance existante de `récupérer` (lot 192) **seulement** comme indice,
pas comme constat de portage. Aucune lecture de position réelle ni de la chronique ; mémoire bornée respectée.

## Vérification
- Deux scènes rechargées : Gorm voit sa réserve fermée et pleine, s'absente, une seule personne passe (Brune) puis la
  réserve est vidée ; au retour, soupçon envers Brune seule, lisible dans la relation et le récit ; autre cas (mine ou
  auberge, autre bien). Contre-épreuves : deux passants (pas de nom), aucun passant perçu, auteur vu (le chemin existant
  `vol_vu` reste seul), bien rendu (soupçon levé). Monde, rendu et scène identiques après recharge et laps découpé.
- Tests ciblés des fichiers concernés (`test_naissance*`, `test_relations*`, `test_reclamer*`, `test_constater*`) ;
  **pas de suite complète**.
- Banc rapide 4 h, cinq scénarios × quatre graines, référence en cache : soupçons nés par nuit, aucune hausse des
  suspects 219, aucun plantage ni usurpation. Calcul long détaché.

Lot de 30 à 45 minutes. **Poste : le PC fixe**, au plus deux processus à priorité réduite. Pas de Luna.
Fichiers attendus : `donjon/esprits.py` (constat d'atteinte et intervalle), `donjon/relations.py` (épreuve), et le
raccord de naissance d'A6 si nécessaire ; ne touche pas `agendas.py`, `echanges.py` ni `deliberation.choisir`.

## Livraison
- Branche `codex-soupcon-deduit` poussée (sinon commit local, et dis-le). Rapport d'une page
  `docs/taches/rapport-codex-267-soupcon-deduit.md` ; entrée « non fusionnée » dans `docs/etat-dev.md`. Bruts dans
  `C:\Users\msics\donjon\artifacts\soupcon-267\`. Termine par `LOT TERMINÉ` (résumé d'une ligne),
  `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
