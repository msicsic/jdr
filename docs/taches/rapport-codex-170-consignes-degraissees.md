# Lot 170 — Consignes d'interprétation sans doublons (L6)

27 octobre 2026 — branche `codex-consignes-degraissees`, **non fusionnée**, base
`123daed`, code `a5f3ec9`. Luna reste `gpt-6-luna`. Logique moteur, schémas,
fournisseurs, `sources.py`, `narration.py`, scénarios et `main` intacts.

**Invariant visé.** Chaque règle à un seul emplacement. `INTERPRETATION` renvoie
aux contrats permanents de parole, assemblage et passage local. `artisanat.REGLES`
réunit la forme d'`assembler`, pièces, dimensions et qualification. Faisabilité
et reprise restent dans le socle ; leurs rappels dans `artisanat`,
`franchissement` et `obstacles` sont retirés. La portée rejoint le passage local.
La durée normale renvoie au dossier ; les DD utiles restent présents.
Localisation et narration finale gardent leurs contrats autonomes.

**Preuves locales.** Douze tests ciblés verts, dont inventaire de onze phrases
clés dans les consignes assemblées, invariance entre tours/refus, console et
recharge. Comparaison au texte de `123daed`, sur Relais et
atelier, chacun proche et éloigné : **4/4 états complets, sorties console et
rendus rechargés identiques**. `tools.mesure_prompt.mesurer` sur ces captures :
**39 910 → 38 828 caractères, −1 082 (−2,7 %)** ; **0/3 variations** avant et
après, schéma identique (30 953 caractères). Aucun serveur local mesuré.

**Luna.** Deux passes des huit scripts distincts : relais, crypte, atelier, échanges,
noms-dialogue, soir-appel, sous-obstacle-relais, poser-sol-relais. Référence
`cdaf371` exclusivement relue du cache ; poser-sol-relais absent du cache, donc
mesuré séparément. **16 parties, 84 tours MJ,
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
**Suite unique : 2 241 tests, 257 fichiers, 16 ignorés, zéro échec/erreur,
2 263,305 s**, deux travailleurs réduits. **4/4 empreintes Relais 2 h identiques**
(chronique, mesures, état complet), graines 1985/7/42/2024, contre `main`
`812ebe5` ; quatre références absentes calculées une fois et rangées.

**Limites.** Revue automatique : rejeu des seize audits archivés refusé
(160 appels, cinq essais par côté), envoi des données jugé non spécifiquement
autorisé. Zéro appel de ce rejeu ; **critère du lot 95 non établi**. L'utilisateur
confie le rejeu à l'orchestrateur : commande exacte dans `luna-a-jouer.txt`,
script `rejouer-refus.py` préparé. Atelier, tour 2 : faisabilité non proposée
dans la seconde passe, contrairement aux deux références ; réponse parlant du
« dossier ». Cause non isolée, conservation sémantique **non validée** :
**candidat partiel, non proposé à la fusion**. L'inventaire lexical n'exclut
pas toute paraphrase redondante. Les fils Luna ne conservent ni monde complet
ni tous les panneaux ; la preuve complète vient des parcours simulés.

**Livraison.** Bruts dans `C:/Users/msics/donjon/artifacts/consignes-170/` ; deux
traces automatiques de tests y ont été rapatriées, aucun brut restant au worktree.
Calculs réduits, deux travailleurs au plus par campagne ; copies seulement.
Vérification au-delà du créneau (suite seule : 37 min 43 s). Aucune clé de
signature configurée : commits non signés, livraison sur cette branche seule.
