# Guide Opérationnel — Agent IA Modélisateur BPMN GNSPD

**Rôle** : Ce guide est destiné à un agent IA dont la mission est de produire des fichiers `.bpmn` compatibles Camunda Platform 7 / GNSPD ATD, directement déployables en production.

---

## Protocole de démarrage (obligatoire avant toute génération)

Avant d'écrire une seule ligne de XML, l'agent **doit** exécuter les étapes suivantes dans l'ordre :

### Étape A — Lire les modèles de référence

Lire impérativement les fichiers de référence suivants :

1. `.agents/skills/bpmn-integrator/PATTERNS.md` → Snippets XML validés et checklist de conformité (source de vérité).
2. `.agents/skills/bpmn-integrator/examples/skeleton-dual-pool.bpmn` → Squelette dual-pool de départ (point de départ obligatoire).
3. `.agents/skills/bpmn-integrator/examples/expert-chaine-documentaire.bpmn` → Pattern chaîne documentaire complète (generateTemplate → QR → pdfImage → certSign).
4. `.agents/skills/bpmn-integrator/examples/expert-odoo-integration.bpmn` → Pattern intégration Odoo (search_read, create, write).

PATTERNS.md a priorité sur tout autre document en cas de contradiction.

### Étape B — Extraire les informations métier

Avant de modéliser, répondre à ces 10 questions à partir du SRS / TO-BE fourni :

| # | Question | Impact sur le BPMN |
|---|----------|-------------------|
| 1 | Le service est-il payant ? Et dans quels cas ? | Boucle paiement XFlow + userTask paiement XPortal |
| 2 | Quelles pièces justificatives sont requises ? | `gnspdAttachments` dans la userTask agent |
| 3 | Quelle est la décision possible de l'agent ? (conforme/correction/rejet) | Nombre de sorties de la gateway de décision |
| 4 | Y a-t-il une vérification dans Odoo ? Quel modèle ? Quel champ ? | Template `tg.gouv.gnspd.odoo` + domain |
| 5 | Y a-t-il une API REST tierce à appeler ? | Template `tg.gouv.gnspd.restBuilder` |
| 6 | Quels canaux de notification ? (Email / SMS / In-App) | `gnspdNotifySendEmail/SMS/InApp` |
| 7 | La boucle de correction est-elle possible ? Combien de fois ? | receiveTask resoumission + limite de boucle |
| 8 | Quel est le nom du service (code fonctionnel) ? | Noms des messages, IDs, noms des fichiers |
| 9 | Quels sont les systèmes tiers à configurer en KMS ? | Bloc configuration du startEvent |
| 10 | La gateway XPortal a-t-elle besoin du pattern simple (expert-2) ou distribué (expert-1) ? | Architecture du pool XPortal |

### Étape C — Déclarer les messages Kafka

Lister **tous** les échanges Kafka du processus avant d'écrire le XML :

```
1. [Portail → XFlow] : Soumission initiale    → MSG_[SERVICE]_START
2. [XFlow → Portail] : Autorisation paiement  → MSG_[SERVICE]_PAY_REQ    (si payant)
3. [Portail → XFlow] : Confirmation paiement  → MSG_[SERVICE]_PAY_CONFIRM (si payant)
4. [XFlow → Portail] : Retour vérification    → MSG_[SERVICE]_RETURN
5. [Portail → XFlow] : Resoumission correction → MSG_[SERVICE]_RESUB      (si boucle)
```

---

## Règles de génération — Priorité absolue

Ces règles ne souffrent aucune exception :

### R1 — Les deux pools DOIVENT être exécutables

```xml
<bpmn:process id="Process_Portal" isExecutable="true">
<bpmn:process id="Process_Xflow" isExecutable="true">
```

### R2 — Chaque message Kafka = un `<bpmn:message>` global

```xml
<!-- Déclaré AVANT <bpmn:collaboration>, à la racine des <bpmn:definitions> -->
<bpmn:message id="MSG_SERVICE_START" name="MSG_SERVICE_START" />
```

### R3 — Toute condition est en JavaScript explicite

```xml
<bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">
  this.data.Activity_X_Agent.result.submissionData.decision == 'oui'
</bpmn:conditionExpression>
```

**JAMAIS** de FEEL, de EL, ni de `language` absent.

### R4 — Toute gateway de décision agent a 3 sorties minimum

```
Gateway_X_Decision:
  → Approuvé   (decision == 'oui' && hasCorrections == 'non')
  → Correction  (decision == 'oui' && hasCorrections == 'oui')
  → Rejeté     (decision == 'non')
```

