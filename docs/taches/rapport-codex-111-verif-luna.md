# Lot 111 — Vérification Luna de l’intégration 91a4351

26 octobre 2026 — **Validation partielle : N1/N3 et la fausse absence non reproduits ; remboursement à Gorm perdu aux deux passes.** Aucun code modifié. Méthode et vingt scripts du lot 99 : **40 parties, 302 saisies, 136 tours MJ, 459 appels**, `gpt-6-luna`/ChatGPT medium/libre, budget 200 par groupe/passe, quatre exécutions au plus, priorité réduite, copies temporaires et `SEUIL_AUTH` principal. Branche issue de `0e03324`, code identique à **91a4351**. Quarante parties cachées sous ce commit, identité SHA-256 vérifiée. Références **42bb9c0, 882907c, b0042c9 exclusivement relues** : **177 fichiers inchangés** ; mesures historiques identiques au lot 99 (f033364/fbcf0ff aussi relus pour ce contrôle, sans rejeu).

Chaque cellule : **main (42bb9c0) → 882907c → b0042c9 → 91a4351**. Moyennes des deux passes ; médiane sur les tours réunis. Refus = validations moteur/fidélité/contre-revue ; relances et replis = détecteurs historiques. Refus locaux sans appel hors compteur ; main ne couvre que onze scripts. Les secondes par fonction ci-dessous sont par tour MJ, attente modèle hors calcul local/rendu.

| Groupe | appels/tour | s/tour | médiane s | relances | refus | tours avec refus | replis | tours MJ |
|---|---|---|---|---|---|---|---|---|
| référence | 3.05→2.63→2.77→3.08 | 12.1→11.6→9.5→10.3 | 10.66→12.04→8.86→9.32 | 3→1→2.5→5 | 12.5→7→7.5→8 | 8→6→6→6 | 0.5→0→1→0.5 | 33→31→31→31 |
| signes | 2.57→2.50→2.42→3.25 | 11.3→13.7→8.4→11.6 | 8.71→11.30→7.33→8.09 | 0.5→1.5→1→2.5 | 2→0→0→0 | 1→0→0→0 | 0→0→0→0 | 7→6→6→6 |
| ambiance | 3.67→2.00→2.67→3.33 | 16.6→10.7→9.1→12.0 | 15.77→9.62→9.75→10.50 | 2.5→0→1→1.5 | 0→0→0→0 | 0→0→0→0 | 0→0→0→0 | 3→3→3→3 |
| noms-soir | 3.57→3.96→4.27→4.62 | 14.1→15.8→14.8→15.5 | 12.46→14.72→12.27→12.77 | 2→2.5→2→3.5 | 1.5→0.5→2→2 | 1.5→0.5→2→2 | 0→0→0.5→0.5 | 14→13→13→13 |
| onze | 3.15→2.91→3.09→3.49 | 12.7→12.8→10.7→11.8 | 10.82→12.55→10.23→9.95 | 8→5→6.5→12.5 | 16→7.5→9.5→10 | 10.5→6.5→8→8 | 0.5→0→1.5→1 | 57→53→53→53 |
| ressources-comptes | —→3.60→4.00→5.00 | —→16.5→14.0→17.6 | —→15.02→14.25→14.58 | —→1.5→0→1 | —→0→0→1 | —→0→0→1 | —→0→0→0.5 | —→5→5→5 |
| sous-obstacle | —→2.20→1.90→1.95 | —→10.5→6.7→7.1 | —→8.73→6.99→7.22 | —→1→0→0 | —→7.5→6.5→7 | —→4→4→4 | —→0→0→0 | —→10→10→10 |
| ensemble vingt | —→2.85→2.99→3.38 | —→12.7→10.3→11.5 | —→11.73→9.59→9.57 | —→7.5→6.5→13.5 | —→15→16→18 | —→10.5→12→13 | —→0→1.5→1.5 | —→68→68→68 |

| Fonction | onze : main → 882907c → b0042c9 → 91a4351 | vingt : 882907c → b0042c9 → 91a4351 |
|---|---|---|
| auditer_narration | 4.90→5.49→3.53→4.57 | 4.99→3.10→4.05 |
| auditer_portee | 0.00→0.00→0.00→0.00 | 0.13→0.00→0.00 |
| contre_revue | 0.35→0.37→0.33→0.27 | 0.42→0.35→0.31 |
| fidelite | 0.31→0.34→0.67→0.68 | 0.27→0.75→0.78 |
| interpretation | 5.04→4.90→4.63→4.31 | 5.11→4.68→4.54 |
| recit | 1.65→1.39→1.17→1.23 | 1.40→1.19→1.25 |
| revision | 0.46→0.33→0.35→0.74 | 0.43→0.27→0.61 |

Sur vingt : **10,335 → 11,543 s/tour (+11,7 %)**, médiane **9,585 → 9,565 s** ; **406 → 459 appels (+13,1 %)**. Passes : **3,46 / 3,29 appels/tour**, **11,69 / 11,40 s/tour**. Achat du soir : **5,38 → 6,00 appels/tour**, **20,4 → 21,0 s/tour**. Charges historiques différentes, autres lots simultanés : aucune attribution causale de latence.

**Défauts suivis**, indices de saisie à partir de zéro :

