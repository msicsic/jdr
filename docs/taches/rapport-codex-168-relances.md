# Lot 168 — Attribution des relances et examen explicite des comptes

27 octobre 2026 ; branche `codex-relances-168`, **non fusionnée**, base
`c16aaac`. **Essai non fusionnable en l'état : faux refus persistants et critère 95 non atteint.**

**Attribution**, 64 parties communes archivées `cdaf371/227c496`, medium/libre,
budget 200 : **24 → 41 relances, 1 → 2 replis**. `attribution.json/.md` donnent
les 41 relances, motifs et comparaisons avec chaque même tour de référence.
Classement principal exclusif :

| Famille | Relances 227c496 | Attribution et suites |
|---|---:|---|
| Comptes omis ou engagement mal lu | 10 | `comptes` p1 t2/p2 t1–2 ; `soir-appel` p1 t5/p2 t4–5. Extraction vide malgré remboursement/dette ; motifs parfois mixtes. Repli p1 t5. |
| Rappels hors avis | 6 | Silences actuels : `echanges` p1 t2/p2 t1, `noms-dialogue` p2 t2 ×2 ; `crypte` p2 t41 ×2, pas tous certifiés indus. |
| Mesures | 3 | Deux pas, `force-4c-fuir` p1/p2 t1 (déjà refusés dans la référence) ; coordonnées du mur, `atelier` p2 t8 (nouveau). |
| Avis désormais typés | 4 | `avis-joueur` p1 t0 ×2/p2 t0–1 : circuit d'audit légitime depuis 164 ; motifs pas tous justifiés. |
| Gestes | 2 | `ressources` p2 t2, `noms-dialogue` p2 t1 : gestes ajoutés à la réponse. |
| Lumière | 2 | `noms-dialogue` p1 t4 : source non contributrice puis pénombre. |
| Perception, savoir, sources, voix d'auteur | 14 | Ensemble hétérogène de refus fondés ou discutables ; repli `atelier` p2 t12 après trois contrôles. |

**Correction partielle de la première famille homogène évitable.** Un récit
déclaré établi peut recevoir `comptes: []`, puis être refusé pour omission.
`narration.schema_comptes/lire_comptes` imposent l'examen de chaque compte
`du`/`rendu` : valeurs affirmées ou `null`, plus les autres comptes. Aucun
préremplissage ; contrôles de rôles, montants, offres, couverture et sauvegarde
inchangés, anciennes listes lisibles. Fichiers réservés, moteur PNJ et modèle intacts.

**Tests.** Treize ciblés verts avant les dernières assertions de rendu ; console
Gorm/Aubin, montant faux rejeté, vrai récit conservé, monde complet et rendu
identiques après recharge ; omission, inversion et enveloppe incomplète refusées.
Suite complète unique, deux travailleurs réduits : **2 233 tests, 256 fichiers,
1 296,437 s, zéro erreur/ignoré, deux échecs MiMo historiques `6 != 5`**
(`test_fournisseurs_jeu`, `test_restes_fusions`). Les quatre tests du fichier
modifié passent ; aucune seconde suite. Vérification au-delà du créneau.

**Rejeux entrelacés, cinq par côté**, entrées/instructions archivées, schéma
`c16aaac` contre nouveau, sans redemande : **120 appels, aucune erreur/illisible**.
Onze audits comptables et un témoin `atelier` sans compte, inclus par « compter »
(hors mesure de correction). Refus par audit, base → lot, sur cinq :

| Audits archivés, dans l'ordre de `audits-comptes.json` | Refus / cinq |
|---|---|
| `comptes` p1 t2 ; p2 t1, audits 1/2 ; p2 t2, audits 1/2 | 1→0 ; 4→2 ; 3→1 ; 5→3 ; 1→0 |
| `soir-appel` p1 t5, audits 1/2/3 | 5→2 ; 5→4 ; 4→0 |
| `soir-appel` p2 t4, audits 1/2 ; t5 | 4→2 ; 5→3 ; 5→3 |
| Témoin `atelier` p2 t12, audit 3 | 1→0 |

**42/55 → 20/55 refus** ; huit audits perdent plus d'un refus sur cinq :
**critère 95 non satisfait**. Les pertes visent surtout les omissions indues,
mais les motifs mixtes empêchent de certifier la conservation de chaque refus juste.

**Luna, une passe**, copies temporaires du dépôt, coffre principal, deux
exécutions réduites au plus : `comptes` **8 appels/2 tours MJ**, aucun refus/repli ;
`soir-appel` **20/4**, un repli au remboursement d'Aubin : solde `absent` extrait
deux fois au lieu de `rendu`, puis source omise. Aucun incident/recharge ;
paiement et engagement racontés. Aucun gain général garanti.

**Limites.** Examen obligatoire, justesse sémantique ; **famille non close**.
La preuve monde/rendu rechargés vient des tests console, pas du harnais Luna.
**114 fichiers de référence inchangés**, aucun rejeu. Bruts :
`C:/Users/msics/donjon/artifacts/relances-168/` ; les auxiliaires créés par les
tests dans le worktree ont été déplacés dans `auxiliaires-tests/` après la suite.
Aucune clé de signature configurée ; commit non signé, branche seule poussée,
`main` intacte.