**JAMAIS** une gateway à 2 sorties (Approuvé / Correction) sans chemin de rejet.

### R5 — La boucle de correction est limitée

Ajouter une variable compteur ou un boundary timer :
```javascript
// Condition de sortie de boucle
this.data.nbCorrections < 3 // continuer la boucle
this.data.nbCorrections >= 3 // forcer le rejet
```

### R6 — Les données Odoo passent par la configuration du startEvent

```javascript
// CORRECT
$this.data.Event_X_Start.parameters.configuration.ODOO.URL

// INCORRECT (valeur en dur)
"https://decc-odoo.sandbox.gouv.tg"
```

### R7 — Le paiement est toujours orchestré côté BPMN

Si le service est payant, le BPMN doit modéliser :
1. XFlow → sendTask(autorisation paiement) → receiveTask(confirmation) → continuer
2. XPortal → receiveTask(autorisation) → userTask(paiement citoyen) → sendTask(confirmation)

**JAMAIS** de paiement géré uniquement dans le formulaire sans confirmation dans le BPMN.

### R8 — Le BPMNDiagram est complet

Chaque `<bpmn:...>` element de la collaboration, des deux processus, ET de tous les messageFlows, doit avoir un `BPMNShape` ou `BPMNEdge` correspondant.

---

## Templates XML prêts à l'emploi

### Template 1 — StartEvent XFlow avec configuration Odoo

```xml
<bpmn:startEvent id="Event_X_Start" name="Réception [Service]"
  camunda:modelerTemplate="tg.gouv.gnspd.startEvent"
  camunda:type="external"
  camunda:topic="flow-start">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdStepName">Début</camunda:inputParameter>
      <camunda:inputParameter name="gnspdDescription">Réception du dossier [Service] depuis Xportal</camunda:inputParameter>
      <camunda:inputParameter name="gnspdPriority">10</camunda:inputParameter>
      <camunda:inputParameter name="gnspdExecution">PORTAIL</camunda:inputParameter>
      <camunda:inputParameter name="gnspdPaymentAmount">0</camunda:inputParameter>
      <camunda:inputParameter name="gnspdCalculationOperator">ADDITION</camunda:inputParameter>
      <camunda:inputParameter name="gnspdCalculationVar1" />
      <camunda:inputParameter name="gnspdCalculationVar2" />
      <camunda:inputParameter name="gnspdTaskIsVisible">false</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskLabel" />
      <camunda:inputParameter name="gnspdTaskStatus">Pending</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskOrder" />
      <camunda:inputParameter name="gnspdTaskKind">citizen</camunda:inputParameter>
      <camunda:inputParameter name="gnspdCostVariable" />
      <camunda:inputParameter name="gnspdCostTotal" />
      <camunda:inputParameter name="gnspdCostUnitaire" />
      <camunda:inputParameter name="development">{
  "ODOO": {
    "URL": "https://[service]-odoo.dev.gouv.tg",
    "PORT": "",
    "DB": "[service]-dev",
    "SECRET_USERNAME": "{dbkms:[SERVICE]_ODOO_USERNAME}",
    "SECRET_PASSWORD": "{dbkms:[SERVICE]_ODOO_PASSWORD}"
  }
}</camunda:inputParameter>
      <camunda:inputParameter name="sandbox">{
  "ODOO": {
    "URL": "https://[service]-odoo.sandbox.gouv.tg",
    "PORT": "",
    "DB": "@{[service]}",
    "SECRET_USERNAME": "{dbkms:[SERVICE]_ODOO_USERNAME}",
    "SECRET_PASSWORD": "{dbkms:[SERVICE]_ODOO_PASSWORD}"
  }
}</camunda:inputParameter>
      <camunda:inputParameter name="preproduction">{
  "ODOO": {
    "URL": "https://[service]-odoo.preprod.gouv.tg",
    "PORT": "",
    "DB": "@{[service]}",
    "SECRET_USERNAME": "{dbkms:[SERVICE]_ODOO_USERNAME}",
    "SECRET_PASSWORD": "{dbkms:[SERVICE]_ODOO_PASSWORD}"
  }
}</camunda:inputParameter>
      <camunda:inputParameter name="production">{
  "ODOO": {
    "URL": "https://[service]-odoo.gouv.tg",
    "PORT": "",
    "DB": "@{[service]}",
    "SECRET_USERNAME": "{dbkms:[SERVICE]_ODOO_USERNAME}",
    "SECRET_PASSWORD": "{dbkms:[SERVICE]_ODOO_PASSWORD}"
  }
}</camunda:inputParameter>
    </camunda:inputOutput>
  </bpmn:extensionElements>
  <bpmn:outgoing>Flow_X01</bpmn:outgoing>
</bpmn:startEvent>
```

