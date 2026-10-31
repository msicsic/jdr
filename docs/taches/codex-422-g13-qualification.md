# Tâche Codex 422 : G13, qualifier une propriété inconnue avant de s'en servir

Lot de la refonte du MJ (`docs/plan-refonte-mj.md`, ligne G13 ; `docs/conception-valeur-llm.md`), après G12 (lot 421, fusionné : une invention admise existe avant manipulation). Quand le joueur veut se servir d'une propriété qu'aucun fait n'établit (la matière d'une planche, la longueur d'une perche, si une torche brûle sous la pluie), Luna peut la qualifier ; le moteur décide si elle est admise.

Lis `AGENTS.md` (contrat du MJ, « Interactif » : une propriété inventée que le moteur ne sait pas calculer passe une revue ciblée à son admission), `docs/etat-dev.md` (court), la ligne G13 du plan, `docs/plan-fabrication.md` (étapes 1 et 2, qualification des objets) et le rapport 421. Pour un lot ancien, cherche dans `docs/historique-lots.md` par mot-clé, sans le lire en entier.

## Invariant
**Une propriété inconnue est admise avant son premier usage, une seule fois, sans écraser ce qui est établi (masse, dimensions, matière déjà connue, état) : une qualification incompatible avec l'établi est refusée avec `attendu` ; admise, elle est enregistrée et sauvegardée, et l'intention du joueur reprend sans la redemander.** La revue ciblée porte sur l'admission, pas sur le récit ; aucun effet ni capacité non typé ; aucune exception de scénario.

Cas : deux matières (une planche dont la matière est qualifiée puis découpée, une ficelle qualifiée puis nouée), une incompatibilité refusée (une perche de fer qui ne pèse que 200 g), reprise sans répétition après recharge.

**Luna : une passe ciblée**, sur copies : `materiaux`, `atelier`, `assemblage`, `lots`. Mesure appels et secondes jusqu'à l'usage. Si la revue automatique bloque la passe, laisse la commande exacte dans les bruts.

## Contraintes
**Poste : le PC fixe.** Fichiers attendus : `donjon/mj.py`, `donjon/faits_locaux.py`, `donjon/coherence_physique.py`, `donjon/matiere.py` si nécessaire, tests. Lots en cours : 402 (vérification d'intégration, calcul seul), 419 (vérification de contact). Pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité réduite, calculs longs détachés : vérifie qu'ils vivent avant de rendre la main. La poussée de ta branche vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Vérification
Les méthodes ciblées vertes sans changer leurs assertions de sécurité (une adaptation seulement si le changement est
voulu et documenté, preuve citée) ; le cas réel et un autre de même nature après recharge et laps découpé ; tests
voisins verts. Empreintes 2 h, quatre graines, scénarios touchés et Relais, si le code du jeu change. Pas de suite
complète (le superviseur la relance), ni Luna hors de la passe demandée ci-dessus.

## Livraison
Branche `codex-g13-qualification`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur ;
poussée autorisée). Rapport d'une page `docs/taches/rapport-codex-422-g13-qualification.md` ; entrée « non fusionnée » de
8 lignes au plus dans `docs/etat-dev.md` (puce commençant par « - » qui nomme la branche entre accents graves). Bruts
dans `C:\Users\msics\donjon\artifacts\g13-qualification-422\`. Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>`
ou `QUESTION : …`.
