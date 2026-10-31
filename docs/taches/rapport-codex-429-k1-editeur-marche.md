# Lot 429 — K1, éditeur de marché à deux termes

Branche `codex-k1-editeur-marche`, base `integration` **`b941c492`**.
Code livré, **vérification finale en cours**, non fusionné.

**Invariant.** Le formulaire compose ce que Corvus donne et ce qu’il demande :
objet entier, part, tâche ponctuelle, pièces (fonds ou source explicite), et
contrepartie éventuellement nulle. Les deux termes de l’aperçu sont ceux
transmis à `echanges.proposer`. Les références publiques sont résolues sans
réécriture des clauses. Une clause inconnue reçoit un refus avec `attendu`.

**Changement.** `accords_publics` étend le catalogue public E5 aux objets et
aux pièces ; `parole_accord` applique le contrat structurel commun
`propositions.erreur_terme` / `verifier` avant de produire la parole déterministe.
Le descripteur K1 transporte `demande` et `contrepartie` entiers. L’adaptateur
E5 conserve les descripteurs K0/E5, sans perte de champ. Le catalogue K0 reste
borné aux achats de parts et de tâches : deux lignes localisées dans
`dialogues.py`. Aucun changement au jugement, aux transferts, à la dette ou
aux engagements d’`echanges.py`.

**Interfaces et libre.** Le web affiche les deux termes, les montants et les
limites ; une limite absolue préremplie reste exacte même hors minute ronde.
Console et TUI réutilisent `AccordTerminal` : à l’étape de la contrepartie,
un entier offre des pièces, `terme N` choisit un autre terme du catalogue.
Les deux termes et leurs délais restent modifiables avant validation.
Après la revue de fidélité existante, un marché non daté compilé en parole
ouvre le même éditeur et le même descripteur, sans publication ni exécution.
Un marché accompagné d’autres actes est refusé explicitement, sans les perdre.
Le raccord daté E6 conserve sa règle : une date non compilable reste à préciser.
Aucun appel au modèle dans l’éditeur ; aucun contrôle de fidélité retiré.

**Vérification acquise.** K0 : **7/7**, 137,8 s ; première passe K1 : **4/4**,
177,8 s. Cas : pièces contre planches d’Aubin au Relais, cloche contre tâche
d’allumage au Relais, lanterne contre part d’huile d’Odile à l’auberge.
Les tests sondent les vrais callbacks web et la boucle console, interceptent
les termes reçus par `echanges.proposer`, puis comparent état et vues après
recharge. Le libre utilise la vraie orchestration du MJ, avec compilation et
revue simulées ; la revue est contrôlée comme toujours appelée. Autres preuves :
clauses inconnues, mélange d’actes, rien, pièces demandées, limite à 6123.

**En cours.** Passe finale K1 (5 tests, incluant TUI et source des pièces),
puis voisins E5/E6, accord daté, U-D, comptes parlés et propositions (six
fichiers). Deux travailleurs au plus, priorité réduite, sur copies ; aucune
suite complète, aucun banc PNJ ni appel Luna. Bruts dans
`C:/Users/msics/donjon/artifacts/k1-editeur-429/` : `k0.json`, `k1.json`,
`voisins.json` et journaux ; **`fin.json` est écrit en dernier** avec le bilan.

**Limites.** Le catalogue des tâches reste celui des prestations ponctuelles E5 ;
pas de nouveau langage de conditions, maintien, prêt ou offre persistante.
La fidélité sémantique de toute saisie libre n’est pas une garantie déterministe :
elle conserve sa revue et le contrôle explicite du joueur. Le verdict du PNJ
reste indépendant de la validité d’un brouillon. La validation finale ne doit
pas être annoncée verte avant lecture de `fin.json`.
