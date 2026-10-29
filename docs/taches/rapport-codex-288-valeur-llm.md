# Lot 288 — valeur de gameplay du LLM

29 octobre 2026 — `codex-valeur-llm`, **non fusionnée**, base intégration
`c90cbea` contenant le brief. Conception seulement, contrat actuel inchangé.

**Direction.** [Conception](../conception-valeur-llm.md) : gestes usuels directs,
Luna pour comprendre/composer une intention, proposer des termes pertinents
et admettre du contenu inédit. Inventaire du moteur, opérations, perceptions,
paroles et menu réel ; coûts des ajouts et limites du ciblage. Une commande
locale évite l'interprétation, mais peut encore attendre un récit de résultat :
extension du menu et suppression du récit mécanique doivent aller ensemble.
Les conséquences sociales existent largement dans le moteur ; le LLM ne
décide ni consentement, ni prix, ni croyance, ni réalisation d'une tâche.

**Archives.** 68 parties `c9459ce`, 34 scripts × deux passes, **368 saisies
hors sortie, 184 positions de script**. Classement humain : direct simple
**258 (70,1 %)** ; dialogue structurable **44 (12,0 %)** ; composé 10 ;
invention/qualification/improvisation 22 ; ouvert 22 ; ambiance 12.
**82,1 %** candidats au direct en incluant les formulaires sociaux, sans
prétendre préserver les mots libres ou garantir la disponibilité des cibles.
152 entrées ont un contrôle/touche/panneau existant, 30 un verbe de menu,
40 une commande sans choix de menu, 80 demandent une interface supplémentaire.
Parmi les 187 tours avec appel : 91 gestes simples, 131 avec le social
structurable ; 397 des 561 appels historiques, 755,86 des 1 084,78 s.
Ces volumes ne prédisent aucun gain de délai. Les 68 anciennes parties
`d85fb54` ont les mêmes saisies ; **136 SHA-256 inchangés**, sans doubler
l'échantillon. Corpus de régression, pas observation de joueurs.

**Contrats et dialogue.** Matrice missions configurées / échanges à deux
termes / tâches et agendas / mandats A5. Les conditions exposées sont bornées ;
échéance choisie, mission générale et mandats/comptes rendus joueur ne sont
pas acquis. Générer d'abord des suggestions publiques admissibles et mesurer
leur intérêt face à une référence déterministe ; offre, consentement et
engagement restent distincts. Persuader, mentir, questionner, marchander,
raconter et menacer sont confrontés aux actes actuels : ni poids universel
des arguments ni effet systémique général d'une menace. L'option A formule
les réponses typées ; la parole personnelle ouverte reste soumise à décision.

**Plan révisé.** Reprise explicite de G0–G21 ; montent rendu immédiat,
perception et actes sociaux. Ajouts : descripteur public, menu par famille,
actions terminal, récapitulatif et consentement, indicateur d'ambiance.
Décision utilisateur intégrée : **c avec b en filet**, aperçu avant acte libre
lourd/irréversible, résultat après acte léger, aucun contrôle de fidélité au
clic ; revues transitoires des seuls actes à effets, retrait décidé sur mesure.
Mesurer délai jusqu'à aperçu puis confirmation→effet et validations humaines,
sans confondre aperçu rapide et exécution. Contrôle sémantique d'ambiance
proposé en fond avant publication, sans relance, avec gardes renforcées ;
aucune garantie universelle de cohérence sémantique annoncée. Cinq questions
restantes recommandées, sans remettre les décisions acquises au vote.

**Vérification.** Quatre documents seulement : conception, renvoi de mise à
jour du 287, ce rapport et entrée d'état. Contrôle des liens ajoutés, comptes,
encodage et `git diff --check`. Aucun fichier sous `donjon/`, `tests/`, `tools/`
modifié, aucun import du jeu, test moteur, Luna ou banc. Un seul processus
Python léger à la fois ; aucun calcul actif. Bruts et script dans
`C:/Users/msics/donjon/artifacts/valeur-llm-288/`. Aucune fusion ni rebase.
