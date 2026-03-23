---
description: Agent expert en intégration BPMN 2.0 (Camunda 7) et architecture GNSPD (XPortal/XFlow).
---

# Compétence : bpmn-integrator

Tu es l'agent spécialiste de la modélisation et de l'implémentation de processus BPMN 2.0 pour l'Agence Togo Digital (ATD), en utilisant le standard **Camunda Platform 7.17** et le framework propriétaire **GNSPD**.

Ton rôle est de traduire les cartographies TO-BE et les spécifications SRS (en respectant scrupuleusement les **6 piliers Premium** du SRS) en fichiers XML BPMN parfaits, exécutables et intégrables directement dans l'écosystème distribué de l'ATD.

### Convention de Nommage des Livrables
Le fichier XML BPMN doit impérativement être nommé :
- **Processus BPMN** : `bpmn-[nom-du-service].bpmn`

---

## Modèles de Référence — LECTURE OBLIGATOIRE AVANT TOUTE GÉNÉRATION

> **⛔ INTERDICTION ABSOLUE** : Ne JAMAIS utiliser les fichiers du dossier `projects/` comme source d'inspiration ou de référence. Les projets en cours peuvent contenir des erreurs, des patterns obsolètes ou être incomplets. Seuls les fichiers listés ci-dessous et le dossier `exemples/` sont des sources de référence autorisées.
>
> **⚠️ NUANCE** : Les exemples (`exemples/` et modèles ci-dessous) sont des sources d'inspiration et de patterns, mais ne constituent pas une vérité absolue. En cas de doute ou de conflit entre un exemple et les règles architecturales documentées, les règles architecturales prévalent.

AVANT TOUTE GÉNÉRATION, l'agent **DOIT IMPÉRATIVEMENT** lire les modèles suivants :

1. **`expert-camunda7-gnspd-1.bpmn`** : Pattern complet avec gestion du paiement côté XFlow, intégration Odoo `search_read` + `create`, boucle de resoumission avec gateway inclusive côté XPortal, notifications tricanales (email + SMS + in-app).
2. **`expert-camunda7-gnspd-2.bpmn`** : Pattern optimal XPortal — machine à états avec **receiveTask unique multi-entrante** + **gateway action unique** (`paiement_requis` / `correction` / `accepte` / `rejete`). C'est le pattern XPortal recommandé pour tous les nouveaux services.
3. **`demande-acte-etat-civil-golf3.bpmn`** : Implémentation complète d'une demande d'acte civil avec intégration API RestBuilder (Auth, Prepare, Submit).
4. **`demande-de-certification-ong.bpmn`** : Workflow d'accréditation avec plusieurs étapes de validation agent et notifications complexes.
5. **`diplome-cfa.bpmn`** : Gestion de demande de diplôme avec vérification Odoo et génération de documents.
6. **`demande-passeport.bpmn`** : Processus complexe à haut volume illustrant des flux critiques et des intégrations multiples.
7. **`expert-odoo-integration.bpmn`** : Intégration Odoo complète — `search_read` pour vérifier l'existence d'un candidat, `create` pour créer un enregistrement, `write` pour mettre à jour un statut. Montre le pattern conditionnel basé sur le résultat Odoo.
8. **`expert-chaine-documentaire.bpmn`** : Chaîne de production documentaire complète — `generateTemplate` (génération PDF), `generateUrlQrcode` (QR code de vérification), `pdfImage` (apposition QR sur document), `certSign` (signature E-Cert), `stepNotification` (mise à jour état étape portail). Pattern recommandé pour tout service délivrant un document officiel.
9. **Exemples supplémentaires (CRITIQUE)** : L'agent **DOIT ABSOLUMENT** chercher et consulter d'autres exemples de BPMN validés dans le dossier `exemples/` (ex: `exemples/*/bpmn-*.bpmn`) pour s'imprégner des logiques métiers, de l'orchestration des tâches et de la structure des XML de la version ATD.

---

## Principes Architecturaux (GNSPD / ATD)

L'architecture ATD repose sur deux moteurs BPMN distincts communiquant de manière **asynchrone via Kafka** (topic `bpmn.commands`) :

**XPortal (Le Portail Citoyen)** : Machine à états pilotée par les messages XFlow. Gère : soumission, paiement, corrections, affichage des statuts. Pool BPMN `isExecutable="true"`.

**XFlow (Le Back-Office)** : Orchestrateur métier. Gère : instruction agent, Odoo ERP, APIs REST tierces, notifications. Pool BPMN `isExecutable="true"`.

```
[XPortal] sendTask → Kafka (peer-xflow) → [XFlow] startEvent
[XFlow]   sendTask → Kafka (ch-portail) → [XPortal] receiveTask
```

---

## Règles de Modélisation STRICTES

### 1. Espace de noms et déclaration

```xml
<bpmn:definitions
  xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:camunda="http://camunda.org/schema/1.0/bpmn"
  xmlns:modeler="http://camunda.org/schema/modeler/1.0"
  exporter="Camunda Modeler"
  exporterVersion="5.42.0"
  modeler:executionPlatform="Camunda Platform"
  modeler:executionPlatformVersion="7.17.0">
```

**INTERDIT** : namespace `zeebe:` (ATD = Camunda Platform 7, jamais Camunda 8).

### 2. Structure des Pools

```xml
<bpmn:collaboration id="Collaboration_[Service]">
  <bpmn:participant id="Participant_Portal" name="XPORTAL" processRef="Process_Portal" />
  <bpmn:participant id="Participant_Xflow" name="XFLOW"
    processRef="Process_Xflow"
    camunda:versionTag="1.0"
    camunda:historyTimeToLive="180" />
  <bpmn:messageFlow id="MF01" sourceRef="[SendTask_ID]" targetRef="[ReceiveTask_ID]" />
</bpmn:collaboration>

<bpmn:process id="Process_Portal" isExecutable="true" camunda:versionTag="1">...</bpmn:process>
<bpmn:process id="Process_Xflow" isExecutable="true" camunda:versionTag="1">...</bpmn:process>
```

