# Lot 342 — attribution réalisée, validation finale en cours

30 octobre 2026. Branche documentaire `codex-attribution-groupe1`, base
`16b18a7`. [Matrice des 33 incidents](attribution-codex-342-groupe1.md).
Le lot ne sera clos qu'après lecture de la validation finale.

**Preuve causale.** Référence exacte `e37d9ee`, puis chaque lot 313/315/332/333
seul : 27/22/23/22/22 tests comptés, 8/14/2/11/1 incidents ; 2 177,100 s,
deux travailleurs réduits au plus. Une méthode absente n'est pas comptée verte.
Six incidents `_retentir/emission` restent au 339 ; l'échec mine est aussi
reproduit sur l'intégration. La lumière superpose un nouvel échec en amont
et une réserve antérieure distincte. Les interactions sont prouvées par retrait
d'un seul lot ; aucune attribution sur la seule lecture du code.

**Correctifs poussés.** Le 313 (`cddc76e`, correctif `de03f87`) admet une
position absente comme inconnue dans la perception commune, sans enrichir le
devis fermé avec le joueur réel. Neuf tests de devis verts : deux charges,
mutation du joueur réel, monde/rendu/scène rechargés. Le 332 (`4da7dc4`)
distingue direction et interprétation : une référence requise absente n'admet
aucun savoir relationnel ; la direction seule ne réveille pas le choix du but
avant la rotation. L'ordonnanceur commun continue de permettre le réflexe au
prochain geste libre. Aucun scénario ni prompt modifié. Les prototypes de
priorité et de rétention de direction sont écartés, sans garantie générale
revendiquée à leur sujet. Dernière passe 332 : **63/64 tests verts**, réserve
unique de la capture d'abri, attente corporelle adaptée ensuite ; nouvelle
régression d'admission verte dans deux scénarios.

**Attentes et scènes.** Quatre captures retrouvent leur hash historique exact
après retrait strict du seul registre vide. Deux captures des étapes chaînées :
différences complètes de registres/provenance des signes seulement, huit autres
oracles identiques ; nouveaux hashes complets, visites 313 conservées. Sève
conclut à 82/83 plutôt que 83/84 : le 315 (`beaecc7`) conserve deux actes
uniques ordonnés et la borne 84. Avec 313/333, Odile réserve le briquet pour
son secours concurrent ; le 333 (`40bd537`) isole ce secours dans la scène qui
mesure l'emprunt pour agir soi-même, sans changer ses assertions. La capture
d'abri finit réellement avec Aubin assommé : corps et indisponibilité remplacent
l'ancien plan attendu ; monde/vue et déplacements bloc-découpé restent exigés.

**Reconstruction et calcul.** Essai `94329d3`, depuis `origin/integration
da5f795`, quatre branches corrigées ; documentation des deux côtés conservée,
aucun changement de `jeu.py` par rapport à cette base. Validation détachée :
seuls fichiers en incident et tests directement concernés, puis banc 4 h ×
cinq scénarios × quatre graines, cache de `main` réutilisé, aucune référence
disponible rejouée. Ni comparaison de vitesse avec des temps de cache, ni Luna,
ni suite complète. Deux travailleurs réduits au maximum, phases séquentielles.
Chaque rouge final hors 339 reçoit un témoin sur `da5f795` ; une méthode rouge
ne suffit pas à établir une cause identique.

Bruts `C:/Users/msics/donjon/artifacts/groupe1-342/`, preuves et prototypes
conservés. Fin attendue : **`validation-finale/fin-validation.json`**.
`calcul_termine` ne signifie pas `lot_valide` : tests et banc restent à lire.
Aucun zéro incident final ni absence générale de boucle revendiqué avant cela.
