# Lot 323 — G5, perception canonique

Branche `codex-g5-perception`, **non fusionnée**, base `integration 4794376`.
Relecture avant fusion : correction de la régression question au MJ → parole,
**passe Luna de correction en cours**.

**Invariant.** Une perception typée est rendue par le moteur et sauvegardée avant
l'affichage. Vue, non-perception, absence dans la surface couverte et souvenir
restent distincts. `rendu.non_perception` lit `non_vus_connus`, `couverture_vue`
et la mémoire existante, sans position cachée ni registre parallèle. Les refus
et attestations réutilisent ce rendu. Une présence non perçue n'est pas une
absence ; un souvenir n'est pas une position actuelle. `Plan.perception_canonique`
retire la contre-revue des seules perceptions sans effet proposé autre que
connaître ce qui est perçu. Compositions et autres actes gardent leurs revues.
La commande `regarder` enregistre aussi son texte avant affichage.

**Correction de relecture.** Le changement initial de `consignes.py` avait retiré
l'orientation explicite des questions d'information vers `dialogue`, et étendu
les actions de perception à ces questions. Dans la première passe G5, les deux
questions de `signes-guet` étaient devenues des paroles : Brune, neuf appels avec
un repli ; Gorm, une demande de destinataire. C'est une **régression**, pas une
limite acceptable à fusionner. Les deux passes historiques `c9459ce` disponibles
sur le PC fixe répondent à ces deux questions sans parole de Corvus.

La clause existante « une question d'information reste un dialogue » et celle
du détail distant sont rétablies, sans ajouter de formulation particulière,
de nom ou de scénario au routage. Le moteur continue de rendre les perceptions
que l'interprétation propose comme actions ; aucun contrôle de dialogue libre
n'est retiré. Le changement de correction ne touche que `consignes.py` et les
tests : aucun changement des décisions PNJ ou du rendu G5.

**Vérification de correction : 67 tests, six fichiers, tous verts**, sans erreur
ni saut, 52,673 s cumulées, deux travailleurs réduits au plus. Les quatre
questions réelles sur les absents, dont les deux régressions, contrôlent les
paroles de Corvus, celles des PNJ, leurs esprits et l'état complet après
recharge ; texte, scène et carte identiques. Les tests d'observation noire
portent désormais le constat G5 sans modèle. Les paroles explicites, vocatifs,
questions à la cantonade intentionnelles et choix du destinataire restent
couverts. Les questions d'atelier et d'obscurité, l'écoute, la fouille et les
admissions gardent leurs voies. Les 117 tests initiaux restent archivés ; ils
ne sont pas additionnés aux 67 tests de cette correction.

**Luna.** Première passe G5 conservée : quatre scripts, 36 appels, aucune erreur
technique/recharge ; son échec de routage est décrit ci-dessus. Relecture :
**une seule passe** de `signes-guet`, `noms-dialogue`, `echanges`, lancée
détachée, priorité `BelowNormal` vérifiée pour le lanceur et le banc, fin écrite même après échec dans
`C:/Users/msics/donjon/artifacts/g5-323/relecture/fin-luna-passe.json`.
Les douze parties historiques des six scripts concernés, passes `integ-r1/r2`
de `c9459ce`, sont lues sans relance ; provenance et empreintes archivées.
`signes-noir`, `atelier`, `luna-restes-ambiance` ne sont pas rejoués avec Luna,
conformément à la relecture ; leurs voies sont vérifiées avec MJ simulé.

**Limites et intégration.** L'interprétation du libre reste sémantique : ne pas
revendiquer une garantie universelle de routage avant l'analyse de la passe.
G5 global reste partiel : le dialogue d'information conserve ses audits, G6
reste à porter ; les détails inconnus et l'ambiance gardent leurs contrôles.
Ni suite complète ni banc PNJ. Recouvrements : `narration.py` avec 320,
`rendu.py` et `jeu.py` avec 319. Bruts dans `C:/Users/msics/donjon/artifacts/g5-323/`.
