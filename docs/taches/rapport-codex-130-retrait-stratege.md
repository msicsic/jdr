# Lot 130 — retrait du stratège Luna des PNJ

2026-10-26. Branche `codex-retrait-stratege`, base `56afc2e`, non fusionnée.

## Invariant et changement

Le moteur conserve seul la décision des PNJ : retirer le stratège, désactivé par défaut,
ne doit changer aucune nuit ordinaire. Suppression de `donjon/stratege.py`, de
`tools/banc_stratege.py`, des tests propres et du test de validation du stratège dans
`test_caractere.py`. Retrait des appels `plan_illicite`, `occupe`, `desoeuvre` de
`deliberation.choisir`, de `terminer`/`verifier` et des branches dédiées de `pnj`, des
options du jeu et du banc, de la connexion Luna du banc et des mesures `stratege_*`.
Les règles ordinaires de choix, de coût moral et d'exécution ne changent pas.
Aucun fichier réservé aux lots 128/129 n'est modifié. Aucun Luna exécuté.

Le champ ancien `data["stratege"]` est ignoré : aucune lecture, validation ou écriture
par le moteur ; il peut rester dans le JSON comme donnée inerte. Aucune migration.
Les anciennes intentions ne sont pas migrées non plus. Quelques libellés historiques
ou lectures du type de but `strategie` dans les modules hors périmètre restent en place ;
ils ne réactivent aucun conseiller ni ne produisent de nouveau plan du stratège.
Documentation d'utilisation corrigée ; bilan historique du jalon E conservé.
Le README ne mentionnait pas cette option.

## Vérification

- `tools/comparer_bancs.py --reference 56afc2e --empreintes --scenarios relais crue mine
  auberge --processus 2` : **16/16 nuits de 2 h strictement identiques**, graines
  1985/7/42/2024 ; chroniques, mesures et états finaux complets. **Aucun champ exclu**.
  Référence absente du cache : calculée une fois puis rangée dans le cache commun ;
  aucun rejeu. Temps non comparés, poste partagé.
- Tests ciblés : **11 verts**, 3,28 s. Deux scènes (Relais, mine) avec l'ancien champ :
  sauvegarde, recharge, cinq minutes de jeu, chronique/mesures/récit identiques au
  témoin, puis recharge et état complet identique hors ce seul champ inerte conservé.
- Pyflakes : **aucun nom indéfini** sur les six fichiers Python conservés touchés.
  Trois avertissements identiques sur la base : imports `sujet` et `flamme` masqués
  dans `pnj.py`, import `SATIETE` inutilisé dans `deliberation.py`. Non corrigés ici.
- Suite complète unique `tools/tests.py --processus 2` : **2 052 tests, deux échecs
  MiMo `6 != 5`, zéro erreur**, 1 047,51 s. Les deux échecs sont reproduits sur
  la base intacte `56afc2e` (13 tests, 10,80 s) ; aucune régression constatée.
- Deux processus de calcul au plus, priorité réduite. Des lancements initiaux ont
  échoué sur les permissions des fichiers temporaires ; reprise hors sandbox,
  après autorisation automatique. Pyflakes installé seulement sous `artifacts/`.

Bruts : `artifacts/retrait-130-empreintes.json`, `retrait-130-cibles.json`,
`retrait-130-suite.json`, `retrait-130-base-mimo.json`. Aucune modification ni fusion de `main` ou `integration`.
Le contrôle automatique a initialement refusé la livraison faute de propriété établie
du remote ; l’API GitHub confirme `msicsic/jdr`, propriétaire identique au compte
connecté `msicsic`, droits admin/push.
Aucune clé Git de signature configurée : commit non signé ; branche poussée sur `origin/codex-retrait-stratege`.
