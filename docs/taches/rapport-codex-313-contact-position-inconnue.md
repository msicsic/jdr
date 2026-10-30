# Lot 313 — contact sans position connue

29 octobre 2026. Branche `codex-contact-inconnu`, **non fusionnée**. Base `integration d76f272`, reprise de `origin/integration eb15b5e` par `19b1bf1`, **sans lot 315** ; corrections d’attribution : `130b57f`.

**Contrat commun.** Une portée insuffisante ou une case inconnue ne prouve pas l’absence. `positions_crues.case_contact`, partagé par `pnj._case_crue` et `Vue.case_objet`, suit les seuls liens crus contenant/support/porteur. La position projetée prime sur l’ancien contenant ; les faces locales des ancrages fixes restent accessibles depuis chaque côté. `_approcher` admet la perception actuelle, marche au point cru ou prépare l’observation ; une localisation perdue pendant la marche entraîne un regard depuis la position atteinte avant l’interruption. Le geste contrôle la portée physique. Une présence vocale crue permet la parole sans case de main ; le devis tient compte du contact supposé acquis par une inspection, sans la compter deux fois.

Une observation infructueuse retient sa cause `contact` dans les renoncements du 225. `refus_etape` et `obstacle_patience` relisent positions/liens crus, lumière, portes, moyens et perception positive : **ni date ni minute seule** ne rouvrent l’essai. Charge conservée, autres recherches possibles. Aucun emplacement mobile caché, changement de `planifier_tache`, d’`echanges.empeche`, ni des règles générales de perception.

**Preuves historiques (`c6cad4a`, avant attribution).** Relais 7 rechargé à 856 : approche **0→30 dixièmes**, Gorm sert Brune à **1009** ; autre source contenue dans une autre salle à la mine. Capture Ilse rechargée à **141000** : 141060 perd la localisation ; 141600 suit une indication d’Aubin et un déplacement ; **142200/142800/143400 : filet seul**, entrées identiques. Ces trois reprises sont corrigées ; cas réel, autre contact et charge dans le noir vérifiés après recharge, monde/rendu/scène et temps entier/découpé identiques. **72 tests / neuf fichiers verts**. Douze nuits 4 h (cinq rejouées, sept réutilisées) : refus matériels **4→0**, interruptions première version→final **12→7**, parts **30→32**, suspects 219 **0 dans chaque nuit**, bascules 0, aucune reprise sans entrée. Sept interruptions restantes : premiers échecs Brune ×2 au Relais 1985, Lucien auberge 42, Mireille/Joss auberge 2024, Rémy mine 1985, Lucien mine 7. Avertissements **4→8** : torches rallumées puis éteintes (Relais 2024/1985), deux paires de portions distinctes de même nom (auberge 1985), transmissions enregistrées. Avis **11→15**, dérives **186→160**, non certifiés bénins ; aucune absence universelle de boucle revendiquée. Ces mesures ne sont pas un nouveau banc de `130b57f` : la reprise demandée porte seulement sur les tests ciblés. Rapport antérieur complet conservé dans les bruts.

**Attribution de `61ced73`.** Journal : 2 889 tests, 22 échecs et une erreur, soit **23 incidents / 21 méthodes**. Rejeux isolés sous `PYTHONHASHSEED=313`, deux travailleurs réduits au plus : intégration `eb15b5e` (322 inclus), puis 313 fusionné avec elle, sans 315. Résultat initial : intégration **4 échecs**, 313 **19 échecs + une erreur**. Les trois incidents du 322 sont verts sur les deux arbres ; ils ne reviennent pas au 315. **A : sept incidents préexistants, dont trois résolus par 322 ; B : seize attribués au 313 ; C : aucun incident de cette liste réservé au 315.**

V = vert, R = rouge ; numéros de `incidents.json`. Chaque suffixe abrégé désigne la méthode unique du fichier indiqué.

