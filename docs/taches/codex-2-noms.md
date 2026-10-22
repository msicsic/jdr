# Tâche Codex 2 : on ne connaît un nom qu'en l'entendant

Décision de l'utilisateur (2026-10-22, `docs/etat-dev.md`, « Décisions prises le 2026-10-22 ») :
un nom ne s'apprend qu'en entendant la personne se nommer ou quelqu'un la nommer, **pas en la
voyant, même de près**. Tant qu'on ne connaît pas son nom, on la désigne par ce qu'on voit d'elle
(« un homme trapu », « une femme en manteau sombre »). Seuls les liens que le scénario déclare
d'avance (des gens qui se connaissent déjà, un savoir du scénario) donnent le nom d'office. Même
règle pour le joueur et pour les PNJ.

## Contexte à lire
`AGENTS.md` (contrat du MJ : aucune fuite d'entité non perçue ; une affirmation mécanique doit être
fondée), `docs/plan-ouie.md` (sections « Les voix », « Nommer, attendre, héler », « Les voix
inconnues », « La suite des voix », « Corrections de la parole »), `docs/contrat-mj.md`.
Aujourd'hui :
- le joueur connaît un personnage qu'il a vu (`data["personnages_vus"]`, `Monde.identifier`), dont il
  connaît la voix, ou dont une voix s'est donné le nom (`paroles.identites`, `_connu_du_joueur`) ;
- la scène (`donjon/scene.py`, carte, page web, terminal) affiche le nom de tout personnage vu ;
- les PNJ retiennent les noms entendus (`voix.apprendre_nom`, champ `noms` de l'esprit,
  `voix.connait_nom`) ; une réplique ne nomme que qui son locuteur connaît (branche `relances-luna`) ;
- une voix inconnue est désignée au MJ par `voix_<n>` (« une voix qui se dit Brune »), sans
  identifiant ni traits.

## À faire (règles communes, jamais par personnage ou par scénario)
1. **Connaître un nom** : par le nom entendu (se nommer, être nommé par une voix ou une parole que
   l'on saisit, une rumeur qui nomme quelqu'un qu'on peut relier), ou par un lien déclaré du
   scénario. Voir quelqu'un fait connaître son **apparence** (on le reconnaît de vue ensuite), pas
   son nom. Garde ce qui existe pour la voix (connaître une voix ≠ connaître un nom).
2. **Désigner un inconnu** : une désignation stable par l'apparence, tirée des données du
   personnage (portrait, `description_visuelle`, genre, âge apparent), courte et unique dans la
   scène (« l'homme trapu », « la vieille femme ») ; le MJ reçoit ces personnes comme
   `personne_<n>` avec cette désignation, sans identifiant ni nom (comme `voix_<n>`). Le joueur peut
   les viser par cette désignation (« je parle à l'homme trapu », « je donne la cloche à la vieille
   femme ») ; la carte, la page web et le terminal l'affichent à la place du nom.
3. **Ce que dit le MJ** : le récit et les répliques ne nomment pas quelqu'un dont le joueur ignore le
   nom (contrôle déterministe dans `narration`, comme pour les voix inconnues) ; une réplique d'un PNJ
   peut nommer qui ce PNJ connaît, et alors le joueur apprend ce nom s'il en saisit les mots.
4. **Les PNJ** suivent la même règle : un PNJ qui n'a jamais entendu le nom de Corvus le désigne
   (« l'étranger », « le voyageur »), et l'apprend quand Corvus se nomme ou qu'on le nomme devant lui.
5. Les scénarios : déclare les liens existants (les PNJ du Relais se connaissent ; à l'auberge,
   Odile connaît ses gens ; etc.) en données. Le joueur commence sans connaître personne, sauf ce
   que l'introduction du scénario lui fait savoir (relis `scenario["objectif"]`, l'introduction, les
   savoirs du joueur).

## Vérifications
- Tests après rechargement, sur le cas réel (Corvus arrive au Relais : il voit Gorm, ne connaît pas
  son nom ; Gorm se nomme ou Aubin l'appelle « Gorm » : il l'apprend) et sur un autre cas de même
  nature (à l'auberge, un PNJ apprend le nom de Corvus) ; ce que voit le joueur (carte, terminal,
  page web) après rechargement.
- Suite complète verte (en priorité réduite).
- Luna (`SEUIL_AUTH=C:\Users\msics\donjon\.seuil-auth`), sur des copies ou des bancs, jamais sur
  `sauvegardes\` : 2 à 3 parties courtes (s'adresser à « l'homme trapu », apprendre un nom, demander
  « comment t'appelles-tu ? ») ; vérifie que Luna ne nomme jamais quelqu'un d'inconnu et que les
  saisies passent par le moteur. Puis les 4 bancs de référence (`tools/banc_multi.py`, relais,
  crypte, atelier, échanges), 2 passes, `main` puis branche : appels et secondes par tour MJ,
  relances, refus, replis.
- Bancs moteur 8 h (Relais 8 graines, auberge 4) : aucune usurpation ni violation.
- Docs : `docs/plan-ouie.md` (nouvelle section), `docs/contrat-mj.md`, `docs/mecaniques.md` (règles du
  joueur), `docs/etat-dev.md` (« Branche `codex-noms`, non fusionnée », compte de tests).

## Rapport
Dans `docs/taches/rapport-codex-2-noms.md` : règles, fonctions, cas vérifiés, mesures Luna avant →
après, limites.
