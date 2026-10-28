# Lot 253 — trois échecs de la suite bf99943

Branche `codex-suite-bf99943`, **non fusionnée**, départ `39db079`.

**Attribution.** Rejeux ciblés sur les sources exactes, avec sauvegardes :
Lucien est vert sur le parent `d532a87`, rouge sur la fusion **246 / f46a0b5**.
Les captures mine et auberge sont vertes sur le parent `1194876`, rouges
sur la fusion **248 / bf99943**. Journaux et états dans
`C:/Users/msics/donjon/artifacts/suite-253/` ; aucune suite complète relancée.

**Invariant corrigé.** Une restitution conserve les moyens du transport
jusqu'à la remise, mais ne doit pas retirer un moyen encore employé par
le plan actif ou le séjour qu'il tient. Dans le cas réel, Lucien empruntait
le bougeoir puis le rendait immédiatement dans la cuisine éclairée :
`necessaire(apres=...)` ignorait le retour déjà prévu au grenier sombre.
Le premier raccord du plan seul différait seulement la faute : arrivé au
grenier, le plan vide tient toujours la garde, mais la restitution le
transportait de nouveau vers Mireille. Ces deux moments sont capturés.

`echanges.necessaire` protège de nouveau les emplois explicites du plan
actif. `deliberation.lumiere_utile` accepte la même projection après remise :
elle juge les moyens conservés à destination, sur les étapes restantes et
sur le séjour courant quand le plan est vide. Le plan de restitution
lui-même ne constitue pas un emploi futur. `_rendre`, les scénarios, le MJ,
`social.py` et `agendas.py` restent inchangés. Aucun cas d'acteur ou de lieu
dans le moteur ; l'ancien oracle de garde de Lucien reste exigé.

**Preuves.** Lucien doit encore finir au grenier éclairé, bougeoir porté et
allumé, sans restitution. La sonde compte les six passages réels, même
entre deux relevés de cinq minutes. Le rendu du joueur au grenier montre
le bougeoir ; état, rendu et scène sont comparés après recharge.
Autre usage (contre-épreuve rouge sur `bf99943` inchangé) : Rémy conserve la lampe de Gaspard pour une visite de galerie
depuis le baraquement éclairé ; la visite est exécutée en bloc/découpé,
avec rechargements et rendus. Avec sa propre lampe en remplacement, il
restitue réellement celle de Gaspard. Les contrôles 246 de Maël, du trajet
sombre et de l'arrivée sans remplacement restent requis.

**Empreintes 248.** Comparaison exhaustive des deux projections avant/après :
retrait de l'axe zéro, de sa bande fausse et de son ancre zéro, y compris
les relations JSON de deux refus, en conservant leur format exact.
Égalité structurelle retrouvée et hashes historiques inchangés : mine
`371b536b…a42ee`, auberge `66e43f96…d2d7` (`preuve-normalisation.json`).
Le test applique cette projection, refuse un ascendant actif et conserve
tous les autres oracles : plans, visites, lignes et vues après recharge.
Aucun hash attendu remplacé, aucun moteur changé pour les empreintes.

**Validation et limites.** **62 tests verts en 191,559 s**, sept fichiers :
`dynamique_besoins`, `etapes_chainees`, `restitution_route`, `echanges_argent`,
`garde_pret`, `contrat_engagement`, `lumiere`. `git diff --check` vert.
Banc rapide détaché : 4 h, cinq scénarios × quatre graines, référence exacte
`bf99943`, cache consulté avant toute nuit manquante (aucun dossier pour ce
commit au départ), deux processus réduits au plus. Les références manquantes
sont calculées et rangées une fois par le comparateur commun.
Sentinelle attendue : `C:/Users/msics/donjon/artifacts/suite-253/banc-fin.json`, écrite en dernier.
La validation des suspects reste en attente du banc. Aucune suite complète
ni Luna. Le jugement reste fondé sur les croyances et les emplois représentés ;
ce lot n'ajoute ni simulation de consommation sur un long trajet ni preuve
universelle sur tous les plans possibles.
