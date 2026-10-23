# Rapport Codex 18 — code des noms lisible

Branche `codex-noms-lisibles`, non fusionnée, issue de `main` **276524c** via le commit
de tâche `27894ea`. Worktree : `tmp-worktrees/codex-noms-lisibles`.
Aucun appel à Luna ni à un autre modèle ; aucune sauvegarde utilisateur modifiée.

## Réécriture et règles conservées

Dans `donjon/noms.py` :

- `_variantes_nom` rassemble les trois variantes historiques du nom, dans leur ordre de
  longueur décroissante, et leurs motifs à frontières de mot insensibles à la casse.
- `_numero` retrouve le numéro enregistré ou calcule le rang trié après les numéros existants,
  aussi bien pour une personne que pour un élément.
- `_nom_reel` retrouve le nom du défunt pour une dépouille.
- `installer` enregistre les références dans l'ordre des identifiants et distingue les
  désignations visuelles homonymes par leur suffixe historique.
- `apparence` extrait la même proposition du portrait et choisit explicitement son article.
- `connait` distingue le nom appris ou déclaré du simple fait de percevoir.
- `apprendre` ajoute une seule fois le nom à la mémoire de l'auditeur.
- `designation` calcule la référence opaque du corps sans modifier la mémoire.
- `resoudre` cherche d'abord la désignation d'un corps perçu, puis celle d'un élément désignable.
- `_designation_texte` choisit la désignation d'un inconnu selon ce que l'observateur en sait.
- `_complement_defunt` transforme l'article de cette désignation pour le complément du corps.
- `_remplacer_noms` applique les substitutions dans le même ordre des personnes et des variantes,
  avec les mêmes majuscules et la même élision pour les dépouilles.
- `_motif_citations` protège les citations et les appellations des voix effectivement entendues.
- `texte` applique les substitutions seulement aux morceaux qui ne sont pas protégés.
- `_elements` suit les parents jusqu'à une personne, en arrêtant les cycles d'imbrication.
- `reference` masque l'identifiant d'une personne inconnue et ceux de ses éléments associés.
- `_garde_citations` porte la liste des champs et les conditions qui conservent les mots cités.
- `public` projette les clés et les valeurs dans le même ordre, masque les alias privés et
  conserve les deux listes nominales réservées aux paroles.
- `verifier_references` collecte les mots fournis et contrôle séparément chaque champ de
  référence, avec les mêmes exceptions nominales et les mêmes refus et `attendu`.
- `references` décode les seuls champs de référence, en conservant l'ancrage littéral d'une parole.
- `presenter` exige toujours la présentation littérale dans les mots prononcés avant de la relier.
- `_designation_valide` décompose les conditions historiques de forme d'une désignation persistante.
- `verifier` contrôle séparément la mémoire nominale, les désignations et l'unicité des numéros,
  avec les mêmes messages d'assertion.

Le cache borné de `_variantes_nom` garde uniquement des chaînes et des expressions régulières,
jamais un monde ou une connaissance ; il évite de repayer l'extraction commune à chaque champ.
Les dépendances circulaires gardent leurs imports locaux. Aucun nouveau champ persistant,
type de proposition, règle d'apprentissage ou consigne au MJ.

Dans les quatre autres fichiers, les retouches sont limitées aux fonctions nominales et aux
blocs ajoutés pour les noms ou la parole de la tâche 8 :

