# Lot 248 — ascendant neutre (A5, lot 1)

Branche `codex-ascendant-neutre`, **non fusionnée**, base `f46a0b5`,
28 octobre 2026. Cette référence remplace `1006204` sur instruction du superviseur.

L'invariant visé est un sixième axe orienté, accessible par `relations.py`,
sans effet sur les décisions. `AXES`, `ETRANGER`, `_nouvelle`, `envers`,
`axes` et `autorite_reconnue` exposent l'ascendant (entier 0–100, neutre à zéro).
Les liens déclarés dans un profil peuvent le fixer ; aucun scénario ni aucune
épreuve n'est modifié. La bande reprend l'hystérésis 60/50 de la confiance ;
l'estompement reprend le retour de l'affection vers le lien initial à 1 point/h.
Une valeur initiale déclarée reste stable. Aucun bonus ni lecteur de décision.

`_completer` fournit une vue pure des relations historiques : valeur zéro,
bande fausse et ancre neutre, sans migration. La validation accepte l'ancien
contrat complet ou le nouveau, rejette les contrats partiels et accepte les
anciennes chroniques. `signature` inclut axe, bande et ancre ; la clé de lecture
inclut le lien initial. `_entrees` énumère déjà `relations.AXES`, sans changement
de `planification.py`. Les signatures des signes restent limitées aux seuils
qu'ils lisent. Aucun fichier moteur hors `relations.py` modifié.

**Tests : 81 distincts verts, six fichiers.** Première passe : 44 en 11,856 s ;
seconde : 50 en 13,809 s (recouvrement compris), relations/voix/signes. Six
nouveaux tests couvrent deux couples orientés (70 contre 20), profil déclaré,
pureté, monde/rendu après recharge, ancien format sans migration puis action
visible identique, estompement en bloc/découpé, hystérésis, signatures/cache et
validation. Contrôle AST renforcé : aucun accès direct à l'axe hors façade.
`git diff --check` vert. Reprises autorisées hors sandbox après des refus
d'écriture des temporaires Windows. Aucune suite complète ni Luna.

**Banc terminé, non validé.** Vingt paires de 2 h, Relais/mine/auberge/crue/
crue_hameau, graines 1985/7/42/2024 : **20/20 chroniques, mesures, récits,
souvenirs et empreintes physiques identiques**, zéro plantage. Les vingt
références manquantes ont été calculées une fois et rangées ; aucune rejouée.

Le retrait direct du champ neutre retrouve seulement 4/20 hashes d'état :
les agendas stockent une empreinte de croyances incluant les relations,
également copiée dans certains contrats d'intention. Deux reprises de la seule
branche capturent les entrées exactes de ces hashes sans changer leur résultat
pendant le jeu ; les vingt références sont relues du cache. La preuve finale
reproduit **20/20 états bruts initiaux**, retire 1 563 champs neutres et recalcule
21 occurrences de hashes dérivés sur leurs projections sans le champ nouveau.
Projections, chemins et valeurs sont archivés ; aucun hash n'est ignoré.

Résultat : **12/20 états complets identiques ; huit écarts non expliqués** :
mine 7/2024, crue quatre graines, crue_hameau 1985/2024. **La neutralité de
l'état complet n'est pas garantie.** Aucun nouveau code ni élargissement de la
normalisation sans cause identifiée. Le cache ne contient que le hash final :
localiser les écarts demanderait l'autorisation de rejouer ces huit références
avec capture d'état, exception à « pas de référence relancée » (`AGENTS.md`).
Deux processus réduits au plus ; environ 223 s cumulées de nuits par reprise.

Bruts : `C:/Users/msics/donjon/artifacts/ascendant-248/` ; verdict final
`fin-preuve-complete.json`, bilan `comparaison-preuve-complete.json`, lanceur
`banc_ascendant_248_preuve_complete.py`, preuves `*-projections-agendas.json`,
`*-retraits.json`, états `*-etat.json`, résultats `*-brut-instrumente.json`.
La sauvegarde brute diffère par le champ ajouté et les hashes qui en dérivent ;
aucune égalité binaire revendiquée. Statuts, jugement et épreuves d'autorité
restent aux lots suivants. Aucune fusion ; aucun calcul encore actif.
