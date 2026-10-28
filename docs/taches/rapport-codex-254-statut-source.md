# Lot 254 — statut sourcé, portée explicite

`codex-statut-source`, **non fusionnée**, base `integration e65fd54`,
28 octobre 2026. Code et tests : `3f4a951`. Aucun scénario historique,
MJ, agenda, jet ou choix du planificateur modifié ; aucun appel Luna.

Le statut réel reste une donnée d'auteur : `profil.statuts` contient une
liste de `{titre, lieux, domaines, connus}`. Chaque portée énumère ses lieux
et ses domaines, tous deux non vides ; aucun effet universel implicite.
`esprits.installer_statuts` n'en donne un savoir qu'aux connaisseurs déclarés
à l'installation initiale des relations. À la recharge, les croyances déjà
installées sont conservées, y compris une prétention fausse ou son retrait.
Les déclarations sont validées par `deliberation.verifier_profil`, les
croyances par `esprits._croyance_valide`. Les identités des connaisseurs
restent valides après leur départ ou leur décès.

`relations.statuts_reconnus(monde, observateur, titulaire, lieu, domaine)`
renvoie une copie de la croyance sourcée, filtrée par les deux portées, ou
`None`. Elle ne lit jamais le profil réel du titulaire ; une ignorance reste
une ignorance. Aucun consommateur de décision n'est ajouté ; contrôle AST
sur les accès au statut et sur les appels à cette lecture.

La transmission utilise les affirmations et les nouvelles de la parole
commune (`social.recevoir`, `_adopter`), avec une fonction distincte
`recevoir_statuts` ; ni `_utile` ni `bavarder` n'ont été touchées. Une parole
garde `dit:<identité>` ou `dit:voix:<signature>`, sa date et une confiance de
0,7, atténuée par le rang d'une nouvelle. Son poids reste celui de sa source,
sans privilège lié au titre prétendu. Une preuve plus forte ou plus récente
résiste ; à poids égal, le dernier contenu entendu prévaut. `[]` retire les
statuts crus. Une parole ne modifie jamais les déclarations réelles.

## Vérification et mesures

- **63 tests ciblés, six fichiers : 62 verts, un échec préexistant.** Les six
  nouveaux tests sont verts : responsable du Relais et employeur de la mine,
  connaisseur/ignorant, deux portées, copies pures, parole propre et tierce,
  prétention fausse, retrait, voix inconnue, nouvelle datée, témoin sans ouïe,
  monde et rendu identiques après sauvegarde/rechargement. Le test de voix
  inconnue isole l'identification par doublure ; les deux scènes de parole
  utilisent l'émission réelle et la réception commune.
- Les cinq autres fichiers : `relations_ascendant`, `relations_socle`,
  `relations_lectures`, `relations_graduees`, `social`. Exécution isolée,
  un travailleur à priorité réduite, **46,035 s**. L'échec
  `test_dette_soldee_une_fois_par_demande_acceptee` donne **40 au lieu de 20**,
  reproduit seul sur `e65fd54` (**0,596 s**) ; aucun oracle changé.
- **Empreintes en cours**, code figé `3f4a951` contre la base `e65fd54`
  (`origin/integration` au départ) : cinq scénarios × quatre graines × 2 h,
  cache commun, référence puis branche, un travailleur à priorité réduite.
  Processus détaché ; fin écrite en dernier dans `fin.json`. L'identité du
  jeu et de l'état complet ne peut pas encore être affirmée.

Bruts : `C:/Users/msics/donjon/artifacts/statut-254/` : `tests.json`,
`echec-base.txt`, `lancer.py`, `empreintes.log`, puis `empreintes.json` et
`fin.json`. Pas de suite complète ni d'audit long.

## Limites

Ce socle ne prouve pas automatiquement un mensonge : une rectification doit
être reçue par la voie commune et assez étayée. La portée utilise des listes
explicites, sans hiérarchie de grades ni déduction de juridiction. Le statut
est transportable comme contenu moteur ; aucun protocole joueur/MJ ni
émission autonome de statut n'est ajouté. Aucune obéissance, aucun bonus ni
garantie universelle hors des épreuves décrites. L'échec de dette préexistant
et les résultats d'empreintes restent à examiner à l'intégration.
