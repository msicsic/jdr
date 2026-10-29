# Lot 302 — autorité déclarée dans la crue du hameau

Branche `codex-a5-donnees-hameau`, **non fusionnée**, base intégration
`79beaf1`, 29 octobre 2026. Données et observation seulement : aucun moteur
de décision ni MJ modifié. Ni Luna ni suite complète.

**Invariant.** Le scénario déclare le statut de Gorm, sans distribuer de
mandat. Responsable du Relais dans ses cinq salles, hors digue extérieure,
il est reconnu pour `amener` et `informer` par lui-même, Aubin, Brune et Ilse.
Gorm doit connaître son propre statut pour l'estimation subjective 258.
Maël et Sève, nouveaux évacués connaissant la rivière mais pas les salles
basses, et Corvus ne reçoivent pas cette connaissance.

Trois ascendants orientés : **Aubin → Gorm 60**, car le passeur observe les
vannes et lui en rend déjà compte ; **Maël → Aubin 30**, confiance dans un
voisin expérimenté du même cours d'eau ; **Sève → Aubin 40**, lien initial
plus confiant et affectueux que celui de Maël. Ni confiance ni dette ni autre
valeur changée. Tous les autres ascendants restent neutres. Aucun ajustement
après mesure pour obtenir artificiellement un mandat.

`banc_pnj.mesures_mandats` lit les copies publiques des projets et filiations :
propositions jugées, acceptations, refus par cause, confirmations séparées,
comptes rendus émis et réaffectations à un nouveau tiers. Les mesures du banc
sont les différences début/fin ; l'audit conserve aussi le cumul et les
projets pour expliquer l'absence de mandat. Une reprise par le mandant n'est
pas comptée comme une réaffectation à un tiers. Aucun texte narratif analysé,
aucun état ajouté au monde, aucun devis hypothétique compté.

**Tests : 69 distincts, onze fichiers verts**, deux travailleurs réduits.
Première passe : 31 tests / six fichiers, 30,918 s ; dernière version du
nouveau fichier et voisins A5/outils : 43 / six, 45,014 s. Recouvrement exclu.
Statut sourcé et deux portées, connaisseurs/ignorants, liens orientés et
neutralité des autres liens, absence d'attribution initiale ; contre-épreuve
sans autorité, deux mandats `amener`/`informer` : même devis et même total,
trois points de DD expliquent seuls l'accord. Demandes ordinaires dans une
scène du Relais hors crue inchangées. Réaffectations hameau/mine et comptes
rendus des deux sortes réellement exécutés, confirmations sans double compte,
pureté des mesures et tranches vides. Monde, scène et rendu après recharge,
plus les tests voisins de compte rendu et réaffectation avec laps découpés.

**Banc rapide en attente de clôture** : hameau 4 h × 1985/7/42/2024,
référence figée `79beaf1` via cache, puis branche figée ; deux processus
réduits au plus. Lanceur détaché, fichier final écrit même en cas d'échec :
`C:/Users/msics/donjon/artifacts/hameau-302/fin.json`. `comparaison.json`,
`analyse.json`, tests et journal dans ce même dossier. L'analyse compare
boucles, constats, usurpations et suspects 219 nuit par nuit ; aucun gain
de performance ne sera déduit des temps en cache.

**Limites établies.** Le scénario ne contient aucun agenda `amener` ou
`informer` ; la naissance commune actuelle produit `obtenir` et `récupérer`.
L'autorité seule ne crée donc pas une charge à déléguer : en l'absence de
mandat, aucun coût ni jugement d'A5 n'est atteint. Le banc doit confirmer
les nombres naturels, pas transformer les données pour contourner ce manque.
Le profil incohérent à échéance négative est refusé avec `attendu`. En
revanche, le validateur historique du **statut incohérent** utilise des
assertions, sans `attendu` : cette garantie du brief n'est pas intégralement
livrée. Sa correction exige un lot moteur, interdit ici ; aucun test ne
fabrique un attendu et aucune validation n'est affaiblie. Le premier essai
de tests sous sandbox échouait sur les temporaires Windows ; les deux
passes retenues ont été autorisées hors sandbox.
