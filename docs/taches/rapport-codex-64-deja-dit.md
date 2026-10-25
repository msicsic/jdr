# Lot 64 — Ce qu'on a déjà dit

Branche `codex-deja-dit`, non fusionnée ; base `de3e986`, brief `a1a0021`.
Aucun appel à Luna, changement de `planification.py` ni de `main`.

**Correction.** Un fait déjà adressé à quelqu'un ne se répète pas tant que sa valeur reste la
même. Le suivi attaché aux souvenirs ou aux croyances disparaissait avec la mémoire bornée,
une nouvelle preuve de lecture ou un ancien relais. `esprit.faits_dits` conserve désormais
identité, dernière valeur et destinataires indépendamment des quarante souvenirs.
`social.faits_dits` normalise les contenus par identifiants : propriétés, intentions,
accusations, gestes et lieu d'un bien. Deux objets homonymes restent distincts ; dates,
épisodes, preuves et confiance ne changent pas le fait.

`nouvelles` écarte les anciennes versions ; `bavarder` ne marque que le contenu prononcé ;
`faire_entendre` inscrit le destinataire explicite. `_a_dire` et l'exécution de `dire`
consultent ce registre. `croire` rouvre un fait dont la valeur change. L'enveloppe des relais
conserve aussi la date d'observation : une ancienne propriété ne remplace pas une connaissance
plus récente et ne rajeunit pas un ancien guet.

**Cas réels.** Les archives indiquées manquent sur ce poste. La capture mine 3 est reproduite
sur `5c2ce81`, avant la confidence de Josse à Lucien à 14, et conservée dans `tests/data`.
Lucien savait déjà le guet depuis Rémy à 4 et figurait dans l'ancien suivi : même l'avertissement
de 14 est supprimé, puis les renouvellements jusqu'à 247. Onze tests nouveaux contrôlent
première confidence unique, objets homonymes, valeur changée puis revenue, mémoires évincées,
lieux, dette, relais périmés et migration. Deux comparaisons portent sur le monde complet et
les paroles après recharge, même laps découpé, dont la capture réelle.

**Banc rapide final.** Quatre scénarios × quatre graines × 4 h, contre `de3e986`, deux processus.
Référence calculée puis réutilisée depuis le cache ; temps non comparables.

| Moyenne par nuit, référence → branche | Relais | Mine | Auberge | Crue |
|---|---:|---:|---:|---:|
| Avertissements redits mot pour mot | 0 → 0 | 2,5 → 0,5 | 0,25 → 0,25 | 0 → 0 |
| Constats confiés | 2,5 → 2,5 | 22,5 → 18,5 | 12,5 → 10,25 | 5 → 5 |
| Maximum des passages/h | 6,75 → 6,75 | 7,25 → 8 | 13,75 → 13,75 | 17,5 → 17,5 |

Aucun plantage, violation ou usurpation ; bascules inchangées, aucune boucle nouvelle signalée.
Les doublons de mine 42 suivent guet → fatigue → guet ; les soupes d'auberge 1985 portent
`marmite_1` et `marmite`. Les anciens relais de mine 2024 ne rouvrent plus l'avertissement.

**Audits 12 h**, mine 3 et auberge 7 : aucun plantage, violation ou usurpation ; aucun guet
redit par Josse à Lucien. Doublons textuels 2 / 3, bascules maximales 0 / 3, passages/h maximaux
13 / 24, constats confiés 32 / 57. Les bûches homonymes de l'auberge sont vérifiées par les
contenus typés : `bois_reserve`, `_1`, `_2`, `_3`.

**Suite unique :** 1 829 tests, quatre ignorés, 866,6 s, trois processus à priorité réduite ;
deux échecs et une erreur. Les **86 tests concernés revalidés passent** (69 sociaux + 17 des deux
parcours ; huile finale reprise seule, 140 s). Bilan consolidé : 1 829 tests, quatre ignorés,
aucun échec restant ; aucune seconde suite complète. Trois scènes actualisées :
valeur du souvenir `dit` ; Odile se présente et porte l'huile vendue ; geste de Gaspard après
la minute de l'accord. Ces deux derniers tests passent sur la base (35,6 s).

**Limites.** 512 identités par PNJ, sans éviction : à saturation, les nouvelles identités sont
tues. Le registre suit les connaissances du PNJ ; les anciennes sauvegardes ne peuvent
reconstituer les paroles dont toute trace a disparu. Défaut révélé hors lot : une tâche faite
dans la minute même de l'accord peut rester non soldée, faute de constat daté après celui-ci.
La scène de bois sépare ces minutes ; ce contrat reste à corriger. Bruts dans `artifacts/`.
