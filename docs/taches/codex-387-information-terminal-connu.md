# Tâche Codex 387 : les tests du terminal d'information après le catalogue connu

Petit lot de correction né de deux fusions sans fichier commun : U-T social information (lot 369, terminal de l'acte
d'information) et le catalogue des choix limité à ce que Corvus connaît (lot 365). Le lot 386 a relevé sur la base
`cbecf8c8` **cinq erreurs** dans `tests/test_information_terminal.py` (dont
`FormulaireTests.test_projection_figee_choix_explicites_et_limite_objet`) : `parcours` cherche le choix `bois` dans un
formulaire qui ne le propose plus, car la fixture `ressources` ne rend pas le bois connu de Corvus (`StopIteration`).
Bruts : `C:\Users\msics\donjon\artifacts\um-social-avis-386\heritage-base.json` (laptop).

Lis `AGENTS.md`, `docs/etat-dev.md` (court), les rapports 365 et 369 (`docs/taches/rapport-codex-365-*.md`,
`rapport-codex-369-*.md`).

## Invariant (un seul)
**Le terminal d'information ne propose que ce que Corvus connaît (contrat du 365), et ses tests le vérifient sur des
scènes où cette connaissance est établie explicitement.** Attribue chaque erreur : prémisse de test devenue fausse (le
bois n'était connu qu'à tort, par l'admission lexicale retirée au 365) ou défaut réel du terminal (un sujet connu
absent du formulaire). Corrige la prémisse par une connaissance déclarée de la scène, sans affaiblir aucune assertion ;
corrige le code seulement si un sujet réellement connu manque, dans le contrat commun web/terminal (même catalogue
que U-M information). Ajoute la contre-épreuve : le même formulaire ne propose pas le bois quand il est inconnu.

## Vérification
`test_information_terminal`, `test_information_publique`, `test_catalogue_connu` (ou le fichier du 365), le test web
d'information, puis recharge et parité web/terminal sur le cas réel et un autre sujet. Pas d'empreintes si aucun
code du jeu ne change ; sinon empreintes 2 h Relais, quatre graines. Pas de suite complète (une tourne déjà sur
`663d1308`), ni Luna.

## Contraintes
**Poste : le laptop.** Lots en cours : 374 (position crue), 375 (rouges de la suite e0826ef), 380 (U-M social comptes,
`web/page.html`), 381 (A2 passage) ; pendant S1, n'ajoute aucun registre d'esprit. Deux processus au plus, priorité
réduite. La poussée de ta branche vers origin (https://github.com/msicsic/jdr.git, dépôt de l'utilisateur) est autorisée.

## Livraison
- Branche `codex-information-terminal-connu`, base `integration`, poussée vers origin.
- Rapport d'une page `docs/taches/rapport-codex-387-information-terminal-connu.md` ; entrée « non fusionnée » de 8
  lignes au plus dans `docs/etat-dev.md` (puce « - » qui nomme la branche entre accents graves).
- Bruts dans `C:\Users\msics\donjon\artifacts\information-terminal-387\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier de fin>` ou `QUESTION : …`.