---

### Template 2 — SendTask Portail → XFlow (soumission initiale)

```xml
<bpmn:sendTask id="Activity_P_SendBO" name="Envoi au back-office"
  camunda:modelerTemplate="tg.gouv.gnspd.sendMessage"
  camunda:type="external"
  camunda:topic="flow-send-message">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdKafkaTopic">bpmn.commands</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTargetElementType">bpmn:StartEvent</camunda:inputParameter>
      <camunda:inputParameter name="gnspdMessageDestination">peer-xflow-local-sp</camunda:inputParameter>
      <camunda:inputParameter name="gnspdMessageRef">MSG_[SERVICE]_START</camunda:inputParameter>
      <camunda:inputParameter name="gnspdMessage">$this.data.Event_P_Start.parameters</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskIsVisible">false</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskLabel" />
      <camunda:inputParameter name="gnspdTaskStatus">Pending</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskOrder" />
      <camunda:inputParameter name="gnspdTaskKind">citizen</camunda:inputParameter>
      <camunda:inputParameter name="gnspdCostVariable" />
      <camunda:inputParameter name="gnspdCostTotal" />
      <camunda:inputParameter name="gnspdCostUnitaire" />
    </camunda:inputOutput>
  </bpmn:extensionElements>
  <bpmn:incoming>Flow_P01</bpmn:incoming>
  <bpmn:outgoing>Flow_P02</bpmn:outgoing>
</bpmn:sendTask>
```

---

### Template 3 — SendTask XFlow → Portail (retour avec action)

```xml
<bpmn:sendTask id="Activity_X_SendReturn" name="Notifier la correction (B09)"
  camunda:modelerTemplate="tg.gouv.gnspd.sendMessage"
  camunda:type="external"
  camunda:topic="flow-send-message">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdKafkaTopic">bpmn.commands</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTargetElementType">bpmn:ReceiveTask</camunda:inputParameter>
      <camunda:inputParameter name="gnspdMessageDestination">ch-portail-local-sp</camunda:inputParameter>
      <camunda:inputParameter name="gnspdMessageRef">MSG_[SERVICE]_RETURN</camunda:inputParameter>
      <camunda:inputParameter name="gnspdMessage">${
  "action": "correction",
  "motif": this.data.Activity_X_Agent.result.submissionData.motif ?? null,
  "reference": this.data.xref
}</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskIsVisible">false</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskLabel" />
      <camunda:inputParameter name="gnspdTaskStatus">Pending</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskOrder" />
      <camunda:inputParameter name="gnspdTaskKind">citizen</camunda:inputParameter>
      <camunda:inputParameter name="gnspdCostVariable" />
      <camunda:inputParameter name="gnspdCostTotal" />
      <camunda:inputParameter name="gnspdCostUnitaire" />
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:sendTask>
```

---

### Template 4 — UserTask agent XFlow (vérification de conformité)

```xml
<bpmn:userTask id="Activity_X_Agent" name="Vérification de conformité"
  camunda:modelerTemplate="tg.gouv.gnspd.userTask"
  camunda:formKey="[FORM_UUID]"
  camunda:type="external"
  camunda:topic="flow-user-task">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdTaskDescription">L'agent vérifie la conformité du dossier et des pièces justificatives</camunda:inputParameter>
      <camunda:inputParameter name="gnspdHandlerType">publish_submission</camunda:inputParameter>
      <camunda:inputParameter name="gnspdSubmissionFormkey">[nom-formulaire-agent]</camunda:inputParameter>
      <camunda:inputParameter name="gnspdFormSetting" />
      <camunda:inputParameter name="gnspdSubmissionData">$this.data.Event_X_Start.parameters.submissionData</camunda:inputParameter>
      <camunda:inputParameter name="gnspdAttachments">${
  "pieceIdentite": this.data.Event_X_Start.parameters.submissionData.pieceIdentite ?? null,
  "acteNaissance": this.data.Event_X_Start.parameters.submissionData.acteNaissance ?? null
}</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskIsVisible">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskLabel">Vérification conformité</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskStatus">Pending</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskOrder">1</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskKind">citizen</camunda:inputParameter>
      <camunda:inputParameter name="gnspdCandidateCompanies" />
      <camunda:inputParameter name="gnspdCostVariable" />
      <camunda:inputParameter name="gnspdCostTotal" />
      <camunda:inputParameter name="gnspdCostUnitaire" />
    </camunda:inputOutput>
  </bpmn:extensionElements>
  <!-- Entrées multiples : initial + resoumissions -->
  <bpmn:incoming>Flow_X_FromOdoo</bpmn:incoming>
  <bpmn:incoming>Flow_X_FromResub</bpmn:incoming>
  <bpmn:outgoing>Flow_X_ToDecision</bpmn:outgoing>
</bpmn:userTask>
```

