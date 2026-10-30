# Lot 346 — A1, projection publique avec provenance

30 octobre 2026 — branche `codex-a1-provenance`, base fournie `da5f795`
(intégration avec le brief 346), **non fusionnée**.

`donjon/projection_publique.py:projeter` produit une copie déterministe de
l'entrée préparée par les producteurs actuels. Chaque valeur, y compris un
conteneur initialement vide, garde son chemin source, sa destination, son
autorité et la révision de projection. Minute/tour/source d'observation
restent attachés aux souvenirs et événements qui les fournissent. Perception,
souvenir, parole entendue, événement joueur et connaissance déclarée restent
distincts des propositions non exécutées, catalogues d'admission et anciens
récits. La conversation est conservée intégralement ; elle ne crée aucun
souvenir. Aucun branchement au MJ, changement de consigne, schéma ou revue.

Les dossiers mixtes ont un contrat fermé : tout champ nouveau non couvert
échoue avec `ProvenanceAbsente`. Les états mentaux, consignes privées de voix,
savoirs propres aux PNJ et états internes des personnages sont exclus ;
les mots transmis restent dans les paroles. Une source lumineuse non
identifiée et un auditeur sans désignation connue ne deviennent pas connus
par leur présence dans les registres internes. La projection réemploie les
désignations publiques existantes, dont `personne_<n>` ; elle n'invente pas
d'identité. Le journal technique des exclusions, susceptible de nommer des
secrets, est séparé de `Projection.publique()`.

**Couverture A0.** Les six archives `230e7b3` du 318/A0 sont relues et leurs
SHA-256 vérifiés : **30 tours, 36 entrées avec reprises, 23 684 valeurs
couvertes, 1 597 exclusions secrètes, zéro exclusion de doublon**. Répartition :
états mentaux 1 082 ; dossiers de formulation 324 ; savoirs privés 103 ;
états internes 67 ; auditeurs inconnus 21. Les 25 sources lumineuses anonymes
(`null`) sont conservées, avec leur effet perçu, sans nouvelle identité.
`verifier_couverture` exige une partition exhaustive, l'équivalence exacte
des valeurs et une justification conforme au contrat ; omission, altération
ou justification arbitraire font échouer le test. Les entrées sont copiées
dans `tests/data/projection_a1_entrees.json.gz` (36 007 octets) pour les
tests portables ; l'outil compare cette copie aux archives scellées.

| JSON UTF-8 compact, somme des 36 entrées | Octets |
|---|---:|
| Entrée actuelle | 736 697 |
| Données publiques conservées | 680 995 |
| Projection avec provenance | 5 851 399 |

La provenance détaillée augmente le volume ; aucune optimisation ou vitesse
de compilation n'est revendiquée. Reproduction : `python tools/couverture_a1.py
--archives C:/Users/msics/donjon/artifacts --sortie artifacts/a1-346/couverture.json`.
`--figer-entrees <fichier.gz>` reproduit l'extrait versionné.

**Vérification : 67 tests distincts verts, quatre fichiers** (A1, oracle A0,
localisation, noms). Consigne réelle `relais/4` et gravure de la crypte :
texte connu et preuve d'examen conservés ; souvenir d'un PNJ à la minute 17,
déplacé ensuite hors de vue : désignation/date conservées, sans position
actuelle ; faux rappel dans la conversation sans nouveau souvenir ; savoir
privé d'un PNJ visible exclu. État complet, projection, texte et scène
identiques après sauvegarde/recharge. Les premières passes rouges sont
conservées (droits temporaires Windows et montages de test corrigés).
Dernier contrôle : une source anonyme ne doit pas être exclue ; une identité
de source inconnue doit l'être sans perdre son effet lumineux.
Deux travailleurs au plus, priorité réduite ; aucun Luna, banc PNJ ou suite
complète. Bruts : `C:/Users/msics/donjon/artifacts/a1-346/`, `fin.json`.

**Limites.** L'entrée doit venir des producteurs actuels et de sauvegardes
valides : ce n'est pas un assainisseur de JSON libre ni une analyse du
français des conversations. La date historique absente de certains
souvenirs visuels anciens reste explicitement inconnue ; elle n'est pas
remplacée par la révision courante. Le souvenir daté exigé est prouvé avec
un personnage. Les nouveaux champs des dossiers mixtes doivent être portés
avant leur admission. Aucun gain I/V/F/P ni raccord A6 n'est validé ici.
Aucun fichier de code commun avec les lots 341, 342, 344 ou 345 ; seul
`docs/etat-dev.md` est partagé. La fusion reste au superviseur.
