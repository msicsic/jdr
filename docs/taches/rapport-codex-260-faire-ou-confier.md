# Lot 260 — faire ou confier sur les croyances du mandant

**Prête pour la nouvelle suite complète du superviseur**, branche non
fusionnée `codex-faire-ou-confier-b`, moteur corrigé `323a0af`. Fusion sans
rebase de l'intégration 259 (`1355f7a`) conservée. Ni Luna ni suite complète
lancée par l'agent ; aucun scénario, MJ ou corps modifié dans ce correctif.

**Régression reconnue.** La suite du superviseur sur `d0f9f7a` : 2 671 tests,
une erreur propre au 260, absente de l'intégration verte (2 663 tests).
Crue/Brune devenue dépouille : le choix de mandataire appelait un validateur
exigeant encore le type vivant. Une garde contre ce seul type aurait masqué
la mort cachée et laissé invalides les jugements et filiations historiques.

**Invariant corrigé : identité persistante, admissibilité crue, projection.**
`agendas._condition_mandat` valide la structure et l'identité avec la famille
commune `noms.PERSONNES`, qui survit au décès. La disponibilité est séparée :
`_personne_disponible_crue` / `_destinataires_disponibles` lisent les seuls
états mort/parti crus par le mandant. Ces lecteurs servent à l'actualisation,
au sous-but, au choix du tiers et au devis. Aucun destinataire disponible :
fin dans l'actualisation, sommeil dans un devis isolé ; un groupe garde ses
membres encore disponibles. Un candidat cru mort/parti n'est pas devisé.
Une cible absente du modèle fermé rend le devis impossible, sans exception.

`ContexteDevis.projeter` reconstruit vie, présence et profil neutre des
personnes depuis les croyances de l'observateur ; type réel, nom de dépouille
et disparition du profil ne deviennent plus des observations à distance.
Le mandat hypothétique est validé sur cette projection. Aucun `try/except`
ne masque un refus de validation : les structures mal formées restent
refusées ; les références historiques à une cible morte restent rechargeables.
Le contrat faire/confier, ses coûts, paroles, jugement réel et filiation
bornée sont conservés ; aucune exception d'objet, de PNJ ou de scénario.

**796/796 tests verts, 92 fichiers ciblés**, deux travailleurs réduits,
**812,656 s**. Les 90 fichiers précédents, `test_corps_blessable` et le nouveau
`test_agendas_destinataires`. **17/17 tests du fichier corps blessable entier,
assertions inchangées**, dont le cas exact signalé ; **six nouveaux tests**
avec sous-cas crue/Brune puis Ilse, `amener` puis `informer`, mort/départ crus
alors que la personne est vivante, décès caché de la cible ou du candidat,
cible inconnue, groupe partiellement disponible, jugement/filiation après
décès. Monde complet, rendu et scène vérifiés après recharge. Quand l'esprit
du mandant reste inchangé dans ces profils, la mort réelle cachée conserve
projection complète, devis et choix. La première passe rouge reste dans
`destinataires-avant.log` ; les passages intermédiaires ne sont pas ajoutés
au compte des 796 tests.

**Stabilité : huit paires 4 h crue/Relais entièrement identiques** contre le
moteur antérieur `ab21fb3` : état final complet, chroniques, mesures, empreintes,
récits et souvenirs. Zéro plantage ; huit références lues dans le cache,
aucune rejouée, seulement huit nuits corrigées calculées. Pas de comparaison
de temps avec les références en cache. `git diff --check` propre.

**Réserves antérieures inchangées**, donc maintenues : après 259, crue 7/42,
oisiveté urgente 0/0 → 55/195 et attente 0/0 → 25/130 PNJ·min ; crue 2024,
oisiveté/attente 250/185 → 215/160. Aucun recours possible non entrepris
certifié par le détecteur. Brune crue 42 : 10 lignes actif / 9 sommeil mais
8 vrais réveils, huit captures rechargées et changements d'empreinte ; à
2441 seule la provenance vu → entendu change, nécessité individuelle non
démontrée. Diagnostic distinct du 268 (hameau 2024). Aucune boucle sans
entrée établie ni non-régression globale revendiquée. Coût du prochain
sous-but seulement, limites structurelles du modèle fermé 258, aucune
garantie d'adhésion/réussite, aucun compte rendu ni réaffectation sur retard.

Bruts : `C:/Users/msics/donjon/artifacts/confier-260/`, fichiers
`destinataires-avant.log`, `destinataires-tests.json`,
`destinataires-stabilite.json`, `destinataires-stabilite-analyse.json`,
`destinataires-fin.json` ; diagnostics antérieurs dans `apres-259/`.
Aucun calcul actif. **Prête pour la relance de la suite complète ; son
résultat reste à établir par le superviseur.**
