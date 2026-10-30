# Lot 363 — E6, compilation libre d'un accord daté

Branche `codex-e6-libre-date`, base `integration a9f02e5c`, PC fixe.
Code vérifié : `f24c6a06`, sources stables pendant les calculs.
**Lot clos, E6 non validé : ne pas fusionner cette réalisation comme E6 acquis.**

**Ce qui est porté.** `propositions.schema_compilation` accepte un délai
structuré `limite: {dans_secondes: n}` ; `compiler_limites` le résout sur copie
à l'instant de la saisie, avant préparation et revue de parole. La transaction
ne conserve que la limite absolue E4. U-C, l'exécution et la sauvegarde gardent
leur contrat absolu : attendre ou confirmer ne recalcule pas la date.
Le dossier commun de fidélité reçoit les termes exécutables rendus par le
moteur, leur limite et leur durée restante, ainsi que le paiement présent.
Les noms passent par la projection publique. Le schéma, les consignes et la
revue exposent la portée E4 et ses exclusions ; aucun contrôle n'est retiré.
`comprehension.py`, `consentement.py` et `transactions.py` sont inchangés.
Recouvrements avec 360/362 : `paroles.py`, `mj.py`, `propositions.py`,
`couverture_action.py`. Aucun changement aux effets ou à l'autonomie du moteur.

**Tests : 145 méthodes distinctes vertes dans 17 fichiers**, zéro échec,
erreur ou saut. Première passe finale : 107 tests en 387,816 s ; complément :
43 en 75,548 s, dont les cinq E6 rejoués. Deux travailleurs réduits au plus.
Huile d'Odile et verrou par Joss : compilation simulée, aperçu, consentement,
annulation, revalidation à instant non entier, termes E5, comptes, engagements,
réponses PNJ et rendu après recharge. Les paroles imposées gardent leurs mots.
Les refus simulés prouvent l'absence d'exécution partielle lorsque la revue
rejette une clause ; ils ne prouvent pas que Luna détecte toutes ces clauses.
La première passe rouge (onze erreurs de sous-cas, audit narratif absent du
harnais) est conservée ; aucun oracle moteur n'a été affaibli. Pas de suite
complète ni de banc autonome, les effets moteur étant inchangés.

**Luna, une passe réelle : 14 scripts, 83 appels**, zéro erreur technique,
mention sans fondement ou erreur de recharge signalée par le banc ; deux
replis narratifs. Les compteurs techniques verts ne valident pas le contrat.
L'huile est compilée avec prestation, prix et dix minutes : aperçu puis accord
effectif après `tenter`, ou annulation sans émission. Son maintien continu est
refusé explicitement. Mais les critères E6 échouent :

- « huile demain » devient 86 400 secondes et un aperçu à la minute 1440 ;
  la revue accepte ce repère inventé, sans demander de précision.
- Le verrou est traduit par une condition `lieu:cellier`, parfois avec les
  parties inversées. La revue le rejette, mais aucune correction n'aboutit au
  verrouillage demandé, malgré sa présence dans le schéma fourni.
- Plusieurs clauses non portées finissent en parole sans effet après refus
  du typage ; le paiement futur peut être reclassé en `propos`. Alternative,
  prêt et maintien ne reçoivent pas systématiquement de raison publique de
  refus. Le prêt à Joss finit même par une réplique « D'accord » sans contrat.

**Conclusion.** La résolution et la conservation du délai typé fonctionnent
dans les parcours éprouvés. L'invariant demandé n'est pas acquis : le contrat
commun ne garantit encore ni l'exhaustivité temporelle de la compilation, ni
la clarification sans calendrier, ni un refus entier sans repli en parole.
L'enrichissement des consignes et du dossier de revue ne suffit pas. Aucun
nouveau mot-clé, cas de scénario ou ajustement de prompt n'a été ajouté après
cette observation ; aucune seconde passe Luna n'est lancée. La reprise doit
porter le contrat commun de compilation, de refus et de repli, en conservant
la protection du consentement et les contrôles transitoires.

Bruts : `C:/Users/msics/donjon/artifacts/e6-363/` : `tests-cibles.json`,
`tests-complement.json`, `sources.json`, `luna/`, `analyse-cloture.json`.
`tools/preparer_banc_e6.py` reproduit les copies et `luna-a-jouer.txt` donne
la commande exacte. `fin-cloture.json` conclut **valide=false**, sans calcul
actif. Branche poussée ; fusion laissée au superviseur, avec cette réserve.