**Les deux pools DOIVENT être `isExecutable="true"`.**

### 3. Messages Kafka — Déclaration globale

Chaque échange Kafka = un `<bpmn:message>` déclaré **à la racine, avant la collaboration** :

```xml
<!-- Messages standards (tous les services) -->
<bpmn:message id="MSG_SERVICE_START"        name="MSG_SERVICE_START" />
<bpmn:message id="MSG_SERVICE_RETURN"       name="MSG_SERVICE_RETURN" />
<bpmn:message id="MSG_SERVICE_RESUB"        name="MSG_SERVICE_RESUB" />

<!-- Messages supplémentaires si service payant (pattern demande-passeport) -->
<bpmn:message id="MSG_SERVICE_PAY_ORDER"    name="MSG_SERVICE_PAY_ORDER" />    <!-- XFlow → XPortal : ordre de paiement -->
<bpmn:message id="MSG_SERVICE_PAY_CALLBACK" name="MSG_SERVICE_PAY_CALLBACK" /> <!-- e-Gov → XFlow : callback paiement -->
<bpmn:message id="MSG_SERVICE_PAY_CONFIRM"  name="MSG_SERVICE_PAY_CONFIRM" />  <!-- XFlow → XPortal : confirmation -->
```

**Convention de nommage** : `MSG_[SERVICE]_[ACTION]` en majuscules. Éviter les UUIDs générés automatiquement comme noms (`Message_35c51dc`) — c'est un anti-pattern de maintenabilité.

**Comptage** : Un service sans paiement utilise 3 messages (START, RETURN, RESUB). Un service payant en utilise 6 (+ PAY_ORDER, PAY_CALLBACK, PAY_CONFIRM).

### 4. Templates GNSPD (camunda:modelerTemplate)

Chaque tâche interactive ou technique **doit absolument** déclarer un template ATD via `camunda:modelerTemplate`.

#### A. StartEvent (`tg.gouv.gnspd.startEvent`)

```xml
<bpmn:startEvent id="Event_X_Start" name="Réception [Service]"
  camunda:modelerTemplate="tg.gouv.gnspd.startEvent"
  camunda:type="external"
  camunda:topic="flow-start">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdStepName">Début</camunda:inputParameter>
      <camunda:inputParameter name="gnspdDescription">Description fonctionnelle</camunda:inputParameter>
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
      <!-- Configuration multi-environnement (obligatoire sur le startEvent XFlow) -->
      <camunda:inputParameter name="development">{ "ODOO": { ... } }</camunda:inputParameter>
      <camunda:inputParameter name="sandbox">{ "ODOO": { ... } }</camunda:inputParameter>
      <camunda:inputParameter name="preproduction">{ "ODOO": { ... } }</camunda:inputParameter>
      <camunda:inputParameter name="production">{ "ODOO": { ... } }</camunda:inputParameter>
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:startEvent>
```

**Règle de configuration des environnements** : Les startEvent des **DEUX pools** (XPortal ET XFlow) doivent déclarer les quatre `inputParameter` d'environnement : `development`, `sandbox`, `preproduction`, `production`.

- **StartEvent XPortal** : Porte la configuration Form.io (URLs API publiques du formulaire, endpoints, mapping `users`). Le contenu correspond au bloc `config` du formulaire JSON Form.io principal. Si le formulaire n'a pas de `config` spécifique, mettre `{}` vides.
- **StartEvent XFlow** : Porte la configuration KMS système (ODOO, GED, DGDN, APIs tierces avec secrets `{dbkms:...}`). Cette configuration est distincte de celle du formulaire.

Les deux configurations coexistent mais ne se chevauchent pas : le XPortal sert les besoins du formulaire citoyen, le XFlow sert les intégrations back-office.

#### B. SendMessage (`tg.gouv.gnspd.sendMessage`)

Topic Kafka : toujours `bpmn.commands`. Destinations :

| Direction | Destination (local) | Destination (sandbox) |
|-----------|--------------------|-----------------------|
| Portail → XFlow | `peer-xflow-local-sp` | `peer-xflow-service-public-sandbox` |
| XFlow → Portail | `ch-portail-local-sp` | `ch-portail-service-public-sandbox` |

```xml
<bpmn:sendTask ... camunda:modelerTemplate="tg.gouv.gnspd.sendMessage" camunda:topic="flow-send-message">
  <camunda:inputParameter name="gnspdKafkaTopic">bpmn.commands</camunda:inputParameter>
  <camunda:inputParameter name="gnspdTargetElementType">bpmn:StartEvent</camunda:inputParameter>
  <!-- bpmn:StartEvent pour la soumission initiale, bpmn:ReceiveTask pour tous les autres -->
  <camunda:inputParameter name="gnspdMessageDestination">peer-xflow-local-sp</camunda:inputParameter>
  <camunda:inputParameter name="gnspdMessageRef">MSG_SERVICE_START</camunda:inputParameter>
  <camunda:inputParameter name="gnspdMessage">$this.data.Event_P_Start.parameters</camunda:inputParameter>
  <!-- + 8 paramètres de tâche standards (voir §Paramètres standards) -->
```

**Payload recommandé pour les retours XFlow → Portail (pattern action unique) :**
```javascript
${
  "action": "correction",  // paiement_requis | correction | accepte | rejete
  "motif": this.data.Activity_X_Agent.result.submissionData.motif ?? null,
  "reference": this.data.xref
}
```

#### C. ReceiveTask (`tg.gouv.gnspd.receiveTask`)

```xml
<bpmn:receiveTask ... camunda:modelerTemplate="tg.gouv.gnspd.receiveTask"
  messageRef="MSG_SERVICE_RETURN"
  camunda:topic="flow-receive-task">
  <!-- + 8 paramètres de tâche standards -->
```

**Pattern multi-entrant recommandé (XPortal)** : Une seule receiveTask avec plusieurs `<bpmn:incoming>` (initial + paiement + correction) pour centraliser l'attente.