| Fichier / fonction | Règle conservée |
|---|---|
| `voix.se_nommer` | Une identité revendiquée reste pesée d'après les connaissances de l'auditeur ; seules la mise en forme et les conditions multilignes changent. |
| `voix.designation` | Un corps vu sans nom et une voix reconnue sans nom gardent leurs références distinctes. |
| `voix.reel` | Chaque préfixe public est décodé dans le même ordre, avec les dépouilles parmi les personnes. |
| `voix.nom_pour_joueur` | Le nom visuel et l'appellation de voix gardent leur contrat, avec les imports de noms regroupés. |
| `paroles.noms_pour_repliques` | Le locuteur peut prononcer seulement les appellations qu'il connaît, dans l'ordre d'origine. |
| `paroles._personnage` | Une appellation entendue désigne sa voix et ne révèle pas le vrai corps qui porte ce nom. |
| `paroles.prevue` | Les contraintes et les choix d'audience sont construits explicitement dans le même ordre de champs. |
| `paroles.mots_dits` | Les mots imposés ou ceux d'une question directe restent littéraux. |
| `paroles._nom_dit` | Le nom revendiqué peut être prononcé sans connaître son porteur. |
| `paroles.nom_dans` | La présentation est cherchée dans les mots, avec les mêmes essais de deux puis d'un mot. |
| `paroles.verifier_nom` | Le contenu nominal suit les mots prononcés, à la même place dans le contenu et avec les mêmes refus. |
| `narration.hors_paroles_etablies` | Seule la citation unique auditée à cet emplacement ou une citation historique autonome est exemptée. |
| `narration.voix_inconnues` | Les contrôles du corps, de l'appellation de voix et de la réplique sont exécutés dans le même ordre. |
| `narration._nom_court` | Les refus citent le même nom littéral. |
| `narration._noms_non_appris_recit` | Le récit ne nomme pas un corps dont le joueur n'a pas appris le nom. |
| `narration._noms_voix_recit` | Une appellation de voix ne devient pas une étiquette de corps dans le récit. |
| `narration._noms_repliques` | Une réplique ne nomme que les personnes connues du locuteur ou établies par l'échange. |
| `MJ._verifier_fidelite_parole` | Le bloc extrait de `_echanger_prepare` soumet la même parole à audience libre à la même contre-revue avant enregistrement. |
| `MJ._echanger` | Le retrait des noms privés pendant l'interprétation garde ses conditions ; seule sa mise en forme change. |

La clarification nominale et les autres voies de ces fichiers restent intactes.

## Preuves hors modèle

`tools/comparer_noms.py` charge le même corpus sous chacun des deux arbres, dans des
interpréteurs séparés (`PYTHONHASHSEED=0`). Il capture les arguments réels de `MJ._appeler`
avant tout fournisseur, pour l'interprétation et pour la narration finale : instructions,
entrée complète et schéma. Les sockets sortantes sont interdites pendant cette extraction.
Il compare également les signatures publiques, les constantes, `noms.public`, toutes les
références, leur décodage, les refus avec leur `attendu`, les audits nominaux avec et sans
répliques, la clarification, la scène web, la carte, le regard et le bilan déterministes,
ainsi que l'état complet, avant et après sauvegarde/rechargement. Les JSON sont comparés
comme octets UTF-8, sans tri des clés : l'ordre des champs est donc contrôlé aussi.

Les sept cas construits sont les deux dépouilles (nom connu ou inconnu, sur la scène réelle
du banc `depouille`), les deux appellations de voix (`se_dit`, `appelee`), l'élément porté par
un inconnu, les deux désignations visuelles homonymes, et les citations contenant des noms.
Les textes exercés dans tous les cas contiennent aussi citations, appellation et complément
du défunt ; le rendu est comparé pour le joueur et chaque observateur PNJ vivant.

Commandes depuis le worktree (interpréteur du dépôt principal) :

```powershell
C:/Users/msics/donjon/.venv/Scripts/python.exe tools/comparer_noms.py --reference ../noms-lisibles-reference
C:/Users/msics/donjon/.venv/Scripts/python.exe tools/tests.py --processus 3 --sortie artifacts/noms-suite-finale.json
C:/Users/msics/donjon/.venv/Scripts/python.exe tools/comparer_bancs.py --reference 276524c --empreintes --heures 2 --scenarios relais mine auberge crue --processus 3 --sortie artifacts/noms-bancs-2h.json
C:/Users/msics/donjon/.venv/Scripts/python.exe tools/comparer_bancs.py --reference 276524c --empreintes --heures 8 --scenarios relais mine auberge crue --processus 3 --sortie artifacts/noms-bancs-8h.json
```

