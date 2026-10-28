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

**Vérifications.** Première passe directement concernée : 31 tests verts
(`echanges_argent`, `garde_pret`, `contrat_engagement`). Passe finale par
fichiers, un seul travailleur réduit : en cours ; résultat attendu dans
`artifacts/restitution-246/tests.json`. Elle ajoute `lumiere` et les nouvelles
régressions. Les essais refusés par le bac à sable Windows pour l'écriture
dans les répertoires temporaires ne constituent pas des résultats du moteur.
Aucune ancienne assertion ni capture réancrée. Aucune suite complète, aucun Luna.

**Banc et limites.** Banc détaché 4 h, cinq scénarios × quatre graines,
un travailleur réduit, compteur 219 et fichier de fin écrit en dernier.
Référence exacte `2b15134` : cache absent, seules les nuits manquantes sont
calculées et rangées une fois ; aucun rejeu de `main`. Résultats en attente,
absence de hausse des suspects non encore revendiquée. Les durées de réserve
ne sont pas davantage simulées qu'auparavant : aucune garantie nouvelle
d'autonomie d'une source pendant un long trajet. Le jugement reste celui
des croyances et des besoins représentés, revalidé à chaque choix.

Bruts : `C:/Users/msics/donjon/artifacts/restitution-246/` ; fin attendue :
`banc-fin.txt`. Livraison provisoire jusqu'à lecture de ce résultat.