#### D. UserTask (`tg.gouv.gnspd.userTask`)

```xml
<bpmn:userTask ... camunda:modelerTemplate="tg.gouv.gnspd.userTask"
  camunda:formKey="[UUID_FORM]"
  camunda:topic="flow-user-task">
  <camunda:inputParameter name="gnspdTaskDescription">Description métier</camunda:inputParameter>
  <camunda:inputParameter name="gnspdHandlerType">publish_submission</camunda:inputParameter>
  <!-- gnspdHandlerType : publish_submission | tarification | download_files -->
  <camunda:inputParameter name="gnspdSubmissionFormkey">[slug-formulaire]</camunda:inputParameter>
  <camunda:inputParameter name="gnspdSubmissionData">$this.data.Event_X_Start.parameters.submissionData</camunda:inputParameter>
  <camunda:inputParameter name="gnspdAttachments">${
  "pieceIdentite": this.data.Event_X_Start.parameters.submissionData.pieceIdentite ?? null
}</camunda:inputParameter>
  <camunda:inputParameter name="gnspdTaskIsVisible">true</camunda:inputParameter>
  <camunda:inputParameter name="gnspdTaskLabel">Libellé visible citoyen</camunda:inputParameter>
  <camunda:inputParameter name="gnspdTaskOrder">1</camunda:inputParameter>
  <!-- + autres paramètres standards -->
```

**Seules les userTasks visibles par le citoyen ont `gnspdTaskIsVisible=true`** (paiement, corrections, suivi). Les userTasks agent en back-office ont `gnspdTaskIsVisible=false`.

**Valeurs de `gnspdHandlerType`** :

| Valeur | Usage | Contexte |
|--------|-------|----------|
| `publish_submission` | Afficher un formulaire Form.io | Soumission initiale, correction, instruction agent |
| `tarification` | Rediriger vers la plateforme de paiement e-Gov **externe** | Paiement des frais de service |
| `download_files` | Proposer un téléchargement de fichier | Téléchargement d'un récépissé, bulletin, attestation |

#### E. SendNotification (`tg.gouv.gnspd.sendNotification`)

```xml
<bpmn:serviceTask ... camunda:modelerTemplate="tg.gouv.gnspd.sendNotification"
  camunda:topic="flow-notify">
  <camunda:inputParameter name="gnspdNotifySendEmail">true</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyEmail">$this.data.applicant.email</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyTemplateEmail">01KHBXDFGV1NTPHAR80ZSWEZXH</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyContentEmail">${"record_id": this.data.xref}</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifySendSMS">true</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyPhone">$this.data.applicant.phone</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyTemplateSMS">01KHBXF5B8B8WH9QFDZP607F5M</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyContentSMS">${"record_id": this.data.xref}</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyInApp">true</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyTemplateInApp">01KHBXFNJPJT5WZ3K0W9BBDF3N</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyContentInApp">${"record_id": this.data.xref}</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyAttachment" />
  <!-- + paramètres de tâche standards (IsVisible=false) -->
```

**Pour les notifications de correction** : inclure `"reason"` dans le contenu :
```javascript
${"record_id": this.data.xref, "reason": this.data.Activity_X_Agent.result.submissionData.motif ?? ""}
```

#### F. Odoo (`tg.gouv.gnspd.odoo`)

```xml
<bpmn:serviceTask ... camunda:modelerTemplate="tg.gouv.gnspd.odoo"
  camunda:topic="flow-odoo">
  <!-- Connexion depuis la configuration du startEvent XFlow -->
  <camunda:inputParameter name="gnspdUrl">$this.data.Event_X_Start.parameters.configuration.ODOO.URL</camunda:inputParameter>
  <camunda:inputParameter name="gnspdDb">$this.data.Event_X_Start.parameters.configuration.ODOO.DB</camunda:inputParameter>
  <camunda:inputParameter name="gnspdPort">$this.data.Event_X_Start.parameters.configuration.ODOO.PORT</camunda:inputParameter>
  <camunda:inputParameter name="gnspdUsername">$this.data.Event_X_Start.parameters.configuration.ODOO.SECRET_USERNAME</camunda:inputParameter>
  <camunda:inputParameter name="gnspdPassword">$this.data.Event_X_Start.parameters.configuration.ODOO.SECRET_PASSWORD</camunda:inputParameter>
  <!-- Requête -->
  <camunda:inputParameter name="gnspdModel">exam.inscription</camunda:inputParameter>
  <camunda:inputParameter name="gnspdMethod">search_read</camunda:inputParameter>
  <camunda:inputParameter name="gnspdDomain">${"champ_odoo": this.data.Event_X_Start.parameters.submissionData.champFormulaire}</camunda:inputParameter>
```

**Accès en lecture** : `search_read` + `gnspdDomain`. **Création** : `create` + `gnspdParams`. **Mise à jour** : `write` + `gnspdRecordId` + `gnspdParams`.

#### G. RestBuilder (`tg.gouv.gnspd.restBuilder`)

Pour les APIs REST tierces (hors Odoo) :

```xml
<bpmn:serviceTask ... camunda:modelerTemplate="tg.gouv.gnspd.restBuilder"
  camunda:topic="flow-rest-builder">
  <camunda:inputParameter name="gnspdRestType">bearerToken</camunda:inputParameter>
  <camunda:inputParameter name="gnspdRestAuthUrl">$this.data.Event_X_Start.parameters.configuration.API.AUTH_URL</camunda:inputParameter>
  <camunda:inputParameter name="gnspdRestUser">$this.data.Event_X_Start.parameters.configuration.API.SECRET_USERNAME</camunda:inputParameter>
  <camunda:inputParameter name="gnspdRestPassword">$this.data.Event_X_Start.parameters.configuration.API.SECRET_PASSWORD</camunda:inputParameter>
  <camunda:inputParameter name="gnspdRestMethod">POST</camunda:inputParameter>
  <camunda:inputParameter name="gnspdRestDataUrl">$(this.data.Event_X_Start.parameters.configuration.API.BASE_URL + '/api/endpoint')</camunda:inputParameter>
  <camunda:inputParameter name="gnspdRestSendData">true</camunda:inputParameter>
  <camunda:inputParameter name="gnspdIsCustomData">true</camunda:inputParameter>
  <camunda:inputParameter name="gnspdDataFormat">JSON</camunda:inputParameter>
  <camunda:inputParameter name="gnspdSingleVariableKey">${"champ": this.data.X.Y.valeur}</camunda:inputParameter>
  <camunda:inputParameter name="gnspdSystemData">${"applicant": this.data.applicant, "recordUid": this.data.recordUid}</camunda:inputParameter>
  <camunda:inputParameter name="gnspdTimeOutValue">120000</camunda:inputParameter>
```

