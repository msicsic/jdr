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

**Banc validé : 20/20 paires de 2 h**, Relais/mine/auberge/crue/crue_hameau,
graines 1985/7/42/2024. Textes de chronique, mesures, récits, souvenirs et
empreintes physiques identiques, zéro plantage. État complet identique après
retrait des champs neutres et recalcul des empreintes qui en dérivent.

Le retrait direct retrouvait seulement 4/20 hashes ; la preuve des hashes
d'agendas et de leurs copies dans les contrats d'intention en retrouvait
12/20. Le superviseur a autorisé une exception ponctuelle : **un seul rejeu
des huit références restantes** avec capture, rangées à part dans
`diagnostic-reference/`, sans remplacer le cache. Ces huit états retrouvent
exactement les hashes du cache. Comparaison structurelle : **15 champs**,
tous expliqués, inventaire exhaustif des chemins dans `diagnostic-champs.json` :

- **12** valeurs de `esprits/<pnj>/attentes_bornees/<clé JSON>` : signature
  de `pnj_propositions._entrees_negatives`, encodée avec le booléen de service.
  Le booléen est inchangé ; seule l'empreinte incluant les relations diffère.
- **2** chaînes JSON dans `esprits/brune/refus/{4,6}/cause/0/3`, crue 2024 :
  relations sérialisées par `deliberation.moyens_crus`, avec le champ neutre
  supplémentaire et sa bande. Format de sérialisation conservé exactement.
- **1** `esprits/brune/agendas/0/croyances`, crue 2024 : hash d'agenda dont
  la projection inclut ces causes de refus sérialisées.

La preuve élargie capture les entrées exactes de `_entrees_negatives` et
`agendas._croyances`, conserve leurs résultats réels pendant la partie,
retire uniquement l'axe neutre (aussi dans le JSON imbriqué) puis recalcule
les hashes pour la comparaison. Les huit états normalisés correspondent
exactement aux captures de référence ; leur état brut et leurs données de
jeu retrouvent également la première passe de branche. **Aucun écart réel
de comportement trouvé.** Les douze autres états étaient déjà identiques.
Aucun code moteur modifié pendant ce diagnostic.

Mesures de preuve, sources et hashes par nuit : `validation-finale.json`
(**20/20**), `preuve-finale.json` (huit reprises), `*-projections-finales.json`
et `*-normalisation-finale.json`. Premières preuves d'agendas conservées dans
`comparaison-preuve-complete.json` et `*-projections-agendas.json`. Lanceurs
archivés, dont `capturer_reference_248.py` et `preuve_finale_248.py`.
Deux processus réduits au plus ; aucune suite complète ni Luna.

Bruts : `C:/Users/msics/donjon/artifacts/ascendant-248/`. **Limite : pas
identité binaire des sauvegardes** ; le schéma, ses JSON imbriqués et ses
empreintes dérivées changent. La neutralité est vérifiée sur ces vingt nuits,
sans garantie universelle supplémentaire. Statuts, jugement et épreuves
d'autorité restent aux lots suivants. Aucune fusion ; aucun calcul actif.
