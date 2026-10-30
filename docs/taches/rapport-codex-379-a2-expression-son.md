# Lot 379 — A2, expression et son

30 octobre 2026 — branche `codex-a2-expression-son`, base `origin/integration`
`85052cf8ead15face37538df8130209dc44158fc`, non fusionnée.

**Invariant.** `donjon/contrats_son.py` réunit le sens des émissions vocales,
des sons d'objet et des formes sonores improvisées. `sons.compiler`,
`improvisation.compiler_effet`, les méthodes et schémas d'`operations`, les
raccourcis de `commandes` et `comprehension.plan_admis` le réemploient.
Les réponses conservent les méthodes et les paroles canoniques d'`appel`.
Un récit, une approche ou un niveau de bruit ne constitue pas un effet son.

**Changement.** Les branches d'`emettre_son` corrèlent méthode, source et
paramètres neutres ; les effets improvisés séparent `son` des autres effets
et exigent joueur, destination vide, catégorie acoustique et intensité 1–3.
Ces contraintes valent aussi dans la suite après admission de faits.
Le moteur conserve ses contrôles de portée, capacité, voix et appel en
attente ; les refus de forme nomment le champ reçu et la valeur acceptée.
« Compris » explicite le son des deux issues, les mots d'une réponse à un
appel et l'absence de son prévu dans une expression sans effet sonore.
Les titres et textes acoustiques proviennent des mêmes tables que l'exécution.
L'ouïe, les durées, jets, appels, réponses et sauvegardes ne changent pas.
Le chuchotement conserve son contrat de parole : manière fixée par le moteur,
destinataire unique au contact ; il n'est pas une nouvelle méthode sonore.

**Preuves.** Huit nouveaux tests : cas historique `relais/2` (« je fredonne
doucement »), rythme frappé avec le corps et faux pendant silencieux dans
la vraie boucle console/PontWeb ; pureté de préparation, absence de jet,
son réellement entendu et sauvegarde avant affichage, plan et réponse relus
après reprise. Même émission suivie de deux minutes en bloc ou huit tranches
de quinze secondes avec recharge à chaque tranche : monde complet et vues
identiques. Identité des raccourcis et des étapes vocales explicites,
paroles des trois réponses, cloche et gong sans dégâts, issues sonores
distinctes, refus sans mutation des champs voisins et schéma effectivement
émis. Le test A2 précédent accepte structurellement les nouvelles branches
du schéma ; toutes ses assertions de sécurité sont conservées.

**Mesures.** Première passe : 193 tests sur 17 fichiers, 253,08 s, sept échecs
de rendu dans `test_voix.py` et `test_voix_inconnues.py`, aucune erreur.
Les deux fichiers rejoués sur la base exacte donnent les sept mêmes méthodes
et les mêmes messages d'échec (40 tests, 33,13 s). Leurs assertions restent
intactes : ce lot n'annonce donc pas tous les voisins verts. Sur le code
`429c0f4c`, la passe finale est verte : **59 tests sur huit fichiers,
135,18 s, zéro échec, erreur ou ignoré**, dont les huit nouveaux tests.
**Empreintes identiques sur quatre nuits Relais de 2 h**, graines
1985/7/42/2024 : chronique, mesures et état final complet, sans plantage.
Référence absente calculée une fois puis rangée dans le cache partagé ;
branche non mise en cache, `PYTHONHASHSEED=0` des deux côtés. Aucun gain de
vitesse revendiqué. `fin.json` : `tests=0`, `empreintes=0`, `erreur=null`,
sept échecs voisins identiques à la base. Bruts dans
`C:/Users/msics/donjon/artifacts/a2-expression-son-379/`, notamment
`tests-voisins.json`, `tests-base-voix.json`, `tests-finaux.json`, `empreintes.json`.
Deux travailleurs à priorité réduite. Pas de suite complète ni Luna.

**Limites.** Le contrat garantit le sens d'une charge sonore typée admise,
pas la fidélité de son choix par Luna : une demande de fredonnement peut
encore être mal compilée en geste sans son ou en effort avec jet. Le faux
pendant silencieux reste légal ; aucun mot de la saisie n'ajoute un effet.
Le plan montre l'omission et les revues actuelles restent en place (A4/A6
hors lot). Le cas historique est exercé avec compilation simulée : aucune
mesure de fidélité Luna n'en est déduite. Pas de registre d'esprit ajouté,
ni de recouvrement de code identifié avec 374/378/380 ; 375 doit tenir compte
de l'évolution structurelle du schéma de séquence. `docs/etat-dev.md` est partagé.