---

### Template 5 — ServiceTask Odoo (search_read)

```xml
<bpmn:serviceTask id="Activity_X_Odoo" name="Vérification candidat Odoo"
  camunda:modelerTemplate="tg.gouv.gnspd.odoo"
  camunda:type="external"
  camunda:topic="flow-odoo">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdUrl">$this.data.Event_X_Start.parameters.configuration.ODOO.URL</camunda:inputParameter>
      <camunda:inputParameter name="gnspdDb">$this.data.Event_X_Start.parameters.configuration.ODOO.DB</camunda:inputParameter>
      <camunda:inputParameter name="gnspdPort">$this.data.Event_X_Start.parameters.configuration.ODOO.PORT</camunda:inputParameter>
      <camunda:inputParameter name="gnspdUsername">$this.data.Event_X_Start.parameters.configuration.ODOO.SECRET_USERNAME</camunda:inputParameter>
      <camunda:inputParameter name="gnspdPassword">$this.data.Event_X_Start.parameters.configuration.ODOO.SECRET_PASSWORD</camunda:inputParameter>
      <camunda:inputParameter name="gnspdModel">exam.inscription</camunda:inputParameter>
      <camunda:inputParameter name="gnspdMethod">search_read</camunda:inputParameter>
      <camunda:inputParameter name="gnspdDomain">${"numero_table": this.data.Event_X_Start.parameters.submissionData.numeroDeTable}</camunda:inputParameter>
      <camunda:inputParameter name="gnspdFields" />
      <camunda:inputParameter name="gnspdParams" />
      <camunda:inputParameter name="gnspdRecordId" />
      <camunda:inputParameter name="gnspdOptions" />
      <camunda:inputParameter name="gnspdReportModel" />
      <camunda:inputParameter name="gnspdReportData">{}</camunda:inputParameter>
      <camunda:inputParameter name="gnspdReportType">docx</camunda:inputParameter>
      <camunda:inputParameter name="gnspdRestFeedback" />
      <camunda:inputParameter name="gnspdRestFeedbackSchema" />
      <camunda:inputParameter name="gnspdTaskIsVisible">false</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskLabel" />
      <camunda:inputParameter name="gnspdTaskStatus">Pending</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskOrder" />
      <camunda:inputParameter name="gnspdTaskKind">citizen</camunda:inputParameter>
      <camunda:inputParameter name="gnspdCostVariable" />
      <camunda:inputParameter name="gnspdCostTotal" />
      <camunda:inputParameter name="gnspdCostUnitaire" />
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

---

### Template 6 — SendNotification tricanal (email + SMS + in-app)

```xml
<bpmn:serviceTask id="Activity_X_NotifCorrection" name="Notifier la correction"
  camunda:modelerTemplate="tg.gouv.gnspd.sendNotification"
  camunda:type="external"
  camunda:topic="flow-notify">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdNotifySendEmail">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyEmail">$this.data.applicant.email</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyTemplateEmail">01KHBXDFGV1NTPHAR80ZSWEZXH</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyContentEmail">${
  "record_id": this.data.xref,
  "reason": this.data.Activity_X_Agent.result.submissionData.motif ?? ""
}</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifySendSMS">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyPhone">$this.data.applicant.phone</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyTemplateSMS">01KHBXF5B8B8WH9QFDZP607F5M</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyContentSMS">${"record_id": this.data.xref}</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyInApp">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyTemplateInApp">01KHBX6AEWCBG136176D2GMZM3</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyContentInApp">${
  "record_id": this.data.xref,
  "reason": this.data.Activity_X_Agent.result.submissionData.motif ?? ""
}</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyAttachment" />
      <camunda:inputParameter name="gnspdTaskIsVisible">false</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskLabel" />
      <camunda:inputParameter name="gnspdTaskStatus">Pending</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskOrder" />
      <camunda:inputParameter name="gnspdTaskKind">citizen</camunda:inputParameter>
      <camunda:inputParameter name="gnspdCostVariable" />
      <camunda:inputParameter name="gnspdCostTotal" />
      <camunda:inputParameter name="gnspdCostUnitaire" />
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

