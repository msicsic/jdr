# Lot 138 — Réplique au discours direct

Branche `codex-discours-indirect`, non fusionnée ; base `e48c2cc`.
Aucune clé Git de signature configurée. Fichiers réservés aux lots 135/136 intacts.

**Cause N8 prouvée dans le fil.** `ressources` p2 n°1 du lot 123 : la première
interprétation propose déjà « Tu demandes à Brune si elle a de quoi manger. »,
avec `ressource=faim`. Ni correction ni secours local. La fidélité accepte :
« La réplique demande bien à Brune si elle a de quoi manger ; le sens “faim”
correspond à cette demande générale. » Elle vérifie le contenu mais admet le cadre
narratif comme mots prononcés. Quatre appels, aucune validation refusée.

**Contrat commun.** `paroles.SENS_REPLIQUE` définit la réplique directe, la
transposition des personnes et de l'interrogation, et la conservation des opérations.
Cette définition est partagée par le schéma, les règles d'interprétation et la revue
MJ de parole uniquement. `forme_rapportee` réutilise les verbes introducteurs de
l'analyse d'adresse et la personne grammaticale ; aucun lexique de faim, personnage
ou scénario. Le raccourci aux mots exacts ne dispense plus une copie rapportée
sans mots imposés de revue. `mots_dits` ne confond plus une question rapportée à
la deuxième personne avec une question directe. Le secours demande alors des mots
directs, sans transposition locale inventée ; citations et mots imposés restent exacts.

**Vérifications.** Console/MJ simulé, sauvegarde et recharge : N8 corrigé avec
opération `ressource` conservée ; affirmation à un autre interlocuteur corrigée,
même lorsque la proposition recopie exactement la saisie indirecte ; citation
narrative volontaire inchangée ; deux refus sans mots directs ne prononcent rien.
Paroles, conversation, absence de paiement et position rechargées contrôlées.
Les tests N3 et d'audience restent verts. Tests ciblés : première série 12 tests,
un échec du nouveau garde grammatical à la deuxième personne, corrigé ; 38 verts
ensuite, puis quatre nouveaux parcours verts après renforcement des assertions.
Deux tentatives initiales du lanceur échouent sur les permissions temporaires
Windows, avant résultats exploitables ; exécution autorisée hors bac à sable.

**Luna, une passe sur copies.** 11 tours MJ, 46 appels (4,18/tour), zéro refus
moteur/fidélité, zéro repli, zéro erreur de recharge. N8 : « Tu as de quoi manger ? »,
`ressource=faim` conservée, quatre appels. Aucune réplique à la deuxième personne
qui décrive la demande. Trois relances narratives, sans échec de parole.

| Script | Appels/tour référence p1 / p2 → lot | Secondes/tour p1 / p2 → lot |
|---|---:|---:|
| ressources | 4,67 / 4,00 → 4,00 | 20,69 / 13,28 → 15,1 |
| soir-appel | 5,00 / 4,00 → 4,75 | 20,83 / 14,83 → 20,1 |
| noms-dialogue | 3,75 / 3,75 → 3,75 | 14,00 / 15,03 → 12,4 |

Les deux passes historiques `057766f` sont relues dans les bruts du lot 123,
jamais rejouées. Suite complète unique (`tools/tests.py --processus 2`) :
**2 077 tests, 228 fichiers, 1 107,42 s, deux échecs MiMo `6 != 5`, zéro erreur
et zéro ignoré**. Les deux échecs sont reproduits sur une archive intacte de
`e48c2cc` : 13 tests en 11,15 s, mêmes deux échecs, zéro erreur ; aucun changement
fournisseur. Bilan du lot vert hors ces deux défauts préexistants, sans seconde
suite complète. Deux calculs au plus, priorité réduite ; Luna une exécution.

**Limites.** La transposition et la reconnaissance d'une réplique narrative par
la revue restent sémantiques. La garde locale ne couvre que les cadres introducteurs
reconnus par le lexique grammatical commun ; elle ne prétend pas analyser tout le
français. L'invariant général reste non garanti pour toute saisie libre. Les mesures
Luna sur une passe et une machine partagée ne prouvent pas une évolution de vitesse.
Bruts : `artifacts/discours-138/`, `artifacts/bancs-multi/20261026-214046-42760/` ;
référence du lot 123 relue sans rejeu dans le dépôt principal.
