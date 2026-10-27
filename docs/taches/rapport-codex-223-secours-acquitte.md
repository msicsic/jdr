# Lot 223 — secours réévalué et acquitté sur constat

27–28 octobre 2026. Branche `codex-secours-acquitte`, **non fusionnée**.
Départ `395834b` vérifié ; intégration 213 `bd45f65` reçue pendant la suite,
puis fusionnée en avance rapide, sans conflit. Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/secours-223/` ; captures sources du lot 222.

**Invariant et fonctions.** `protection` reste une lecture pure, notamment pour
la sonde 219. Dans `planification.reagir`, la réaction réelle acquitte les
secours dont l'appelant est actuellement vu, ou dont l'état a été vu à une
minute strictement postérieure à l'appel. Champ persistant `examine` et événement
`intervention` existants. Les agressions connues sont toujours réévaluées :
acquitter un cri ne supprime pas un agresseur. Un appel non élucidé ne déclenche
plus une enquête vers un lieu connu dangereux (`lieux_dangereux`, contrat de la
fuite) ; il reste en attente et une destination redevenue sûre reste accessible.
Le joueur conserve le choix de ses gestes, sans plan autonome. Aucun délai,
coût, identité ou scénario ajouté. **Seules `defense.protection` et
`planification.reagir` changent** ; contrôle AST dans `perimetre.json`.
`pnj.py`, `deliberation.py`, `agendas.py`, l'inspection et le MJ sont inchangés.

**Cas réel et autre cas.** Sur `bd45f65`, les captures 022/026 reproduisent le
plan de retour vers Brune. Pendant chaque reprise d'une minute, le retour
effectif vers le danger connu passe de **1 à 0**, avec acquittement ultérieur
sur constat. Ce n'est pas une suppression du combat : coups **24→24** (022),
**15→20** (026). `reproduction-finale.json` sépare l'interrogation initiale des
choix réellement effectués. Autre scénario, rixe : cri reconnu d'Aubin, Gorm
puis Ilse protecteurs, secours joué jusqu'au constat ; vue directe sans
inspection également vérifiée, puis départ sans réactivation. Monde complet,
`regarder` et `scene_percue` identiques après recharge et pour un même laps
entier/découpé (captures : 1 minute/quatre quarts ; autre scène : 2 minutes/quatre
demies). Pureté de la lecture contrôlée sur les deux captures.

**Vérifications.** **63 ciblés verts sur l'arbre final**, dont trois nouveaux,
81,443 s ; défense, protection, fuite, sonde 219 et contrat 213.
Suite complète unique initiale : **2 446 tests / 284 fichiers, 2 239,365 s**,
deux échecs MiMo historiques `6 != 5` (également documentés/reproduits par 213)
et une erreur Windows `os.replace` de sauvegarde TUI. Ce cas TUI repasse
isolément vert après fusion (1,800 s), fichier temporaire rangé dans les bruts.
La suite avait été lancée avant l'annonce de 213 et avant le déplacement final
de publication dans `reagir` : elle ne certifie pas seule l'arbre final.
Aucune seconde suite, les fichiers de code de 213 et du correctif étant
disjoints ; ciblés finaux et banc portent sur l'arbre fusionné. Créneau dépassé.

**Banc final : 24 paires de 4 h**, Relais/mine/auberge/crue/crue_hameau/rixe,
1985/7/42/2024, contre **`bd45f65`**, classes 219 actives. **24/24 chroniques,
mesures, états finaux complets et constats identiques**. Suspects **5→5**,
préemptions **58→58**, cycles **566→566**, à expliquer **68→68** ; aucune nouvelle
alerte. **Zéro plantage/usurpation/coup**, **9→9 appels à l'aide** dans le récit.
Les 24 références exactes manquaient : calculées une fois et rangées dans le
cache. Temps de cache non comparés. Premier essai contre le `main` local ancien
`812ebe5` invalide (sonde exigeant `interposition` absent), bruts conservés.

**Limites.** Les dates à la minute ne départagent pas une vue et un cri de la
même minute : sans vue actuelle, l'appel reste en attente. Pas de garantie
générale contre toutes les boucles ni de baisse de violence revendiquée.
Le joueur entend les appels via `ouie._au_joueur`, sans mémoire `secours` :
la mémoire joueur injectée est testée, mais le raccordement automatique de ce
parcours réel reste **hors périmètre et non établi**, extension demandée sans
réponse. Aucun Luna. Aucune clé de signature Git configurée : commit non signé.
