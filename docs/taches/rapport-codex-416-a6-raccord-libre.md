# Lot 416 — A6, raccord libre

31 octobre 2026 — `codex-a6-raccord-libre` ; raccord `f7dc9203`, revue
`20ac5f1e`/`3281dc00`, correctif d'entrave `bcd5729e`.
**Dernier blocage corrigé et ciblés verts ; vingt voisins en cours.**

**Régression confirmée.** La méthode
`ForceLunaTests.test_prendre_lier_delier_liberer_et_tuer_via_console` est verte
sur le dernier `origin/integration`, **`8c5eaaa7`**, sans ignoré : les deux cas
de libération y passent. L'antériorité constatée sur `f7dc9203`, commit de
cette branche, n'excusait donc pas le refus : c'était bien une régression A6.
Le contrôle A1 refusait `objet:entrave_*.entrave` avant tout appel du modèle.

**Contrat corrigé.** `projection_publique.OBJET_PUBLIC` porte désormais le
marqueur mécanique `entrave`. Le contrat commun de `tenir.finir` le pose à
`True` sur le lien qui retient un corps, puis le retire à la libération ;
`banc_pnj.appliquer_etats` produit le même état typé. L'admission ne dépend
d'aucun identifiant, type d'objet, lieu, personnage ou formulation. La
projection conserve la valeur et sa provenance, sur les seuls objets déjà
admis par le contexte public. Aucun autre champ sans contrat n'est accepté ;
les exclusions privées et les refus A1 restent inchangés. Aucun changement
de compilation sonore, aucune nouvelle passe Luna.

**Vérification ciblée : 36 tests verts, zéro ignoré, 189,30 s**, trois fichiers,
deux travailleurs à priorité réduite. La méthode de force passe maintenant
aussi sur la branche. Les deux nouveaux oracles portent sur le marqueur
projeté avec provenance et refus d'un champ inconnu, puis la vraie saisie libre
de libération avec deux PNJ et deux producteurs : lien de l'état de banc,
corde réellement ligotée par le moteur. Ils contrôlent le consentement avant
effet, la disparition des liens et du marqueur, le monde, le rendu et la
conversation après recharge ; un laps entier est comparé à ses tranches.
Aucune assertion de sécurité existante n'est relâchée.

**Vingt fichiers voisins relancés sur `bcd5729e`.** La liste exacte de la passe
précédente est réutilisée, deux travailleurs au plus, priorité réduite ;
commandes et résultats dans `entraves/`. Le bilan sera écrit en dernier dans
`entraves/fin.json`. Pas de suite complète, pas de recalcul PNJ ni de Luna.
Les trois méthodes de ressources, matérialisation et refus narratifs qui
échouent aussi sur la base sont acceptées comme limites par le superviseur ;
le nouveau bilan doit distinguer ces signaux de toute régression.

**Garanties acquises dans les étapes précédentes.** Le libre et ses reprises
partagent la forme A ; A1 projette le contexte public, A2/A3 lient les modes
et paramètres, A4/A5 conservent dossier de revue et reprise, U-P/U-C protègent
l'affichage et le consentement. La revue des gestes compare chaque paramètre
typé dans une table exhaustive avec valeur demandée, jugement individuel et
périmètre mécanique. Champs omis, classements cosmétiques, jugements
incohérents et JSON illisible sont refusés avec attendu. Deux rapports
illisibles n'admettent plus le geste ; les références restent publiques.
Le registre des quatre familles A2 est partagé, sans heuristique de saisie.

Les trois contre-épreuves Luna passent : sifflement fidèle admis ; voix
mélodique pour « je siffle » refusée ; vraie nuance joyeux/gai admise dans une
manière effectivement exposée. La passe atelier ×2/crypte a donné **69 appels /
31 tours, 2,23 appels et 9,78 s/tour**, sans erreur technique ou de recharge.
Un atelier refuse les propositions inadéquates et finit sans geste ; l'autre
exécute le sifflement canonique. Aucun effet sonore substitué n'est admis.
Le superviseur accepte cette limite de compilation et le coût ; aucune
fidélité universelle n'est revendiquée.

Pour la crypte, la passe Luna de base `19b711bf` ne reproduisait pas le repli,
mais le rejeu de ses vingt réponses défaillantes sur cette base reproduit
exactement le même repli ; les modules de contrôle sont identiques. Cette
limite est acceptée par le superviseur, sans assouplissement d'audit. Les
premières mesures et leurs incidents de lancement restent archivés.

**Bruts.** `C:/Users/msics/donjon/artifacts/a6-raccord-libre-416/` :
`reprise/` conserve les preuves de revue et les limites acceptées ;
`entraves/base.json`, `entraves/tests-cibles.json`, commandes, scripts et
`entraves/fin.json` portent ce dernier correctif. Validation finale des voisins
encore attendue ; calcul détaché vivant au lancement.
