# Attribution des 33 incidents du groupe 1 — validation finale en cours

Suite source `6f490ba` : 13 échecs et 20 erreurs. Référence exacte `e37d9ee`.
Témoins isolés : 313 `e5d5d9e`, 315 `1b6e2b3`, 332 `d42bb4e`, 333 `ac8bf5d`.
V = méthode verte, R = incident reproduit. Une méthode absente n'est jamais
une preuve verte. Les numéros et noms complets viennent de
`C:/Users/msics/donjon/artifacts/groupe1-342/reprise-1/incidents.json`.

P : V référence, R 313 seul, `KeyError: position` dans la perception du devis.
Correction `de03f87` : une position inconnue ne donne aucune présence visible,
sans réintroduire une position réelle dans le modèle fermé.
E : même `_retentir/emission` reproduit sur référence exacte, réservé au 339.

| Nº | Incident (fichier et cas unique) | Lot / classe | Preuve et correctif |
|---:|---|---|---|
| 1 | agendas_destinataires / deux décès, Ilse | 313 / défaut | P. |
| 2 | boucles_pnj / palier menacé, laps découpé | 313 / défaut | P. |
| 3 | boucles_pnj / gagner un abri sans alternance | 313 / défaut | P. |
| 4 | bourse_redemandee / mine Mathe–Rémy | 332 / défaut | V référence, R 332 seul ; sans le seul réveil ajouté dans `lire`, V. Admission du signal corrigée, oracle inchangé. |
| 5 | completion_preuves / joss-622-epuise | 332 / attente périmée | Seuls `regards_suivis={}` ajoutés ; retrait strict → ancien hash exact `9aa2fb…`. |
| 6 | completion_preuves / tilo-566-epuise | 332 / attente périmée | Même preuve → ancien hash exact `862c87…`. |
| 7 | completion_preuves / joss-622-plan | 332 / attente périmée | Même preuve → ancien hash exact `c4f41c…` ; résultat/coût conservés. |
| 8 | completion_preuves / mine-480 | 332 / attente périmée | Même preuve → ancien hash exact `9bbfd4…`. |
| 9 | corps_blessable / dépouilles, crue/Ilse | 313 / défaut | P. |
| 10 | detecter_changements_avis / audit mesuré | Préexistant | E. |
| 11 | dynamique_besoins / Lucien après reprise du ballot | 332 / défaut | V référence, R 332 seul ; sans réflexe V. Réveil avant geste retiré, oracle inchangé. |
| 12 | eau / debout dans l'eau | 313 / défaut | P. |
| 13 | eau / entrer trempe le joueur | 313 / défaut | P. |
| 14 | eau / salle noyée infranchissable | 313 / défaut | P. |
| 15 | eau / alarme sans passage | 313 / défaut | P. |
| 16 | eau / feu noyé | 313 / défaut | P. |
| 17 | eau / salles basses mouillées puis noyées | 313 / défaut | P. |
| 18 | etapes_chainees / mine | 332 / attente périmée | V référence, R 332 seul. Diff complet : registres/provenance des signes seulement, huit autres oracles identiques. Nouveau hash complet `f6fef4…`, visites 313 conservées. |
| 19 | etapes_chainees / auberge | 332 / attente périmée | Même preuve : registres vides et `directions={}` ; huit autres oracles identiques. Hash complet `52bb40…`. |
| 20 | localisation_crue / temps entier ou découpé | 313 / défaut | P. |
| 21 | lumiere / Rémy allume puis ménage sa lampe | 332 / attente de parcours périmée, et oracle antérieur incohérent | Sans 332, extinction puis `1 != 2` ; avec 332, Rémy reste au baraquement obscur sans connaître la chandelle et garde légitimement sa lampe. La chandelle réelle a `luminosite=1`. `c3db8e2` prépare explicitement le second stimulus du test (bureau, source connue de niveau 2), sans forcer l'extinction ; toutes assertions finales conservées, test vert. |
| 22 | mine / noir et protecteurs | Préexistant | Même assertion `False is not true : set()` sur référence et 315 seul. 313/333 rendent parfois la méthode verte sans démontrer la correction de sa cause. Inchangé. |
| 23 | pas_compagnons / service admissible, vente prioritaire | 332 / défaut | V référence, R 332 seul ; sans interprétation d'une relation privée de référence, ordre original V. Référence exigée par le contrat du signe, pas par sa phrase ; oracle inchangé. |
| 24 | reclamations_repetees / Sève avant 83 | 313 × 315 / attente périmée | 315 seul ou essai sans 313 : 83/84 ; sans 332 ou sans 333 : 82/83. Deux remboursements uniques, monde/textes bloc-découpé identiques. `dee756a` conserve ordre et borne maximale 84. |
| 25 | recours_prioritaire / capture sans navette | 332 / défaut d'ordonnancement, avec interactions ultérieures | V référence initiale, R 332 seul. Le signal préparé devait attendre derrière le bavardage facultatif ; `3acd5c7` le fait exécuter à la disponibilité du PNJ, sans réveiller le choix du but avant sa perception. L'oracle initial d'abri est intégralement restauré par `c3db8e2`, test vert dans l'assemblage. Le KO observé sur l'ancien témoin n'est plus utilisé comme oracle de substitution. |
| 26 | rejeu / lumière, autre scénario | Préexistant | E. |
| 27 | rejeu / page et filtres | Préexistant | E. |
| 28 | rejeu / gestes illicites et témoins | Préexistant | E. |
| 29 | rejeu / page par graine | Préexistant | E. |
| 30 | rejeu / setUpClass RejeuTests | Préexistant | E ; échec de classe conservé comme un incident. |
| 31 | taches_payees / emprunter le bien du payeur | 313 × 333 / attente de scène périmée | V chaque lot seul ; retrait 313 ou 333 → V, retrait 332 → R. À 116 Odile engage un allumage d'empathie et réserve son briquet : devis Tilo encore disponible, fourniture indisponible. `b6045cf` isole ce secours dans la scène d'emprunt ; toutes assertions conservées. |
| 32 | verifier_eau / ne pas descendre ni chauffer en salle bientôt noyée | 313 / défaut | P. |
| 33 | verifier_eau / sortir avant noyade | 313 / défaut | P. |

