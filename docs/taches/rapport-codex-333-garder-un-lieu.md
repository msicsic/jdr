# Lot 333 — A4b, interposition d'un lieu gardé

Branche `codex-garder-lieu`, **non fusionnée**, base d'intégration `4a54090`,
code et tests `887a5b0`, poussés vers origin.
Bruts : `C:/Users/msics/donjon/artifacts/lieu-333/`. Aucun scénario historique,
MJ ou modèle modifié ; ni Luna ni suite complète.

**Invariant.** Une charge crue, bien, protégé ou lieu déclaré par `garder`,
emploie la même observation d'approche, le même poste physique et la même parole
typée. `defense.charges` conserve aussi les lieux ; `_acces_charge` projette
leur géométrie sur les seuils des sorties, et les biens sur leur position crue.
`approche_vue` exige deux observations visuelles continues : retrouver quelqu'un
ailleurs après l'avoir perdu de vue ne prouve pas un mouvement observé. La vue
précédente reste donc disponible jusqu'à la fin de `esprits._percevoir`.

Le poste doit être libre et atteignable dès l'approche, puis à chaque pas.
Sa libération ultérieure ne fabrique pas une interception rétroactive. La
lecture emploie obstacles, occupants et portes crus, franchissements communs
et admissibilité des routes d'eau ; aucune destination privée de l'approchant.
Ces lectures sont recalculées hors de `chercher` : aucune nouvelle entrée du
graphe de planification ni de son cache, `_entrees` reste inchangé.
`agendas` donne le même premier sous-but aux gardes d'objet et de lieu,
y compris endormies. `pnj.agir` marche réellement vers le poste sans
demander de déplacement ni pousser pour cette interposition. L'exécution
revalide matériellement l'accès, enregistre l'avertissement et sa parole
avant affichage. La preuve commune empêche de le répéter lors de la reprise
du même poste. Persister après l'avertissement garde l'épreuve relationnelle
existante, même lorsqu'il est trop tard pour intercepter sans déplacer autrui.

**Vérification ciblée.** **135 tests distincts, douze fichiers verts**,
première consolidation 63,188 s ; reprise de 22 tests après l'exigence de
source visuelle précédente, 19,649 s ; huit nouveaux tests repris après ajout
du contrôle du registre des paroles, 16,161 s. Huit nouveaux tests : Gorm à l'accès
d'une salle du Relais contre Corvus ; Hugues devant le cellier de l'auberge
contre Lucien. Gardes déclarées dans les seules données d'épreuve. Poste,
parole typée réellement entendue, confiance/rancune, monde, rendu et scène
après recharge ; même laps entier ou découpé. Personne sûre, approche non
vue, guet lu, accès occupé ou bloqué, trente et une minutes sans répétition,
reprise du poste et gardien venant de l'intérieur vérifiés. Aucun coup dans
ces scènes. Les échecs intermédiaires sont conservés : placements et agendas
du montage, puis défauts de vue et d'accès rétroactif corrigés. L'ancien test
de protection regarde maintenant le joueur avant ses deux positions, au lieu
de seulement le retrouver dans son champ ; ses assertions sont conservées.

**Banc en cours.** `tools/valider_lieu_333.py` lance 4 h × Relais, mine,
auberge, crue, hameau × 1985/7/42/2024, un travailleur réduit. Référence
`f08ef58` : `git diff --quiet f08ef58 4a54090 -- donjon tools` vaut 0 ;
les vingt nuits ont été relues du cache, aucun recalcul de
référence autorisé par le lanceur. Il conserve chaque nuit, exige aucune
hausse des suspects 219 par paire, zéro plantage/usurpation/coup, et écrit
`bilan.json`, puis **`fin.json` en dernier, même en échec**. Démarrage réel
vérifié : PID Python `47816`, priorité `BelowNormal`, `debut.json` sur
`887a5b0`, vingt références chargées ; fenêtre cachée. Aucune conclusion
de banc ni de vitesse avant lecture de ce fichier.

**Recouvrements et limites.** Lot 330 : `pnj.py` ; lot 332 : `esprits.py` et
`pnj.py`. Changements localisés, sans reprendre leur code. Le poste reste
contournable ; cette garde n'est ni un verrou ni une attaque préventive.
Perception continue, carte déclarée et poste admissible restent nécessaires.
Les nuits historiques ne contiennent aucun nouvel agenda : les charges de
lieu sont prouvées par les scènes ciblées, pas par leur fréquence au banc.
