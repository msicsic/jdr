# Tâche Codex 338 : tout recours admissible a un coût, et son moyen tient jusqu'au constat

Premier correctif proposé par le diagnostic 317. Lis `AGENTS.md`, `docs/etat-dev.md`, puis le
[rapport 317](rapport-codex-317-boucles-progression.md) (cause « Gorm ») et les rapports 260 (faire ou confier) et
309 (rendu de l'agenda `amener`).

## Constat
Crue 3, 12 h, départ tiré, joueur passif en `chambre_cloche` : Gorm fait encore **298 passages par heure** sur
l'intégration. À son arrivée, `agendas._amener` propose `inspecter chambre_cloche` pour constater l'aide attendue,
sans remplir `mesure`. `agendas.choisir_mandataire` valorise alors le recours propre à l'infini et choisit une
délégation. Hors du rendez-vous, le retour vers la galerie redevient le moyen propre le moins coûteux, et
`deliberation.choisir` remplace le suffixe avant qu'il soit accompli. Le circuit repart sans inspection ni constat
conservé.

## L'invariant
**Tout recours admissible porte un coût mesuré par le devis commun, inspection et attente comprises.** Aucun recours
admissible ne vaut l'infini, et l'infini reste réservé à l'impossible. Un moyen adopté tient jusqu'à son constat
utile ou jusqu'à une entrée nouvelle pertinente. Ni un simple retour au même lieu, ni une variation de coût due au
seul déplacement ne le remplacent. La reprise se fait sur un événement, sans délai arbitraire et sans interdiction de
revisiter un lieu.

## Contraintes de conception
- Contrat commun du devis (`planification`, `agendas.choisir_mandataire`, `deliberation.choisir`) : pas de cas
  propre à Gorm, à la crue ou à l'agenda `amener`.
- L'hystérésis existante (`INERTIE`) n'est pas changée pour masquer la boucle.
- Toute lecture nouvelle de la recherche entre dans `_entrees`. Ce qui doit survivre à une recharge va dans
  l'esprit.
- Le second correctif du 317 (contact obtenu transmis à la tentative préparée, côté Aubin et Sève) est hors lot :
  il recoupe le lot 313.

## Vérification
- Capture du 317 à 160 min (crue 3) : Gorm constate l'aide puis cesse son circuit. Autre cas de même nature : un
  autre agenda dont un recours est une inspection ou une attente, dans un autre scénario. Contrôle après rechargement
  du monde, du rendu et de la scène, avec le même laps entier ou découpé.
- Tests ciblés des fichiers touchés ; pas de suite complète.
- Banc rapide 4 h × cinq scénarios × quatre graines, références lues du cache : aucune hausse des suspects 219 par
  nuit, zéro plantage ou usurpation. Rejoue aussi la nuit crue 3 de 12 h : maximum de passages par heure de Gorm.
- Ni Luna ni suite complète.

## Contraintes
**Poste : le laptop.** Deux processus au plus, priorité réduite. Banc détaché, avec un fichier de fin écrit en
dernier.

## Livraison
- Branche `codex-recours-sans-cout`, base `integration`, poussée vers origin (https://github.com/msicsic/jdr.git,
  dépôt de l'utilisateur ; la poussée est autorisée).
- Rapport d'une page `docs/taches/rapport-codex-338-recours-sans-cout.md`, entrée « non fusionnée » dans
  `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\recours-338\`.
- Termine par `LOT TERMINÉ`, `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