Le worktree de référence est créé depuis le dépôt principal par
`git worktree add --detach tmp-worktrees/noms-lisibles-reference 276524c` et supprimé après
validation. Les bancs sont joués successivement, référence puis branche, 2 h puis 8 h,
avec les graines par défaut **1985, 7, 42, 2024** et au plus **trois processus**.
Les **16 paires de nuits à 2 h** et les **16 paires à 8 h** sont identiques pour la chronique,
les mesures et l'état final complet ; aucun plantage, aucune divergence.

**Identité finale : 53 mondes** (32 départs de banc, 14 captures, sept cas construits),
**106 états avant/après recharge et 212 requêtes MJ**, plus le contrôle du contrat public.
Les deux fichiers sont identiques : **18 376 770 octets**, SHA-256
`630212d12dd6062dee6161eb220801e25baa730e0e0f886ddad9fcd7f153060a`.
Manifestes, corpus complets et temps : `artifacts/noms-lisibles/{rapport.json,avant/,apres/}`.

**Suite complète finale : 1 508 tests, quatre ignorés, aucun échec ni erreur**, en
**257,451 s**, trois processus à priorité réduite (`artifacts/noms-suite-finale.json`).
La première passe complète était également verte : 1 508 tests, quatre ignorés, 290,824 s ;
la passe finale couvre les dernières retouches de lecture sur les sources figées.
`git diff --check` ne signale rien.

**Coût des fonctions**, en secondes CPU médianes de neuf lots, après la suite et les bancs,
référence puis branche, à priorité réduite sur le poste partagé :

| Fonction | 276524c | Branche | Écart |
|---|---:|---:|---:|
| `noms.public` | 4,312500 | 1,625000 | −62,32 % |
| `noms.texte` | 4,625000 | 4,546875 | −1,69 % |

Chaque lot appelle `public` dix fois par contexte (530 appels) et `texte` dix fois par
texte, avec et sans protection des citations (1 060 appels). Le chargement, les captures
et les rendus sont hors du chronométrage. Les contextes et textes mesurés sont les mêmes
dans les deux arbres ; le cache de motifs est chaud dans les lots répétés. Les deux coûts
restent sous le plafond de +5 %. Ces mesures ne mesurent pas le coût d'un appel au modèle.

Les bancs d'identité et leurs empreintes sont dans `artifacts/noms-bancs-{2h,8h}.json`.
Les campagnes de 2 h puis de 8 h ont été exécutées l'une après l'autre ; aucune suite ni
autre campagne de ce lot n'a été lancée en parallèle avec ces bancs. Les temps CPU cumulés
des 16 nuits de 8 h sont 233,23 s puis 232,80 s, sans changement des empreintes.

## Défauts et limites

Aucun nouveau défaut fonctionnel identifié pendant cette réécriture ; aucun correctif de
comportement ni test `expectedFailure` ajouté. Les limites sémantiques documentées par les
tâches 2 et 8 restent présentes : ce lot n'en revendique aucune résolution.

`tests/data/scenes` n'existe pas sur cette base. Le comparateur prend tous les départs de
`tests/data/bancs` et toutes les captures de monde JSON ou JSON gzip réellement présentes
sous `tests/data`, en plus des cas construits. Cette preuve porte sur ces états et sur les
nuits indiquées, pas sur toute histoire possible ni sur une réponse probabiliste de Luna.

Pyflakes 4.0.3 est installé seulement dans `artifacts/qa`, sans modifier le `.venv` partagé.
Il ne trouve aucun nom indéfini dans les fichiers touchés. Ses cinq imports inutilisés
(`paroles.croire`, `paroles.percevoir`, `paroles._place`, `mj.lire_flux`, `mj.designer`) sont
déjà signalés sur `276524c` et restent hors périmètre.

Les premiers essais sous bac à sable ont échoué sur les permissions Windows des fichiers
temporaires, avant toute comparaison ou suite exploitable ; les exécutions retenues ont été
relancées avec les permissions nécessaires. Aucun de ces échecs d'environnement ne compte
comme une validation.
