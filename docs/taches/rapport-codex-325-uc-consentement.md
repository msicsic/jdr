# Lot 325 — U-C, consentement du texte libre

Clôture du 30 octobre 2026. Branche `codex-uc-consentement`, **non fusionnée**.
Base initiale `865aff3` (U-P) ; intégrations `9f261f9`, `ad0e5a8` et
`60c476a` fusionnées sans rebase. Dernière fusion : `709db18`, conflit
`jeu.py` résolu en conservant U-C, G6 et G17 ; documents des deux côtés conservés.

`consentement.py` prépare sur copie transactions, admissions et plan entier.
La gravité porte sur les effets typés de toutes les branches et sous-plans ;
un effet inconnu reste lourd. Une étape lourde retient toute la composition.
La fiche « Compris » précède l'exécution ; annuler ne publie aucune conséquence.
Tenter revalide sans modèle : changement d'état ou de plan, même sans nouvelle
révision, impose un nouvel aperçu. Actes légers et gestes directs gardent leur politique.

G6 répond immédiatement aux consultations du contrat commun `PERCEPTIONS` ;
les autres faisabilités gardent leur fiche. G17 publie les mots du registre
réellement admis, aussi dans une composition. Après revalidation, les sceaux
sont recalculés sans perdre l'action ; les autorisations non formulées ne
sont pas des paroles entendues. Une réplique libre périmée est écartée.
Résultats et paroles sont sauvegardés avant affichage.

## Vérification

**200 tests distincts validés, vingt fichiers ciblés** : 191 résultats verts
conservés et neuf tests des comptes parlés rejoués verts en **65,076 s**.
La passe initiale (**1 485,276 s**) portait deux erreurs de sous-cas d'une
même méthode (Corvus/Alix), aucun échec d'assertion ni saut : un harnais
secondaire quittait avant `tenter`. Il utilise désormais le même parcours
de consentement ; ses assertions de mots, paiement, service et recharge restent intactes.
Aucun changement du code de production après la passe initiale.

Console, web et vraie TUI : paiement, offre G1/U-P, avis, enfermement,
composition avec étape lourde, offre puis dépôt ; aperçu, annulation,
confirmation, état complet, mots, sauvegarde et rendu rechargés.
G6 vérifie les perceptions immédiates. G17 vérifie rôles, montants,
ordre/multiplicité et répliques libres résiduelles. La revalidation décale
réellement les identifiants d'émission (2 → 3) et conserve le plan composé.
Les 28 tests TUI sont verts. Aucun oracle mécanique affaibli.

Mesures des 18 parcours lourds, secondes min–max :

| Interface | Saisie → aperçu | Confirmation → effet |
|---|---:|---:|
| Console | 0,027–4,576 | 0,019–5,901 |
| Web | 0,045–4,892 | 0,047–5,721 |
| TUI | 0,437–5,456 | 2,199–9,601 |

Temps humain simulé séparé : zéro. **Zéro appel après les 18 confirmations**.
Mesures avec interface, sans latence Luna réelle. Bruts dans
`C:/Users/msics/donjon/artifacts/uc-325/fusion-60c476a/` : `tests.json`,
`reprise-comptes-paroles.json`, `mesures.jsonl`, `analyse-cloture.json`,
`fin-cloture.json`. Premier `fin.json` avec `ok=false` conservé.

## Limites et livraison

La revalidation conservatrice peut redemander un aperçu sans conséquence
sur l'acte. Une fiche relue ne réactive pas le consentement. Fidélité au
français imparfaite ; aucune revue retirée ni consigne modifiée par U-C.
Pas de suite complète, Luna ou banc ; un travailleur réduit, calcul long détaché.
Reprise terminée et poussée, aucun calcul actif ; `fin-cloture.json` vert.