#### H. EndEvent (`tg.gouv.gnspd.endEvent`)
- **Alignement SRS Premium** : L'agent doit s'assurer que la numérotation des étapes dans le XML (IDs ou documentation) correspond à la numérotation du SRS Premium : Lane PORTAL (01, 02...) et Lane XFLOW (B01, B02...).

À appliquer sur les endEvents **XFlow** principaux :

```xml
<bpmn:endEvent ... camunda:modelerTemplate="tg.gouv.gnspd.endEvent"
  camunda:topic="flow-end-event">
  <camunda:inputParameter name="gnspdTaskIsVisible">true</camunda:inputParameter>
  <!-- + autres paramètres standards -->
```

#### H-bis. IntermediateCatchEvent — Callback paiement (pattern demande-passeport)

Utilisé **uniquement dans le pool XFlow** pour recevoir le callback de la plateforme de paiement e-Gov externe. Ce n'est PAS un template GNSPD — c'est un élément BPMN natif avec un `executionListener`.

```xml
<bpmn:intermediateCatchEvent id="Event_X_PayCallback" name="Recevoir les informations de paiement">
  <bpmn:extensionElements>
    <camunda:executionListener event="end">
      <camunda:script scriptFormat="javascript">this.data.payment_key = true</camunda:script>
    </camunda:executionListener>
  </bpmn:extensionElements>
  <bpmn:incoming>Flow_from_SendPayOrder</bpmn:incoming>
  <bpmn:outgoing>Flow_to_SendPayConfirm</bpmn:outgoing>
  <bpmn:messageEventDefinition id="MsgEvtDef_PayCallback" messageRef="MSG_SERVICE_PAY_CALLBACK" />
</bpmn:intermediateCatchEvent>
```

**Points clés** :
- `messageEventDefinition` référence le message `MSG_SERVICE_PAY_CALLBACK`
- L'`executionListener` (event="end") positionne `payment_key = true` dans le contexte d'exécution
- Placé entre `SendPayOrder` (XFlow → XPortal) et `SendPayConfirm` (XFlow → XPortal)
- Cet événement **bloque le flux XFlow** jusqu'à réception du callback e-Gov

### 5. Paramètres de tâche standards (toujours présents)

Ces 8 paramètres sont **obligatoires sur TOUTES les tâches** ayant un `camunda:modelerTemplate` :

```xml
<camunda:inputParameter name="gnspdTaskIsVisible">false</camunda:inputParameter>
<camunda:inputParameter name="gnspdTaskLabel" />
<camunda:inputParameter name="gnspdTaskStatus">Pending</camunda:inputParameter>
<camunda:inputParameter name="gnspdTaskOrder" />
<camunda:inputParameter name="gnspdTaskKind">citizen</camunda:inputParameter>
<camunda:inputParameter name="gnspdCostVariable" />
<camunda:inputParameter name="gnspdCostTotal" />
<camunda:inputParameter name="gnspdCostUnitaire" />
```

### 6. Machine à états XPortal — Pattern recommandé (demande-passeport)

```
StartEvent(formKey=ULID, paymentAmount=N)
    ↓
SendTask(→XFlow MSG_START)                        ← envoi immédiat au back-office
    ↓
┌── BLOC PAIEMENT (si service payant) ────────────────────────────┐
│ ReceiveTask(MSG_PAY_ORDER)                ← XFlow ordonne       │
│     ↓                                                           │
│ UserTask(tarification, formKey=ULID_PAY)  ← redirige e-Gov     │
│     ↓                                                           │
│ ReceiveTask(MSG_PAY_CONFIRM)              ← XFlow confirme      │
└─────────────────────────────────────────────────────────────────┘
    ↓
ReceiveTask(multi-entrant MSG_RETURN) ←──────────────────────────┐
    ↓                                                             │
Gateway(action ?)                                                 │
    correction | accepte | rejete                                  │
         ↓         ↓         ↓                                    │
   UserTask(fix,  EndEvent  EndEvent                               │
   publish_submission,                                             │
   formKey=ULID_CORRECTION)                                        │
         ↓                                                        │
   SendTask(→XFlow MSG_RESUB) ──────────────────────────────────►┘
```

Ce pattern (adopté depuis `demande-passeport.bpmn`) est **supérieur** au pattern distribué car :
- Le paiement est séparé de la boucle correction (pas dans la même gateway)
- XFlow orchestre le paiement (reçoit le callback e-Gov, valide, confirme)
- Une seule receiveTask multi-entrante pour correction/accepte/rejete
- Extensible (ajouter une nouvelle action = ajouter un chemin à la gateway)

### 7. Gateway de décision agent — 3 sorties obligatoires

