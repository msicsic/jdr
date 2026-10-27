# Lot 170 — Consignes d'interprétation sans doublons (L6)

27 octobre 2026 — branche `codex-consignes-degraissees`, **non fusionnée**, base
`123daed`. Luna reste `gpt-6-luna` ; aucun changement moteur, schéma, fournisseur,
`sources.py`, `narration.py`, scénario ou `main`.

**Invariant visé.** Un contrat d'interprétation à un seul emplacement dans les
consignes assemblées. Le socle renvoie aux règles permanentes de parole,
d'assemblage et de passage local. La forme complète d'`assembler` est réunie dans
`artisanat.REGLES` avec ses contraintes de pièces, dimensions et qualification.
La faisabilité et la reprise restent définies dans le socle ; les rappels dans
`artisanat`, `franchissement` et `obstacles` sont retirés. L'indication de portée
du passage local rejoint sa définition. Le temps d'une fabrication normale
renvoie au dossier plutôt qu'au barème d'une échelle de trois mètres. Les DD
utiles au premier essai restent présents. Les règles de localisation et les
autres voies de narration gardent leurs textes autonomes ; leur indépendance
interdit de supprimer globalement un rappel nécessaire à une autre voie.

**Preuves locales.** Douze tests ciblés verts, dont inventaire de onze phrases
clés dans les consignes réellement assemblées, invariance entre tours et refus,
console et recharge. Comparaison au texte exact de `123daed`, sur Relais et
atelier, chacun proche et éloigné : **4/4 états complets, sorties console et
rendus rechargés identiques**. `tools.mesure_prompt.mesurer` sur ces captures :
**39 910 → 38 828 caractères, −1 082 (−2,7 %)** ; **0/3 variations** avant et
après, schéma identique (30 953 caractères). Estimation en caractères, aucune
mesure sur serveur local ni gain de latence causale déduit.

**Luna.** Deux passes des huit scripts distincts : relais, crypte, atelier, échanges,
noms-dialogue, soir-appel, sous-obstacle-relais, poser-sol-relais. Référence
`cdaf371` exclusivement relue du cache ; poser-sol-relais absent du cache, donc
mesuré séparément. Aucun rejeu de référence manquante. **16 parties, 84 tours MJ,
281 appels**, zéro arrêt/erreur technique/recharge. Sur les sept scripts communs
(82 tours), référence → lot : **266 → 271 appels**, **3,24 → 3,30 appels/tour**,
**10,51 → 11,42 s/tour** ; relances **14 → 19**, refus moteur/contre-revue
**21 → 25**, obstacles narratifs **32 → 32**, replis **3 → 1**. Cache commun :
interprétation **567 808 → 1 188 608**, audit **452 352 → 449 408**, fidélité
**0 → 13 440**, contre-revue **0 → 3 584**, récit **0 → 8 832**, révision
**134 784 → 251 648** jetons. Ensemble avec pose : cache d'interprétation
**1 242 880**, consignes invariantes **0/81 variations**. Référence historique,
changements moteur cumulés et charges différentes : aucun gain causal conclu.
Passage dessous abouti 2/2 ; pose aboutie après correction de destination 2/2.
**Suite complète unique : en cours**, deux travailleurs réduits.

**Limites.** La revue automatique a rejeté le rejeu des seize audits archivés
(cinq répétitions par côté, 160 appels), considérant l'envoi des données archivées
comme non spécifiquement autorisé. Aucun appel de ce rejeu n'a été effectué.
Le critère du lot 95 reste **non établi**, donc aucune certification de conservation
des refus. Commande exacte et script préparé dans `luna-a-jouer.txt` et
`rejouer-refus.py`. L'inventaire lexical protège les contrats mutualisés ; il
ne démontre pas l'absence de toute paraphrase redondante dans le prompt entier.
Les tests simulés prouvent la conservation des parcours, pas l'équivalence
sémantique exhaustive de Luna après une modification du texte.
Au tour 2 de l'atelier, la seconde passe répond en dialogue après le refus
« C'est au moteur de dire si Corvus le peut », au lieu de proposer l'assemblage
comme les deux références cachées. La première passe propose bien ce geste.
Le texte final parle aussi du « dossier ». Une occurrence ne permet pas
d'attribuer causalement ce défaut au retrait du rappel de faisabilité, mais
la conservation du comportement attendu n'est **pas validée** ; le lot demeure
un candidat partiel, **non proposé à la fusion**.
Le harnais Luna recharge chaque partie mais ne conserve pas son monde complet
ni tous les panneaux : la preuve d'état complet et de rendu vient des parcours
simulés, pas des seuls fils Luna.

**Livraison.** Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/consignes-170/`. Deux calculs simultanés au plus,
priorité réduite, copies temporaires de scénarios seulement. Aucune clé Git de
signature configurée : commits non signés. État de poussée à compléter.
