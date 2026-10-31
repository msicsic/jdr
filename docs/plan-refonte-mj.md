# Refonte du MJ — feuille de route

29 octobre 2026. Suivi unique des lots par le superviseur. Le contrat cible est
dans [AGENTS.md](../AGENTS.md#contrat-du-mj). Le [contrat détaillé](contrat-mj.md)
décrit aussi les contrôles de transition. Les conceptions
[287, sections 9 et 10](conception-refonte-mj.md#9-plan-de-lots-un-invariant-et-30-à-45-minutes-chacun)
et [288, sections 7 et 8](conception-valeur-llm.md#7-révision-du-plan-g0g21)
donnent les contre-épreuves et les décisions. Les décisions du 29 octobre dans
[l'état du développement](etat-dev.md#décisions-prises-le-2026-10-29) priment
sur leurs anciennes questions. K0, K1, K2 et D0 sont décidés.

Chaque ligne est un lot de 30 à 45 minutes. Les chemins sont probables,
pas une autorisation d'étendre le périmètre. Sauf mention `docs/`, ils sont
relatifs à `donjon/`. Les tests concernés accompagnent chaque portage.
Les dépendances sont minimales ; l'ordre des groupes reste celui du 288 :

**G0 → G2/G4/U-D → G1/U-P/U-C → G5/G6/G7/G20 → premiers U-M/U-T →
G15 à G19 et menus sociaux → G12/G13 puis K0/K1/K2/D0 →
G14 et G8 à G11/U-A → G21.**

G3 accompagne G1 si le transport le nécessite. Le serveur local peut attendre.
G8 peut être construit et vérifié avant ses raccords. Aucune ambiance n'est
activée avant G9/G10/G11/U-A et le ciblage G14.
Le portage reprend `origin/prompt-simplifie`, sans fusion globale de la branche.
Luna reste `gpt-6-luna`. La comparaison de modèles reste désactivée.
Une famille non portée garde ses contrôles et ses interactions actuels.

Dans la colonne des mesures : **I** = interprétation ; **V** = vitesse perçue ;
**F** = invention à la volée ; **P** = richesse des interactions PNJ.
« Stable » demande de vérifier l'absence de régression sur cet axe.
Les mesures sont à faire dans les lots de jeu. G0 n'exécute aucune mesure de jeu.

| Lot | Invariant | Dépendances | Fichiers probables | Mesures I / V / F / P | État |
|---|---|---|---|---|---|
| G0 — contrat | Cible et transition sont distinctes dans les documents. | Décisions 287/288, contrat adopté | `docs/contrat-mj.md`, plans, état, rapport 290 | I : fidélité et consentement définis ; V : blocage/fond définis ; F : admission définie ; P : parole et vérité séparées. Lecture seule. | fusionné (290, e1ccee4) |
| G2 — validation et refus | Une proposition reste sur copie jusqu'à admission. Le refus public vient du moteur. | G0 | `mj.py`, `transactions.py`, `refus.py` | I : corrections récupérées, aucune exécution de question ; V : zéro explication Luna ; F : aucun ajout refusé conservé ; P : raisons sociales conservées. | fusionné (291, 6036d0e) |
| G4 — résultat public | Une exécution a un rendu complet après sauvegarde, sans reformulation. | G2 | `jeu.py`, `narration.py`, `moteur.py` | I : résultat conforme au plan ; V : zéro récit/audit après geste ; F : faits admis retrouvés ; P : effets sociaux complets. | fusionné (292, 80738af) |
| U-D — descripteur public | Une entrée structurée garde son identité jusqu'au validateur commun. | G2/G4 | `commandes.py`, `moteur.py`, `web/pont.py` | I : deux cibles, aucun secret transmis ; V : zéro compilation/revue au clic ; F : préalables manquants comptés ; P : voix inconnue préservée. | fusionné (293, add5c7e) |
| G1 — compilateur public | Le petit contexte couvre les actes actuels du libre, dont la négociation de mission. | G2/G4/U-D | `compilateur.py`, `paroles.py`, `sources.py`, `mj.py` | I : fidélité au premier coup, clauses et corrections ; V : un appel nominal, taille/préfixe ; F : demande d'admission conservée ; P : négociation jouable. | suspendu (294, 296, 304, 311 non fusionnables) ; décision du 2026-10-29 après la conception 318 : U-P puis U-C sur la voie actuelle, puis G1 sous la forme A (lots A0 à A6, `docs/conception-g1.md`) |
| G3 — transports | Le schéma cloud et le prompt local portent le même sens. | Avec G1 si nécessaire | `fournisseurs/contrat.py`, `fournisseurs/local.py`, `sources.py` | I : contrat identique ; V : cache par voie, local mesuré seulement si disponible ; F : qualifications conservées ; P : actes sociaux conservés. | à faire |
| U-P — récapitulatif | Le moteur expose le plan admis sans omettre parties, termes, portée ou étapes. | G2 (dépendance à G1 levée le 2026-10-29) | `moteur.py`, `rendu.py`, `jeu.py`, `web/page.html` | I : clauses omises/corrigées, question sans effet ; V : zéro appel de résumé ; F : préalable distinct ; P : offre/avis lisibles. | fusionné (319) |
| U-C — consentement | Tout effet lourd ou irréversible du libre impose l'aperçu du plan entier, puis sa confirmation revalidée. | U-P | `transactions.py`, `jeu.py`, `web/pont.py`, `web/page.html` | I : annulation sans effet, plan périmé ; V : saisie→aperçu puis confirmation→effet, temps humain séparé ; F : admission distincte ; P : aucun accord implicite. | fusionné (325, 37dccfa) |
| G5 — perception | Présence, vue, non-perception et souvenir ont un rendu canonique distinct. | G4/G1 | `rendu.py`, `narration.py`, `pnj.py` | I : noir/absent correctement distingués ; V : zéro audit de perception moteur ; F : aucune recherche remplacée par invention ; P : présence publique exacte. | livré, suite d’essai à faire (323) |
| G6 — repères | La phrase de position vient du repère public courant ou mémorisé. | G5 | `localisation.py`, `rendu.py`, `mj.py` | I : orientation et souvenir exacts ; V : zéro relance de position ; F : aucun repère inventé ; P : aucune position privée divulguée. | livré, à fusionner après 323 (328) |
| G7 — déplacements | Le cumul décrit seulement les mouvements exécutés, avec acteur, unité et intervalle. | G4/G6 | `moteur.py`, `narration.py` | I : plan non exécuté distinct ; V : zéro second récit ; F : stable ; P : fuite et son distincts. | fusionné (343, d20fce9) |
| G20 — signes | Une attitude affichée vient d'un signe ou d'une impression encore perçus. | G5 | `signes.py`, `rendu.py`, `mj.py` | I : signe disparu retiré ; V : zéro extraction d'attitude par audit commun ; F : aucun état mental inventé ; P : signes utiles, sans agenda privé. | livré non validé (329) : Luna n’a jamais choisi la sélection typée, gestes accolés aux répliques non contrôlés ; à repenser (routage par le moteur), non fusionné |
| U-M inventaire | Menu et commande soumettent le même geste d'inventaire. | U-D/G4 | `web/page.html`, `web/pont.py`, `commandes.py` | I : cible/quantité identiques ; V : choix jusqu'à effet ; F : stable ; P : remise sans destinataire inventé. | fusionné (298) |
| U-M outils | Les paramètres d'outil et destination viennent des seules ressources connues. | U-M inventaire | `web/page.html`, descripteur U-D | I : outil/cible exacts ; V : choix et refus ; F : propriété absente explicitée ; P : aucun inventaire privé lu. | fusionné (300, 2537e4f) |
| U-M corps | Le menu de corps et violence conserve geste, méthode et risque. | U-D/U-C/G4 | `web/page.html`, `force.py`, descripteur U-D | I : deux cibles, méthodes distinctes ; V : choix jusqu'à effet ; F : stable ; P : opposition et conséquences identiques. | livré non fusionné (344, intégration 014fc35 reprise ; 179/180 ciblés, une erreur antérieure prouvée) |
| U-M passage | Le menu emploie les passages déjà qualifiés. | U-D/G6/G7 | `web/page.html`, `franchissement.py`, descripteur U-D | I : passage/cible exacts ; V : choix jusqu'à effet ; F : aucune dimension inventée ; P : stable. | terminé, non fusionné (349) |
| U-M fabrication | Le formulaire transmet la recette connue et ses paramètres publics. | U-D/G4 | `web/page.html`, `atelier.py`, descripteur U-D | I : recette/matériaux identiques ; V : saisies nécessaires ; F : inconnue laissée à admission ; P : propriété des biens conservée. | fusionné (305, 43440c6) |
| U-T — premier geste | Console et TUI choisissent les mêmes identifiants publics que le web. | U-D/G4 | `jeu.py`, `tui.py`, descripteur U-D | I : deux cibles, ambiguïté/inconnu ; V : touches jusqu'à effet ; F : stable ; P : aucune identité privée. | fusionné (299, f1cb8fd) |
| G15 — émissions | Toute parole entendue possède une émission typée unique. | G2/G4 | `paroles.py`, opérations d'avis, `narration.py` | I : issue/faits cohérents, cas 86/87 ; V : aucune double émission ; F : stable ; P : répondant distinct du témoin, écoute distante et inconscient. | fusionné (320, e0be70d) |
| G16 — information parlée | Le moteur formule identité, localisation crue, ressource et refus. | G15/G5 | `paroles.py`, `dialogues.py`, formateurs | I : voix qui se nomme, croyance fausse ; V : zéro reformulation/audit de réplique typée ; F : stable ; P : réponses et raisons exactes. | fusionné (345) |
| G17 — comptes parlés | Les mots gardent les rôles, termes et règlements de l'issue. | G15 | `comptes_narratifs.py`, `paroles.py`, `dialogues.py` | I : dette/offre/solde exacts ; V : zéro réécriture ; F : stable ; P : aucune opération perdue, aucun paiement de brouillon. | fusionné (326) |
| G18 — avis | Un avis reste un jugement cru et une parole enregistrée. | G15/U-P/U-C | `paroles.py`, formateurs | I : avis contraire conservé ; V : zéro audit de réplique typée ; F : stable ; P : adoption/dispute distinctes de la vérité. | fusionné (351) |
| G19 — rappels | Le rappel restitue les mots entendus sans nouvelle émission. | G15 | `narration.py`, formateurs | I : rappel réel/inventé, autre locuteur ; V : zéro audit de citation exacte ; F : aucune connaissance créée ; P : historique fidèle. | fusionné (327, b2be2b7) |
| U-M social information | Le formulaire transmet l'acte d'information et ses paramètres publics. | U-D/G16 | `web/page.html`, `dialogues.py`, descripteur U-D | I : bien/adresse exacts ; V : choix jusqu'à réponse ; F : stable ; P : croyances et refus préservés. | fusionné (354) |
| U-M social comptes | Les raccourcis soumettent les termes visibles sans accord anticipé. | U-D/G17 | `web/page.html`, `dialogues.py`, descripteur U-D | I : prix/dû exacts ; V : choix jusqu'à verdict ; F : stable ; P : transfert seulement après accord moteur. | en cours (380, PC fixe) |
| U-M social avis | Le choix d'avis conserve sujet et valeur sans réinterprétation. | U-D/G18 | `web/page.html`, `paroles.py`, descripteur U-D | I : deux lieux, avis contraire ; V : zéro compilation ; F : stable ; P : mêmes réception et dispute. | fusionné (386) |
| U-T inventaire | Le choix terminal conserve le geste du menu d'inventaire. | U-T/U-M inventaire | `jeu.py`, `tui.py`, descripteur U-D | I : parité de cible/quantité ; V : touches/effet ; F : stable ; P : parité des remises. | fusionné (301, 41fda83) |
| U-T outils | Le terminal transmet les mêmes choix publics d'outil. | U-T/U-M outils | `jeu.py`, `tui.py`, descripteur U-D | I : parité des paramètres ; V : touches/refus ; F : inconnue conservée ; P : aucun bien privé révélé. | fusionné (307, 2be43e5) |
| U-T corps | Le terminal conserve méthode et risque du geste corporel. | U-T/U-M corps | `jeu.py`, `tui.py`, descripteur U-D | I : parité des méthodes ; V : touches/effet ; F : stable ; P : mêmes conséquences. | fusionné (353) |
| U-T passage | Le terminal choisit le même passage qualifié. | U-T/U-M passage | `jeu.py`, `tui.py`, descripteur U-D | I : parité des cibles ; V : touches/effet ; F : aucune mesure inventée ; P : stable. | fusionné (353) |
| U-T fabrication | Le terminal soumet la même recette paramétrée. | U-T/U-M fabrication | `jeu.py`, `tui.py`, descripteur U-D | I : parité des matériaux ; V : touches/effet ; F : même admission requise ; P : mêmes droits sur les biens. | fusionné (321, 6037855) |
| U-T social information | Le terminal transmet le même acte d'information. | U-T/U-M social information | `jeu.py`, `tui.py`, `dialogues.py` | I : parité de sens/adresse ; V : touches/réponse ; F : stable ; P : mêmes croyances et refus. | fusionné (369) |
| U-T social comptes | Le terminal garde les termes du raccourci comptable. | U-T/U-M social comptes | `jeu.py`, `tui.py`, `dialogues.py` | I : parité prix/dû ; V : touches/verdict ; F : stable ; P : même accord requis. | à faire |
| U-T social avis | Le terminal conserve l'avis structuré. | U-T/U-M social avis | `jeu.py`, `tui.py`, `paroles.py` | I : parité sujet/valeur ; V : touches/réponse ; F : stable ; P : même réception/dispute. | fusionné (389) |
| G12 — portée de création | Un ajout interactif ne remplace ni perception ni indice protégé. | G1/G2 | `mj.py`, `faits_locaux.py`, `portee_narrative.py` | I : intention reprise ; V : appels jusqu'à manipulation ; F : ajout utile persistant, faux indice refusé ; P : aucun engagement cosmétique. | à faire |
| G13 — qualification | Une propriété inconnue est admise avant usage sans écraser l'établi. | G12 | `mj.py`, `faits_locaux.py`, `coherence_physique.py` | I : reprise sans répétition ; V : appels/secondes jusqu'à usage ; F : deux matières, incompatibilité refusée ; P : stable. | à faire |
| K0 — candidats de contrat | Une suggestion déterministe porte des termes publics admissibles, sans accord ni paiement. | G12/G13/G17/U-D | `echanges.py`, `dialogues.py`, descripteur U-D | I : termes compréhensibles ; V : délai de suggestion ; F : référence sans Luna ; P : marchés utiles, ressources puis autre famille. | à faire |
| K1 — éditeur de marché | Les deux termes affichés sont ceux soumis à l'accord. | K0/G17/U-D/U-P | `echanges.py`, `dialogues.py`, `web/page.html`, `tui.py` | I : clauses conservées ; V : choix jusqu'au verdict ; F : clauses inconnues refusées ; P : accord/dette/exécution distincts. | à faire |
| K2 — assistance Luna | Une demande sociale devient des alternatives admises sans décider à la place du PNJ. | K0/K1/G1 | `compilateur.py`, `echanges.py`, `dialogues.py` | I : intention et clauses gardées ; V : appels jusqu'à offre utile ; F : alternatives absentes de K0 ; P : stratégies réellement jugées. | à faire |
| D0 — parole ouverte | Un contenu inédit autorisé devient parole enregistrée sans effet non typé. | G12/G15/G19 | `paroles.py`, `connaissances.py`, `mj.py`, `dialogues.py` | I : sujet et mots conservés ; V : aucun appel pour reformuler le connu ; F : contenu admis persistant ; P : deux PNJ, secret et promesse non typée refusés. | à faire |
| G14 — ciblage d'ambiance | Le détail ciblé est matérialisé une fois avant manipulation, ou déclaré non manipulable. | G12/G13 | `narrateur.py`, `narration.py`, `faits_locaux.py` | I : cible conservée ; V : appels jusqu'au geste ; F : objet unique après recharge, odeur non manipulable ; P : stable. | à faire |
| G8 — producteur d'ambiance | Une sortie cosmétique contrôlée en fond est admise entière ou jetée sans relance. | G14/G5/G6/G20 | `narrateur.py`, `narration.py` | I : aucune fausse réalisation ; V : zéro attente mécanique, contrôle en fond séparé ; F : aucune entité créée ; P : aucune parole/attitude inventée. | à faire |
| G9 — connexions | L'ambiance et son contrôle ne retiennent jamais le compilateur. | G8 | `fournisseurs/openai.py`, `fournisseurs/local.py`, `mj.py` | I : requêtes isolées ; V : concurrence, panne/401/fermeture ; F : admission prioritaire ; P : dialogue non retardé. | à faire |
| G10 — publication | Une ambiance contrôlée est sauvegardée avec son lieu avant affichage. Une sortie périmée est jetée. | G8/G9 | `jeu.py`, `narration.py` | I : provenance exacte ; V : rendu mécanique indépendant ; F : détail établi conservé ; P : stable. Départ, autre lieu, panne et recharge. | à faire |
| G11 — interfaces | Une tâche de fond ne retient ni saisie, ni menu, ni sortie du jeu. | G9/G10 | `jeu.py`, `web/page.html`, `web/pont.py` | I : saisie conservée ; V : délai artificiel sans effet mécanique ; F : admission accessible ; P : dialogue accessible. | à faire |
| U-A — indicateur | Terminal et web affichent l'état de préparation de l'ambiance, jusqu'à fin ou abandon. | G9/G10/G11 | `jeu.py`, `tui.py`, `web/page.html`, `web/pont.py` | I : état distinct du MJ ; V : indicateur non modal, retiré aussi en panne ; F : stable ; P : stable. | à faire |
| G21 — fermeture | Toutes les voies publiques suivent le contrat ; seuls les contrôles remplacés sont retirés. | Tous les portages requis ci-dessus | `mj.py`, `jeu.py`, `narration.py`, `docs/contrat-mj.md` | I : couverture et décision de retrait des revues sur observation joueur ; V : zéro audit cosmétique bloquant ; F : admissions résiduelles explicites ; P : aucune interaction perdue. | à faire |

G0 est rédigé sur `codex-g0-contrat`, non fusionnée. Son état reste `en cours`
jusqu'à intégration. Les autres lignes ne prétendent pas que ces voies sont livrées.
Les suffixes U-M et U-T séparent les familles. Si une ligne dépasse le créneau,
le superviseur la découpe avant ouverture. K1 commence par un type d'échange.
Les offres spontanées, missions générales, menaces et échéances nouvelles restent
des lots de mécanique distincts. Finir A5 précède le choix de la mécanique suivante.

Pour chaque portage : cas réel, autre cas de même nature et faux pendant.
Vérifier l'état et le rendu après sauvegarde/rechargement. Les tests sont ciblés.
Une interface pure demande une preuve déterministe de parité. Si le chemin MJ
change, faire une seule passe Luna ciblée, sur copies. Réutiliser la référence
exacte ; ne comparer les secondes que sous charge comparable. Suite complète
et vérifications lourdes restent groupées à l'intégration. Aucun banc PNJ si
seule la couche MJ change. Ne pas annoncer un gain à partir des temps du cache.

U-P suit l'exécution des actes libres légers. U-C la précède pour les actes
lourds ou irréversibles, selon les effets typés, y compris dans une composition.
Le clic ne demande ni réinterprétation ni revue de fidélité. Les confirmations
de risque existantes restent applicables. Les revues du libre à effets restent
transitoires. Leur retrait exige une mesure de ce que le joueur repère réellement.
La validité d'un plan ne prouve jamais sa fidélité à toute phrase libre.
La prose cosmétique libre ne garantit pas toute absence de contradiction implicite.
