# Lot 99 — Vérification Luna de l’intégration b0042c9

26 octobre 2026 — **Validation partielle : achats exécutés aux deux passes, fausse absence d’Ilse toujours affichée.** Aucun code modifié. Même méthode et vingt scripts que le lot 79 : **40 parties, 302 saisies, 136 tours MJ, 406 appels**, Luna `gpt-6-luna`/ChatGPT medium/libre, budget 200 par groupe/passe, quatre exécutions au plus à priorité réduite, copies temporaires et `SEUIL_AUTH` principal. Branche issue de `49a7df3`, code identique à **b0042c9**. Quarante parties rangées sous ce commit, SHA-256 source/cache identiques. Références **42bb9c0, f033364, fbcf0ff et 882907c uniquement relues** ; 257 fichiers de cache inchangés, 142 parties historiques sélectionnées identiques aux bruts antérieurs.

Chaque cellule : **main (42bb9c0) → 882907c → b0042c9** ; moyennes des deux passes, médiane sur leurs tours réunis. Refus = validations moteur/fidélité/contre-revue ; relances et replis = détecteurs du lot 79. Les refus locaux sans appel restent hors de ce compteur. Main ne couvre que onze scripts.

| Groupe | appels/tour | s/tour | médiane s | relances | refus | tours avec refus | replis | tours MJ |
|---|---|---|---|---|---|---|---|---|
| référence | 3.05→2.63→2.77 | 12.1→11.6→9.5 | 10.66→12.04→8.86 | 3→1→2.5 | 12.5→7→7.5 | 8→6→6 | 0.5→0→1 | 33→31→31 |
| signes | 2.57→2.50→2.42 | 11.3→13.7→8.4 | 8.71→11.30→7.33 | 0.5→1.5→1 | 2→0→0 | 1→0→0 | 0→0→0 | 7→6→6 |
| ambiance | 3.67→2.00→2.67 | 16.6→10.7→9.1 | 15.77→9.62→9.75 | 2.5→0→1 | 0→0→0 | 0→0→0 | 0→0→0 | 3→3→3 |
| noms-soir | 3.57→3.96→4.27 | 14.1→15.8→14.8 | 12.46→14.72→12.27 | 2→2.5→2 | 1.5→0.5→2 | 1.5→0.5→2 | 0→0→0.5 | 14→13→13 |
| onze | 3.15→2.91→3.09 | 12.7→12.8→10.7 | 10.82→12.55→10.23 | 8→5→6.5 | 16→7.5→9.5 | 10.5→6.5→8 | 0.5→0→1.5 | 57→53→53 |
| ressources-comptes | —→3.60→4.00 | —→16.5→14.0 | —→15.02→14.25 | —→1.5→0 | —→0→0 | —→0→0 | —→0→0 | —→5→5 |
| sous-obstacle | —→2.20→1.90 | —→10.5→6.7 | —→8.73→6.99 | —→1→0 | —→7.5→6.5 | —→4→4 | —→0→0 | —→10→10 |
| ensemble vingt | —→2.85→2.99 | —→12.7→10.3 | —→11.73→9.59 | —→7.5→6.5 | —→15→16 | —→10.5→12 | —→0→1.5 | —→68→68 |

Vingt scripts : **12,747 → 10,335 s/tour (−18,9 %)**, médiane **11,725 → 9,585 s (−18,3 %)** ; appels **388 → 406 (+4,6 %)**. Passes nouvelles : **2,97/3,00 appels/tour**, **10,42/10,25 s/tour**. Achat du soir seul : **16,5 → 20,4 s/tour**, **4,25 → 5,38 appels/tour**. Charges historiques différentes et autre lot CPU simultané : aucune attribution causale ni garantie générale de latence.

Secondes par fonction et par tour : comparaison commune sur les onze scripts ; dernière colonne sur les vingt. Attente modèle, hors calcul local et rendu.

| Fonction | main → 882907c → b0042c9 (onze) | 882907c → b0042c9 (vingt) |
|---|---|---|
| Interprétation | 5.04→4.90→4.63 | 5.11→4.68 |
| Récit | 1.65→1.39→1.17 | 1.40→1.19 |
| Audit narratif | 4.90→5.49→3.53 | 4.99→3.10 |
| Fidélité | 0.31→0.34→0.67 | 0.27→0.75 |
| Contre-revue | 0.35→0.37→0.33 | 0.42→0.35 |
| Révision | 0.46→0.33→0.35 | 0.43→0.27 |

Portée : **0,129 → 0 s/tour** sur vingt. Le fil contient les débuts/fins, premiers deltas, jetons et chemins critiques ; détail par groupe/fonction dans `instrumentation.json`. Premiers deltas moyens nouveaux sur onze : interprétation **2,05 s**, récit **1,12**, audit **1,35**, fidélité **1,07**, contre-revue **1,21**, révision **1,20**. Sur vingt : entrée **4 491 939 → 5 155 543** jetons, cache **1 053 440 → 1 823 360**, sortie **51 289 → 45 876** ; réflexion déclarée nulle.

