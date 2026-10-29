# Lot 322 — trois échecs nouveaux : diagnostic et oracles

29 octobre 2026. Branche `codex-trois-echecs`, base `integration 0a0bc9d`.
**Vérification en cours**, deux travailleurs de calcul au plus, priorité réduite.
Bruts : `C:/Users/msics/donjon/artifacts/trois-echecs-322/`.

**Diagnostic.** Les trois attentes historiques confondent une scène isolée
avec un jeu où le secours peut maintenant préparer le contact d'un
bénéficiaire inconnu (contrat du lot 303). Aucun fichier du moteur modifié ;
les lots 313 et 315 ne sont donc pas concernés par une correction de code.

- **Voix : changement légitime.** Mathurine conserve le but de nourrir
  Mireille et la cherche après avoir cherché Odile pour obtenir des vivres.
  Elle appelle réellement « la grande fille de vingt-huit ans ? » depuis
  le couloir (instant 3451, niveau reçu 7), puis le grenier (3616, niveau 8).
  Le joueur saisit les mots par l'ouïe commune et entend une troisième voix
  anonyme ; aucun nom d'auteur n'est révélé. `diagnostic.json` conserve les
  étapes, intentions, bruits, paroles rendues et contrôles de recharge.
  Dans les deux tests historiques, `sans_souci` retire seulement le secours
  spontané de ce tiers, comme le placement le fait déjà pour Hugues et Tilo.
  Les égalités exactes des deux voix, l'absence de nom et les assertions
  d'invitations sont conservées. Un nouveau test garde la scène avec ce
  tiers actif : appel réel audible, trois voix, anonymat, monde, scène et
  rendu de l'écoute identiques après sauvegarde/rechargement.
- **Service : changement légitime.** Avec la voix connue, Mathe croit Odon
  au baraquement ; le plan est déjà `None`. Avec la voix inconnue, le montage
  retire toutes ses croyances sur Odon : le plan est une inspection de la
  réserve pour le localiser, sans service ni passage de porte. Le verrou
  reste cru fermé à clé. Il s'agit d'un préfixe incertain, pas d'une promesse
  de repas. La demande effective est toujours refusée comme impossible,
  même au jet 20, avec ou sans localisation préalable. Le test place
  désormais le lieu entendu d'Odon dans les deux variantes avant d'éprouver
  l'accès aux vivres ; `None` et le refus `impossible` restent exigés.

**Bissection en cours.** Rejeu des trois tests originaux sur des copies
`git archive`, sans changer le worktree courant. `d1c0722` : trois verts ;
`79fca6a` et le milieu `f8fbff2` : les trois échecs attendus. La recherche
continue jusqu'à la fusion introductrice et son parent direct ; résultats
par commit dans `bissection.json`, bornes finales dans `bornes.json`.

**Vérification ciblée en cours.** Les trois fichiers touchés sont lancés
par `tools/tests.py --processus 1`, en parallèle du seul travailleur de
bissection. `fin-bissection.json` et `fin-tests.json` sont écrits en dernier,
même en cas d'échec. Les contrôles de diagnostic déjà achevés conservent
l'état complet, le rendu et la scène après recharge pour les six variantes.
Pas de Luna, suite complète ni banc : aucun code du jeu ne change.
Le suivi détaché écrit `fin-calcul.json` après les deux fichiers de fin ;
les processus ont été vérifiés actifs avant de rendre la main.

**Limites.** Le verdict porte sur ces scènes et les garanties des tests ;
il ne certifie ni tous les secours, ni toute absence de boucle. La
clôture du lot attend les bornes historiques et les trois fichiers verts.
