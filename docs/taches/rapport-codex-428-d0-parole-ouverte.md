# Lot 428 — D0, parole ouverte personnelle

Branche `codex-d0-parole-ouverte`, non fusionnée. Départ `ce64ba7e` ; ancêtre commun
avec `integration` : `60f857c5`. Bruts sur le PC fixe :
`C:/Users/msics/donjon/artifacts/d0-parole-428/`.

**Invariant moteur.** Le compilateur choisit seulement `{personnage, sujet}`. Pour un sujet
inédit, Luna formule une parole, puis une admission indépendante type ses engagements,
ses sources et sa compatibilité. `paroles.verifier_ouverte/preparer_ouverte` contrôlent
présence, audition, sujet, grammaire, sources et provenance de l'admission avant inscription
dans le registre G15. `connaissances.verifier_sources_parole` refuse un savoir absent du
PNJ ou fermé par le catalogue d'auteur ; `promesse` et `accord` sont refusés avec `attendu`.
Les gardes communes des références, voix et unités restent appliquées. Aucun analyseur
de mots-clés, registre d'esprit ou effet social nouveau. L'admission est liée aux mots et à
la révision ; la transaction est rejouée avant sauvegarde, puis publication immuable.

Hors journaux d'affichage, seuls changent la révision et l'émission : aucune dette, promesse,
croyance, connaissance, ressource ou entité créée. Pour le même auteur, sujet et destinataire
ayant entendu, le moteur reprend le registre ; **zéro appel de formulation et d'admission**,
aucune réémission. Le rendu historique et sa revérification utilisent G19. Le contexte public
expose les sujets et leur état entendu, jamais les savoirs privés. Le scénario du Relais
ouvre explicitement le souvenir personnel de Gorm, auparavant fermé à toute invention.
`dialogues.py` : ajout localisé du catalogue public ; le raccord K0 reste indépendant.

**Vérifications.** Six tests D0 sur Gorm au Relais et Odile à l'auberge : vraie console,
MJ simulé, recharge, texte conservé et monde entier comparé ; secret gardé, savoir absent,
promesse/accord omis du typage initial, incompatibilité, admission altérée, destinataire
distinct et panne de sauvegarde. Les fichiers voisins G15, G19, rappels exacts, dialogues,
projection, schémas et consentement totalisent **94/94 tests distincts verts sur onze fichiers**,
sans suite complète ; `test_connaissances` compte **10 succès et une erreur préexistante**. Les premiers essais
ont révélé les raccords de forme, de consentement et de désignation historique, corrigés.
L'ancienne attente de `connaissances_pnj` dans le contexte public laisse **un test voisin en
erreur**, reproduite avec les neuf modules modifiés repris de `ce64ba7e` (`base-overlay/`) ;
aucun oracle modifié. Résultats détaillés : `tests-finaux.json`, `tests-cloture.json`,
`tests-d0-final.json`, `test-connaissances-base.txt` ; ne pas additionner les reprises.

**Luna, une passe seulement.** Deux scripts ajoutés, quatre tours, sept appels : aucun
plantage, repli, fuite nominale signalée ni erreur de recharge. Relais : trois appels,
5,3 s/tour ; parole vague de Gorm puis restitution, aucune anecdote concrète. Auberge :
quatre appels, 7 s/tour ; deux refus de texte vide. Cette passe **précède la séparation
finale choix/formulation**, motivée par ces résultats ; celle-ci est vérifiée avec MJ simulé,
pas rejouée avec Luna conformément au budget d'une passe. Aucun succès général de qualité
narrative ni gain causal de latence revendiqué. Commande exacte : `commande-luna.txt`.

**Banc rapide.** Branche seule, Relais et auberge, quatre heures et graines 1985/7/42/2024,
un travailleur réduit, lancé détaché par `artifacts/d0-banc-rapide.py`. Aucun rejeu de référence.
Terminé : **8/8 nuits**, `fin-banc-rapide.json` porte `ok=true`, journal d'erreurs vide.
Zéro usurpation, écart ou minute urgente sans recours compté ; Relais : 102–134 gestes,
62,1 s/nuit en moyenne ; auberge : 122–183 gestes, 122,7 s/nuit. Les quatre graines donnent
quatre issues distinctes dans chaque scénario. Ces temps ne sont pas comparés à une référence.
Lecture des chroniques et épisodes : rondes, repas et services se poursuivent ; auberge 2024,
Lucien appelle Hugues douze fois entre 109 et 131 min. Sans référence, aucune attribution de
cette répétition à D0 ni garantie générale d'absence de boucle. Ce banc passif n'exerce pas
la parole ouverte ; sa preuve reste celle des tests console. Détail : `analyse-banc-rapide.json`.

**Limites.** Les effets, l'enregistrement et les refus sur les types/sources sont déterministes.
L'extraction des engagements, des paraphrases d'un secret et la compatibilité du français
restent sémantiques : aucune garantie absolue de leur reconnaissance ni de la qualité d'un
souvenir. La voie historique `enrichir_savoirs` et les dialogues non portés gardent leurs
contrôles ; D0 ne supprime aucun audit de ces voies. Une nouvelle question sur le même sujet
reprend le contenu admis ; elle ne génère pas automatiquement un deuxième souvenir.
