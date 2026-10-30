# Lot 351 — G18, avis parlés

Branche `codex-g18-avis`, **terminée, non fusionnée**, base `integration`
**`59e65f81`**, code validé **`b0c0413c`**. Aucun calcul actif ; aucune suite
complète ni campagne longue lancée.

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

**Tests : 89/89 verts, 12 fichiers distincts.** Sept nouveaux tests (161,147 s) : avis positif et négatif,
deux lieux, doute sans adoption, avis contraire et dispute, PNJ entendus,
composition avec information, propos résiduel audité, omission/altération/
double publication refusées. Les parcours console vérifient monde, sources,
mots entendus, conversation, scène et rendu après recharge, sans appel de
rédaction ou d'audit de ces répliques. G16 (7) et disputes (6) verts sur
la première passe, résultats conservés. Vérification finale : **69/69 tests,
neuf fichiers, 629,681 s**, dont avis joueur, émissions, contenus de parole,
avis réels/redits/menace, compréhension, consentement et comptes parlés.
Zéro échec, erreur ou ignoré ; deux travailleurs réduits au plus.
Les tests d'avis anciens confirment désormais l'aperçu par « tenter » ; les
oracles G15 lisent les préparations réelles au lieu d'attendre l'appel narratif
retiré. Aucun oracle mécanique n'est retiré.

**Empreintes : 8/8 paires identiques**, chronique, mesures et état final
complet, sans plantage : 2 h crue/Relais × graines 1985, 7, 42, 2024. Référence
exacte `59e65f81`, pour isoler G18 des changements d'intégration hérités depuis
`main` ; huit références manquantes calculées une fois et rangées en cache.
Avis non justifiés : zéro ; sept avis à expliquer inchangés, sans prétendre
les certifier bénins. Aucune comparaison de vitesse revendiquée.

**Luna, une seule passe.** `avis-joueur` : trois avis typés sur trois, six
appels (compilation et fidélité), zéro rédaction/audit narratif, repli, refus
ou erreur de recharge. Le script original s'arrête aux aperçus U-C ; ses
réponses archivées sont confirmées hors réseau sur copies indépendantes du
même état initial, sans deuxième passe Luna : **3/3 exécutées**, dont une
dispute et une adresse à tous. Chaque rejeu ne consomme que ses deux réponses
archivées (compilation/fidélité), sans nouvel appel réseau ni audit narratif.
Mots publiés présents dans les émissions ; crue inchangée, monde, scène et
rendu identiques après recharge (`rejeu-luna.json`).
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
Bilan final **`fin-cloture.json`, `ok=true`**, terminé le 2026-10-30 à
03:22:29 +01:00 ; `voisins.json`, `nouveaux.json`, `premiers.json`,
`empreintes.json` et `rejeu-luna.json` conservent les preuves. Les échecs du
premier passage des anciens harnais restent archivés, corrigés et rejoués.
Code et clôture documentaire poussés vers origin ; validation du lot achevée.
