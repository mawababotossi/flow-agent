# Cahier de Simulation — Autorisation Ouverture École Privée

**Processus :** `Process_XFlow_Ecole` + `Process_XPortal_Ecole`
**Fichier BPMN :** `autorisation-ouverture-ecole-privee.bpmn`
**Date :** 2026-03-27

---

## Cartographie des gateways

| Gateway | Type | Rôle | Variable de décision |
|---|---|---|---|
| `Gateway_JoinInst` | ExclusiveGateway (convergent) | Merge : paiement initial OU retour correction | — |
| `Gateway_InstResult` | ExclusiveGateway (divergent) | Résultat instruction DEP | `decision_instruction` |
| `Gateway_Delib` | ExclusiveGateway (divergent) | Résultat délibération | `decision_direction` |
| `Gateway_JoinRej` | ExclusiveGateway (convergent) | Merge : tous les rejets | — |
| `Gateway_ActionPath` | ExclusiveGateway (divergent, XPortal) | Routage selon action reçue | action dans message |
| `Timer_Correction` | BoundaryEvent (15 jours) | Expiration attente correction | — (temporel) |

---

## Scénarios de simulation

### SC-01 — Chemin nominal : Favorable direct

**Objectif :** Valider le chemin heureux complet sans correction.
**Résultat attendu :** `EndEvent_X_Succes` (XFlow) + `EndEvent_PA` (XPortal)

#### Variables à injecter

| Étape | Variable | Valeur |
|---|---|---|
| `Activity_X_Instruction` | `decision_instruction` | `accepte` |
| `Activity_X_Deliberation` | `decision_direction` | `accepte` |

#### Déroulement XFlow

| # | Élément | Token entrant | Token sortant | Vérification |
|---|---|---|---|---|
| 1 | `StartEvent_XFlow` | — | `Flow_1` | Message `MSG_ECOLE_START` reçu |
| 2 | `Activity_X_DemandePaiement` | `Flow_1` | `Flow_2` | Topic `flow-send-message`, messageType=`MSG_ECOLE_PAY_REQ` envoyé |
| 3 | `Activity_X_AttentePaiement` | `Flow_2` | `Flow_3` | En attente message `MSG_ECOLE_PAY_CONFIRM` |
| 4 | `Gateway_JoinInst` | `Flow_3` | `Flow_4` | Convergence, passage direct |
| 5 | `Activity_X_Instruction` | `Flow_4` | `Flow_5` | Form `instructionAutorisationOuvertureEcole`, `decision_instruction=accepte` |
| 6 | `Gateway_InstResult` | `Flow_5` | `Flow_GoInsp` | Condition `decision_instruction == 'accepte'` vraie |
| 7 | `Activity_X_Inspection` | `Flow_GoInsp` | `Flow_6` | Form `inspectionAutorisationOuvertureEcole` |
| 8 | `Activity_X_Deliberation` | `Flow_6` | `Flow_7` | Form `deliberationAutorisationOuvertureEcole`, `decision_direction=accepte` |
| 9 | `Gateway_Delib` | `Flow_7` | `Flow_GoSign` | Condition `decision_direction == 'accepte'` vraie |
| 10 | `Activity_X_Signature` | `Flow_GoSign` | `Flow_8` | Signature physique |
| 11 | `Activity_X_NotifierRetrait` | `Flow_8` | `Flow_9` | Topic `flow-notify`, template=`SMS_CONVOCATION` |
| 12 | `Activity_X_Remise` | `Flow_9` | `Flow_10` | Confirmation remise physique |
| 13 | `Activity_X_CloseSucces` | `Flow_10` | `Flow_11` | action=`accepte`, messageType=`MSG_ECOLE_RETURN` |
| 14 | `EndEvent_X_Succes` | `Flow_11` | — | **FIN : Dossier Favorable** |

#### Déroulement XPortal (parallèle)

| # | Élément | Déclencheur | Token sortant | Vérification |
|---|---|---|---|---|
| P1 | `StartEvent_P` | — | `Flow_P1` | |
| P2 | `Activity_P_Soumission` | Manuel | `Flow_P2` | Message start envoyé vers XFlow |
| P3 | `Activity_P_RedirectionPaiement` | Reçoit `MSG_ECOLE_PAY_REQ` | `Flow_P3` | Paiement 40 000 FCFA E-Gov effectué, message `MSG_ECOLE_PAY_CONFIRM` envoyé |
| P4 | `Gateway_P_Action` | Reçoit `MSG_ECOLE_RETURN` (action=accepte) | `Flow_P4` | |
| P5 | `Gateway_ActionPath` | `Flow_P4` | `Flow_P_ACC` | Branche "accepte" |
| P6 | `Activity_P_Retrait` | `Flow_P_ACC` | `Flow_P_EndACC` | Convocation retrait physique |
| P7 | `EndEvent_PA` | `Flow_P_EndACC` | — | **FIN : Dossier Favorable** |