- **N1 non reproduit 2/2**, `atelier` n°8 : p1 « Tu vois le mur de l’atelier à quelques mètres » ; p2 « Tu aperçois le mur de l’atelier à deux mètres vers le nord et trois vers l’ouest ». Aucun message technique, trois appels chacun.
- **N2 non reproduit, cas exact non exercé** : aucun refus pour « données » dans les fils. `soir-appel` n°4 dit deux fois « ne t’ont pas été remises ». La génération n’a pas proposé la phrase historique « ne t’ont pas encore été données » : cette campagne ne prouve pas son admission.
- **N3 non reproduit 2/2**, `soir-noir` n°1 : « Tu dis : “il y a quelqu’un ?” », puis p1 « Oui, quelqu’un est là. Qui parle ? », p2 « Oui, il y a quelqu’un. » Cinq appels chacun après refus de fidélité, parole exécutée ; aucun « Reformule-la ».
- **Fausse absence non reproduite 2/2**, `signes-noir` n°2 : p1 « Tu ne sais pas si Ilse a peur de Brune », p2 « tu ne les vois ni l’une ni l’autre dans l’obscurité ». Ilse, Brune et Corvus restent dans l’antichambre rechargée. Cela ne garantit pas toutes les paraphrases.
- **Achat exécuté 2/2**, `soir-appel` n°5 : comptes de l’issue moteur joueur→Aubin trois pièces rendues, Aubin→joueur `planches_1` due ; planches portées dès n°6 rechargé. Confusion comptable déjà connue encore affichée : p1 « Tu m’as rendu les deux pièces que je te devais », p2 « Les trois pièces que tu me devais sont rendues ». Aucun repli sur l’achat lui-même.
- **Identité toujours incohérente 2/2**, `soir-noir` n°2 puis n°5 : p1 « C’est Ilse » puis « Je ne te dirai pas qui je suis » ; p2 « Je m’appelle Ilse » puis « Je ne te dirai pas qui je suis vraiment ». Paroles de PNJ, pas preuve que leur contenu est vrai.

**Nouveaux constats**, sans correction ni attribution certaine à un lot :

4. **N4 — Réclamation valide dégradée en parole sans remboursement**, `comptes` p1/p2 n°1, « Gorm, rends-moi les deux pièces que tu me dois. » La revue rejette deux fois `reclamer` parce que le contenu ne précise pas « deux », puis secours aux mots exacts sans opération. Dette de deux maintenue dans les comptes transmis au récit, contrairement au remboursement des deux passes b0042c9. Affichage p1 « Tu ne m’en as jamais prêté. C’est Brune qui te doit de l’argent, pas moi » ; p2 « Gorm t’a entendu, sans te répondre ». Cause probable : faux refus sémantique d’une quantité déjà portée par la dette, suivi d’une perte de l’opération contestée. La parole mensongère seule ne prouve pas une contradiction moteur ; le non-remboursement est l’effet constaté.
5. **N5 — Justification de méta-preuve affichée**, `luna-restes-ambiance` p2 n°1, « quels bruits de fond est-ce que j’entends ? » → « les faits sur la pièce décrivent sa lumière et ses obstacles, pas ses sons ». Après refus de l’absence sonore, cette réserve passe l’audit. Cause probable : classement sémantique et garde d’auteur insuffisants ; l’ambiance libre n’est pas restituée. Famille de réserve déjà connue, nouvelle occurrence dans cette campagne.
6. **N6 — Non-perception refusée comme absence**, `signes-guet` p1 n°1, « Que fait Gorm en ce moment ? » : candidat « tu ne le vois pas depuis la galerie » rejeté car « La non-perception de Gorm n’est pas établie par la vue partielle ». Texte final « Tu ne sais pas ce que fait Gorm en ce moment ». Cause probable : surinterprétation sémantique de la couverture ; huit appels sur ce tour, sans fuite affichée. Famille motifs/verdicts déjà connue.

**Incidents et limites.** Aucun plantage du jeu, erreur réseau, budget épuisé, tour écarté ni défaut de recharge. Trois tours avec repli : `atelier` p1 n°12 (recherche d’une pierre : « Précise ce que tu veux regarder, examiner ou tenter »), `soir-appel` p2 n°2 (conversation validée), `comptes` p2 n°1. Quatorze parcours sous obstacle cohérents après recharge, positions/passages et durées 12/12/6 s conservés. Orientation de Gorm : refus de portée aux deux passes de `crypte` n°26, aucune prise. Recherche de traces toujours « Le sol en pierre ». Le harnais recharge après sauvegarde et en fin de partie ; six premiers `regarder` précèdent la sauvegarde, panneaux capturés par marqueurs et état résumé sans solde d’or : pas de preuve universelle de rendu persistant ni de vérité sémantique. Les comptes de transaction sont contrôlés dans le fil de l’issue moteur, pas dans un solde rechargé capturé. Aucune suite moteur relancée, aucun code corrigé.

Un incident auxiliaire d’affichage du générateur de tableau (stdout Windows cp1252, `UnicodeEncodeError` sur la flèche) a été corrigé par sortie UTF-8 puis repris sans appel Luna ; tableau déjà écrit intact, trace dans les bruts. Aucun incident du lanceur de parties.

Bruts : `C:\Users\msics\donjon\artifacts\verif-luna-91a4351\` : quarante JSON/HTML, quatre journaux, `mesures.json`, `instrumentation.json`, `verification.json`, `cache-sha256.json`, `preuves-incidents.json`, `revue.txt`, `controles.txt`, fils/textes, constats et lanceurs. Détail par script et fonction conservé hors rapport.
