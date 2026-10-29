# Lot 286 — La réserve est découverte déverrouillée après le refus

29 octobre 2026, PC fixe. Branche `codex-demande-sans-renaissance`, base
intégration **`f93ba93`**, brief présent, **non fusionnée**.
**Second cas du préalable : aucun correctif moteur.** Le refus de 117170
cesse de tenir parce qu’Aubin apprend une entrée pertinente après ce refus.
La seule perception renouvelée d’Ilse ne décrit donc pas toute la séquence.

**Établissement.** Relecture de `trace.json` du lot 272 et chargement des
captures historiques avant **117503** et **117518**, avec les fonctions
`moyens_crus` et `tient` de la base du présent lot :

| Instant (dixièmes de seconde) | Croyance d’Aubin sur la réserve | Refus `necessaire` |
|---|---|---|
| 117170, avant et après la demande refusée | Verrouillée, `dit:marchand`, minute 4 ; fermée vue à 162 | Cause retenue : `[[moyen, vivres, reserve, null]]` ; tient |
| 117312, avant l’inspection | Même croyance de verrouillage | Tient |
| 117312, après l’inspection de l’antichambre | Non verrouillée et ouverte, `vu`, minute 195 | Nouveau moyen `[ouvert, reserve, null, null]` ; ne tient plus |
| 117503 et 117518, captures rechargées | Même croyance nouvelle, conservée | Ne tient plus dans les deux captures |

L’inspection est le geste `inspecter`, à la case `[5,3]`, orientation sud.
Le premier constat dans la trace intervient **14,2 secondes après** le refus,
bien que les deux portent la même minute entière, 195. Le fait `ouvert` de
`moyens_crus` signifie ici **absence de verrouillage cru** : il ne dépend
pas à lui seul de l’attribut `ouverte`.

**Preuve causale.** Dans chacune des deux captures rechargées, remplacer
uniquement la croyance `reserve.verrouillee` par celle d’avant le refus
supprime exactement ce moyen supplémentaire et fait tenir le refus.
Aucun changement de perception d’Ilse n’est nécessaire à cette ablation.
Pour 117170 et 117312, les croyances complètes avant/après proviennent de
la trace ; elles ont été injectées dans une copie de 117503 pour appeler
le juge commun. Ces reconstitutions d’entrées ne sont pas des sauvegardes
complètes de ces deux instants.

**Contrôles et limites.** Deux captures originales et deux contre-épreuves
sauvées puis rechargées : **16 contrôles verts**, monde/rendu/scène
identiques et lectures sans mutation. Empreintes SHA-256 des trois sources
historiques inchangées. Un seul processus à priorité réduite, établissement
**0,335 s**, `fin-etablissement.json` **`ok=true`**. Aucun calcul actif.
Aucune fonction, aucun test ou scénario modifié ; aucun code des branches
273 repris. Ni Luna, ni suite complète, ni banc rapide : le préalable du
brief prescrit de rapporter ce second cas au lieu de corriger. Aucun second
cas de jeu ni découpage temporel éprouvé ; aucune garantie générale nouvelle,
aucune mesure S/F/D ou 219 nouvelle. Le classement brut historique reste
inchangé ; le retour est expliqué selon le juge des croyances existant.

Bruts : `C:/Users/msics/donjon/artifacts/renaissance-286/` : `etablir.py`,
`preuve.json`, quatre captures et leurs vues, `fin-etablissement.json`.

**QUESTION : le déverrouillage étant appris à 117312 après le refus de
117170, faut-il clore le lot 286 sans correctif et requalifier le retour
117518 comme reprise admissible selon les croyances d’Aubin ?**
