# Lot 323 — G5, perception canonique

Lot clos le 2026-10-29 après relecture ; branche `codex-g5-perception`,
**non fusionnée**, base `integration 4794376`. Correctif de relecture `d683184`.

**Invariant livré.** Une perception typée est rendue par le moteur et sauvegardée
avant affichage. Vue, non-perception, absence dans la surface couverte et souvenir
restent distincts. `rendu.non_perception` lit `non_vus_connus`, `couverture_vue`
et la mémoire existante, sans position cachée ni registre parallèle. Les refus
et attestations réutilisent ce rendu. Une présence non perçue n'est pas une
absence ; un souvenir n'est pas une position actuelle. `Plan.perception_canonique`
retire la contre-revue des seules perceptions sans effet proposé autre que
connaître ce qui est perçu. Compositions et autres actes gardent leurs revues.
La commande `regarder` enregistre aussi son texte avant affichage.

**Régression corrigée.** Le changement initial de `consignes.py` avait retiré
l'orientation des questions d'information vers `dialogue`. La première passe G5
avait transformé les deux questions de `signes-guet` en paroles : neuf appels,
un repli et une demande de destinataire. La clause antérieure « une question
d'information reste un dialogue » et celle du détail distant sont rétablies,
sans exception de formulation, d'objet ou de scénario. Les perceptions proposées
comme actions gardent leur rendu moteur ; aucun audit de dialogue n'est retiré.

**Tests de correction : 67 tests, six fichiers, tous verts**, sans erreur ni saut,
52,673 s cumulées, deux travailleurs réduits au plus. Les quatre questions
réelles sur les absents, dont les deux régressions, contrôlent les paroles de
Corvus, celles des PNJ, leurs esprits et l'état complet après recharge ; texte,
scène et carte identiques. Perceptions noires sans modèle, paroles explicites,
vocatifs, questions à la cantonade intentionnelles, écoute, fouille et admission
restent couverts. Les 117 tests initiaux sont archivés séparément.

**Luna de relecture : une passe achevée**, `gpt-6-luna`, 115,391 s, code 0,
17 tours hors « quitter », 36 appels, zéro erreur technique/recharge, zéro repli.
Deux processus `BelowNormal` vérifiés au lancement, aucun calcul actif.

| Script | Appels c9459ce, passes 1 / 2 | Correction | Résultat |
| --- | ---: | ---: | --- |
| signes-guet | 6 / 4 | 4 | Deux dialogues au MJ, sans parole de Corvus ni demande de destinataire. |
| noms-dialogue | 13 / 17 | 19 | Même routage que les deux références. |
| echanges | 15 / 11 | 13 | Même routage que les deux références. |

Pour **les 17 tours**, la présence ou l'absence d'une parole de Corvus publiée
correspond aux deux références. Dans `signes-guet`, chaque question produit
exactement une interprétation `dialogue` et un audit ; l'état observé du banc
est identique aux deux références. La demande de bois de `noms-dialogue`, le
salut interrogatif et les mots cités d'`echanges` **étaient déjà des paroles**
dans les références : aucune conversion nouvelle de question au MJ en parole.
La seule correction de typage refusée concerne « le gardien », inconnu, puis
reproposé comme propos. Trois mentions signalées dans `echanges` sont les noms
saisis repris par les refus locaux (Brune, Aubin, Ilse), sans identité apprise.
Deux révisions de réponse de Brune et une revue d'ambiance expliquent notamment
le surcroît d'appels de `noms-dialogue` ; aucun gain global revendiqué.

Les douze archives des six scripts concernés de `c9459ce` ont été lues sans
relance. Aucun temps comparé entre campagnes de charges différentes. Les trois
autres scripts G5 ne sont pas rejoués avec Luna, conformément à la relecture ;
leurs voies sont couvertes avec MJ simulé. Bruts, provenance, empreintes et
`analyse-relecture.json` : `C:/Users/msics/donjon/artifacts/g5-323/relecture/` ;
`fin-luna-passe.json ok=true`. Code/tests inchangés depuis les 67 tests verts.

**Limites.** Une passe ne garantit pas le routage de tout texte libre. G5 global
reste partiel : dialogues d'information toujours audités, G6 à porter ; détails
inconnus et ambiance gardent leurs contrôles. Ni suite complète ni banc PNJ.
Recouvrements à l'intégration : `narration.py` avec 320 ; `rendu.py` et `jeu.py`
avec 319. Branche poussée vers origin, sans fusion.
