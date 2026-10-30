# Lot 333 — A4b, interposition d'un lieu gardé

Branche `codex-garder-lieu`, **non fusionnée**, base d'intégration `4a54090`,
code et tests `887a5b0`, poussés vers origin.
Bruts : `C:/Users/msics/donjon/artifacts/lieu-333/`. Aucun scénario historique,
MJ ou modèle modifié ; ni Luna ni suite complète.

**Invariant.** Biens, protégés et lieux déclarés par `garder` partagent
observation d'approche, poste physique et parole typée. `defense.charges`
inclut les lieux ; `_acces_charge` projette les seuils déclarés ou la position
crue du bien. `approche_vue` exige deux observations visuelles continues ;
`esprits._percevoir` conserve la vue précédente jusqu'à la fin des constats.
Le poste doit être libre et atteignable dès l'événement, puis à chaque pas :
sa libération ultérieure ne crée pas d'interception rétroactive. Obstacles,
occupants, portes et eau viennent des croyances, sans intention privée.
Ces lectures sont recalculées hors de `chercher` ; `_entrees` reste inchangé.
`agendas` partage le premier sous-but, garde endormie comprise. `pnj.agir`
marche sans demander de déplacement ni pousser pour cette interposition.
L'accès est revalidé matériellement ; avertissement et parole sont enregistrés
avant affichage. Une preuve commune empêche la répétition lors de la reprise
du poste. Persister conserve l'épreuve relationnelle existante.

**Vérification ciblée.** **135 tests distincts, douze fichiers verts**,
63,188 s ; reprises finales de 22 puis huit tests, 19,649 et 16,161 s, sans
cumul. Huit nouveaux tests : Gorm/Corvus au Relais et Hugues/Lucien devant
le cellier de l'auberge, gardes déclarées en données d'épreuve seulement.
Poste, parole typée entendue, confiance/rancune, monde, rendu et scène après
recharge ; laps entier/découpé identiques. Personne sûre, approche non vue,
guet lu, accès occupé/bloqué, 31 minutes sans répétition, reprise du poste et
gardien venant de l'intérieur ; aucun coup. Échecs intermédiaires conservés :
montage, vue et accès rétroactif corrigés. L'ancien test de protection regarde
le joueur avant ses deux positions ; assertions conservées.

**Banc terminé, critères du brief satisfaits sur 20/20 paires.** 4 h × Relais,
mine, auberge, crue, hameau × 1985/7/42/2024 : **suspects 219 : 0 → 0 dans
chaque nuit**, zéro plantage, usurpation, coup ou poussée. Référence `f08ef58`
identique en code à la base `4a54090` (`donjon/` et `tools/`) ; vingt nuits
relues du cache, aucune rejouée. Sept chroniques identiques (Relais × quatre,
auberge 1985/7, crue 7), dont six états complets identiques ; crue 7 diffère
en état seulement. Interpositions prononcées **21 → 9** : les conditions
communes de vue et de poste changent aussi les gardes d'objets historiques.
Deux alertes de répétition crue 42 : l'agenda de dette `a1` de Brune passe
sept fois par actif/sommeil sur la référence, dix sur la branche, entre
les minutes 1 et 8 ; origine générale non établie, à surveiller. Une bascule
isolée crue 2024 (Brune ouvre la réserve à 121, Gorm la ferme à 213), sans
série répétée. Aucune garantie générale d'absence de boucle revendiquée.
Calcul détaché réduit, un travailleur : **714,694 s écoulées**, CPU branche
**663,141 s**, sans comparaison aux temps du cache. **`fin.json ok=true`**,
écrit en dernier ; `bilan.json` et `analyse-cloture.json` conservés. Sources
du calcul `887a5b0` inchangées, empreintes vérifiées ; aucun calcul actif.

**Recouvrements et limites.** 330 : `pnj.py` ; 332 : `esprits.py`, `pnj.py`.
Poste contournable ; perception continue, carte déclarée et accès admissible
nécessaires. Aucun agenda historique ajouté : les charges de lieu sont
prouvées par les scènes ciblées, pas par leur fréquence au banc.
