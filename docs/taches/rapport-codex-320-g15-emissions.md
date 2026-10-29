# Lot 320 — G15, émissions de parole

Branche `codex-g15-emissions`, **non fusionnée**, base `integration 0fcc99e`.
Vérifications finales détachées : `C:/Users/msics/donjon/artifacts/g15-320/fin.json`.

Chaque parole passe par le registre `emissions_parole` : identifiant et ordre
croissants, auteur, acte, paramètres, modalité, événement source, destinataires,
auditeurs acoustiques, mots, rendu, lieu et instant. La source atteste la parole
et son audition, jamais la vérité de son contenu. `emissions.py` est l'accès
commun ; `ouie.retentir`, les dialogues admis de `faits_locaux` et
`narration.consigner` y écrivent avant publication. Les anciennes sauvegardes
sont migrées sans conserver deux historiques concurrents. Leur ordre intra-tour
irrécupérable est explicitement marqué inconnu. Les anciennes lectures joueur
gardent une projection d'adresse, distincte des auditeurs acoustiques du registre.

`paroles.preparer_parole` produit le flux courant et ses autorisations de réponse,
distinctes des paroles déjà prononcées. `faits` et `repondent` en sont des
projections ; les témoins ne sont plus déclarés silencieux. Le contrôle narratif
lit les autorisations et reconnaît une citation courante par auteur et mots
enregistrés (seules variantes typographiques admises). Sa restitution ne crée
aucune nouvelle émission. Le raccord de rendu conserve les répliques moteur,
dans leur ordre et une fois, même si Luna les omet ou si le repli est utilisé.
L'écoute distante référence la même émission. La projection publique retire les
auditeurs cachés et les paramètres privés de réception ; le nom d'un auteur vu
mais inconnu n'est pas publié avec son attribution.

Les archives 86/87 ont été copiées du laptop sur le PC fixe pendant le lot.
La contradiction est au **deuxième tour**, indice 1 du fichier (galerie de ronde),
après le premier tour sur la conduite basse. Extraction gzip portable et SHA
original dans `tests/data/emissions-320-86-87.json.gz`. Rejeu des deux tours avec
propositions, dialogues et audits originaux, sans réseau : le silence reste
refusé ; les trois citations suivantes sont admises comme restitutions.
**Gorm seul reste répondant**, Aubin et Ilse gardent leurs émissions de dispute ;
aucun doublon dans la sauvegarde. Monde, texte enregistré, scène et rendu
rechargés sont contrôlés. Autre dispute Ilse/Aubin au beffroi, écoute depuis une
autre salle, inconscients, répétition des mêmes mots, migration et auteurs
inconnus complètent les dix nouveaux tests.

Mesures de développement : une passe de **38/38** tests puis une passe pivot
de **29/29** (recouvrement, pas de cumul). Les **dix nouveaux tests sont verts**,
36,279 s, y compris le rejeu des archives 86/87. La suite ciblée finale reprend tous
les fichiers portés vers l'accès commun et les voisins directs, deux travailleurs
réduits au maximum, sans suite complète. Empreintes Relais/crue, 2 h × quatre
graines : référence `0fcc99e` réutilisée depuis le cache, seules nuits manquantes
calculées puis rangées. Les empreintes brutes restent conservées. Le schéma
ajoute le registre et les liens `bruits[].emission` : une seconde empreinte
explicitement privée de ces deux ajouts contrôle l'identité du reste de l'état,
de la chronique et des mesures ; elle n'est pas présentée comme identité brute.
Luna : une seule passe de `avis-joueur` et `echanges`, référence historique
relue dans l'archive `c9459ce`, aucun appel de référence relancé. Résultats finaux
et temps attendus dans les bruts, pas encore déclarés validés.

Limites : aucun portage G16–G19 ; contrôles transitoires conservés. Les paroles
indirectes restent marquées discours rapporté, sans citation historique exacte
inventée. Les anciennes sauvegardes ne permettent pas de reconstituer l'ordre
intra-tour perdu. La preuve sur nuits est bornée aux huit paires. Aucun
recouvrement avec les fichiers signalés pour U-P 319 : `moteur.py`, `rendu.py`
et `jeu.py` inchangés. Aucune nouvelle mécanique sociale.
