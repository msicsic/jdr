# Lot 246 — restitution et transport

Branche `codex-restitution-route`, non fusionnée ; base `2b15134`.

**Invariant.** Le bien reste dans les moyens de la recherche jusqu'à la
destination de restitution. `_rendre` reprend la recherche commune d'`aller`
et son état terminal (portes, acquisitions et allumages compris), puis retire
le bien pour juger la remise avec `echanges.necessaire(apres=...)`.
Admission et revalidation passent par ce même chemin. Le plan remplacé ne
constitue plus un besoin après remise ; la lumière et les moyens conservés
sont lus dans l'état projeté. Une autre clé portée peut maintenir un accès
nécessaire. Une destination encore inconnue autorise seulement la recherche
du destinataire, sans remise publiée. Aucun acteur, lieu ou bien particulier
dans le moteur ; contrat de cession compensée 228 inchangé.

**Preuves.** Rejeu séquentiel de `4306c14`, hameau 42, départ tiré,
joueur `chambre_cloche`, jusqu'à 421. Capture brute conservée, nouvelle
fixture compressée sans modification de l'état historique : Maël dans la
crypte, torche encore portée et ancien contrôle `necessaire=True`.
Le code exact de `_rendre` de `2b15134` rejette cette capture et la scène
de Rémy à la mine ; la branche admet les deux (contre-épreuve archivée).
Le test historique confirme l'adoption, la revalidation après recharge,
la restitution effective et la clôture du prêt. Autre bien : lampe de
Gaspard utilisée depuis la galerie sombre vers le baraquement éclairé.
Contre-épreuves : arrivée sombre sans autre source (refus), puis avec
une autre lampe portée (restitution). Monde, rendu, scène et laps de cinq
minutes en bloc/découpés avec rechargements sont contrôlés.

**Vérifications.** **47 tests verts / cinq fichiers, 452,688 s** :
`echanges_argent`, `garde_pret`, `contrat_engagement`, `lumiere` et les
trois nouvelles régressions ; zéro échec, erreur ou saut. La capture réelle
et les contre-épreuves exécutées après le dernier raccord sont vertes.
Les trois premiers fichiers repris sur le code final sont **31/31 verts,
63,743 s** ; les 47 tests distincts sont donc validés sur ce code.
Les essais refusés par le bac à sable Windows pour l'écriture
temporaire ne constituent pas des résultats du moteur. Aucune ancienne
assertion ni capture réancrée. Aucune suite complète, aucun Luna.

**Banc et limites.** Banc détaché 4 h, cinq scénarios × quatre graines,
un travailleur réduit, compteur 219 et fichier de fin écrit en dernier.
Référence exacte `2b15134` : cache absent, vingt nuits manquantes calculées
et rangées une fois ; aucun rejeu de `main`. Branche finale **`efbc2e6`**,
worktree propre au relevé. **20/20 paires identiques** : état final complet,
chroniques, récits, souvenirs, empreintes, mesures et audits. Zéro plantage
ou usurpation. Suspects 219 **4 → 4**, aucune hausse par nuit : Relais/mine/
auberge/crue/hameau **1/0/1/2/0**. Cycles **498 → 498**, préemptions
**46 → 46**, à expliquer **51 → 51**, dérives ouvertes **216 → 216**.
Les durées de réserve ne sont pas davantage simulées qu'auparavant : aucune garantie nouvelle
d'autonomie d'une source pendant un long trajet. Le jugement reste celui
des croyances et des besoins représentés, revalidé à chaque choix.

Bruts : `C:/Users/msics/donjon/artifacts/restitution-246/`.