**Défauts du lot 79** (indices de saisie à partir de zéro).

- **Absence d’Ilse non corrigée** : `signes-noir`, p1 n°2, « aucune des deux n’est ici » ; Corvus, Ilse [2,4] et Brune [4,5] sont tous dans l’antichambre rechargée. Audit `neutre/aucune`, deux appels. P2 : « L’obscurité […] ne te permet pas de la distinguer », compatible.
- **Orientation de Gorm non reproduite** : `crypte` n°26, p1 « Rien ne permet […] de savoir si Gorm a le dos tourné », p2 refus moteur de portée. Aucune prise, pas de temps consommé. Cela ne prouve pas une correction sémantique générale.
- **Motifs/verdicts : partiel** : rapports contradictoires rejetés dans `signes-guet` p1 n°0 et `soir-appel` p2 n°5 ; la fausse absence passe comme neutre. Les motifs libres des verdicts positifs sont désormais absents : l’ancien défaut motif/acceptation ne peut être déclaré corrigé.
- **Comptes nominaux : non reproduit** : `comptes` n°1, deux fois « Gorm te rend les deux pièces », sans relance ; or 24→26, Brune reste débitrice. Les extractions de cette campagne emploient déjà les identifiants : pas de nouveau rejeu nominatif.
- **Achat du soir exécuté 2/2** : `soir-appel` n°5, or 26→23 avant récit ; `planches_1` portée dès le premier `ouest` rechargé. P2 finit sur le repli « La contrepartie immédiate est remise ; la demande sera livrée selon l’engagement enregistré. » P1 dit encore « Je te les rends », alors qu’Aubin reçoit les pièces : famille de confusion comptable déjà connue. Faux rejet de « Les planches […] restent à moi » toujours présent au remboursement p2 n°4.

**Nouveaux constats de campagne, sans correction ni attribution certaine à un lot.**

1. **N1 — Description remplacée par une erreur de contrat**, `atelier`, p1/p2 n°8, « à quoi ressemble le mur de l’atelier ? » → « Faits narratifs invalides. Aucun ajout enregistré. » Un appel ; `faits` contient des libellés internes en liste, au lieu de faits structurés. État rechargé identique au tour précédent ; les deux références 882907c répondaient. Cause probable : forme d’interprétation invalide quittant la chaîne de correction.
2. **N2 — Mot courant censuré**, `soir-appel`, p2 n°5 : « les planches ne t’ont pas encore été données » est refusé pour « données », comme vocabulaire du jeu. Après les refus précédents, cela déclenche le repli technique cité plus haut. Cause probable : garde lexical commun trop large ; transaction conservée.
3. **N3 — Appel de présence abandonné**, `soir-noir`, p1/p2 n°1, « il y a quelqu’un ? » → « Ta demande n’a pas été exécutée. Reformule-la. » Trois appels ; interprétation `qui` puis fidélité refusée pour différence présence/identité, sans récupération. Dans 882907c les deux paroles étaient dites et recevaient une réponse. Cause probable : désaccord de typage sémantique suivi d’un abandon de l’intention.

**Incidents et limites.** Aucun plantage du jeu, erreur réseau, budget épuisé, tour écarté ni défaut de recharge ; le plantage `profil` nul du planificateur n’est pas revenu. Une erreur de nom de fichier dans le lanceur auxiliaire a interrompu le rangement après les quatre groupes, sans affecter leurs parties ; rangement repris sans appel Luna, trace complète de reproduction dans `erreur-rangement-lanceur.txt`. Trois replis détectés : les deux descriptions invalides et l’achat p2. Les quatorze parcours sous-obstacle gardent les positions, passages et durées 12/12/6 s après recharge. Présentation d’Ilse restituée deux fois ; recherche de traces toujours « Le sol en pierre ». Le harnais recharge après sauvegarde et en fin de partie, mais six premiers `regarder` précèdent la sauvegarde et seuls les marqueurs des panneaux sont capturés : aucune garantie générale de rendu persistant ou de vérité sémantique. Aucune suite moteur relancée pour ce lot sans code.

Bruts : `C:\Users\msics\donjon\artifacts\verif-luna-b0042c9\` : quarante JSON/HTML et quatre journaux, `mesures.json`, `instrumentation.json`, `verification.json`, `cache-sha256.json`, `preuves-incidents.json`, `revue.txt`, `controles.txt`, `constats.md` et scripts de reproduction. Mesures f033364/fbcf0ff et résultats par script conservés dans les bruts.
