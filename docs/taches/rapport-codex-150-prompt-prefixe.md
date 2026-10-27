# Rapport 150 — préfixe du MJ par voie

`codex-prompt-prefixe`, **non fusionnée**, base `4641dc3`, code `9a55cc1`.
Portage ciblé de `9d53229` après lecture de `d7913ce`, sans fusion de l’essai.
**L1 porté ; réserve de validation sur le critère des refus.**

**Invariant.** `sources.ordonner_faits/ordonner_entree` ordonnent les faits et
chaque entrée du contexte vers la proposition, sans perte ; les corrections
restent en fin. La révision n’apparaît qu’en relance, les clés distinguent les
voies. Consignes conditionnelles, `INSTRUCTIONS_RESULTAT` et schéma conservés ;
aucune règle moteur ni branche de refus du lot 151 modifiée. Luna reste `gpt-6-luna`.

**Local.** Fournisseur OpenAI-compatible, `response_format`, usage/cache,
quatre slots regroupés comme la source. `--connexion local`, variables
`LOCAL_LLM_URL`, `LOCAL_LLM_MODEL`, `LOCAL_LLM_KEY`. Aucun serveur disponible
à l’adresse configurée `127.0.0.1:8080` ni aux ports usuels : réseau simulé seulement.

**Preuves.** Neuf ciblés verts : deux scènes console (clé, ficelle), empreintes
comparées au MJ de `4641dc3`, requêtes identiques à l’ordre près, état complet et
rendu rechargé identiques ; relances, audits et sept clés sur les deux fournisseurs.
Syntaxe Python 3.11 valide. Suite unique : **2 169 tests, 243 fichiers, 16 ignorés,
zéro erreur, 3 530,46 s**, un travailleur. Seul échec : ancienne assertion d’ordre
entrée/enum, adaptée à l’égalité des clés avec multiplicité et reprise verte.
Complément d’ordre des audits couvert par les ciblés ; aucune seconde suite.
**4/4 empreintes Relais 2 h identiques** à `4641dc3` : chronique, mesures, état
complet ; quatre références absentes cachées une fois, aucun rejeu.

**Luna**, sept scripts (Relais/crypte/atelier/échanges, noms-dialogue/soir-noir/soir-appel).
Sept références absentes jouées une fois puis cachées ; branche deux passes.
**21 parties, 132 tours, 454 appels ; aucun incident technique/recharge.**

| Mesure par passe | Réf. `cdaf371` | Branche 1 | Branche 2 |
|---|---:|---:|---:|
| Appels / tour, moyenne | 3,43 | 3,52 | 3,36 |
| Appels / tour, médiane | 3,5 | 3,5 | 3,5 |
| Secondes / tour, moyenne | 10,70 | 12,29 | 11,67 |
| Secondes / tour, médiane | 9,80 | 10,96 | 10,39 |
| Relances / refus moteur | 9 / 10 | 7 / 15 | 7 / 13 |
| Replis | 2 | 1 | 0 |

| Jetons cachés par voie | Référence | Branche 1 | Branche 2 |
|---|---:|---:|---:|
| Interprétation | 393 856 | 368 000 | 441 472 |
| Narration | 21 632 | 25 216 | 0 |
| Résultat | 0 | 0 | 0 |
| Audit narratif | 293 120 | 336 384 | 333 824 |
| Audit action | 0 | 0 | 0 |
| Audit portée | 0 (3 appels) | aucun appel | aucun appel |

Capacités non exercées. `usage.attribution` (réf./1/2), cache tools
**369 252/392 688/400 741**, instructions **309 586/304 818/338 628**, items
**29 770/32 094/35 927** ; entrée et détails dans `mesures.json`.
**Aucun gain de vitesse démontré** sur ce poste partagé ; L2/L3 restent à faire.

**Refus : réserve.** Huit audits entiers, cinq rejeux par côté, **80 appels**, zéro
rapport illisible : refus référence→branche **0→2, 5→5, 2→1, 5→5, 3→1, 5→0, 5→4,
4→1**. **Seuil brut du lot 95 non atteint sur trois cas d’Aubin** (remboursement
et réponse nouvelle). Les textes de remboursement concordent avec l’issue, et la
réponse d’Aubin est autorisée : ces audits comprennent des faux refus de comptes
ou de parole. Cela ne suffit pas à déclarer le critère acquis. Le faux souvenir
attribué à Gorm reste refusé **5/5 des deux côtés**. Motifs variables, comparaison
de l’audit entier : aucune garantie par cause ni garantie sémantique générale.
Bruts : `artifacts/prompt-150/`, `artifacts/bancs-multi/20261027-013306-27580/`
(référence), `20261027-014208-27580/` (branche). Copies seulement, calcul réduit à
un travailleur pour cohabiter, Luna une exécution à la fois. Aucune clé de signature
configurée : commits non signés ; branche seule poussée, `main` intacte.