---

### SC-02 — Rejet à l'instruction (direct)

**Objectif :** Valider le chemin rejet sans passer par l'inspection.
**Résultat attendu :** `EndEvent_X_Rejet` (XFlow) + `EndEvent_PR` (XPortal)

#### Variables à injecter

| Étape | Variable | Valeur |
|---|---|---|
| `Activity_X_Instruction` | `decision_instruction` | `rejete` |

#### Déroulement XFlow

| # | Élément | Token entrant | Token sortant | Vérification |
|---|---|---|---|---|
| 1-5 | *(idem SC-01 jusqu'à Instruction)* | | | |
| 6 | `Gateway_InstResult` | `Flow_5` | `Flow_GoRej1` | Condition `decision_instruction == 'rejete'` vraie |
| 7 | `Gateway_JoinRej` | `Flow_GoRej1` | `Flow_12` | Convergence rejet |
| 8 | `Activity_X_AvisRejet` | `Flow_12` | `Flow_13` | action=`rejete`, messageType=`MSG_ECOLE_RETURN` |
| 9 | `EndEvent_X_Rejet` | `Flow_13` | — | **FIN : Dossier Rejeté** |

#### Déroulement XPortal

| # | Élément | Déclencheur | Vérification |
|---|---|---|---|
| P4 | `Gateway_P_Action` | Reçoit `MSG_ECOLE_RETURN` (action=rejete) | |
| P5 | `Gateway_ActionPath` | `Flow_P_REJ` | Branche "rejete" |
| P6 | `Activity_P_Refus` | Prise de connaissance du refus | |
| P7 | `EndEvent_PR` | — | **FIN : Dossier Rejeté** |

**Point de vigilance :** Vérifier que `Gateway_JoinRej` laisse bien passer le token depuis `Flow_GoRej1` (entrée 1/3).

---

### SC-03 — Rejet à la délibération (sans correction)

**Objectif :** Valider que le rejet post-inspection converge correctement vers `Gateway_JoinRej`.
**Résultat attendu :** `EndEvent_X_Rejet` + `EndEvent_PR`

#### Variables à injecter

| Étape | Variable | Valeur |
|---|---|---|
| `Activity_X_Instruction` | `decision_instruction` | `accepte` |
| `Activity_X_Deliberation` | `decision_direction` | `rejete` |

#### Déroulement XFlow

| # | Élément | Token entrant | Token sortant | Vérification |
|---|---|---|---|---|
| 1-8 | *(idem SC-01 jusqu'à Délibération)* | | | `decision_direction=rejete` |
| 9 | `Gateway_Delib` | `Flow_7` | `Flow_GoRej2` | Condition `decision_direction == 'rejete'` vraie |
| 10 | `Gateway_JoinRej` | `Flow_GoRej2` | `Flow_12` | Convergence rejet |
| 11 | `Activity_X_AvisRejet` | `Flow_12` | `Flow_13` | action=`rejete` |
| 12 | `EndEvent_X_Rejet` | `Flow_13` | — | **FIN : Dossier Rejeté** |

**Point de vigilance :** Vérifier que `Gateway_JoinRej` laisse bien passer le token depuis `Flow_GoRej2` (entrée 2/3).

---

### SC-04 — Correction unique puis favorable

**Objectif :** Valider la boucle de correction : le token repasse bien par `Gateway_JoinInst` et re-déclenche l'instruction.
**Résultat attendu :** `EndEvent_X_Succes` + `EndEvent_PA`

#### Variables à injecter

| Étape | Variable | Valeur |
|---|---|---|
| `Activity_X_Instruction` (1er passage) | `decision_instruction` | `correction` |
| `Activity_X_Instruction` (2e passage) | `decision_instruction` | `accepte` |
| `Activity_X_Deliberation` | `decision_direction` | `accepte` |

#### Déroulement XFlow

| # | Élément | Token entrant | Token sortant | Vérification |
|---|---|---|---|---|
| 1-5 | *(idem SC-01 jusqu'à Instruction)* | | | `decision_instruction=correction` |
| 6 | `Gateway_InstResult` | `Flow_5` | `Flow_GoCor` | Condition `decision_instruction == 'correction'` vraie |
| 7 | `Activity_X_AvisCorrection` | `Flow_GoCor` | `Flow_CorWait` | action=`correction`, messageType=`MSG_ECOLE_RETURN` |
| 8 | `Activity_X_RecCo` | `Flow_CorWait` | (attente) | En attente message `MSG_ECOLE_RESUB`. Timer 15j actif. |
| — | *(XPortal : citoyen reçoit notif correction, complète le dossier)* | | | Message `MSG_ECOLE_RESUB` envoyé |
| 9 | `Activity_X_RecCo` | Message reçu | `Flow_AfterCor` | Timer annulé |
| 10 | `Gateway_JoinInst` | `Flow_AfterCor` | `Flow_4` | **Boucle : 2e passage** |
| 11 | `Activity_X_Instruction` | `Flow_4` | `Flow_5` | `decision_instruction=accepte` |
| 12-19 | *(idem SC-01 à partir de Gateway_InstResult)* | | | Fin favorable |

#### Déroulement XPortal

| # | Élément | Déclencheur | Vérification |
|---|---|---|---|
| P4 | `Gateway_P_Action` (1er) | Reçoit `MSG_ECOLE_RETURN` (action=correction) | |
| P5 | `Gateway_ActionPath` | `Flow_P_COR` | Branche "correction" |
| P6 | `Activity_P_Correction` | Compléter les pièces, envoi `MSG_ECOLE_RESUB` | |
| P7 | `Gateway_P_Action` (2e) | `Flow_P_Loop` | Retour sur Gateway_P_Action |
| — | *(attend prochain message XFlow : action=accepte)* | | |
| P8 | `Gateway_ActionPath` | `Flow_P_ACC` | Branche "accepte" |
| P9 | `EndEvent_PA` | | **FIN : Favorable** |

**Points de vigilance critiques :**
- Token dans XFlow ne doit PAS rester bloqué à `Gateway_JoinInst` après `Flow_AfterCor`
- Token XPortal boucle correctement via `Flow_P_Loop` → `Gateway_P_Action`
- Le timer `Timer_Correction` doit être annulé dès réception du message RESUB

---

### SC-05 — Correction unique puis rejet à l'instruction

**Objectif :** Valider rejet après une boucle de correction.
**Résultat attendu :** `EndEvent_X_Rejet` + `EndEvent_PR`

#### Variables à injecter

| Étape | Variable | Valeur |
|---|---|---|
| `Activity_X_Instruction` (1er passage) | `decision_instruction` | `correction` |
| `Activity_X_Instruction` (2e passage) | `decision_instruction` | `rejete` |

#### Déroulement XFlow (à partir du 2e passage)

| # | Élément | Token entrant | Token sortant | Vérification |
|---|---|---|---|---|
| 10 | `Gateway_JoinInst` | `Flow_AfterCor` | `Flow_4` | 2e passage |
| 11 | `Activity_X_Instruction` | `Flow_4` | `Flow_5` | `decision_instruction=rejete` |
| 12 | `Gateway_InstResult` | `Flow_5` | `Flow_GoRej1` | |
| 13 | `Gateway_JoinRej` | `Flow_GoRej1` | `Flow_12` | |
| 14 | `Activity_X_AvisRejet` → `EndEvent_X_Rejet` | | | **FIN : Rejeté** |

---

### SC-06 — Correction unique puis rejet à la délibération

**Objectif :** Valider rejet post-inspection après une boucle de correction.
**Résultat attendu :** `EndEvent_X_Rejet` + `EndEvent_PR`

#### Variables à injecter

| Étape | Variable | Valeur |
|---|---|---|
| `Activity_X_Instruction` (1er passage) | `decision_instruction` | `correction` |
| `Activity_X_Instruction` (2e passage) | `decision_instruction` | `accepte` |
| `Activity_X_Deliberation` | `decision_direction` | `rejete` |

#### Déroulement XFlow (à partir du 2e passage instruction)

| # | Élément | Vérification |
|---|---|---|
| 2e Instruction → Gateway_InstResult | `Flow_GoInsp` (accepte) | |
| Inspection → Délibération | `decision_direction=rejete` | |
| `Gateway_Delib` | `Flow_GoRej2` | |
| `Gateway_JoinRej` → AvisRejet → `EndEvent_X_Rejet` | **FIN : Rejeté** | |

---

### SC-07 — Expiration du timer (15 jours sans correction)

**Objectif :** Valider que le timer boundary sur `Activity_X_RecCo` interrompt l'attente et déclenche le rejet automatique.
**Résultat attendu :** `EndEvent_X_Rejet` (sans action XPortal)

#### Variables à injecter

| Étape | Variable | Valeur |
|---|---|---|
| `Activity_X_Instruction` | `decision_instruction` | `correction` |
| Timer | — | Laisser expirer P15D (ou forcer en test) |

#### Déroulement XFlow

| # | Élément | Token entrant | Token sortant | Vérification |
|---|---|---|---|---|
| 1-7 | *(idem SC-04 jusqu'à Activity_X_RecCo)* | | | Attente `MSG_ECOLE_RESUB` |
| 8 | `Timer_Correction` | (15 jours écoulés) | `Flow_TimerRej` | Interruption d'`Activity_X_RecCo` |
| 9 | `Gateway_JoinRej` | `Flow_TimerRej` | `Flow_12` | Convergence rejet (entrée 3/3) |
| 10 | `Activity_X_AvisRejet` | `Flow_12` | `Flow_13` | action=`rejete` |
| 11 | `EndEvent_X_Rejet` | `Flow_13` | — | **FIN : Rejeté (timeout)** |

**Points de vigilance :**
- Token dans `Activity_X_RecCo` doit être interrompu (pas de double token)
- `Gateway_JoinRej` doit accepter `Flow_TimerRej` (entrée 3/3)
- Vérifier que `Gateway_P_Action` XPortal reçoit bien le message rejet côté citoyen

---

### SC-08 — Corrections multiples (N cycles) puis favorable

**Objectif :** Valider que la boucle correction peut s'effectuer plus d'une fois.
**Résultat attendu :** `EndEvent_X_Succes` + `EndEvent_PA`

**Exemple avec 2 corrections :**

| Cycle | `decision_instruction` | Action |
|---|---|---|
| 1 | `correction` | Correction 1 soumise |
| 2 | `correction` | Correction 2 soumise |
| 3 | `accepte` | → Inspection → Délibération (accepte) → Favorable |

#### Points de vigilance

- Token XFlow repasse 3 fois par `Gateway_JoinInst` (1x initial + 2x boucles)
- Token XPortal boucle 2 fois via `Flow_P_Loop` → `Gateway_P_Action`
- Chaque boucle déclenche un nouveau timer P15D sur `Activity_X_RecCo` (vérifier qu'il est bien réinitialisé)
- `Gateway_ActionPath` XPortal reçoit 2 messages "correction" puis 1 message "accepte"

---

## Matrice de couverture des gateways

| Gateway | SC-01 | SC-02 | SC-03 | SC-04 | SC-05 | SC-06 | SC-07 | SC-08 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `Gateway_JoinInst` via `Flow_3` (paiement) | X | X | X | X | X | X | X | X |
| `Gateway_JoinInst` via `Flow_AfterCor` (boucle) | | | | X | X | X | | X |
| `Gateway_InstResult` → accepte | X | | X | | | X | | X |
| `Gateway_InstResult` → correction | | | | X | X | X | X | X |
| `Gateway_InstResult` → rejete | | X | | | X | | | |
| `Gateway_Delib` → accepte | X | | | X | | | | X |
| `Gateway_Delib` → rejete | | | X | | | X | | |
| `Gateway_JoinRej` via `Flow_GoRej1` (inst.) | | X | | | X | | | |
| `Gateway_JoinRej` via `Flow_GoRej2` (delib.) | | | X | | | X | | |
| `Gateway_JoinRej` via `Flow_TimerRej` (timer) | | | | | | | X | |
| `Gateway_ActionPath` → accepte | X | | | X | | | | X |
| `Gateway_ActionPath` → rejete | | X | X | | X | X | X | |
| `Gateway_ActionPath` → correction | | | | X | X | X | | X |

**Couverture : 8 scénarios couvrent 100% des branches de toutes les gateways.**

---

## Checklist de vérification par scénario

Pour chaque scénario, vérifier :

- [ ] Le token ne se bloque pas à un gateway convergent
- [ ] La bonne branche est prise au gateway divergent (condition vérifiée)
- [ ] Les messages inter-pool (XPortal ↔ XFlow) sont bien corrélés
- [ ] Le token XPortal reçoit bien le message de retour sur `Gateway_P_Action`
- [ ] Aucun token orphelin ne reste actif en fin de processus
- [ ] Les endEvents corrects sont atteints (Succes vs Rejet)
- [ ] Le timer `Timer_Correction` est bien annulé si le message RESUB arrive avant expiration (SC-04, SC-08)
