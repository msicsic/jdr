# Lot 146 e — amener, sous-buts sociaux et reprise avant fusion

Branche `codex-amener-social-e`, **non fusionnée**, base `116be91`, première
livraison `eef4925`. **Évacuation universelle non acquise ; boucle de torche corrigée.**

**Contrat livré.** `agendas._amener` choisit les destinataires non arrivés sur
leurs positions crues, proximité locale puis identifiant ; avis de menace non
répété, `confier` commun, refus retenu selon sa cause, sommeil/réessai sur
croyance nouvelle. Le porteur marche lui-même et attend les engagements
acceptés ; inspection locale puis perception ordinaire constatent l'arrivée.
Aucun transport implicite, accord ou arrivée connus à distance. Le terminal de
parole du graphe paie approche et coût communs ; l'exécution valide l'ouïe.
Publication différée du choix conservée (146 b). La crue déclare l'évacuation
d'Ilse et Brune à la galerie. L'annonce d'abandon invalide désormais seulement
l'aide du même auteur et de même condition (`echanges.retenir_abandon`) ;
deux scènes rechargées échouent avec la fonction de `116be91`.

**Validation initiale.** Scènes collectives 2024/42, route ouverte et lanterne :
Ilse puis Brune, agenda atteint, monde/rendu rechargés, laps continu/découpé
identiques. Suite unique : **2 212 tests, 252 fichiers, 1 084,053 s**, zéro
erreur/ignoré, sept échecs : deux MiMo historiques `6 != 5`, cinq assertions
de scènes eau/services/marchés perturbées par le nouvel agenda. Scènes isolées
explicitement, assertions conservées : **49 repris verts**, 29,706 s.
**12/12 empreintes** Relais/mine/auberge × quatre graines identiques à `main`
`812ebe5`, références relues. VERIFIER + spatial 0,2, crue fixe 42/2024 × 2 h :
sans arrêt, monde/rendu rechargés identiques (85,94/49,43 s).

**Boucle 1985, preuve et invariant.** Même crue 4 h, départ tiré, joueur à la
galerie, rejouée séquentiellement sur `116be91` et `eef4925` : torche
allumée/éteinte **1/1 → 10/9**. Captures avant premier allumage (109/102 min),
sauvegardées puis rechargées. La répétition apparaît donc avec le lot dans cette
nuit ; sa trajectoire révèle un désaccord : le plan prévoit l'éclairage devant
la serrure, mais l'économie de combustible jugeait celui de la salle. Elle
éteignait ainsi la source nécessaire au crochetage, qui la rallumait.
`lumiere_devant_crue` partage maintenant l'observation de la cible et l'apport
des sources nouvellement posées entre `Vue.lumiere_devant` et `lumiere_utile`,
sans compter la source portée qu'on envisage d'éteindre. Aucune exception
d'objet, personne ou scénario.

La capture 102, dérivée en fixture comprimée, est rejouée jusqu'à 240 min ;
autre cas : Gorm/lanterne, serrure sombre et salle claire, crochetage exécuté,
état et rendu rechargés. Réinjection de la seule ancienne `lumiere_utile` :
**deux échecs**, dont dix allumages sur la capture. Correctif : **51 ciblés et
voisins verts**, 37,926 s. Contrat local de lecture : aucune nouvelle suite complète.

**Quatre crues corrigées.** Aucun arrêt/usurpation ni constat de répétition de
torche ; **4/3** allumages/extinctions sur 1985, plus de rafale 213–218.
États complets et mesures de **7/42/2024 identiques à `eef4925`**. Sur 1985,
conserver la lumière permet de poursuivre le crochetage : jets **19 → 25**,
gestes **164 → 148**, recherches **1 203 → 1 177** ; choix et échanges suivent
ce fil différent. Galerie finale, eau, passages horaires et usurpations restent
inchangés : **2/8**, **92,5 min**, **15,5/h**, **0** (référence `main` :
3/8, 128,75 min, 13,25/h, 0). Seule alerte conservée : eau longue 2024.
Deux agendas atteints, 7/37 min et 42/36 min ; les personnes peuvent ensuite repartir.

**Limites et livraison.** Refus 1985/2024 respectés ; pas de maintien imposé à
la galerie ni garantie générale d'absence de boucle. Préférence entre lieux
limitée à l'avis de menace de l'eau, approche actuelle au contact plutôt qu'à
la seule portée vocale, proximité estimée, réveil relationnel et coopération
aux portes non garantis. Pas de Luna, fichier MJ réservé, sauvegarde utilisateur
ou `main` modifiés. Deux calculs réduits au plus ; aucun temps caché comparé.
Aucune clé Git de signature configurée ; commits non signés, même branche poussée.

Bruts exclusivement `C:\Users\msics\donjon\artifacts\amener-146e\` :
`boucle-base*`, `boucle-branche*`, `preuve-boucle.log`, `tests-boucle-voisins.json`,
`crue-sans-boucle.json`, vérifications initiales. Copie détachée de la base supprimée.
