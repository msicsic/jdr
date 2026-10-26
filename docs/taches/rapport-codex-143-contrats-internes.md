# Lot 143 — Contrats internes dans les explications

Branche `codex-contrats-internes`, non fusionnée, base `4725388`.

**Cause N10.** Les réponses du lot 141 sont relues dans `entrees.json` et
les parties `reference-p1/*-atelier.json` et `reference-p2/*-relais.json` de
`C:/Users/msics/donjon/artifacts/verif-luna-9a39738/`.
Atelier n°12 : après une contre-revue d'examen du sol non conforme, le MJ
produit un avis `impossible`, dont la `justification` est auditée. Relais n°22 :
le déplacement composé d'une cible inconnue est refusé ; le MJ répond en
`dialogue`, dont le `texte` est audité. Les deux audits acceptent la mécanique.
Les deux voies appellent déjà `voix_auteur` ; ni attestation, ni segment exact,
ni repli, ni `ExplicationCedee` ne dispense ces textes du garde. Le trou est
lexical : le motif reconnaissait quelques verbes immédiatement après
« le moteur », éventuellement après « a/avait », mais ni « fournisse », ni
« n’en reconnaît ». Aucun changement de routage n'est nécessaire.

**Invariant et changement.** Toute explication destinée au joueur reste dans
la fiction. `narration.CONTEXTE_TECHNIQUE` partage la catégorie des opérations
du contrat (`OPERATIONS_CONTRAT`) et reconnaît leur lien au moteur avec
négation, pronoms et auxiliaires. Les noms de champs, identifiants,
propositions et schémas explicitement qualifiés de techniques sont contrôlés.
Les noms communs isolés, le moteur du moulin et les répliques restent admis.
Le même garde protège les avis, dialogues, segments récupérés et
l'enregistrement existants ; aucun prompt, scénario ou fichier réservé aux
lots 140/142 n'est modifié. `docs/contrat-mj.md` précise le contrôle.

**Preuves console.** `tests/test_contrats_internes.py` reproduit les deux
phrases intégrales par leurs voies réelles, malgré un audit favorable, puis
vérifie leur correction en fiction et l'absence de persistance du texte refusé.
Après sauvegarde/rechargement : objets (dont possessions et ressources),
joueur, temps, journal et rendu identiques. Une autre limite de perception et
« champ » ordinaire persistent ; moteur concret, identifiant ordinaire,
schéma dessiné et citation ne sont pas censurés. Un audit favorable altéré
ne permet pas non plus d'enregistrer les textes N10.

**Vérifications.** 33 tests ciblés verts (10,10 s), puis garde d'écriture
supplémentaire inclus dans la suite complète unique : **2 119 tests, 235
fichiers, 1 241,41 s, deux échecs MiMo historiques `6 != 5`, zéro erreur ou
ignoré**, deux processus réduits. Les deux échecs sont ceux documentés dans
les lots 134/137/138 (`test_fournisseurs_jeu`, `test_restes_fusions`) ; aucune
référence moteur rejouée. Bruts et lanceur : `artifacts/contrats-143/`.

Luna `gpt-6-luna`, ChatGPT medium/libre, **une passe sur copies**, une seule
exécution réduite ; au plus deux calculs du lot (recouvrement avec le dernier
fichier de tests seul). Six parties de `9a39738` lues du cache, empreintes
inchangées, aucun rejeu. Appels/tour, références p1 / p2 → branche :

| Script | Référence p1 / p2 | Branche |
|---|---:|---:|
| atelier | 3,18 / 3,27 | 3,00 |
| relais | 2,50 / 2,63 | 2,50 |
| luna-restes-ambiance | 2,00 / 2,00 | 2,00 |

**22 tours MJ, 61 / 63 → 59 appels**, 2,77 / 2,86 → **2,68 appels/tour** ;
relances **1 / 4 → 1**, replis **0 / 1 → 0**. Aucun arrêt technique ni défaut
de recharge. Tous les textes finaux relus : aucune explication technique,
cas pierre et pied-de-biche exprimés dans la fiction ; « champ de vision »
conservé. Cette passe ne reproduit pas les formulations techniques N10 : leur
rejet déterministe est prouvé par les simulations, pas par une nouvelle
occurrence naturelle. Le garde historique refuse une réserve « confirmées »
au Relais, sans relance, puis le refus de portée est affiché. L'unique relance
vient d'un jugement sémantique de non-perception à l'atelier. Aucune hausse
observée ; aucune conclusion de vitesse sur ce poste partagé.

**Limites.** Le lien grammatical et le vocabulaire restent lexicaux : toutes
les paraphrases françaises et tous les sens polysémiques ne sont pas prouvés.
L'audit sémantique demeure nécessaire ; aucune garantie universelle annoncée.
Aucune clé Git de signature configurée ; livraison par commit non signé sur
la branche du lot, sans fusion dans `main`.
