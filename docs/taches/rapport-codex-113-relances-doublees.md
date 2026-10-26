# Lot 113 — Relances du MJ et quantité implicite d'une dette

26 octobre 2026. Branche `codex-relances-doublees`, **non fusionnée**, base
`2ef7a07`, code signé `4fc1719`.
**N4 corrigé dans les deux passes ; aucun gain global de latence établi.**

**Attribution sans rejeu Luna.** Quarante parties de chaque version relues,
bruts principaux en lecture seule, empreintes conservées. Chaque appel, cause,
contrôle et `attendu` figure dans `artifacts/relances-113/*-attribution.json`.
`qualification.json` sépare chaque motif justifié/évitable, avec deux lectures
ambiguës laissées explicites.
Minimum structurel : premier appel de chaque rôle réellement emprunté dans le tour
(interprétation, récit du résultat ou de la parole, fidélité, audits) ; les répétitions
sont supplémentaires. Ce n'est pas une preuve du nombre optimal d'appels.
Deux passes réunies ; secondes = somme des durées archivées des appels supplémentaires,
pas différence causale de temps de réponse. Les familles sont exclusives ; un refus
mixte est rattaché à sa cause de reprise, ses motifs distincts restent dans les bruts.

| Famille | Appels supplémentaires b0042c9 → 91a4351 | Secondes | Relances narratives |
|---|---:|---:|---:|
| Rapport illisible (verdict/portée incompatibles) | 9 → 44 | 36,95 → 161,16 | 2 → 13 |
| Comptes dans le récit, termes et extraction | 8 → 16 | 31,96 → 55,94 | 4 → 8 |
| Perception, absence, lumière, ambiance | 12 → 13 | 36,55 → 49,30 | 6 → 6 |
| Quantité implicite d'une dette (N4) | 0 → 4 | 0 → 12,99 | 0 → 0 |
| Validation moteur, portée et faisabilité | 19 → 19 | 78,90 → 67,06 | 0 → 0 |
| Fidélité présence/identité et opération omise | 6 → 6 | 20,50 → 22,15 | 0 → 0 |
| Voix d'auteur | 2 → 0 | 5,80 → 0 | 1 → 0 |
| **Total** | **56 → 102** | **210,66 → 368,60** | **13 → 27** |

Avec les minima **350 → 357**, on retrouve **406 → 459 appels**. Le contrôle des
rapports illisibles vient du **lot 83**, et non du lot 102 ; ce dernier renforce
la couverture de vue, mais les seules campagnes non appariées ne prouvent pas
qu'il cause cette amplification. N6 est un faux refus (non-perception confondue
avec absence), la prise d'objets portés comme posés devant soi reste refusée à
juste titre. Comptes/extraction et ambiance mêlent vrais écarts et faux refus.
Le lot 101 modifie le garde d'auteur ; aucun appel supplémentaire de cette famille
ici. Le lot 106 ne change pas les contrôles : aucune attribution mécanique établie.
Les refus de portée, franchissement impossible, identité ajoutée et opération
omise sont justifiés et anciens.

**Famille traitée : N4, nouvelle perte d'opération.** Le dossier sémantique incomplet
précède ces lots ; le faux refus de quantité n'est donc pas causalement attribuable
à leur code. En revanche, les lots **100/104** permettent au typage contesté de
céder aux seuls mots : ici la créance n'est plus réclamée. Corriger cette lacune
de donnée évite le faux refus sans rétablir une obligation issue d'un typage erroné.
Preuve locale sur le verdict N4 exact : obligations après refus
`b0042c9={reclamer}`, contrôle issu du lot 104 `={}` (`provenance-n4.json`).
`MJ._verifier_fidelite_parole` fournit désormais les comptes connus **avant** le
règlement de la copie ; `couverture_action.entree` en nomme les références.
Toutes les paroles partagent ce dossier, sans cas de personnage, scénario ou
formulation, ni consigne ajoutée au prompt. Aucun verdict n'est forcé.

**Vérification.** Console avec MJ simulé : Gorm/deux pièces et Aubin/cinq pièces
payés une fois, monde, compte et texte rechargés ; trois pièces demandées contre
deux dues toujours refusées, aucun transfert issu de la copie rejetée, comptes
privés exclus. Deux tests ciblés verts, 6,06 s. Les 275 audits narratifs archivés
sont rejoués localement sur leurs entrées exactes : mêmes décisions que le code
91a4351 (28 refus lisibles et 42 rapports illisibles compris). Les contre-revues
archivées sont également rejouées ; aucun garde de décision n'est modifié.

Deux passes Luna `comptes`, `signes-guet`, `soir-noir`, copies, ChatGPT
`gpt-6-luna` medium/libre ; deux exécutions réduites, deux références intégralement
en cache. **18 tours MJ : 95 → 94 appels (5,28 → 5,22/tour), 17,8 → 18,5 s/tour** ;
relances **7 → 10**, replis **1 → 2**. Corvus réclame et reçoit les deux pièces de Gorm
**2/2**, **6/10 → 4/4 appels** sur le tour réel ; les deux revues citent le montant
de `comptes_avant`. Les huit appels économisés sur ce tour sont en grande partie
absorbés par les autres familles. Aucun arrêt, erreur technique ou défaut de recharge.
Le harnais Luna ne capture pas le solde d'or rechargé ; cette preuve est apportée
par les tests console. Charges différentes : pas de conclusion causale de latence.

Rejeu Luna supplémentaire des entrées exactes archivées, méthode 93/95 :
**21 appels, cinq refus de fidélité conservés** (identité ajoutée/omise et geste
ajouté), **huit refus narratifs conservés, six admissions, deux illisibles**.
Admissions : fausses réserves sur les comptes, ambiance, lumière d'une source
non vue et non-perception N6. Le véritable écart « objets portés devant soi »
reste non admis, mais sa revue est illisible : pas de preuve de jugement correct
sur ce cas. Les prompts et entrées de ce rejeu sont strictement archivés ;
le dossier enrichi est exercé dans les parties et tests ci-dessus.
Suite complète unique : **2 018 tests, 16 ignorés, aucune erreur, 217 fichiers,
1 925,76 s**, deux processus réduits. Les sept assertions historiques de deux fichiers
attendaient exactement les trois anciens champs du dossier ; attentes adaptées,
avec contrôle de l'absence de paiement futur dans `comptes_avant` et de comptes
privés. **Reprise des deux fichiers : 23 tests verts, 54,01 s**, un processus réduit.
Aucun échec de test restant reproduit ; aucune seconde suite complète.

**Limites et suite.** Les audits illisibles et faux refus de perception dominent
encore ; le classement des comptes et l'ambiance restent faillibles. Ce lot
garantit la donnée transmise, pas tout jugement sémantique ni toute absence de
perte d'opération. Aucune seconde famille corrigée, aucune seconde suite complète.
Bruts locaux `artifacts/relances-113/` et
`artifacts/bancs-multi/20261026-060056-33568/`.
