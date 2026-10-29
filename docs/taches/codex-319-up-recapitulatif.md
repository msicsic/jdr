# Tâche Codex 319 : U-P, le récapitulatif « Compris : … » du plan admis

Décision de l'utilisateur du 2026-10-29 : **U-P puis U-C sur la voie actuelle, puis G1 sous la forme A** du lot 318.
Lis `AGENTS.md` (contrat du MJ, « Fidélité de la saisie »), `docs/plan-refonte-mj.md` (ligne U-P),
`docs/conception-valeur-llm.md` (sections « Décisions déjà prises », table des lots ajoutés, paragraphe qui suit),
et `docs/conception-g1.md` (sections 3 et 6 : U-P développe les raccourcis et montre attente, cibles et termes).

## L'invariant
**Quand une saisie libre produit un plan admis, le moteur écrit une ligne « Compris : … » qui désigne exactement ce
plan : opérations et leur ordre, cibles et parties en références publiques, montants et quantités, conditions et
attentes (y compris celles qu'un raccourci contient), destinataires ou portée d'une parole.** Aucune clause n'est
omise pour tenir en une ligne ; plusieurs lignes valent mieux qu'un résumé qui cache une étape. La ligne est écrite
par le moteur, sans appel au modèle, à partir du plan typé et d'un sens des opérations défini une seule fois (pas un
dictionnaire de formulations du joueur).

Placement, selon la décision : pour un acte léger, la ligne suit l'exécution (ligne de résultat). Pour un acte lourd
ou irréversible, elle précède l'exécution : c'est la fiche `tenter/annuler` existante qui la porte. La classification
« lourd » selon les effets typés et le consentement appartiennent au lot suivant (U-C) ; ici, réutilise seulement la
fiche existante quand elle s'affiche déjà. Une action venue d'un clic ou d'un menu n'affiche pas de « Compris ».
Une question au MJ ou une faisabilité n'exécute rien et le dit.

## Ce qui ne change pas
Aucune revue, contre-revue ou audit retiré : U-P n'est pas une preuve de fidélité. Aucun changement de compilation, de
schéma ou de consignes de Luna. La ligne est enregistrée et sauvegardée avec le tour, avant affichage, comme tout
rendu moteur ; elle reste la même après recharge.

## Vérification
- Cas réels du corpus G1 (`C:\Users\msics\donjon\artifacts\g1-318\saisies.json`) rejoués avec MJ simulé, sans réseau :
  au moins une offre ou un paiement, un avis, une attente puis prise (vol avec attente), une séquence perche puis
  saut, une question au MJ sans exécution, une parole adressée. Pour chacun : la ligne attendue mot pour mot, le monde,
  le texte sauvegardé et le rendu après recharge ; console, TUI et web.
- Un plan périmé (cible disparue entre la compilation et l'exécution) : le moteur refuse publiquement et n'affiche
  pas un « Compris » trompeur.
- Clic et menu : aucune ligne « Compris ».
- Tests ciblés des fichiers touchés. Pas de Luna : aucun chemin du modèle ne change. Pas de suite complète ni de banc.

## Contraintes
**Poste : le laptop.** Deux processus au plus, priorité réduite. Le lot 307 (PC fixe) modifie le catalogue des gestes
publics et la liste du terminal : évite `gestes_publics.py` et `web/pont.py` sauf nécessité, et dis-le alors.

## Livraison
- Branche `codex-up-recapitulatif`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt
  de l'utilisateur : la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-319-up-recapitulatif.md`, entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\up-319\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
