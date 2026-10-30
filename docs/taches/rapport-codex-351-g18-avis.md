# Lot 351 — G18, avis parlés

Branche `codex-g18-avis`, base `integration` **`59e65f81`**. Vérification ciblée
en cours ; aucune suite complète ni campagne longue lancée.

**Invariant.** Le moteur formule la réception d'un avis depuis son issue typée :
« Je retiens ton avis » ou « Je doute de ton avis », suivi du sujet annoncé
et de « selon toi ». Cette parole établit sa réception, jamais la vérité de la
menace. Les avis contraires, leur conviction, leur source et la dispute restent
ceux de la mécanique existante ; aucune règle sociale ni donnée de scénario
ne change.

**Contrat commun.** `paroles.preparer_parole` conserve l'issue de réception ;
`avis_parles.formuler` en tire les mots. `repliques_moteur` les compose avec
G16/G17, les inscrit dans G15 sur copie et les scelle pour la transaction,
la sauvegarde et le contrôle exact de publication. Les émissions sociales
d'avis déjà formulées suivent ce même contrôle, sans reformulation ni audit.
La projection publique conserve leur provenance moteur sans transporter leurs
paramètres privés. Une dispute fournit déjà ses paroles : elle ne donne plus
une seconde autorisation de réponse libre sur ce même contenu. Les autres
contenus, notamment les propos libres résiduels, gardent leurs contrôles.
Le consentement U-C et la revue de fidélité de la saisie sont conservés.

**Tests.** Sept nouveaux tests verts (161,147 s) : avis positif et négatif,
deux lieux, doute sans adoption, avis contraire et dispute, PNJ entendus,
composition avec information, propos résiduel audité, omission/altération/
double publication refusées. Les parcours console vérifient monde, sources,
mots entendus, conversation, scène et rendu après recharge, sans appel de
rédaction ou d'audit de ces répliques. G16 (7) et disputes (6) verts sur
la première passe. Avis joueur (12) et émissions (11) verts après portage des
harnais ; tests voisins en cours. Empreintes prévues : 2 h crue/Relais, quatre
graines, contre la base exacte `59e65f81` (cache réutilisé), pour isoler G18
des changements d'intégration déjà hérités depuis `main`.
Les tests d'avis anciens confirment désormais l'aperçu par « tenter » ; les
oracles G15 lisent les préparations réelles au lieu d'attendre l'appel narratif
retiré. Aucun oracle mécanique n'est retiré.

**Luna, une seule passe.** `avis-joueur` : trois avis typés sur trois, six
appels (compilation et fidélité), zéro rédaction/audit narratif, repli, refus
ou erreur de recharge. Le script original s'arrête aux aperçus U-C ; ses
réponses archivées sont confirmées hors réseau sur copies indépendantes du
même état initial, sans deuxième passe Luna (résultat à compléter).
`echanges` : dix appels, zéro repli ou erreur technique/recharge ; un refus
de fidélité sur une parole mixte et trois noms non reliés refusés localement.
Ce script ne démontre pas l'exécution d'un avis G18. Aucun script de dispute
Luna n'existe ; les épisodes sont couverts par les tests sans réseau.

**Limites et livraison.** Garantie sur les paroles typées admises, pas sur
toute la compréhension du français libre ; prédicat d'avis existant limité
à la menace d'eau. Aucun changement de `social.py`, des poids de sources,
de `page.html`, `agendas.py`, `echanges.py` ou `biens.py`. Fichiers communs
à surveiller à la fusion : `paroles.py`, `emissions.py`, `repliques_moteur.py`
et `etat-dev.md`. Bruts dans `C:/Users/msics/donjon/artifacts/g18-351/`.
Vérification restante détachée, deux travailleurs réduits au plus, fichier
de fin écrit en dernier : **`fin-cloture.json`**, à relire avant fusion.
Le superviseur doit reprendre ce lot pour intégrer ses résultats et clôturer
ce rapport ; la livraison n'est pas encore déclarée validée.
