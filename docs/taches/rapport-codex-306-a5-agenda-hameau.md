# Lot 306 — agenda d'évacuation du hameau

Branche **`codex-a5-agenda-hameau`**, non fusionnée, base initiale `7ec839e`.
Nouvelle reprise laptop, 30 octobre 2026 : fusion sans rebase de
`origin/integration` **`19c9b6da`** (358 et 335) dans `fa537794`.
**Capture corrigée et tests ciblés verts ; nouveau banc détaché en cours.**

**Invariant et données.** Gorm reçoit `evacuer_crue`, `amener` vers
`chambre_cloche`, comme dans la crue, pour Ilse, Brune, Maël et Sève.
Gorm accueille les évacués ; Maël connaît Gorm, Sève connaît Aubin/Ilse ;
les deux nouveaux évacués ignorent les salles basses. Aucun mandat initial,
lien, coût, savoir ou charge `informer` ajouté ; aucune attribution forcée
ni donnée ajustée après mesure. Moteur et MJ identiques à l'intégration.

**Fusion et tests.** Seul `etat-dev.md` était en conflit : version de
l'intégration plus une entrée de huit lignes. Les deux assertions d'occasions
restent strictes : empreinte complète **85955d0e…**, puis **72a33d77…** en
retirant le seul agenda 306 ; six autres empreintes inchangées.
**69 tests / onze fichiers verts, 149,283 s**, deux travailleurs réduits :
les neuf fichiers du 306 (agendas/autorité/scénario du hameau, occasions,
faire/confier, devis de l'observateur, compte rendu, réaffectation, récit),
plus les huit régressions 358 et les sept tests de suivi vocal 335.
Maël/Sève marchant après accord, monde et rendu après recharge, temps
entier/découpé contrôlés. Aucune suite complète ni Luna.

**Capture réelle 1985 à t=4200, après 358.** Fichier original du premier banc,
strictement identique à la fixture du 358, SHA-256 **1529ca9f…630c004a**.
Le refus de Maël minute 6 tient encore ; le plan de Gorm date de minute 4.
`refus_etape` refuse désormais l'étape, puis `agir` renvoie **MANQUE** :
aucune parole, aucun geste et état complet inchangé. Sauvegardes/recharges
monde, rendu, scène et écoute identiques. Sur deux minutes, reprise en bloc
et quatre demi-minutes donnent le même état et le même affichage ; aucun
`confier` à **4200**. Les réessais à **4461** ne passent que si le refus
n'est plus retenu ; l'espion le vérifie sur chaque trajet (bloc et découpé).
Preuve dans `verification-capture.json`, captures avant/après conservées.
Le défaut bloquant du premier banc est donc levé sur sa capture originale.

**Nouveau banc demandé.** Hameau **4 h × 1985/7/42/2024**, contre `main`
**`0bad227`** : les quatre nuits avec la clé exacte **923e7cae47** sont
présentes dans le cache commun et relues, sans recalcul. Branche jouée
ensuite à deux processus réduits au plus, captures finales et vérification
de recharge monde/rendu/scène/écoute. Puis crue d'origine : empreintes
**2 h × quatre graines** contre l'intégration `19c9b6da`, pour isoler les
données du 306. Références manquantes de cette configuration seules jouées
et rangées. `analyse.json` et `comparaison.json` donneront mandats, causes
des refus, comptes rendus, réaffectations, évacuations, suspects 219,
boucles, usurpations et plantages. `fin.json` est écrit même en cas d'échec.
**Validation comportementale en attente** : la preuve sur capture ne remplace
pas les quatre nuits. Aucune causalité exclusive ni gain de performance
attribué au 306 face à `main`, antérieur aux autres lots de l'intégration.

**Première reprise conservée** (`2d696f65`, avant 358/335) : 20 propositions,
six accords, cinq comptes rendus ; quatre évacués dans chaque graine,
zéro plantage/usurpation, crue 4/4 empreintes identiques. Suspects 219 zéro,
23 retours à expliquer ; banc non validé à cause du `confier` à 4200.
Les mesures complètes et le diagnostic restent dans Git `fa537794` et
`C:/Users/msics/donjon/artifacts/agenda-hameau-306/reprise-integration/`.
Les conclusions de ce banc ne sont pas attribuées au nouveau calcul.

**Nouveaux bruts, dans le dépôt principal du laptop :**
`C:/Users/msics/donjon/artifacts/agenda-hameau-306/reprise-358-335/`
(`tests.json`, `verifier_capture.py`, preuves, `lancer.py`, journaux,
comparaisons, captures finales, fichier de fin attendu **`fin.json`**).
