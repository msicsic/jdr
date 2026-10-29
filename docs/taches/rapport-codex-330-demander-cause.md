# Lot 330 — Demander à un proche ce qui l'inquiète

29 octobre 2026 — branche `codex-demander-cause`, **non fusionnée**, base
fournie `f08ef58` (descendante de l'intégration). PC fixe `msi-desktop`.

**Invariant.** Le secours de proximité peut commencer par une question lorsque
le PNJ retient la détresse du proche sans connaître de cause. `planification._pulsion`
propose un seul geste `demander`, puis le choix reprend sur la réponse réelle.
Le contact, l'approche et la priorité des périls restent ceux des actions sociales.
`causes.connues` ne consulte que les croyances du locuteur : violence encore
active contre lui, menace d'eau à son emplacement, bruit sans auteur identifié
encore retenu. Un cri attribué au proche est un signe de détresse, pas une
explication de sa cause. Aucune position de danger n'est ajoutée par la réponse.

**Parole et continuité.** `echanges.executer` rejoint `causes.demander` après les
contrôles communs. Question et réponse passent par `social.faire_entendre` et le
registre des émissions ; destinataire et tiers reçoivent le même contenu typé
`cause_detresse` par `social.recevoir`. La réponse conserve la date du fait,
sa source et sa confiance ; les avis d'eau utilisent `recevoir_prevision`.
Une preuve propre plus récente ou plus solide prime. La réponse peut être fausse.
Ignorance, méfiance, rancune ou inconscience ne donnent aucune cause utile.
La dernière réponse reste dans `refus`, hors des quarante souvenirs ; `deliberation.tient`
ne la libère que sur une nouvelle entrée de détresse du demandeur. La perte du
signe, le délai et l'estompement numérique des relations ne suffisent pas.

**Preuves déjà exécutées.** Dix tests nouveaux verts, puis reprise du test
d'inconscience après remplacement de la fixture par `corps.endormir` : vert.
Deux agressions réellement exécutées, au Relais et à la mine, sont suivies
d'une question autonome, d'un ouï-dire enregistré et d'une fuite ou riposte
par les recours existants. Capture réelle de crue du 266 relue sans altération.
État complet, émissions, scène et rendu final identiques après sauvegarde et
recharge ; laps entier et découpé comparés. Les aperçus intermédiaires du joueur
dépendent de ses points d'affichage et ne sont pas annoncés identiques.
Autres contrôles : cause connue, absence de détresse, ignorance, méfiance,
inconscience physique, croyances fausses de violence et d'eau, bruit, tiers,
absence de position transmise, preuve plus forte et nouvelle entrée perceptive.

**Première validation analysée.** `fin.json` initial : échec, code 1,
169,741 s, 192 tests : 24 erreurs dues à l'import local `demander` qui masquait
la fonction d'échange d'objets, et quatre échecs de subtests dans deux méthodes
de proximité. Import renommé ; le test du préfixe suppose désormais la question
déjà répondue, les assertions de maintien, apaisement et recharge restent.
Le test du maintien a ensuite révélé deux questions pour un même signe dont
la date était rafraîchie : la date est désormais exclue de l'identité de la
réponse, y compris pour les sauvegardes du premier format du lot.
**24 tests directement concernés verts** (proximité et cause), puis test de
date renforcé. Aucun banc n'a commencé pendant cette première validation.

**Reprise détachée préparée, résultats en attente.**
`tools/valider_cause_330.py` reprend les neuf fichiers concernés (126 tests),
les 66 tests des cinq autres fichiers verts restant acquis, puis vingt nuits
de 4 h : Relais, mine, auberge, crue, hameau × 1985/7/42/2024. Deux travailleurs
réduits au plus ; ni Luna ni suite complète. Référence exacte `f08ef58`, cache
commun consulté avant tout calcul ; ses nuits de 4 h sont absentes au lancement
et seront calculées et rangées une seule fois selon `AGENTS.md`.
Le bilan contrôle les suspects 219 nuit par nuit, les plantages et usurpations.
Il compte demandes, réponses crues et premiers choix qui les suivent, avec
leurs intentions typées : une succession observée ne prouve pas la causalité.
Bruts : `C:/Users/msics/donjon/artifacts/cause-330/`, première fin conservée ;
reprise dans `reprise-1/`, `fin.json` écrit en dernier même sur échec.
**Le critère du banc et la consolidation des tests voisins ne sont pas
encore validés ; le lot n'est pas déclaré terminé.**

**Périmètre et limites.** PNJ seulement : `paroles.py`, `CHAMPS_CONTENU`, le
compilateur du joueur et Luna restent inchangés. La question est un moyen du
secours de proximité ; elle n'est pas un nouvel objectif prioritaire, ni une
recherche à distance. Une réponse porte au plus une cause, dans l'ordre
violence/eau/bruit ; aucune garantie d'exhaustivité ou d'amélioration générale
des réactions. Recouvrement G17/326 : **`docs/etat-dev.md` seulement**, aucun
fichier de code commun avec la branche G17 présente sur ce poste.
