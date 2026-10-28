# Lot 273 — demande adoptée et moyen démenti

29 octobre 2026. **Branche `codex-demande-adoptee`, non fusionnée**, base
`c9459ce`, correctif moteur **`3ec23bb`**. **Banc encore à recevoir.**

**Invariant.** L'échec d'un moyen ne certifie pas la fin d'une demande
adoptée. `deliberation.choisir` libère ses gestes sans effacer son identité
ni son palier ; la revalidation existante trouve un autre moyen, attend
sans geste, constate une fin ou cède à une priorité gagnante. Aucun
suffixe démenti recopié ni délai ajouté ; refus et renoncements conservés.
Aucun changement dans `planification`, `agendas`, `echanges` ou `signes`.
La condition exacte de la demande reste tenue : un autre objet cible
n'est pas assimilé à un autre moyen de cette condition.

**Preuves initiales : 21 tests verts**, contrat et empathie entiers,
**98,600 s**, un processus réduit. Capture réelle **Aubin Relais 2024,
117503** : Ilse hors perception, demande revalidée, identité et palier
conservés, aucune sortie ni renaissance sur son retour perceptif. Le refus
ancien ne tenant plus, la tête peut être reproposée, mais l'exécuteur
interdit toujours le réessai dans la minute. Deuxième cas **Mathé/Lucien,
mine** : attente hors perception faute de nourriture, reprise sur constat
d'un moyen disponible, repas effectivement servi. Monde, rendu et scène
contrôlés après recharge ; laps entiers/découpés identiques. Fins attestées,
préemptions et absence de recopie d'un suffixe vérifiées. Les scènes de
repas isolent explicitement les vivres portés, sans premier but d'achat.

**Erreur Lucien instruite.** Les compléments avaient donné **28/29**
(**398,297 s**) : contrats internes 5/5, dynamique 9/10, échelle 4/4,
réessai 7/7, secours acquitté 3/3. Le test inchangé de recherche après
reprise du ballot **passe sur `c9459ce` isolée (92,579 s)** et **échoue sur
la branche (67,480 s)** : `KeyError: 'anselme'` à 120 minutes.

La nouvelle trajectoire est conforme au contrat : Anselme conserve sa
demande d'entretien du poêle après le refus d'une lanterne. À 120 min,
fin et reprise sans réponse, attente **palier 4 / valeur 50** ; sécurité
**4 / 11,485**, marge **7,5**, aucun candidat dominant. Il demeure témoin,
le renoncement de Lucien tient, le ballot reste dans le coffre : aucun vol
puis aucune recherche d'Anselme n'ont lieu. En partant du contrôle
historique à 95 min, une seconde dépendance apparaît : après refus de
restitution, Anselme conserve aussi cette demande ; il croit le ballot
sur Lucien et ignore son dépôt à l'étable. L'ancienne trajectoire le
faisait retrouver fortuitement par un autre plan après abandon du but.

**Prémisses du test explicitées, moteur inchangé.** Départ de la capture
95 min (garde sans demande d'entretien en cours), puis information au
propriétaire à 110 min sur le dépôt réel. Il reprend légitimement le
ballot ; Lucien épuise ensuite sa recherche et attend sans nouveau départ.
**Les 30 assertions originales sont identiques** (comparaison AST) et le
test passe en **51,387 s**, avec neuf contrôles monde/rendu/scène après
recharge à 110/120/165 min. Les 49 autres tests étaient déjà verts ;
aucune nouvelle suite complète ni répétition des fichiers inchangés.
Bruts : `lucien-base/`, `lucien-branche/`, `lucien-premisse-finale/`,
`diagnostic-lucien.json`, scripts et captures archivés.

**Banc seul détaché**, indépendant du retour des tests : vingt paires
4 h, Relais/mine/auberge/crue/hameau × 1985/7/42/2024, référence
`0e3e626` en cache ou calculée une seule fois, sonde actuelle 265/271,
un processus réduit. Suspects 219 comparés **nuit par nuit** et retours
Aubin conservés. **Aucun résultat du banc encore revendiqué.** Ni Luna
ni suite complète. Bruts dans
`C:/Users/msics/donjon/artifacts/demande-273-sol/` ; fichier attendu
**`fin-banc.json`**, écrit en dernier. L'ancien `fin.json` (`ok=false`)
reste l'archive de la première campagne arrêtée avant banc. La garantie
porte sur les cas vérifiés ; aucune stabilité générale n'est certifiée.
