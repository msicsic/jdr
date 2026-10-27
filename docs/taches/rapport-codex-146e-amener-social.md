# Lot 146 e — sous-buts sociaux d'amener

Branche `codex-amener-social-e`, **non fusionnée**, base `116be91`.
Livraison des sous-buts sociaux ; **critère global de la crue non atteint**.

**Invariant et code.** Un projet portant sur la position d'autrui passe par une
parole et un engagement autonome, jamais par un transport implicite.
`agendas._amener` choisit les destinataires non arrivés selon les routes crues,
avec proximité spatiale locale et identifiant pour départager. Il avertit de la
menace du lieu quitté, sans répéter un avis transmis, puis emploie le `confier`
commun. Les refus gardent leur cause ; le sommeil n'est réessayé qu'après une
nouvelle croyance. Le porteur marche lui-même vers la destination et y attend
les engagements acceptés ; une inspection locale, puis la perception ordinaire,
permettent de constater les arrivées. La routine ne reprend pas entre deux
attentes du même engagement, ce qui supprime les navettes exploratoires de Gorm.
`planification.gestes` propose un terminal de parole, avec approche et coût
communs ; il ne prédit ni l'accord ni la marche d'autrui. L'exécution conserve
le contrôle commun de l'ouïe. Les transitions restent privées jusqu'à la sortie
du choix (146 b). La crue déclare l'évacuation d'Ilse et Brune à la galerie.

**Défaut commun isolé.** Une annonce d'abandon conservait l'aide attendue.
`echanges.retenir_abandon` retire maintenant seulement l'aide du même auteur
portant exactement la même condition, au moment où l'abandon est reçu. Avant
l'annonce, aucune connaissance à distance. Réinjection de la fonction de
`116be91` : les deux scènes Ilse/galerie et Brune/échoppe échouent ; correctif :
refus conservé, aide supprimée, monde et rendu identiques après recharge.

**Vérification.** Les tests sociaux couvrent demande sans déplacement immédiat,
marche autonome, avis entendu avant demande, sommeil motivé, essai sur croyance
nouvelle, réveil avec recours retrouvé, désespoir prioritaire et publication
différée. Deux scènes collectives 2024/42, route ouverte et lanterne portée,
amènent Ilse puis Brune à la galerie : état et rendu après recharge, agenda
atteint, égalité du laps continu et découpé. Les tests de fin et de coupure
restent couverts. Suite complète unique : **2 212 tests, 252 fichiers,
1 084,053 s, zéro erreur/ignoré, sept échecs** : deux MiMo historiques
`6 != 5` et cinq assertions de scènes eau/services/marchés qui déclenchaient
désormais aussi l'évacuation. Ces scènes isolent explicitement leur mécanique
en désactivant l'agenda du scénario, sans changer leurs assertions. Reprise
ciblée finale : **49 tests verts en 29,706 s** ; aucune seconde suite complète.

Douze empreintes 2 h Relais/mine/auberge × quatre graines **identiques** à
`main` `812ebe5` : chronique, mesures, état complet ; références toutes relues.
Crue 4 h × quatre graines : **aucun arrêt ni usurpation** ; agenda atteint
sur 7/37 min et 42/36 min. Galerie à 4 h **3/8 → 2/8** : les personnes peuvent
repartir après avoir atteint l'objectif. Eau **128,75 → 92,5 min**, maximum
horaire de passages **13,25 → 15,5** en moyenne. Deux répétitions nouvelles
sur 1985 : Brune allume dix fois et éteint neuf fois sa torche ; eau longue
de Brune sur 2024 conservée. Aucun gain de temps revendiqué : références en
cache, charge différente. VERIFIER et spatial 0,2 sur crue fixe 42/2024 × 2 h :
sans arrêt (85,94 et 49,43 s) ; sauvegarde complète et rendu rechargés contrôlés.

**Limites.** L'évacuation universelle, le maintien à la galerie et l'absence de
toute boucle ne sont pas garantis. Les refus de persuasion/rancune de 1985 et
2024 sont respectés ; aucun succès forcé. Le test collectif isole le social
avec route ouverte et lumière : il ne prouve pas une coopération générale pour
les portes. La proximité reste estimée entre salles et géométrique sur place ;
la parole exige actuellement une approche de contact, plus stricte que la seule
portée vocale. L'avis disponible concerne la menace de l'eau, sans préférence
générale entre lieux ni lecture de l'esprit du destinataire. Les seules
relations nouvelles ne réveillent pas encore un agenda. Une inspection sans
arrivée visible attend ensuite la perception ordinaire et la durée commune
des engagements. Pas de Luna, fichier MJ réservé, sauvegarde utilisateur ou
`main` modifiés. Deux calculs au plus, priorité réduite. Aucune clé Git de
signature configurée : livraison non signée, branche seule poussée.

Bruts exclusivement : `C:\Users\msics\donjon\artifacts\amener-146e\`
(`crue-livree.json`, `empreintes.json`, `verifier-*-monde.json`, résultats des
tests et preuve sur la base ; premiers bancs exploratoires conservés à part).