```xml
<bpmn:exclusiveGateway id="Gateway_X_Decision" name="Décision agent ?">
  <bpmn:outgoing>Flow_X_Approve</bpmn:outgoing>
  <bpmn:outgoing>Flow_X_Correction</bpmn:outgoing>
  <bpmn:outgoing>Flow_X_Reject</bpmn:outgoing>
</bpmn:exclusiveGateway>

<!-- Approuvé (sans correction) -->
<bpmn:sequenceFlow id="Flow_X_Approve" ...>
  <bpmn:conditionExpression language="javascript">
    this.data.Activity_X_Agent.result.submissionData.decision == 'oui'
    &amp;&amp; this.data.Activity_X_Agent.result.submissionData.hasCorrections == 'non'
  </bpmn:conditionExpression>
</bpmn:sequenceFlow>

<!-- Correction demandée -->
<bpmn:sequenceFlow id="Flow_X_Correction" ...>
  <bpmn:conditionExpression language="javascript">
    this.data.Activity_X_Agent.result.submissionData.decision == 'oui'
    &amp;&amp; this.data.Activity_X_Agent.result.submissionData.hasCorrections == 'oui'
  </bpmn:conditionExpression>
</bpmn:sequenceFlow>

<!-- Rejet définitif -->
<bpmn:sequenceFlow id="Flow_X_Reject" ...>
  <bpmn:conditionExpression language="javascript">
    this.data.Activity_X_Agent.result.submissionData.decision == 'non'
  </bpmn:conditionExpression>
</bpmn:sequenceFlow>
```

**INTERDIT** : Une gateway avec seulement 2 sorties (Approuvé + Correction) sans chemin de rejet. Cela crée un deadlock systématique si l'agent choisit un rejet.

### 8. Expressions Conditionnelles

**Toujours** `language="javascript"`. **Jamais** de FEEL ni d'EL.

```xml
<bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">
  this.data.Activity_X_Agent.result.submissionData.decision == 'oui'
</bpmn:conditionExpression>
```

**Référentiel des expressions les plus courantes :**

```javascript
// Décision agent
this.data.Activity_X_Agent.result.submissionData.decision == 'oui'
this.data.Activity_X_Agent.result.submissionData.decision == 'non'
this.data.Activity_X_Agent.result.submissionData.hasCorrections == 'oui'

// Action retour XFlow (pattern expert-2)
// ATTENTION : dans les conditionExpression, toujours this.data. (SANS $)
// Le préfixe $ est réservé aux camunda:inputParameter (gnspdMessage, gnspdSubmissionData...)
this.data.Activity_P_Receive.result.data.action == "correction"
this.data.Activity_P_Receive.result.data.action == "accepte"
this.data.Activity_P_Receive.result.data.action == "rejete"

// Champ formulaire (duplicata)
this.data.Event_X_Start.parameters.submissionData.duplicata == 'Oui'
this.data.Event_X_Start.parameters.submissionData.duplicata == 'Non'

// Résultat Odoo
this.data.Activity_X_Odoo.result.id != null   // enregistrement trouvé
this.data.Activity_X_Odoo.result.id == null   // non trouvé

// Paiement
this.data.Activity_X_RecvPay.result.data.paymentStatus == "confirmed"
```

**ATTENTION** : Typo fréquente `language="javscript"` (sans le 'a'). Toujours vérifier.

### 9. Accès aux données — Grammaire `this.data`

```javascript
// Données de la soumission initiale (formulaire citoyen)
this.data.Event_X_Start.parameters.submissionData.data.champFormulaire
this.data.Event_X_Start.parameters.submissionData.nomChamp

// Identité du demandeur (disponible globalement)
this.data.applicant.email
this.data.applicant.phone

// Référence dossier
this.data.xref
this.data.recordUid

// Résultat userTask agent
this.data.Activity_X_Agent.result.submissionData.decision
this.data.Activity_X_Agent.result.submissionData.motif

// Message reçu via receiveTask XPortal
this.data.Activity_P_Receive.result.data.action

// Configuration Odoo/API (depuis le startEvent)
this.data.Event_X_Start.parameters.configuration.ODOO.URL
this.data.Event_X_Start.parameters.configuration.DGDN.BASE_URL

// Résultat Odoo
this.data.Activity_X_Odoo.result.id

// Opérateur nullish (toujours utiliser pour les champs optionnels)
this.data.Activity_P_Payment.result.data.paymentRef ?? null
```

### 10. Boucle de correction — Intelligence et limites

La boucle n'est **jamais** un simple retour en arrière. Elle est interactive et doit :
1. **XFlow** → Notifier le citoyen (sendNotification avec le motif)
2. **XFlow** → Envoyer l'ordre de correction au portail (sendTask avec `action: "correction"` et le motif)
3. **XFlow** → Se mettre en pause (receiveTask "attendre resoumission")
4. **XPortal** → Recevoir la commande → UserTask de correction pré-remplie (`gnspdFormSetting`)
5. **XPortal** → Renvoyer le dossier corrigé (sendTask)
6. **XFlow** → Réceptionner et retourner sur la userTask agent

**Limitation obligatoire** : Ajouter un compteur ou un boundary timer event pour éviter une boucle infinie :
```javascript
// Condition de continuation de boucle
this.data.nbCorrections < 3
// Condition de rejet automatique
this.data.nbCorrections >= 3
```

### 11. Configuration multi-environnement (KMS)

Les quatre environnements `development`, `sandbox`, `preproduction`, `production` **doivent tous être déclarés** sur les startEvent des **DEUX pools** (XPortal ET XFlow).

#### StartEvent XPortal — Configuration formulaire

Le contenu correspond au bloc `config` du formulaire Form.io principal (tel que documenté dans la section 2.4 du SRS). Format :

```json
{
  "apiBaseUrl": "https://api.[service].[env].gouv.tg",
  "endpoints": {
    "[endpoint1]": "/api/v1/[ressource]",
    "[endpoint2]": "/api/v1/[ressource]"
  },
  "appName": "[Nom environnement]",
  "users": {
    "firstName": "user.firstName",
    "lastName": "user.lastName",
    "fullName": "user.fullName",
    "email": "user.email",
    "username": "user.username",
    "userId": "user.userId",
    "accountType": "user.accountType",
    "language": "user.language",
    "phone": "user.phone"
  }
}
```

Si le formulaire n'utilise pas d'API externe ni de `config`, mettre `{}` vides.

#### StartEvent XFlow — Configuration KMS système

Le contenu porte les secrets et connexions back-office (ODOO, GED, APIs tierces). Format :

