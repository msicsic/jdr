# Lot 434 — K2, assistance de Luna à la négociation

Branche `codex-k2-assistance-luna`, base `integration` **`364e8722`**.
Code réalisé ; **vérification en cours, lot non déclaré terminé**.

**Invariant et réalisation.** L’aide demandée emprunte le mode `accord` du
compilateur public, avec une charge distincte portant un obstacle ou au plus
deux alternatives. Aucun routage lexical ni nouvelle mécanique sociale.
`negociation.py` réutilise les termes du moteur et le catalogue public K1,
ajouté au contexte avec sa provenance ; aucun dossier mental privé n’est
ajouté. Une alternative passe par `parole_accord`, puis par
`echanges.candidat_proposition`, étendu aux deux termes sur copie : droits,
fonds, disponibilité, doublons, livraison et devis du PNJ. Aucun jet social,
paiement ou engagement à cette étape. La possession actuelle ne peut servir
de preuve que pour un bien visible ; sinon seule la preuve mémorisée est lue.

**Clauses et interfaces.** Une clause supplémentaire ne se répare pas : le
candidat entier est écarté. Un obstacle déclaré arrête l’ensemble du marché,
même si le modèle joint des alternatives. Les limites ponctuelles existantes
sont compilées en instants par `compiler_limites` et admises par le contrôle
temporel commun ; aucun événement incertain n’est une nouvelle date.
Les libellés affichés sont écrits par le moteur. La sélection ouvre K1
prérempli en console, TUI et web ; le web accepte désormais aussi la liste
d’alternatives d’un brouillon vide. Modifier, valider et tenter restent les
étapes ordinaires, avec revalidation et verdict du PNJ.

**Vérification lancée.** `compileall` et `git diff --check` réussis. Les tests
K2 contrôlent Aubin/planches contre tâche ponctuelle et Odile/huile contre
lanterne, le vrai callback web, la sélection terminale, les termes soumis,
le verdict, l’état et les vues après recharge. Autres preuves : mélange de
candidats admis/refusés, fonds insuffisants, référence privée, propriété sans
preuve, clause inconnue, arrêt sur obstacle, déduplication, plafond de deux,
limite relative puis instant exact, contexte inchangé quand un besoin privé
varie. La première exécution ciblée a révélé trois erreurs du test, corrigées
(signature du helper et nom du registre des paroles).
La vérification voisine porte sur K0, K1, E5, E6, propositions et projection
publique ; une reprise K2 et raccord libre couvre les dernières modifications.
Deux travailleurs au plus à priorité réduite ; pas de suite complète ni banc PNJ.

**Luna et mesure.** `tools/banc_negociation_aide.py` prépare les mêmes scènes
sur copies, garde K0, les requêtes, les sorties admises et les appels, puis
soumet la première alternative au moteur et compare état/vues rechargés.
La troisième demande porte sur « ramène Brune avant la crue », payé seulement
en cas de succès. Une seule passe attend la fin des tests. Aucun résultat
Luna ni gain de richesse n’est encore revendiqué. Le compteur hors K0 compare
les termes canoniques, indépendamment des anciens champs `prestation/prix`.

**Limites.** La détection d’une clause inexprimable dans le français libre
reste sémantique : un candidat typé valide ne prouve pas la fidélité à toute
saisie. Les deux termes restent exposés au contrôle du joueur dans K1 ; aucun
audit des voies à effets n’est retiré. Une tâche promise par Corvus ne reçoit
pas de plan autonome ni de garantie de réussite. L’admission ne prédit pas
l’utilité privée de la contrepartie ni l’acceptation du PNJ.

**Bruts et reprise.** `artifacts/k2-assistance-434/` dans ce worktree :
`verification.json`, `final-cibles.json`, `luna/bilan.json` et fils par scène ;
le fichier de fin de toute la chaîne est **`fin.json`**, écrit en dernier.
Copie de livraison : `C:/Users/msics/donjon/artifacts/k2-assistance-434/`.
Commande Luna exacte :
`$env:SEUIL_AUTH='C:\Users\msics\donjon\.seuil-auth'; & C:/Users/msics/donjon/.venv/Scripts/python.exe tools/banc_negociation_aide.py --sortie artifacts/k2-assistance-434/luna`.
Le bilan final doit être lu avant de conclure le lot et d’annoncer les mesures.