Bruts sous `C:/Users/msics/donjon/artifacts/groupe1-342/` :
`reprise-1/`, `retrait313/`, `retrait332/`, `retrait333/`,
`decomposition332/` (ablation d'une seule fonction, pas un correctif),
`preuve-empreintes.json`, `tache-abandon.json`, `abri332.json`.
Les prototypes non retenus restent dans `experiences332.diff` et `sonde332-*`.
Première reconstruction `94329d3` sur `da5f795` : **279 tests / 27 fichiers,
11 incidents**. Huit réserves finales étaient aussi rouges sur cette nouvelle
intégration : deux dans `boucles_pnj`, deux dans `dynamique_besoins`, deux
sous-cas des étapes chaînées, lampe vide et aide 541. Les différences de
trajectoire ne sont pas déclarées identiques pour cette seule raison.
Les six incidents du 339 et celui de la mine passent sur cette reconstruction,
sans être attribués aux correctifs du 342.

Les trois points restants (regard non suivi dans la fenêtre du test, lampe,
capture d'abri) sont repris par `3acd5c7` et `c3db8e2` : **12/12 tests ciblés
verts**, y compris tous les tests d'attention conjointe et les deux scènes
historiques, monde/rendu/scène et laps découpé conservés. Nouvel essai
`93d5a25` ; reprise des fichiers concernés et vingt nuits de branche sous
`cloture-1/`, résultats encore à lire. Référence historique : vingt nuits du
cache `c870c8b`, instrumentation `1f6b05da83`, sans réexécution ; observation
distincte de l'outil actuel, aucune comparaison de vitesse.

Limite conservée : dans les témoins de retrait sur la base récente, enlever
332 laisse encore 33 passages d'Aubin, enlever 313 en laisse dix. Cette
interaction 313/base récente n'est pas déclarée corrigée en général parce
que l'assemblage avec le réflexe ordonnancé retrouve l'abri ; la preuve du
342 porte sur ses contrats et ses parcours exercés, pas toutes les variantes.