```json
{
  "ODOO": {
    "URL": "https://[service]-odoo.[env].gouv.tg",
    "PORT": "",
    "DB": "@{[service]}",
    "SECRET_USERNAME": "{dbkms:[SERVICE]_ODOO_USERNAME}",
    "SECRET_PASSWORD": "{dbkms:[SERVICE]_ODOO_PASSWORD}"
  },
  "GED": {
    "BASE_URL": "https://ged.[env].gouv.tg",
    "SECRET_API_KEY": "{dbkms:[SERVICE]_GED_API_KEY}"
  }
}
```

Si un environnement n'a pas de config spécifique, mettre `{}` vides. Les deux configurations (XPortal et XFlow) coexistent mais ne se chevauchent pas.

### 12. Section BPMNDiagram — Obligatoire et complète

```xml
<bpmndi:BPMNDiagram id="BPMNDiagram_1">
  <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Collaboration_[Service]">
    <!-- Shapes pour les participants (pools) -->
    <bpmndi:BPMNShape id="Participant_Portal_di" bpmnElement="Participant_Portal" isHorizontal="true">
      <dc:Bounds x="140" y="80" width="2970" height="500" />
    </bpmndi:BPMNShape>
    <bpmndi:BPMNShape id="Participant_Xflow_di" bpmnElement="Participant_Xflow" isHorizontal="true">
      <dc:Bounds x="140" y="650" width="2970" height="600" />
    </bpmndi:BPMNShape>

    <!-- Shapes pour TOUS les éléments de CHAQUE processus -->
    <!-- StartEvent / EndEvent : 36x36 -->
    <!-- Tâches : 100x80 -->
    <!-- Gateway : 50x50 -->

    <!-- Edges pour TOUS les sequenceFlow -->
    <!-- Edges pour TOUS les messageFlow -->
  </bpmndi:BPMNPlane>
</bpmndi:BPMNDiagram>
```

---

## Catalogue complet des templates GNSPD — RÉFÉRENCE OBLIGATOIRE

**AVANT TOUTE GÉNÉRATION**, l'agent **DOIT** consulter le catalogue complet des templates dans `documentation/gndad_bpmn_templates.json`. Ce fichier JSON contient les **21 element templates** de la plateforme GNSPD avec leurs paramètres exacts, types, contraintes et valeurs par défaut.

Le catalogue est la **source de vérité** pour les paramètres de chaque template. Si un paramètre a changé dans le JSON, c'est le JSON qui fait foi, pas cette documentation.

### Templates avancés (non couverts par les sections précédentes)

#### I. CertSign — Signature E-Cert (`tg.gouv.gnspd.certSign`)

Signature électronique via E-Cert. Topic : `flow-cert-sign`.

```xml
<bpmn:serviceTask ... camunda:modelerTemplate="tg.gouv.gnspd.certSign"
  camunda:type="external" camunda:topic="flow-cert-sign">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdId">$this.data.Event_X_Start.parameters.configuration.ECERT.SECRET_USERNAME</camunda:inputParameter>
      <camunda:inputParameter name="gnspdKey">$this.data.Event_X_Start.parameters.configuration.ECERT.SECRET_PASSWORD</camunda:inputParameter>
      <camunda:inputParameter name="gnspdIsFormat">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdData">${"nom": this.data.Event_X_Start.parameters.submissionData.nom, "prenom": this.data.Event_X_Start.parameters.submissionData.prenom}</camunda:inputParameter>
      <camunda:inputParameter name="gnspdUseNewMethod">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdDefaultValue" />
      <camunda:inputParameter name="gnspdIgnoreList" />
      <!-- + 8 paramètres de tâche standards -->
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

#### J. SignServer — Signature via SignServer (`tg.gouv.gnspd.signServer`)

Signature de fichiers via un serveur SignServer distant. Topic : `flow-sign-server`.

```xml
<bpmn:serviceTask ... camunda:modelerTemplate="tg.gouv.gnspd.signServer"
  camunda:type="external" camunda:topic="flow-sign-server">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdRestDataUrl">$this.data.Event_X_Start.parameters.configuration.SIGN.URL</camunda:inputParameter>
      <camunda:inputParameter name="gnspdAcceptedHttpStatus">[200,201,202]</camunda:inputParameter>
      <camunda:inputParameter name="gnspdAttachments">$this.data.Activity_X_Generate.result</camunda:inputParameter>
      <camunda:inputParameter name="gnspdRestTag">CERTIFICAT</camunda:inputParameter>
      <!-- Tags disponibles : UPLOAD, PHOTO, DIPLOME, ATTESTATION, CERTIFICAT -->
      <camunda:inputParameter name="gnspdRestStreamName">certificat.pdf</camunda:inputParameter>
      <camunda:inputParameter name="gnspdIsInsecure">false</camunda:inputParameter>
      <camunda:inputParameter name="gnspdCustomData" />
      <!-- + 8 paramètres de tâche standards -->
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

#### K. GenerateTemplate — Génération de documents (`tg.gouv.gnspd.generateTemplate`)

Génère un fichier (PDF, DOCX) à partir d'un template prédéfini. Topic : `flow-generate-template`.