| Nº | Test / sous-test | Intégration | 313 avant→après | Attribution et traitement |
|---:|---|:---:|:---:|---|
| 1 | deliberation_evenements / objet absent | V | erreur→V | B : marteau vu enregistré avant son déplacement. |
| 2 | constater_rumeurs / seulement des voix | V | V→V | A, résolu par 322. |
| 3 | rendez_vous_tenu / Mireille sans invitation | V | V→V | A, résolu par 322. |
| 4 | occasions_scenarios / inverse, crue_hameau | R | R→R | A : même empreinte divergente. |
| 5 | appel_negocie / Josse–Gaspard réel | V | R→V | B : parole sans case de main connue. |
| 6 | gestes_par_noeud / successeurs et coûts | V | R→V | B : projection/contact supposé ; oracle exact inchangé. |
| 7 | audience / paiement des planches d’Aubin | R | R→R | A : même `23 != 26`. |
| 8 | ou_est_il / question et retrouvailles | V | R→V | B : prémisse historique capturée avant la question. |
| 9 | voix_inconnues / réserve verrouillée | V | V→V | A, résolu par 322. |
| 10 | defense / fuite interrompue par inconscience | V | R→V | B : attaque sur un adversaire déjà repéré. |
| 11 | combat / assommer puis réveil | V | R→V | B : même prémisse de visée connue. |
| 12 | enfermer / assommer, traîner, verrouiller | V | R→V | B : contact local des ancrages fixes. |
| 13 | enfermer / sortie par crochetage | V | R→V | B : même contrat des faces locales. |
| 14 | enfermer / sortie forcée avec outil | V | R→V | B : même contrat des faces locales. |
| 15 | portee_seuil / préparer sans franchir | V | R→V | B : perception actuelle admise avant approche. |
| 16 | pas_compagnons / demande, crue_hameau | V | R→V | B : observer le contact perdu avant interruption. |
| 17 | pas_compagnons / demande, relais | V | R→V | B : même correction, autre scénario. |
| 18 | etapes_chainees / capture mine | R | R→R | A ; visites 313 recalées, monde préexistant laissé rouge. |
| 19 | etapes_chainees / capture auberge | R | R→R | A ; visites/diagnostics recalés, même monde laissé rouge. |
| 20 | lumiere_garde / Joss cherche Odile | V | R→V | B : contact vocal sans précision inventée. |
| 21 | agendas_proteger / appel et course | V | R→V | B : arrivée constatée dans les cinq minutes. |
| 22 | protection / Ilse appelle, Gorm accourt | V | R→V | B : même test appelé par le précédent. |
| 23 | completion_preuves / joss-622-plan | V | R→V | B : devis corrigé, résultat/coût exacts inchangés. |

**Prémisses et oracles, sans assertion affaiblie.** Les fixtures d’attaque commandent un adversaire déjà repéré ; orienter le regard vers le marteau ne l’enregistrait pas. Gorm arrive au secours puis suit Ilse : le test constate l’arrivée dans la même borne de cinq minutes, au lieu d’exiger son immobilité au terme. La scène initiale de localisation préfère désormais l’appel direct (1875), retrouve Gorm et obtient la part (2771) : l’absence de question à Brune est légitime. La capture `eb15b5e`, **1800 avant le premier pas d’Aubin et toute question**, conserve le choix autonome historique. Brune, qui a déjà fait son premier pas commercial dans cette capture, est explicitement replacée au point vu de la scène d’auteur : toutes les assertions de question, trajet, parole, refus, réunion et recharge restent exigées. Générateur et diagnostic conservés dans les bruts.

Captures des étapes chaînées : monde **complet**, plans, textes et deux vues rechargées identiques entre intégration et 313. Seules les visites passent **16309→16349** (mine) et **8573→8525** (auberge), plus les diagnostics de cette dernière ; seules ces attentes exactes sont recalées. Les deux empreintes de monde déjà fausses sur l’intégration ne sont pas remplacées. Les six graphes de `gestes_par_noeud` et les quatre contrats de `completion_preuves` gardent intégralement leurs oracles historiques.

**Validation de l’attribution.** **226 tests distincts / vingt fichiers**, 209,645 s ; première passe : trois échecs, zéro erreur/saut. Le témoin de localisation replacé explicitement, **18/18 tests de ce seul fichier verts** à la reprise (52,036 s). Bilan consolidé : **aucun échec nouveau**, seuls les deux sous-tests de monde préexistants restent rouges dans ces vingt fichiers ; les deux autres incidents préexistants restent attestés par les rejeux isolés. Les seize incidents B sont résolus. Deux régressions ajoutées : contact perdu puis retrouvé par observation (Relais et crue, parole et engagement persistés), positions projetées prioritaires. Bruts : `C:/Users/msics/donjon/artifacts/contact-313/attribution-suite/` et `attribution-corrections/` ; bancs antérieurs dans `reprises-validation/`. Le `ok=true` du lanceur d’attribution signifie « rejeux produits », pas « tests verts ». Ni Luna, ni nouvelle suite complète, ni nouveau banc de nuit. Branche poussée, lot terminé non fusionné.