---

## Carte des séquences XFlow (logique métier standard)

```
┌─ StartEvent (reception Kafka) ──────────────────────────────────────────┐
│                                                                          │
│ → GED / Enregistrement (optionnel)                                       │
│ → Notification accusé de réception (sendNotification)                    │
│ → Gateway : Duplicata / Payant ?                                         │
│     OUI → Notification paiement → SendTask(autorisation paiement)       │
│           → IntermediateCatch(confirmation paiement)                     │
│           → Gateway(paiement OK ?)                                       │
│               KO → SendTask(rejet paiement) → EndEvent(Rejet)           │
│               OK → ↓ (merge)                                             │
│     NON → ↓ (merge gateway)                                             │
│                                                                          │
│ → [Optionnel] Odoo : vérification candidat                              │
│     → Gateway(candidat inscrit ?)                                        │
│         NON → Notification → SendTask(rejet) → EndEvent(Rejet)          │
│         OUI → ↓                                                          │
│                                                                          │
│ → UserTask Agent : Vérification de conformité                           │
│     (multi-entrant : initial + retour resoumission)                     │
│ → Gateway(décision agent ?)                                              │
│     APPROUVÉ  → Odoo:create → Notification succès → SendTask(accepte)  │
│                → EndEvent(Succès)                                        │
│     CORRECTION → Notification correction → SendTask(correction portail) │
│                → ReceiveTask(resoumission) → ↑ UserTask Agent           │
│     REJETÉ    → Notification rejet → SendTask(rejet portail)            │
│                → EndEvent(Rejet)                                         │
└──────────────────────────────────────────────────────────────────────────┘
```

## Carte des séquences XPortal (machine à états — pattern expert-2)

```
┌─ StartEvent (soumission formulaire) ───────────────────────────────────┐
│                                                                         │
│ → SendTask(→ XFlow : soumission initiale)                              │
│ → ReceiveTask(attendre retour XFlow) ◄──────────────────┐             │
│ → Gateway(action ?)                                       │             │
│     paiement_requis → UserTask(paiement citoyen)          │             │
│                     → SendTask(→ XFlow : confirm paiement) │             │
│                     → ↑ ReceiveTask                        │             │
│     correction      → UserTask(corrections citoyen)        │             │
│                     → SendTask(→ XFlow : resoumission)     │             │
│                     → ↑ ReceiveTask                        │             │
│     accepte         → EndEvent(Succès — Document disponible)            │
│     rejete          → EndEvent(Rejet)                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Auto-vérification avant livraison

Exécuter mentalement ce test pour chaque fichier généré :

### Test 1 — Traçabilité des messages
Pour chaque `<bpmn:message>` déclaré à la racine :
- [ ] Il y a exactement un `sendTask` ou `startEvent` qui l'envoie (via `gnspdMessageRef`)
- [ ] Il y a exactement une `receiveTask` ou `intermediateCatchEvent` qui l'attend (via `messageRef`)
- [ ] Il y a un `messageFlow` dans la collaboration reliant les deux

### Test 2 — Chemins complets
Partir de chaque startEvent et tracer tous les chemins possibles :
- [ ] Chaque chemin atteint un endEvent
- [ ] Aucun chemin ne crée un deadlock (gateway sans chemin de sortie satisfait)
- [ ] Les boucles ont une condition de sortie

### Test 3 — Cohérence des références
- [ ] Chaque `sourceRef`/`targetRef` dans les sequenceFlow pointe sur un ID existant
- [ ] Chaque `messageRef` dans les receiveTask pointe sur un `<bpmn:message>` existant
- [ ] Chaque `gnspdMessageRef` dans les sendTask pointe sur un nom de message existant

### Test 4 — Variables de données
- [ ] Chaque `this.data.XXXXX` référence soit un élément BPMN dont l'ID est `XXXXX`, soit un champ global (`applicant`, `xref`, `recordUid`)
- [ ] Les champs Odoo existent dans le modèle Odoo correspondant
- [ ] Les pièces jointes dans `gnspdAttachments` correspondent aux clés de champs `file` du formulaire

### Test 5 — Paramètres standards présents
Pour chaque tâche avec un `camunda:modelerTemplate`, vérifier que ces 7 paramètres sont présents :
```
gnspdTaskIsVisible, gnspdTaskLabel, gnspdTaskStatus, gnspdTaskOrder,
gnspdTaskKind, gnspdCostVariable, gnspdCostTotal, gnspdCostUnitaire
```