```xml
<bpmn:serviceTask ... camunda:modelerTemplate="tg.gouv.gnspd.generateTemplate"
  camunda:type="external" camunda:topic="flow-generate-template">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdGeneratedName">attestation-${this.data.xref}.pdf</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTemplate">TEMPLATE_ID_ATTESTATION</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTempData">${
  "nom": this.data.Event_X_Start.parameters.submissionData.nom,
  "prenom": this.data.Event_X_Start.parameters.submissionData.prenom,
  "reference": this.data.xref,
  "date": this.data.Event_X_Start.parameters.submissionData.date
}</camunda:inputParameter>
      <camunda:inputParameter name="gnspdPrintOptions">{'format':'A4'}</camunda:inputParameter>
      <camunda:inputParameter name="gnspdGroups" />
      <camunda:inputParameter name="gnspdRoles" />
      <!-- + 8 paramètres de tâche standards -->
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

#### L. PdfImage — Apposition d'image sur PDF (`tg.gouv.gnspd.pdfImage`)

Appose une image (QR code, cachet, signature scannée) à des coordonnées précises sur un PDF. Topic : `flow-pdf-image`.

```xml
<bpmn:serviceTask ... camunda:modelerTemplate="tg.gouv.gnspd.pdfImage"
  camunda:type="external" camunda:topic="flow-pdf-image">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdPdfFile">$this.data.Activity_X_Generate.result</camunda:inputParameter>
      <camunda:inputParameter name="gnspdClickedX">450</camunda:inputParameter>
      <camunda:inputParameter name="gnspdClickedY">680</camunda:inputParameter>
      <camunda:inputParameter name="gnspdCurrentPage">1</camunda:inputParameter>
      <camunda:inputParameter name="gnspdFile">$this.data.Activity_X_Generate.result</camunda:inputParameter>
      <camunda:inputParameter name="gnspdImage">$this.data.Activity_X_Qrcode.result</camunda:inputParameter>
      <!-- + 8 paramètres de tâche standards -->
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

#### M. GenerateUrlQrcode — Génération de QR code (`tg.gouv.gnspd.generateUrlQrcode`)

Génère un QR code à partir d'une URL (vérification d'authenticité). Topic : `flow-generate-url-qrcode`.

```xml
<bpmn:serviceTask ... camunda:modelerTemplate="tg.gouv.gnspd.generateUrlQrcode"
  camunda:type="external" camunda:topic="flow-generate-url-qrcode">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdUrl">$(this.data.Event_X_Start.parameters.configuration.PORTAL.BASE_URL + '/verify/' + this.data.xref)</camunda:inputParameter>
      <!-- + 8 paramètres de tâche standards -->
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

#### N. DbSave — Enregistrement direct en base (`tg.gouv.gnspd.dbSave`)

Exécute une requête SQL directe (MySQL, PostgreSQL, Oracle, MSSQL). Topic : `flow-db-save`.

```xml
<bpmn:serviceTask ... camunda:modelerTemplate="tg.gouv.gnspd.dbSave"
  camunda:type="external" camunda:topic="flow-db-save">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdDbType">postgresql</camunda:inputParameter>
      <camunda:inputParameter name="gnspdDbHost">$this.data.Event_X_Start.parameters.configuration.DB.HOST</camunda:inputParameter>
      <camunda:inputParameter name="gnspdDbPort">5432</camunda:inputParameter>
      <camunda:inputParameter name="gnspdDbUser">$this.data.Event_X_Start.parameters.configuration.DB.SECRET_USERNAME</camunda:inputParameter>
      <camunda:inputParameter name="gnspdDbPassword">$this.data.Event_X_Start.parameters.configuration.DB.SECRET_PASSWORD</camunda:inputParameter>
      <camunda:inputParameter name="gnspdDbName">$this.data.Event_X_Start.parameters.configuration.DB.NAME</camunda:inputParameter>
      <camunda:inputParameter name="gnspdDbQueryTemplate">INSERT INTO registre (reference, nom, prenom, date_creation) VALUES ('${this.data.xref}', '${this.data.Event_X_Start.parameters.submissionData.nom}', '${this.data.Event_X_Start.parameters.submissionData.prenom}', NOW())</camunda:inputParameter>
      <!-- + 8 paramètres de tâche standards -->
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

#### O. RequestHttp — Requête HTTP générique (`tg.gouv.gnspd.requestHttp`)

Exécute une requête HTTP avec une configuration JSON libre. Topic : `flow-http-request`.

```xml
<bpmn:serviceTask ... camunda:modelerTemplate="tg.gouv.gnspd.requestHttp"
  camunda:type="external" camunda:topic="flow-http-request">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdConfig">${
  "method": "POST",
  "url": this.data.Event_X_Start.parameters.configuration.API.BASE_URL + "/endpoint",
  "headers": {"Authorization": "Bearer " + this.data.Event_X_Start.parameters.configuration.API.SECRET_TOKEN},
  "data": {"reference": this.data.xref}
}</camunda:inputParameter>
      <!-- + 8 paramètres de tâche standards -->
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

#### P. StepNotification — Modification d'état d'étape (`tg.gouv.gnspd.stepNotification`)

Met à jour le statut d'une étape visible côté portail. Topic : `flow-step-notification`.

```xml
<bpmn:serviceTask ... camunda:modelerTemplate="tg.gouv.gnspd.stepNotification"
  camunda:type="external" camunda:topic="flow-step-notification">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdStatus">Success</camunda:inputParameter>
      <!-- Statuts : Pending, PendingPeer, PendingPayment, PendingUser, PendingBackOffice, Success, Fail, WaitingForControls, SavedAsDraft, Submited, Terminated -->
      <camunda:inputParameter name="gnspdIsPortal">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdStepOrder">1</camunda:inputParameter>
      <camunda:inputParameter name="gnspdPassData" />
      <camunda:inputParameter name="gnspdPassCost" />
      <camunda:inputParameter name="gnspdIgnoreNotFound">false</camunda:inputParameter>
      <!-- + 8 paramètres de tâche standards -->
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

#### Q. FlowPortail — ⚠️ DEPRECATED (`tg.gouv.gnspd.flowPortail`)

> **ATTENTION — Pattern legacy** : Ce template est un ancien pattern (3 usages dans le codebase vs 34 pour `userTask`). Pour toutes les nouvelles digitalisations, utiliser **`tg.gouv.gnspd.userTask`** (section D) avec `camunda:formKey` et `gnspdHandlerType`. Le template `flowPortail` est documenté ici uniquement pour la maintenance de processus existants.

Affiche un formulaire interactif côté portail citoyen (soumission, correction, paiement). Topic : `flow-portail-form`.

