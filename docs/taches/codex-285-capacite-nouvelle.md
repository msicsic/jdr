# Tâche Codex 285 : un objet sans capacité nouvelle n'ouvre aucun geste (C1)

Lot de coût (« À revoir », *Coût, suites retenues*, C1, dans `docs/etat-dev.md`). Pas de Luna.

Lis `AGENTS.md`, puis l'entrée du lot 46 (`codex-une-source`) dans `docs/etat-dev.md`, son brief
`docs/taches/codex-46-une-source.md` et son rapport `docs/taches/rapport-codex-46-une-source.md`. Lis ensuite
`docs/plan-planificateur.md` (« Lumière employée », borne du lot 48) et `donjon/planification.py` : `Vue.pertinent`,
`Vue.capacite`, `Vue.couvre`, `Vue.capacites_portees`, `Vue.doublon`, ses deux appelants (`gestes`, vers la
ligne 1530 ; `_aide_sur_place`, vers la ligne 1722), `_entrees`, `VERIFIER`, `REFERENCE` et `BORNES`.

## Le constat
Le lot 46 n'applique sa règle qu'aux sources de lumière portables (`sources_seules`). Une seconde source qui
n'apporte rien n'est plus acquise : à la mine, cela a donné −34 % de CPU à décisions identiques ou au coût de la
recherche complète. Les autres objets que lisent les gestes restent sans cette règle : outils de choc et de coupe
(`force.CHOC`, `force.COUPE`), outils de crochetage, clés (`ouvre`) et contenants. `Vue.pertinent` les rend
pertinents par catégorie, par exemple tout outil de choc dès qu'une serrure est crue verrouillée. La recherche
développe donc des inventaires où le PNJ prend un deuxième marteau, un deuxième couteau ou une deuxième clé de la
même porte. Le diagnostic du lot 46 trouvait, en fin de nuit, 94 à 99 % des états avec des préparatifs.

## L'invariant
**Un objet que le but ne vise pas n'ouvre aucun geste d'acquisition dans la recherche s'il n'apporte aucune
capacité absente de ce que l'acteur porte déjà.** Les gestes concernés : prendre, demander, acheter, le saisir sur
un porteur, le faire remettre par une aide sur place. La règle vaut pour toute catégorie d'objets que lisent les
gestes, et la capacité se définit une fois par catégorie, sur ce que ces gestes lisent réellement : jamais une liste
d'objets, de personnages ou de scénarios.

Généralise `doublon` et `capacite`, sans fonction parallèle. Les sources de lumière gardent exactement leur règle
actuelle. La règle est appliquée dans `gestes` et `_aide_sur_place`, comme aujourd'hui, et reste indépendante
d'`emplois`, afin que la référence de `VERIFIER` l'applique aussi.

- **Choc et coupe** : définis la capacité par ce que lit `force` (dégâts, ce qu'on peut couper ou briser, faute à
  toucher l'objet).
- **Crochetage** : ce que lit le seuil du jet (`pnj.seuil_crochetage`).
- **Clés** : l'ensemble de ce qu'elle `ouvre`.
- **Contenants** : traite-les aussi si leur emploi par les gestes est un besoin exact (capacité, transport) ;
  sinon laisse-les hors du lot et dis-le.
- **Consommables** (combustible, vivres, parts) : hors du lot. Deux charges ne valent pas une seule.

Quand deux objets d'une même catégorie ne se comparent pas exactement (par exemple deux outils dont aucun ne domine
l'autre sur tout ce que lisent les gestes), garde les deux : la règle n'écarte qu'un objet dominé. Aucun coût, prix,
plafond de nœuds, scénario ni consigne du MJ ne change.

**Décisions** : contrat du lot 48.
- Là où la recherche actuelle ne plafonne pas, les décisions sont identiques ; prouve-le par les empreintes.
- Là où elle plafonne, le résultat doit égaler celui de la recherche complète (`REFERENCE`), ou bien il n'y a aucun
  plan si la recherche complète n'en trouve pas.

`VERIFIER` contrôle ce contrat.

**Commence par mesurer** sur une capture de fin de nuit à la mine et à l'auberge (par exemple
`tests/data/cout-12h/mine-1985-480.json.gz`, ou une capture produite par `tools/mesure_cout.py`). Compte :
- la part des états qui portent un doublon de chaque catégorie hors lumière ;
- ce que retirer ces inventaires change au nombre de nœuds.

Si le gain est négligeable (moins de 5 % des nœuds sur ces captures), arrête-toi et rapporte la mesure
(`QUESTION : …`) au lieu d'implémenter.

Lot de 30 à 45 minutes. Pas de suite complète : le superviseur la lance. **Poste : le PC fixe**, deux processus au
plus, priorité réduite. Une validation du lot 283 y tourne déjà sur un seul travailleur : n'en ajoute qu'un seul
tant qu'elle n'est pas finie (fichier `C:\Users\msics\donjon\artifacts\compte-rendu-283\fin-verification.json`).

**Fichiers attendus** : `donjon/planification.py`, et un raccord à `force.py` ou `pnj.py` seulement pour lire une
capacité. Le lot 283, non fusionné, modifie `agendas.py`, `echanges.py` et `social.py` : n'y touche pas.

## Vérification
- **Tests après rechargement**, sur la capture mine et un cas de même nature à l'auberge :
  - moins d'états, même résultat que la recherche complète ;
  - un cas où le but vise le second objet (une clé d'une autre porte, un outil qui coupe ce que l'autre ne coupe
    pas) : il reste pris ;
  - un cas où l'objet porté est contrarié ou illicite et le second licite : le second reste pris.
- Les fichiers de tests qui exercent `doublon`, `pertinent` et les gestes d'acquisition (trouve-les en cherchant les
  appelants), dont `tests/test_une_source.py`.
- **Empreintes 2 h**, cinq scénarios (`relais`, `mine`, `auberge`, `crue`, `crue_hameau`) × quatre graines, contre
  l'intégration à ta base (`tools/comparer_bancs.py --empreintes`, référence en cache si présente) : identiques, ou
  chaque écart expliqué par une recherche bornée et comparé à `REFERENCE`.
- **`VERIFIER` et `spatial.VERIFICATION=1`**, 2 h, mine et auberge 42 : aucun écart.
- **Coût** : `tools/mesure_cout.py`, base de l'intégration contre la branche, mine 1985 12 h fixe et auberge 1985
  12 h fixe. Compte les nœuds et les recherches, et le CPU indicatif. Lance les deux versions ensemble
  (`--sans-cache`) si tu compares des temps.
- Calculs longs détachés.

## Livraison
- Branche `codex-capacite-nouvelle` poussée. Si la poussée échoue, laisse le commit local, donne son hash et
  l'erreur exacte, sans passer par l'API GitHub.
- Rapport d'une page `docs/taches/rapport-codex-285-capacite-nouvelle.md` : capacité par catégorie, mesures,
  limites.
- Entrée « non fusionnée » dans `docs/etat-dev.md`.
- Bruts dans `C:\Users\msics\donjon\artifacts\capacite-285\`.
- Termine par `LOT TERMINÉ` (résumé d'une ligne), `CALCUL EN COURS : <fichier>` ou `QUESTION : …`.
