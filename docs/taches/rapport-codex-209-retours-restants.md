# Lot 209 — Retours restants : attribution avant 196 c

27 octobre 2026, `codex-retours-restants`, base exacte **78ba505** vérifiée.
Diagnostic seul : aucun fichier du jeu ni test modifié, aucun Luna. Un seul
travailleur de calcul, priorité `BelowNormal` vérifiée. Bruts exclusivement dans
`C:/Users/msics/donjon/artifacts/retours-209/`.

**Reproduction.** Audit de vingt nuits, cinq scénarios × graines 1985/7/42/2024,
4 h, départ tiré, `--processus 1`, compteur 199 : **57 retours suspects**
(Relais **0**, mine **1**, auberge **5**, crue **27**, hameau **24**), zéro
plantage. Les vingt nuits sont dans `nuits/`. L'inventaire exhaustif
`inventaire-exhaustif.md` et `inventaire-attribue.json` donne pour **chacune des
57 occurrences** le PNJ, les instants, les décisions, la condition de code, le lot
et la capture. Les numéros ci-dessous
sont ceux de cet inventaire (0–56) ; minutes décimales depuis le départ.

| Famille | Cas et décisions | Cause observée | Lot |
|---|---|---|---|
| **Eau : 25** | N° 5–19, 25–26, 34–36, 39, 47–49, 54. Aubin, Ilse, Gorm ; crue/hameau, min 78,90–237. Abri → aucune intention, ronde ou rejoindre → abri. | **6 à 99 cm d'eau crue présente** à l'abandon. `eau.en_peril` exempte le préfixe `aller` admissible ; `_candidats` retire `PERIL_EAU`. Sécurité sous `SECURITE_FIN` : pas de progrès pour retenir l'évacuation ; sans ce plan, le péril revient. | **205**, y compris les interruptions par ronde/service. 196 c ne remplace pas le juge de péril indépendant du plan. |
| **Cibles d'abri : 7** | N° 42–44, 50–53. Ilse, hameau 2024/7, min 1,80–2,06 (dernier retour 2024 à 30,04). Chambre de la cloche ↔ antichambre. | `_plan_abri` réessaie `abri(en_route)` ; `planification._endure` peut rendre `None` sans rendre la cible impossible. Arrivée à l'antichambre, `ici != salles[0]` fait essayer la chambre préférée avant le séjour ici. `_continuer_progres` rend aussi cette autre cible ; `choisir.retenu` ne retrouve donc pas le but courant. Eau montante et péril **faux** sur la relecture hameau 7. | **205** pour le contrat commun de l'abri, **196 c** pour distinguer admissibilité, gain et stabilité de cible. Ne pas réduire ces sept cas à l'évacuation. |
| **Secours/perception/rondes : 21** | N° 0–4, 20, 22–24, 27–29, 32–33, 37, 40–41, 45–46, 55–56. Rémy, Mireille, Tilo, Aubin, Ilse, Maël, Sève ; min 0,425–238,27. Nourrir/entretenir → aucune intention/ronde/rendez-vous → secours ; cycles inverses de ronde. | `secours` exige une cible **actuellement perçue** pour réémettre le candidat. Faim connue persistante ; chez Sève, froid de Brune connu. `choisir` ne conserve pas séparément le but engagé. Plans non vides ou coupés à `[]` avant remise attendue. | **196 c complet**, naissance distincte de poursuite. N° 23/27/33 : préemption permise d'une ronde (13) par secours (12) ; n° 24 : secours par rendez-vous (7). Ces préemptions ne sont pas toutes fautives. |
| **Localisation inconnue : 3** | N° 21/30/31. Ilse, crue 2024/42/7, min 1,255–1,723. Abri échoppe → aucune intention → même abri. | Sans croyance `aubin.lieu`, `_lieu_cru` utilise `o['lieu']` parce que `not o.get('mobile')`. Un personnage est ainsi traité comme un objet fixe : Aubin réellement en crypte puis à l'échoppe fait disparaître/revenir `_plan_abri.sures`, sans information reçue par Ilse. | **Hors 205/196 c** : autorité des localisations crues. Maintenir une intention ne supprime pas cet accès à une position cachée. |
| **Précondition temporaire : 1** | N° 38. Gorm, hameau 1985, min 6–6,117. Livrer `vivres_6` à Aubin → verrouiller la réserve → livraison avec nouveau déverrouillage. | La branche `remettre` de `_pulsion` passe par `_devis_remise` et livre un plan sans restauration du verrou. `retabli_par_son_plan` exige une étape `verrouiller`, absente. `_candidats` place alors biens pressant (4) devant parole due (5). | **Hors 205/196 c** : effets temporaires et restauration des charges. La liste fermée de 196 c autorise précisément cette préemption par palier supérieur. |

**Cas du lot 208.** Rejoués sur les sources exactes `74a4bc4`, depuis
`cout-208/74a4bc4-crue-tire/ilse-32.json` et `aubin-81.json` ; traces nouvelles
`208-trace.json`. Ilse 33/34 perd/retrouve Brune dans `percus`, **sans effacement
de sa faim connue** : engagement du secours, donc 196 c, pas preuve d'une croyance
de protégé perdue. Le nom de fonction effectif est `secours`, et non
`_secours_crus` cité au rapport 208. Aubin à **t=49200** adopte l'abri avec
`en_peril=True`, puis, au même instant et à sécurité **9,482**, le perd avec
`en_peril=False` ; à t=49255 le péril réapparaît. **205**, pas un seuil ordinaire
de sécurité ni un problème de perception de protégé. Ces trois anciens retours
ne s'ajoutent pas aux 57 de la base actuelle.

**Deux lots supplémentaires, un invariant chacun.**

- **Localisation crue** : aucune position réelle d'entité mobile par nature ne
  supplée une connaissance absente ; le repli structurel appartient aux éléments
  fixes du décor. Auditer les appelants communs de `_lieu_cru`/`salle_crue`, sans
  ajouter de cas particuliers. Captures `localisation-ilse-753.json`
  et `localisation-ilse-1034.json`, contre-épreuves rechargeables dans deux
  scénarios (`preuve-localisation.json`) : même esprit, cible non perçue, seule
  sa position physique change, et la position prétendument crue change aussi.
- **Restauration des charges** : un plan qui suspend une obligation pour agir
  porte cette suspension et sa restauration jusqu'au terme, même après coupe
  pour livraison ; la réévaluation ne combat pas sa précondition. Examiner
  ensemble devis, plan publié, replanification et garde. Capture réelle
  `crue_hameau-1985/avant-0.json`, abandon à t=3600 ; autre contenant/service à
  éprouver lors du correctif. Aucun ajout isolé de `verrouiller` proposé comme
  garantie générale.

**Preuves et limites.** Douze nuits touchées réinstrumentées : comptes détaillés,
empreintes, chronique, récit et souvenirs **identiques** au premier banc.
**35 captures**, monde, `regarder` et `scene_percue` identiques après recharge
(`captures-checks.json`) ; relectures depuis captures par famille dans
`causes-profondes.json`, contrôles 208 et localisation supplémentaires conservés.
Instrumentation initiale incomplète arrêtée et remplacée. Aucune suite complète :
diagnostic seul.
Les sept arbitrages d'abri demandent les deux contrats, sans promesse de baisse
chiffrée ; les 21 cycles de secours comprennent des préemptions permises. **Ni
57 défauts certifiés, ni zéro retour garanti après 205/196 c** : le compteur
reste une alerte, sans dépendances causales exhaustives ni certificat de sortie.
Les quatre occurrences hors de ces deux lots justifient les lots proposés.
