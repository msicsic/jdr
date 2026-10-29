# Lot 303 — rejoindre un participant de lieu inconnu avant le geste

29 octobre 2026. Branche **`codex-service-rejoindre`, non fusionnée**, base
intégration **`79beaf1`**. Aucun MJ, scénario ni modèle modifié ; ni Luna,
ni suite complète. Un seul travailleur réduit pour les vérifications.

**Invariant.** Une localisation inconnue ne rend pas le but impossible, mais
ne fournit plus une présence gratuite au geste. Les participants viennent
de `pnj._a_reunir`, avec les venues déjà convenues. La normalisation des
transitions prépare leur contact par `_chercher` : inspection, appel négocié
ou question à un tiers, selon les moyens communs. Le devis peut projeter la
rencontre ; `_couper` arrête le plan publié avant les effets qui en dépendent.
`_mesurer_direct` refuse le geste final sans présence projetée ;
`pnj.refus_etape` revalide les anciens plans avec la cause distincte
« participant à localiser », sans affirmer son absence.

**Charge durable.** `_pulsion` prépare aussi les participants du geste visé
avant la recherche de ses moyens matériels. C'est nécessaire sur la capture :
le parent adopté vise `marmite_1`, désormais vide, tandis que la portion
effective `marmite_1_1` est portée. La même lecture de `_a_reunir` conserve
ce parent pendant la localisation, puis le choix ordinaire reprend sur les
croyances acquises. Aucun délai, registre d'échec ou champ de sauvegarde ajouté.

**Preuves ciblées.** Cinq nouvelles épreuves vertes : capture exacte 289
retrouvée dans les archives 273, Mathe/Lucien à la mine, indépendance du plan
aux positions réelles du bénéficiaire dans toutes les salles des deux
scénarios, devis sans effet, graphe avec suffixe supposé non publié, venue
convenue conservée. Les deux chaînes vérifient le parent adopté, le contact,
le service réussi avec lieu cru connu, les portions et la chronique ; monde,
rendu, scène et texte identiques après recharge, six minutes entières ou
découpées. La capture n'est adaptée que par le retrait des deux champs
expérimentaux du 273, comme au diagnostic 289.

La passe des neuf fichiers directement concernés est consignée dans
`tests-cibles.json` ; les contre-épreuves 251 pour un lieu cru connu sont
conservées sans modification. Les premiers onze tests voisins et les cinq
nouvelles épreuves ont aussi été exécutés séparément pendant le travail.

**Banc rapide en attente.** Auberge, mine, Relais × 1985/7/42/2024 × quatre
heures, référence intégration `79beaf1` par le cache commun du comparateur,
puis worktree courant. Un travailleur, priorité réduite ; sortie et fichier
de fin même en cas d'échec dans
`C:/Users/msics/donjon/artifacts/service-303/` : `banc.json`, `banc.log`,
`synthese.json`, **`fin.json` écrit en dernier**. La synthèse donne par nuit
suspects 219, alertes de boucle, usurpations, services de portions, appels,
questions de localisation et recherches du planificateur. Ces dernières
comptent les calculs de plans, pas chaque inspection physique. Les références
manquantes seules sont calculées et rangées ; aucun temps issu du cache
n'est comparé. Les critères du banc restent à lire avant clôture du lot.

**Limites.** La rencontre et l'accord restent incertains ; une croyance
périmée sur un tiers peut encore faire échouer une question, comme dans la
capture (Hugues cru présent). Les nouvelles chaînes garantissent l'absence
de service exécuté en échec, pas la réussite de tout geste social préparatoire.
Pas de preuve universelle d'absence de boucle ; aucune conclusion de nuit
avant le bilan détaché. Les rendus du joueur et l'exécution continuent de
constater le monde réel ; sa position cachée n'entre pas dans le plan.
