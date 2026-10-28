# Lot 260 — faire ou confier sur les croyances du mandant

Branche `codex-faire-ou-confier-b`, **non fusionnée**, base et brief
`634b869`, 28 octobre 2026. Aucun scénario, MJ, `social.py`, `esprits.py`,
`planification._mesurer_direct` ou `pnj.refus_etape` modifié. Ni Luna ni suite
complète. **Vérification élargie et banc en cours ; lot non déclaré validé.**

`agendas.planifier` appelle une fois `_prochain_sous_but`, puis une fois
`choisir_mandataire`. Les devis explicites restent directs. Pour une charge
sociale, le coût propre est comparé au trajet cru vers le candidat, aux
paroles préparatoires et au devis de son prochain sous-but vu du mandant.
Ce dernier est divisé par la chance d'accord estimée et la fiabilité crue :
`chance_demande + bonus autorite_estimee / 20`, plafonné à 0,95 ; confiance
dirigée / 100, plancher 0,1. L'égalité se départage par identifiant, y compris
face au faire soi-même. Aucun profil ou esprit privé du candidat n'est lu
pour ce classement ; les cycles et la profondeur excluent les candidats
interdits. Un propre plan impossible peut laisser place à une délégation.

Seuls la localisation crue de la cible et le contenu à transmettre sont
projetés comme connaissances transmises. Ces faits passent réellement par
des étapes ordinaires `dire`, puis `echanges.executer` appelle
`echanges.confier(mandat=...)` : accueil et jugement réel du 256, filiation
du 252, enregistrement avant récit. L'avis ne transmet qu'une prévision
qualitative, jamais une mesure inventée. Le devis observateur prépare son
agenda hypothétique sans publier une filiation : les ancêtres privés sont
absents du modèle fermé, notamment lors d'une seconde délégation.

Les acceptations entendues réservent leur sous-but dans le parent ; les
autres destinataires restent essayables. Le parent attend ensuite son
propre constat, sans lire l'avancement privé de l'enfant. Les refus portent
l'identité du mandat dans le contrat commun `deliberation` : deux charges
visant la même personne restent distinctes. Une impossibilité est retenue
sur les croyances du mandant sans les dates de regard ni la trace de ce
refus lui-même ; les autres causes suivent leur durée commune. Après refus,
le choix recalcule un autre tiers ou le plan propre.

**Preuves déjà exécutées : 22 tests distincts**, dont sept nouveaux (les
quinze voisins ont précédé les dernières extensions de refus/avis ; leur
relance est incluse ci-dessous). Gorm → Aubin → Brune et information à Ilse,
clé crue chez Aubin, choix réel par `deliberation.choisir`, paroles et
acceptation enregistrées, aucun déplacement implicite de la cible,
prochain plan social du mandataire ; laps 1800 dixièmes ou 3 × 600
identiques. Monde complet, rendu et scène perçue conservés après recharge.
Déplacement réel hors perception, savoir, possession et relations privés
modifiés sans effet sur le choix ; départ inconnu cru avec effet. Refus
d'accueil puis faire soi-même, identité des refus, égalité, avis qualitatif
et plusieurs destinataires couverts. `git diff --check` propre.

**Calcul détaché prévu/lancé**, deux processus au plus, priorité réduite :
88 fichiers sélectionnés par `rg -l 'choisir\(|agendas\b' tests -g
'test_*.py'` (sur 309, donc aucune suite complète), puis banc 4 h, cinq
scénarios × graines 1985/7/42/2024, référence figée `634b869` avec cache,
puis `mesure_cout` mine 1985, 4 h, départ fixe. Arrêt au premier échec.
Bruts et fichier de fin : `C:/Users/msics/donjon/artifacts/confier-260/`
(`tests.json`, `comparaison.json`, `cout.json`, journaux, `fin.json`).
Les écarts, le compteur 219 et les coûts restent **à lire à la reprise** ;
aucune absence de régression ni conclusion de performance annoncée.

Limites : comparaison du prochain sous-but, pas de garantie d'acceptation
ou de réussite complète ; hypothèse explicite d'une parole préparatoire
crue, vérifiée ensuite par l'échange réel. Le modèle fermé conserve les
limites structurelles du 258. Une croyance nouvelle peut réouvrir une
impossibilité. Aucun compte rendu, suivi vocal, réaffectation sur retard ou
évolution d'ascendant ajouté ; une acceptation n'autorise pas une relance
automatique. Le banc et sa lecture conditionnent la validation du lot.
