# Lot 260 — faire ou confier sur les croyances du mandant

**Reprise après 259, en cours.** Fusion sans rebase de
`origin/integration 1355f7a` dans `ab21fb3` ; aucun conflit de code, seul
`etat-dev.md` réconcilié en conservant les deux bilans. Relance des
88 fichiers ciblés et des voisins `test_corps` / `test_relations_socle`
(90 fichiers, aucune suite complète), puis comparaison crue/Relais 4 h,
quatre graines, contre `1355f7a`, avec cache. Les réserves ci-dessous
décrivent **l'ancien moteur sans 259** : elles ne valent pas verdict sur la
fusion. Lecture croisée des quatre versions prévue pour isoler l'effet du
259 sur l'attente, l'oisiveté et les activations/sommeils de Brune.
Calcul détaché, deux travailleurs réduits au plus, résultats par fichier
conservés au fil de la passe ; arrêt avant le banc si les tests échouent.
Bruts : `C:/Users/msics/donjon/artifacts/confier-260/apres-259/` ;
fin attendue `fin.json`. Branche pas encore déclarée prête pour la suite
complète du superviseur.

`codex-faire-ou-confier-b`, **non fusionnée**, base `634b869`, moteur
`23a1b83` (implémentation `c5d7301`), 28 octobre 2026. Ni scénario, MJ,
`social.py`, `esprits.py`, `_mesurer_direct` ou `pnj.refus_etape` modifié ;
ni Luna ni suite complète.

**Contrat.** `agendas.planifier` appelle le prochain sous-but puis le choix
de mandataire. Coût propre contre trajet cru vers le tiers, paroles
préparatoires et devis observateur du prochain sous-but, pondéré par chance
d'accord (`chance_demande + autorite_estimee.bonus / 20`, plafond 0,95) et
fiabilité crue (confiance / 100, plancher 0,1). Égalité par identifiant ;
cycles et profondeur exclus, aucun esprit privé du tiers dans le classement.
Le lieu de la cible et le contenu sont réellement énoncés par `dire`, puis
`echanges.executer` passe par `echanges.confier(mandat=...)` : accueil,
jugement réel, filiation et enregistrement avant récit. L'avis reste
qualitatif. Le devis hypothétique ne reconstruit pas les ancêtres privés.
Les refus distinguent les mandats ; leur cause matérielle retient les
croyances sans dates de regard ni sa propre trace. Après refus : autre tiers
ou plan propre. Les acceptations réservent leur cible, sans lire l'enfant.

**Arbitrage propre au 260.** Deux preuves après recharge ont révélé qu'un
agenda terminal pouvait encore proposer une délégation. La garde commune
actif/sommeil est corrigée dans `23a1b83` ; preuve rouge sur `c5d7301`
conservée dans `cycle-vie-avant.json`, deux charges vertes après correction.

**Tests : 754 / 88 fichiers ciblés**, huit assertions et une erreur
héritées, **neuf traces complètes identiques sur la base exacte** (huit
méthodes rejouées seules, seuls chemins et numéros de ligne neutralisés).
`arbitrage-tests.json` distingue ces défauts du 251/259 ; le 259 n'est pas
repris. **115 tests d'agendas / 17 fichiers verts**, dont huit nouveaux ;
**32 tests / cinq fichiers revérifiés verts** après la garde terminale,
sans double compte. Gorm → Aubin → Brune et information à Ilse : choix réel,
paroles, jugement et prochain plan social, aucun portage implicite. Monde,
rendu et scène rechargés ; laps 1800 ou 3 × 600 identiques. États privés
sans effet sur le choix, départ cru avec effet, refus puis plan propre,
égalité, avis et plusieurs cibles couverts.

**Banc terminé : vingt paires 4 h, zéro plantage ou violation signalée.**
Relais/mine/auberge/crue/hameau × quatre graines ; référence `634b869`,
branche `23a1b83`. Vingt références absentes calculées et rangées une fois,
aucune rejouée. **16 paires entièrement identiques** ; crue 1985 : monde et
chronique identiques, **1 980 → 2 042 recherches** seulement. Crue 7/42/2024 :
à l'instant 978, Gorm envisage un tiers (tête de plan vers la crypte), puis
les observations font reprendre le plan propre ; ordre des gestes et des
échanges modifié. **Aucun mandat prononcé dans le banc** : acceptations
réelles prouvées par les profils de test. Compteur 219 : suspects **2 → 1**,
aucune hausse par nuit (auberge 2024 **1 → 1**, crue 7 **1 → 0**) ; cycles
**489 → 490**, préemptions **46 → 53**, à expliquer **55 → 59**, dérives
**233 → 232**. Réserve : crue 42, deux alertes de répétition (9 activations /
9 sommeils de Brune) ; oisiveté urgente crue 7/42/2024 **0/0/80 → 50/70/215**,
attente **0/0/45 → 15/70/160** minutes. Ces effets ne certifient pas une
boucle, mais interdisent une conclusion de non-régression globale.

**Coût mine 1985, 4 h fixe : compteurs et empreintes identiques**,
**823 recherches, 364 neuves, 13 464 nœuds, 88 477 gestes produits**.
CPU indicatifs **20,766 / 22,000 s**, sans conclusion de performance.
Deux travailleurs réduits au plus ; aucun calcul actif. Le premier lanceur
interrompu avant résultats est conservé dans `fin-interruption.json`.

**Limites et décision.** Correction fonctionnelle conservée ; réserves du
banc et neuf défauts hérités explicitement maintenus, pas d'exception de
scénario. Coût du prochain sous-but, pas garantie d'adhésion ou de réussite ;
limites structurelles du modèle fermé 258 conservées. Une nouvelle croyance
peut rouvrir une impossibilité. Une acceptation attend le constat propre,
sans compte rendu ni réaffectation sur retard. Bruts et analyses :
`C:/Users/msics/donjon/artifacts/confier-260/` ; `fin.json` termine la reprise.
