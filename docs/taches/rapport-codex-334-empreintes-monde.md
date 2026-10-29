# Lot 334 — trois empreintes de monde historiques

29 octobre 2026. Branche `codex-empreintes-monde`, **non fusionnée**,
base `5f4e0d5` de l'intégration distante. Bruts :
`C:/Users/msics/donjon/artifacts/empreintes-334/`.
Lot terminé ; branche poussée vers origin, aucun calcul actif.

**Hameau : empreinte périmée par le lot 302.** Rejeu natif de l'inverse
du 200 : parent direct `37f68d4` vert, fusion `99143c2` rouge ; empreinte
`f06d24b4…` → `72a33d77…`, identique à la base du lot 334. Le lot 302
déclare le statut de Gorm (responsable du Relais, cinq salles, domaines
`amener`/`informer`, quatre connaisseurs) et les ascendants Aubin→Gorm 60,
Maël→Aubin 30, Sève→Aubin 40. Ces données légitimes sont postérieures aux
occasions du 200 : l'inverse doit les conserver. `analyse.json` prouve
exhaustivement ces quatre ajouts et l'identité avec l'état courant.
Commit de données : `d28317f` ; aucun autre champ ne diffère.

**Mine et auberge : empreintes périmées par le lot 320 / G15.** Pour les
deux captures, parent direct **`6037855` vert**, fusion **`e0be70d` rouge**,
code `6f60266`. Le monde projeté ne change que par `emissions_parole`
(14 entrées mine, 24 auberge) et `bruits[].emission` (12 liens mine,
8 auberge). En retirant ces seuls ajouts pour la preuve, on retrouve
exactement le monde du parent. Le test conserve le registre complet.
Mine : `371b536b…` → `4c214091…` ; auberge : `66e43f96…` → `3eb6aaf3…`.
Plans, visites, diagnostics, lignes et deux vues ont exactement leurs
empreintes attendues ; monde entier, rendu et scène restent comparés
après recharge par l'observateur historique. Aucun écart entre la bascule
et la base du lot. `bornes.json` et `analyse.json` conservent ces preuves.

**Changement : trois empreintes seulement.** Le hameau garde
les données du 302 ; les captures gardent leur monde complet, nouveau
registre inclus. Aucun code moteur ni projection historique ne change,
aucune assertion de plans, visites, lignes, rendus ou recharge ne disparaît.
Recouvrement avec le lot 313 non fusionné : `tests/test_etapes_chainees.py` ;
ses ajustements de visites restent indépendants et ne sont pas repris ici.

**Indépendance au hachage.** États et observations complets identiques
sous `PYTHONHASHSEED=313` et `42` sur chacun des deux parents directs
des trois bascules, sans ne comparer que leurs empreintes. Les copies
historiques et leurs journaux sont conservés. Bissection : 112,753 s,
`fin-bissection.json ok=true`. Un seul travailleur de calcul à la fois,
coordinateurs et travailleur détachés à priorité `BelowNormal` vérifiée.
Les marqueurs de fin sont écrits en dernier, même en cas d'échec.
Ni Luna, banc PNJ, empreintes de nuits ni suite complète : moteur inchangé.

**Tests ciblés : 8 tests distincts / deux fichiers, deux passes vertes.**
Sous `313` : 8/8, 41,011 s ; sous `42` : 8/8, 38,105 s.
Zéro échec, erreur ou saut. `fin-verification.json ok=true`, tous les
codes 0, 99,140 s (preuves de hachage et tests inclus).
`fin-lot.json` consigne le commit livré, les sources et la poussée.

**Limites.** Les observations portent sur les données d'auteur du hameau
et les deux captures 480–485 minutes ; elles ne constituent pas une
preuve universelle de déterminisme. Aucune correction moteur n'est
justifiée par ces écarts ; le lot 313 reste à intégrer séparément.
