# Cartographie TO-BE : Demande de Casier Judiciaire (Bulletin n°3)

**Organisme** : Ministère de la Justice — Direction des Affaires Civiles et du Sceau (DACS)

## Vision Générale

Le citoyen soumet sa demande de casier judiciaire **entièrement en ligne** via le portail XPortal, paie les frais (2 000 FCFA) sur la plateforme e-Gov, puis est notifié automatiquement par SMS/email quand le bulletin est prêt. Il ne se déplace **qu'une seule fois** — pour retirer le bulletin original signé et cacheté au guichet.

**Service hybride** : la signature manuscrite et le cachet humide sont légalement requis (Code de procédure pénale). Le retrait physique reste obligatoire tant que la signature électronique n'est pas reconnue pour ce type de document.

**Contrainte technique** : le fichier national des condamnations est un registre papier non informatisé. L'instruction reste donc humaine (pas d'intégration Odoo/API pour la vérification automatique).

### Frictions résolues

| Friction AS-IS | Solution TO-BE | Règle appliquée |
|---------------|----------------|-----------------|
| F1 — Deux déplacements physiques | Soumission en ligne, **un seul déplacement** (retrait) | Règle 1 (zéro papier) |
| F2 — Paiement caisse uniquement | Paiement e-Gov en ligne (Flooz, TMoney, Visa, Mastercard) | Règle 3 (paiement sans contact) |
| F4 — Aucune notification | SMS + email automatiques à chaque jalon (réception, paiement, bulletin prêt) | Règle 5 (communication proactive) |
| F5 — 15% de rejet au dépôt | Validation Form.io temps réel + boucle de correction asynchrone (max 3 tentatives) | Règle 5 (validation au fil de l'eau) |
| F6 — Registre papier | Traçabilité XFlow complète, statut temps réel sur le portail | Règle 6 (transparence totale) |

### Frictions non résolues (contraintes légales/techniques)

| Friction AS-IS | Raison du maintien |
|---------------|-------------------|
| F3 — Fichier des condamnations papier | Non informatisé — l'agent consulte manuellement. Sera résolu lors de la numérisation du fichier national. |
| F7 — Signature manuscrite + cachet | Obligation légale — le bulletin n°3 n'admet pas la signature électronique. |

## Architecture Technique

- **Frontend / Orchestrateur Citoyen** : XPortal (pool BPMN exécutable, machine à états).
- **Moteur de workflow Métier** : XFlow (Camunda Platform 7, pool de traitement).
- **Bus de messaging** : Kafka (topic `bpmn.commands`) pour la synchro inter-pools.
- **Identité** : Pré-remplissage e-ID automatique (nom, prénom, téléphone, email).
- **Paiement** : Plateforme de paiement e-Gov **externe** (2 000 FCFA fixe). Le citoyen est redirigé hors de XPortal pour payer.
- **Notifications** : Service Tasks `tg.gouv.gnspd.sendNotification` (SMS + email + in-app).

## Acteurs et Systèmes

| Acteur / Système | Rôle TO-BE |
|------------------|-----------|
| Citoyen | Soumet en ligne, paie en ligne, reçoit notifications, retire physiquement. |
| Moteur XPortal | Machine à états citoyen : soumission → paiement → attente → correction/retrait. |
| Plateforme e-Gov | Paiement en ligne (2 000 FCFA fixe) — externe à XPortal/XFlow. |
| Moteur XFlow | Orchestration back-office : enchaîne instruction, validation, notifications. |
| Agent instructeur DACS | Vérifie les pièces, consulte le fichier des condamnations (papier), rédige le bulletin via formulaire d'instruction XFlow. |
| Chef de service DACS | Contrôle le bulletin rédigé, valide ou rejette via interface XFlow. |
| Service de notification | SMS/email automatiques aux jalons clés. |

## Étapes Digitalisées

### 1. Soumission en ligne (Citoyen → XPortal)
- Le citoyen se connecte au portail, son identité est pré-remplie via e-ID.
- Il remplit le formulaire : motif de la demande, upload pièce d'identité, upload acte de naissance.
- Validation Form.io temps réel (format fichier, taille max, champs obligatoires).
- Accusé de réception automatique par email et SMS.
- Durée : immédiat.

### 2. Paiement des frais (Citoyen → Plateforme e-Gov)
- XFlow reçoit le dossier et ordonne le paiement (2 000 FCFA fixe).
- XPortal redirige le citoyen vers la plateforme de paiement e-Gov externe.
- Le citoyen paie (Flooz, TMoney, Visa, Mastercard).
- Le callback e-Gov confirme le paiement à XFlow.
- XFlow envoie la confirmation au portail.
- Durée : immédiat à quelques minutes.

### 3. Instruction du dossier (Agent instructeur → XFlow)
- L'agent instructeur reçoit le dossier dans son tableau de bord XFlow (userTask).
- Il vérifie la conformité des pièces jointes (identité valide, acte de naissance lisible).
- Il consulte manuellement le fichier national des condamnations.
- Il rédige le bulletin via le formulaire d'instruction : résultat (néant / mentions), observations.
- Décision :
  - **Conforme** → le bulletin rédigé passe à la validation du chef.
  - **Correction requise** → notification au citoyen avec le motif (pièce illisible, identité expirée...).
  - **Rejet** → notification de rejet (motif : usurpation d'identité, fraude documentaire...).
- SLA : 72 heures.
- Timer non-interrompant : escalade SLA si dépassement (notification au chef de service).

### 3a. Boucle de correction (Citoyen → XPortal)
- Le citoyen reçoit une notification (SMS + email) avec le motif de correction.
- Il corrige son dossier via le portail (reupload pièces, modification formulaire) **sans recréer de dossier**.
- Le dossier corrigé repart à l'instruction (étape 3).
- Maximum 3 tentatives. Au-delà, rejet automatique.
- Timer : si pas de correction sous 15 jours, clôture automatique.

### 4. Validation par le chef de service (Chef de service → XFlow)
- Le chef de service reçoit le bulletin rédigé dans son tableau de bord XFlow (userTask).
- Il contrôle l'exactitude (identité, mentions, rédaction).
- Décision :
  - **Validé** → le bulletin est signé et cacheté manuellement (hors système).
  - **Rejeté** → notification de rejet.
- SLA : 24 heures.

### 5. Notification et mise à disposition (Système → XFlow)
- XFlow met à jour le statut portail : « Bulletin prêt à retirer ».
- Notification tricanale (SMS + email + in-app) : « Votre bulletin de casier judiciaire est prêt. Présentez-vous au guichet de la DACS avec votre récépissé et votre pièce d'identité originale. »
- Un récépissé de retrait est disponible sur le portail (téléchargeable / affichable).
- Durée : immédiat.

### 6. Retrait du bulletin — PHYSIQUE (Citoyen → Guichet DACS)
- Le citoyen se présente au guichet de la DACS.
- Il présente son récépissé (imprimé ou affiché sur téléphone) et sa pièce d'identité originale.
- L'agent de guichet remet le bulletin signé et cacheté.
- Obligation légale : signature manuscrite + cachet humide (Code de procédure pénale).
- Durée : 1 visite unique.

## Patterns d'orchestration inter-pools (OBLIGATOIRE)

### Messages Kafka (service payant = 6 messages)

| Message | Direction | Déclencheur |
|---------|-----------|-------------|
| `MSG_CASIERJUD_START` | XPortal → XFlow | Soumission initiale du formulaire |
| `MSG_CASIERJUD_PAY_ORDER` | XFlow → XPortal | Ordre de paiement après réception du dossier |
| `MSG_CASIERJUD_PAY_CALLBACK` | e-Gov → XFlow | Callback de la plateforme de paiement |
| `MSG_CASIERJUD_PAY_CONFIRM` | XFlow → XPortal | Confirmation de paiement |
| `MSG_CASIERJUD_RETURN` | XFlow → XPortal | Décision (action : correction / accepte / rejete) |
| `MSG_CASIERJUD_RESUB` | XPortal → XFlow | Resoumission après correction |

### P1. Symétrie des gateways
La gateway "Action XFlow ?" est répliquée dans les deux pools. XPortal lit `this.data.Recv_P_Return.result.data.action` et XFlow lit `this.data.Activity_X_Agent.result.submissionData.decision` — chaque pool route indépendamment.

### P2. ReceiveTask multi-entrante
Côté XPortal, une seule `Recv_P_Return` reçoit 3 chemins : après confirmation paiement, après envoi initial (si paiement échoue/annulé), et après resoumission correction.

### P3. Notification PUIS SendMessage
XFlow notifie le citoyen (SMS/email) AVANT d'envoyer le message Kafka qui change l'état du portail.

### P4. Nœud de rejet DRY
Un seul bloc de notification de rejet reçoit tous les chemins de rejet : rejet agent, rejet chef, max corrections atteint, non-paiement.

### P5. Pas de vérification système avant agent
Exception documentée : le fichier des condamnations n'est pas informatisé. L'agent fait la vérification manuellement. Pas de serviceTask Odoo/API avant la userTask agent.

### P6. Boucle de correction avec re-vérification
La boucle revient directement à l'agent instructeur (pas de vérification système intermédiaire, car il n'y en a pas — voir P5).

### P7. Terminaison explicite de chaque branche
EndEvents prévus :
- `End_P_Accepte` — Bulletin retiré (XPortal)
- `End_P_Rejete` — Demande rejetée (XPortal)
- `End_X_Success` — Bulletin validé et mis à disposition (XFlow)
- `End_X_Reject` — Dossier rejeté (XFlow, DRY)
- `End_X_Escalade` — Fin du jeton parallèle de l'escalade SLA (XFlow)

### P8. Appariement SendTask/ReceiveTask
6 messages, 7 messageFlows (MSG_CASIERJUD_RETURN est utilisé dans 2 chemins : acceptation et correction — mais via un seul ReceiveTask multi-entrant côté XPortal).

## Gains Attendus

| Indicateur | AS-IS | TO-BE | Gain |
|-----------|-------|-------|------|
| Déplacements physiques | 2 (dépôt + retrait) | 1 (retrait uniquement) | -50% |
| Délai de traitement | 3 jours ouvrables | 2-3 jours ouvrables (instruction humaine inchangée) | Notification immédiate dès que prêt |
| Rejet au dépôt | 15% | ~0% (validation Form.io + correction en ligne) | -100% de déplacements inutiles |
| Paiement | Espèces au guichet | En ligne (Flooz, TMoney, Visa, MC) | Traçabilité 100%, zéro file d'attente |
| Notifications | Aucune | 4 jalons (réception, paiement, correction, prêt) | Transparence totale |
| Traçabilité | Registre papier | XFlow temps réel | Suivi 100% numérique |
