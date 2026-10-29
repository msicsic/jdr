# Lot 298 — U-M inventaire

Branche `codex-um-inventaire`, base intégration `83a2e89`, **non fusionnée**.

## Changement et invariant

Le panneau d'inventaire propose poser, remettre à une personne explicitement
choisie, manger une portion, allumer/éteindre et prélever une pièce d'un lot.
Chaque choix envoie un `DescripteurPublic` U-D : référence exacte du bien,
destinataire public et quantité moteur, sans analyse de texte ni modèle.
Les mêmes constructeurs et validateurs produisent le plan de la commande
équivalente ; le refus G2 ou le résultat G4 reste celui du moteur, sauvegardé
avant affichage. Aucun changement de scénario ni règle de faisabilité en page.

`pont.inventaire_public` projette les affaires directement dans la besace,
avec leurs seuls nom, référence, type et quantité ; l'état lumineux ne figure
que s'il est vu. Les affaires portées restent ciblables dans le noir.
`destinataires_publics` ne donne que les personnes vues et à portée. Les
identités inconnues gardent leurs références opaques ; une référence privée,
un destinataire absent, une quantité non admise ne sont jamais substitués ou
ignorés. La réception revalide le choix, sans nom ou alias recherché.
`geste_local` construit aussi le raccourci `prelever <lot>` vers l'opération
existante. Aucun fichier du MJ, `jeu.py`, `tui.py` ou mécanique PNJ modifié.

## Vérification et mesures

**42 tests distincts / quatre fichiers verts**, zéro échec, erreur ou ignoré :
inventaire, descripteur U-D, web et matière. Deux travailleurs au plus,
priorité réduite, interpréteur du dépôt principal. Les vrais boutons et
callbacks Node envoient les corps HTTP contrôlés, ensuite joués par la boucle
réelle avec MJ actif et interdit d'appel, analyseur interdit pour le clic.
Douze couples geste/bien comparent plan, effets, texte exact, monde, scène,
fiche et carte après recharge : second bien homonyme, deux lots de tailles
différentes, deux sources de lumière, portions, deux destinataires homonymes.
Autres épreuves : cible périmée pour les six gestes, personne partie/éloignée,
lot devenu pièce unique, prélèvement et affaires dans le noir, absence de
destinataire, mode sans carte, contenu fermé caché et projection sans règles
ni identités privées. Les tests U-D conservent leur transport HTTP réel.

`mesures.json` conserve dix parcours des callbacks : **10 saisies textuelles
évitées**, **2 clics jusqu'à l'effet**, **3 pour la remise** (bien, geste,
personne). Zéro appel modèle sur les parcours exécutés ; aucun gain de délai
réseau ou gain causal d'appels déduit. Pas de Luna, de banc PNJ ou de suite
complète : entrée d'interface seule, garanties moteur existantes réutilisées.

## Limites et livraison

Quantités actuelles du moteur : une portion mangée ou une pièce prélevée ;
poser/remettre conserve le lot entier. Pas de quantité arbitraire inventée,
ni d'outils/destinations, de corps ou de social supplémentaire. Les contenus
de contenants portés ne sont pas ajoutés au panneau. Le menu annonce le verbe,
sans garantir l'accord ni la réussite ; confirmations moteur conservées.

Bruts, sonde, mesures, essais initiaux et bilan retenu `fin-cloture.json` :
`C:/Users/msics/donjon/artifacts/um-inventaire-298/`. Les premiers échecs étaient
des fixtures invalides (charge, identité ajoutée, lieu de PNJ et souvenirs
avant rafraîchissement), corrigées sans changement moteur. Branche livrée
sur `origin/codex-um-inventaire`. Aucun calcul actif ; fusion au superviseur.