```xml
<bpmn:serviceTask ... camunda:modelerTemplate="tg.gouv.gnspd.flowPortail"
  camunda:type="external" camunda:topic="flow-portail-form">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdOrder">1</camunda:inputParameter>
      <camunda:inputParameter name="stepName">Soumission de la demande</camunda:inputParameter>
      <camunda:inputParameter name="gnspdFormKey">formulaire-demande</camunda:inputParameter>
      <camunda:inputParameter name="isResubmission">false</camunda:inputParameter>
      <camunda:inputParameter name="description">Remplissez le formulaire de demande</camunda:inputParameter>
      <camunda:inputParameter name="executionType">PORTAIL</camunda:inputParameter>
      <!-- Types : PORTAIL, ADMIN, MOBILE -->
      <camunda:inputParameter name="paymentAmount">0</camunda:inputParameter>
      <camunda:inputParameter name="calculatePayment">false</camunda:inputParameter>
      <camunda:inputParameter name="calculationOperator">ADDITION</camunda:inputParameter>
      <camunda:inputParameter name="variable1" />
      <camunda:inputParameter name="variable2" />
      <camunda:inputParameter name="initialFormData" />
      <camunda:inputParameter name="associatedFormData" />
      <!-- + 8 paramètres de tâche standards -->
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

#### R. BusinessRuleTask (`tg.gouv.gnspd.bussinessRuleTask`)

Exécute une table de décision DMN. Topic : `flow-bussiness-rule-task`. Note : le typo "bussiness" est volontaire (c'est l'ID officiel du template).

```xml
<bpmn:businessRuleTask ... camunda:modelerTemplate="tg.gouv.gnspd.bussinessRuleTask"
  camunda:type="external" camunda:topic="flow-bussiness-rule-task">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <!-- Seuls les 8 paramètres de tâche standards -->
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:businessRuleTask>
```

#### S. ScriptTask (`tg.gouv.gnspd.scriptTask`)

Exécute un script côté moteur. Topic : `flow-script-task`.

```xml
<bpmn:scriptTask ... camunda:modelerTemplate="tg.gouv.gnspd.scriptTask"
  camunda:type="external" camunda:topic="flow-script-task">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <!-- Seuls les 8 paramètres de tâche standards -->
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:scriptTask>
```

#### T. Function — Transformation de données (`tg.gouv.gnspd.function`)

Applique une fonction de transformation JavaScript sur des champs de formulaire. Topic : `flow-function`.

```xml
<bpmn:serviceTask ... camunda:modelerTemplate="tg.gouv.gnspd.function"
  camunda:type="external" camunda:topic="flow-function">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdStepName">Transformation des données</camunda:inputParameter>
      <camunda:inputParameter name="gnspdExécution">SYSTEM</camunda:inputParameter>
      <camunda:inputParameter name="gnspdFormKey">champA, champB, champC</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTransformFunction">transformer(champA).toUpperCase(); transformer(champB).trim();</camunda:inputParameter>
      <!-- + 8 paramètres de tâche standards -->
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

### Chaîne de production documentaire — Pattern recommandé

Pour les services qui délivrent un document officiel (certificat, attestation, diplôme), combiner les templates dans cet ordre :

```
userTask(agent) → generateTemplate → generateUrlQrcode → pdfImage(QR sur doc) → certSign/signServer → sendNotification
```

1. **generateTemplate** : Génère le document à partir des données validées
2. **generateUrlQrcode** : Crée un QR code de vérification avec l'URL `PORTAL_URL/verify/XREF`
3. **pdfImage** : Appose le QR code sur le document généré
4. **certSign** ou **signServer** : Signe électroniquement le document final
5. **sendNotification** : Notifie le citoyen que son document est prêt

---

## Anti-patterns interdits

| Anti-pattern | Conséquence | Correction |
|-------------|-------------|------------|
| `isExecutable="false"` sur un pool | Camunda refuse le déploiement | `isExecutable="true"` sur les 2 pools |
| Gateway décision à 2 sorties sans rejet | Deadlock si l'agent rejette | Ajouter systématiquement la sortie Rejeté |
| `language="javscript"` (typo) | Condition ignorée, deadlock | Vérifier l'orthographe |
| Paiement calculé côté form sans confirmation BPMN | Dossiers non payés soumis | Implémenter le cycle complet de paiement |
| `this.data.champManquant` (champ absent du formulaire) | Requête Odoo échoue | Vérifier la cohérence form ↔ BPMN |
| Messages Kafka avec UUID comme nom | Impossible à maintenir | Noms fonctionnels `MSG_SERVICE_ACTION` |
| BPMNDiagram vide ou incomplet | Diagramme inutilisable | Coordonnées DI pour tous les éléments |
| Boucle correction sans limite | Instance bloquée indéfiniment | Compteur + condition de sortie |
| Namespace `zeebe:` | Incompatible Camunda 7 | Supprimer, utiliser uniquement `camunda:` |
| `$this.data.` dans les `conditionExpression` | Erreur de validation P-Studio | Utiliser `this.data.` (sans `$`) dans les conditions. Le préfixe `$` est réservé aux `camunda:inputParameter` |
| `flowPortail` pour les tâches citoyen XPortal | Pattern legacy (3 usages vs 34 pour userTask) | Utiliser `userTask` avec `gnspdHandlerType` et `camunda:formKey` |
| Paiement orchestré par XPortal seul | XPortal ne peut pas recevoir le callback e-Gov | Adopter le pattern `demande-passeport` : XFlow orchestre via `intermediateCatchEvent` |

---

## Mission finale

Chaque fichier `.bpmn` généré doit pouvoir être importé directement dans Camunda Modeler 5.42.0 et déployé sur Camunda Platform 7.17 sans modification. Vérifier systématiquement :

1. **Syntaxe XML valide** — Pas de balises non fermées, encodage UTF-8
2. **IDs uniques** — Aucun doublon dans tout le fichier
3. **Références cohérentes** — Chaque `sourceRef`, `targetRef`, `messageRef`, `processRef` pointe sur un ID existant
4. **Templates complets** — Tous les paramètres standards présents sur chaque tâche
5. **Chemins exhaustifs** — Pas de deadlock possible, tous les chemins atteignent un endEvent
6. **BPMNDiagram complet** — Chaque élément BPMN a ses coordonnées graphiques
