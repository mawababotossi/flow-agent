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

## Stratégie de génération en deux passes

> **⚠️ CONTRAINTE CAPACITÉ** : Un fichier BPMN dual-pool complet (XML fonctionnel + bpmndi) atteint ~1000 lignes, ce qui dépasse la capacité de génération fiable d'un modèle IA en une seule passe. La génération se fait donc en **deux passes distinctes**.

### Passe 1 — XML fonctionnel (messages, collaboration, processus, flux)

L'agent génère **tout le contenu fonctionnel** du fichier BPMN :
- `<bpmn:message>` declarations
- `<bpmn:collaboration>` avec participants et messageFlows
- `<bpmn:process>` XPortal complet (startEvent, tâches, gateways, endEvents, sequenceFlows)
- `<bpmn:process>` XFlow complet (startEvent, tâches, gateways, endEvents, sequenceFlows)
- Section `<bpmndi:BPMNDiagram>` **vide** (placeholder) :
```xml
<bpmndi:BPMNDiagram id="BPMNDiagram_1">
  <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Collaboration_[Service]" />
</bpmndi:BPMNDiagram>
```

Le fichier est écrit avec `Write` à ce stade. Il est valide XML mais **non visualisable** dans Camunda Modeler (page blanche sans bpmndi).

### Passe 2 — Génération du BPMNDiagram (layout)

L'agent **relit** le fichier généré en Passe 1, extrait tous les IDs d'éléments BPMN, puis génère la section `<bpmndi:BPMNDiagram>` complète avec :
- `BPMNShape` pour chaque participant (pool), startEvent, endEvent, tâche, gateway, boundaryEvent, intermediateCatchEvent
- `BPMNEdge` pour chaque sequenceFlow et messageFlow
- Coordonnées cohérentes respectant la disposition dual-pool (XPortal en haut, XFlow en bas)

L'agent utilise `Edit` pour remplacer le placeholder bpmndi vide par la section complète.

> **Règle d'or** : Ne JAMAIS tenter de générer le XML fonctionnel et le bpmndi dans la même passe. La Passe 2 est une passe séparée qui lit le résultat de la Passe 1.

---

## Lectures obligatoires avant toute génération

> **⛔ INTERDICTION ABSOLUE** : Ne JAMAIS utiliser les fichiers du dossier `projects/` comme source d'inspiration ou de référence. Seuls les fichiers listés ci-dessous et le dossier `exemples/` sont des sources de référence autorisées.
>
> **⚠️ NUANCE** : Les exemples sont des sources d'inspiration et de patterns validés, mais ne constituent pas une vérité absolue. En cas de conflit entre un exemple et les règles architecturales documentées ici, les règles prévalent.

### Étape 1 — Lectures systématiques (TOUJOURS, pour tout service)

| Fichier | Contenu | Lignes |
|---------|---------|--------|
| **`PATTERNS.md`** (même dossier que SKILL.md) | Bibliothèque de wiring XML annoté P1-P8 + scénarios complets (XPortal machine à états, XFlow backbone, chaîne doc, paiement, boucle correction, boundary timer) | ~450 |
| **`examples/skeleton-dual-pool.bpmn`** | Squelette dual-pool valide à compléter — NE PAS générer de zéro, partir de ce fichier | ~300 |

> **Règle d'or** : Le squelette est le point de départ. L'agent complète les sections TODO de `Process_Xflow` avec les snippets de `PATTERNS.md`. Il ne génère jamais un BPMN entier de zéro. Le bpmndi est généré en Passe 2 uniquement.

### Étape 2 — Lectures conditionnelles (selon le SRS)

Lire les fichiers ci-dessous **uniquement si le scénario correspondant est présent dans le SRS** :

| Condition dans le SRS | Fichier à lire | Ce qu'il apporte |
|----------------------|----------------|-----------------|
| Service avec **paiement e-Gov** | `demande-passeport_correct.bpmn` | Pattern XFlow paiement + callback |
| Service avec **vérification Odoo** complexe (create/write) | `expert-odoo-integration.bpmn` | Odoo search_read + create + write avec gestion d'erreurs |
| Service avec **génération de document officiel** ou **orchestration inter-pools avancée** | `diplome_cfa_correct.bpmn` | Chaîne documentaire complète (generateTemplate → QR → pdfImage → certSign) + référence P1-P8 en XML opérationnel |
| Service avec **intégration API REST tierce** (non-Odoo) | `demande-acte-etat-civil-golf3.bpmn` | Pattern RestBuilder Auth + Prepare + Submit |
| Service avec **> 5 étapes XFlow** ou **validations multiples** | `demande-passeport.bpmn` | Flux complexe multi-étapes à haut volume |

---

## Principes Architecturaux (GNSPD / ATD)

L'architecture ATD repose sur deux moteurs BPMN distincts communiquant de manière **asynchrone via Kafka** (topic `bpmn.commands`) :

**XPortal (Le Portail Citoyen)** : Machine à états pilotée par les messages XFlow. Gère : soumission, paiement, corrections, affichage des statuts. Pool BPMN `isExecutable="true"`.

**XFlow (Le Back-Office)** : Orchestrateur métier. Gère : instruction agent, Odoo ERP, APIs REST tierces, notifications. Pool BPMN `isExecutable="true"`.

> **⚠️ RÈGLE DE CONFORMITÉ CRITIQUE** : Toutes les tâches techniques (UserTask, ServiceTask, SendTask, ReceiveTask) **DOIVENT** impérativement déclarer `camunda:type="external"` pour être pilotables par les workers du framework GNSPD.

```
[XPortal] sendTask → Kafka (peer-xflow) → [XFlow] startEvent
[XFlow]   sendTask → Kafka (ch-portail) → [XPortal] receiveTask
```

---

## Patterns d'orchestration inter-pools (OBLIGATOIRE)

Ces 8 patterns garantissent qu'aucun jeton BPMN ne se perd. Ils sont tirés du modèle de référence `diplome_cfa_correct.bpmn` et doivent être appliqués systématiquement.

### P1. Symétrie des gateways entre pools
Toute décision de routage conditionnel (ex: duplicata oui/non) doit être **répliquée en miroir** dans les deux pools. Chaque pool lit la même donnée source et prend sa propre décision. Aucun pool ne dépend de l'autre pour son routage.

### P2. ReceiveTask multi-entrante comme point de convergence (jamais d'ExclusiveGateway merge)
Lorsque plusieurs chemins doivent converger (ex: après paiement, après correction, chemin direct), utiliser **un seul ReceiveTask** (ou ServiceTask/UserTask) avec plusieurs `<bpmn:incoming>`. Cela évite la duplication de logique et garantit un seul point d'attente avant la gateway de décision. **Ne jamais utiliser un ExclusiveGateway comme simple point de merge** (N entrées → 1 sortie) : le validateur exige au moins 2 flux sortants avec conditions sur tout ExclusiveGateway. Les ExclusiveGateway servent uniquement à la **divergence** (1 entrée → N sorties conditionnelles).

### P3. Notification PUIS SendMessage (jamais l'inverse)
Côté XFlow, toujours enchaîner :
1. **ServiceTask `flow-notify`** (notification email/SMS/in-app au citoyen)
2. **SendTask `flow-send-message`** (message Kafka vers XPortal)

Le citoyen est informé **avant** que l'état de son dossier ne change sur le portail. Ne jamais inverser cet ordre.

### P4. Noeud de rejet unique (DRY)
Tous les chemins de rejet (non-inscrit, rejet agent, non-paiement, dépassement de tentatives) convergent vers **un seul ServiceTask de notification de rejet** avec plusieurs `<bpmn:incoming>`. Un seul template, une seule logique.

### P5. Vérification système AVANT instruction agent
Toute vérification automatisable (Odoo `search_read`, API REST) s'exécute **avant** la userTask agent. L'agent reçoit des données pré-vérifiées et ne fait que valider.

### P6. Boucle de correction avec re-vérification
La boucle de correction revient à la **vérification système** (Odoo/API), pas directement à l'agent. Flux :
```
Agent "nonConforme" → Notify → SendMessage XPortal → ReceiveTask resoumission
→ Retour à vérification Odoo → Gateway inscrit? → SendMessage → UserTask agent
```

### P7. Terminaison explicite de chaque branche
Chaque chemin alternatif se termine par un **EndEvent explicite**. Aucun jeton ne reste en suspens. Vérifier que le nombre de EndEvents couvre tous les cas (succès, rejet, non-paiement, non-inscrit, etc.).

### P8. Appariement SendTask/ReceiveTask
Chaque SendTask inter-pool a un ReceiveTask (ou StartEvent) correspondant dans l'autre pool. **Aucun message orphelin**. Avant de finaliser le XML, vérifier que chaque `messageRef` apparaît exactement dans un SendTask ET un ReceiveTask/StartEvent.

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

> **`isExecutable` — Règle** : Les **deux** `<bpmn:process>` (XPortal ET XFlow) doivent être `isExecutable="true"`. Sans cela, Camunda 7 refuse le déploiement. XFlow démarre via message Kafka, mais `isExecutable="true"` est requis pour le déploiement, pas pour l'instanciation manuelle.

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
  <!-- gnspdTargetElementType :
       - bpmn:StartEvent  → pour la sendTask initiale XPortal → XFlow startEvent uniquement
       - bpmn:ReceiveTask → pour toutes les autres sendTask (retours, confirmations, corrections)
  -->
  <camunda:inputParameter name="gnspdMessageDestination">peer-xflow-local-sp</camunda:inputParameter>
  <camunda:inputParameter name="gnspdMessageRef">MSG_SERVICE_START</camunda:inputParameter>
  <camunda:inputParameter name="gnspdMessage">$this.data.Event_P_Start.parameters</camunda:inputParameter>
  <!-- + 8 paramètres de tâche standards (voir §Paramètres standards) -->
```

**Valeurs de `gnspdMessage` selon le contexte :**
- Envoi complet des données formulaire : `$this.data.Event_P_Start.parameters`
- Signal booléen simple (déclenchement) : `true`
- JSON structuré : `${"action": "correction", "motif": this.data.X.result.submissionData.motif ?? null}`

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
<!-- Tâche de soumission initiale (XPortal) -->
<!-- ⚠️ camunda:type="external" OBLIGATOIRE sur toute userTask — sinon validateur "Implementation Type vide" -->
<bpmn:userTask ... camunda:modelerTemplate="tg.gouv.gnspd.userTask"
  camunda:type="external"
  camunda:formKey="[UUID_FORM]"
  camunda:topic="flow-user-task">
  <camunda:inputParameter name="gnspdTaskDescription">Description métier</camunda:inputParameter>
  <camunda:inputParameter name="gnspdHandlerType">publish_submission</camunda:inputParameter>
  <camunda:inputParameter name="gnspdAttachments">${
  "pieceIdentite": this.data.Event_X_Start.parameters.submissionData.data.pieceIdentite ?? null
}</camunda:inputParameter>
  <camunda:inputParameter name="gnspdTaskIsVisible">true</camunda:inputParameter>
  <camunda:inputParameter name="gnspdTaskLabel">Libellé visible citoyen</camunda:inputParameter>
  <camunda:inputParameter name="gnspdTaskOrder">1</camunda:inputParameter>
  <!-- + autres paramètres standards -->
```

**Tâche de correction XPortal** (`gnspdHandlerType="publish_submission"` avec pré-remplissage conditionnel) :

```xml
<!-- Tâche correction citoyen (XPortal) — pré-remplie avec données existantes -->
<bpmn:userTask id="Task_P_Correction" name="Corriger le dossier"
  camunda:modelerTemplate="tg.gouv.gnspd.userTask"
  camunda:type="external"
  camunda:formKey="[UUID_FORM_CORRECTION]"
  camunda:topic="flow-user-task">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdHandlerType">publish_submission</camunda:inputParameter>
      <camunda:inputParameter name="gnspdSubmissionData">$(this.data.Task_P_Correction &amp;&amp; this.data.Task_P_Correction.result ? this.data.Task_P_Correction.result : this.data.Event_P_Start.parameters.submissionData.data)</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskIsVisible">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskLabel">Corriger mon dossier</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskStatus">PendingPortal</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskOrder">2</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskKind">citizen</camunda:inputParameter>
      <camunda:inputParameter name="gnspdCostVariable" />
      <camunda:inputParameter name="gnspdCostTotal" />
      <camunda:inputParameter name="gnspdCostUnitaire" />
    </camunda:inputOutput>
    <camunda:taskListener class="" event="create" />
  </bpmn:extensionElements>
  ...
</bpmn:userTask>
```

> **Pattern `gnspdSubmissionData` conditionnel** : `$(this.data.TASK_ID && this.data.TASK_ID.result ? this.data.TASK_ID.result : this.data.EVENT_START.parameters.submissionData.data)`
> - `$()` wrapping obligatoire pour l'expression JavaScript
> - 1ère correction → utilise les données initiales (`Event_P_Start.parameters.submissionData.data`)
> - Corrections suivantes → réutilise la dernière saisie (`Task_P_Correction.result`)
> - **Important** : le chemin des données initiales se termine par `.submissionData.data` (avec `.data`)
> - `gnspdSubmissionFormkey` est **optionnel** (absent du passeport de référence)

**Seules les userTasks visibles par le citoyen ont `gnspdTaskIsVisible=true`** (paiement, corrections, suivi). Les userTasks agent en back-office ont `gnspdTaskIsVisible=false`.

**Valeurs de `gnspdHandlerType`** :

| Valeur | Usage | Contexte |
|--------|-------|----------|
| `publish_submission` | Afficher un formulaire Form.io | Soumission initiale (XPortal), correction citoyen (XPortal), instruction agent (XFlow back-office) |
| `tarification` | Rediriger vers la plateforme de paiement e-Gov **externe** | Paiement des frais de service |
| `download_files` | Proposer un téléchargement de fichier | Téléchargement d'un récépissé, bulletin, attestation |

#### E. SendNotification (`tg.gouv.gnspd.sendNotification`)

> **⚠️ RÈGLE TEMPLATES OBLIGATOIRES** : Si un canal est activé (`true`), son template correspondant **DOIT** être renseigné (JAMAIS vide).
> - `gnspdNotifyInApp=true` → `gnspdNotifyTemplateInApp` obligatoire (ex: `TODO_TPL_INAPP_xxx`)
> - `gnspdNotifySendEmail=true` → `gnspdNotifyTemplateEmail` obligatoire (ex: `TODO_TPL_EMAIL_xxx`)
> - `gnspdNotifySendSMS=true` → `gnspdNotifyTemplateSMS` obligatoire (ex: `TODO_TPL_SMS_xxx`)
>
> ⛔ Laisser un template vide (`<camunda:inputParameter name="gnspdNotifyTemplateInApp" />`) déclenche l'erreur validateur : "Le champ Template In-App est obligatoire".

```xml
<bpmn:serviceTask ... camunda:modelerTemplate="tg.gouv.gnspd.sendNotification"
  camunda:topic="flow-notify">
  <camunda:inputParameter name="gnspdNotifySendEmail">true</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyEmail">$this.data.applicant.email</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyTemplateEmail">TODO_TPL_EMAIL_xxx</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyContentEmail">${"record_id": this.data.xref}</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifySendSMS">true</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyPhone">$this.data.applicant.phone</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyTemplateSMS">TODO_TPL_SMS_xxx</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyContentSMS">${"record_id": this.data.xref}</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyInApp">true</camunda:inputParameter>
  <camunda:inputParameter name="gnspdNotifyTemplateInApp">TODO_TPL_INAPP_xxx</camunda:inputParameter>
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
  <!-- gnspdSystemData : inclure sur TOUS les restBuilders XFlow — envoie applicant + recordUid au système tiers -->
  <camunda:inputParameter name="gnspdTimeOutValue">120000</camunda:inputParameter>
  <!-- outputParameter payment_key : initialiser à false sur le restBuilder de création de dossier
       sera remis à true par l'executionListener de l'IntermediateCatchEvent paiement -->
  <camunda:outputParameter name="payment_key">false</camunda:outputParameter>
```

> **`gnspdSystemData`** : pattern standard `${"applicant": this.data.applicant, "recordUid": this.data.recordUid}` — à inclure sur **tous** les restBuilders XFlow pour transmettre le contexte métier à l'API.

> **`payment_key` initialisation** : Sur le **premier restBuilder** de création du dossier, ajouter `<camunda:outputParameter name="payment_key">false</camunda:outputParameter>`. Valeur mise à `true` exclusivement par l'`executionListener event="end"` de l'IntermediateCatchEvent paiement (voir §H-bis).

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
      <!-- ⚠️ ÉVALUATION CONDITIONNELLE OBLIGATOIRE — JAMAIS affecter true inconditionnellement -->
      <camunda:script scriptFormat="javascript">this.data.payment_key = (this.data.Event_X_PayCallback.result.paymentStatus == 'paid')</camunda:script>
    </camunda:executionListener>
  </bpmn:extensionElements>
  <bpmn:incoming>Flow_from_SendPayOrder</bpmn:incoming>
  <bpmn:outgoing>Flow_to_SendPayConfirm</bpmn:outgoing>
  <bpmn:messageEventDefinition id="MsgEvtDef_PayCallback" messageRef="MSG_SERVICE_PAY_CALLBACK" />
</bpmn:intermediateCatchEvent>
```

**Points clés** :
- `messageEventDefinition` référence le message `MSG_SERVICE_PAY_CALLBACK`
- L'`executionListener` (event="end") évalue **conditionnellement** le statut du callback e-Gov
- ⛔ **ANTI-PATTERN** : `this.data.payment_key = true` (inconditionnel) rend la branche PayKO morte (code inatteignable)
- Placé entre `SendPayOrder` (XFlow → XPortal) et `SendPayConfirm` (XFlow → XPortal)
- Cet événement **bloque le flux XFlow** jusqu'à réception du callback e-Gov

#### D-bis. ScriptTask — Compteurs et initialisations de variables

`bpmn:scriptTask` natif Camunda (pas de `camunda:modelerTemplate`). Utilisé pour manipuler des variables globales de contexte (compteurs de boucle, flags, resets). **Pas de 8 paramètres standards** — element simple.

```xml
<!-- Initialisation du compteur (avant la première entrée dans la boucle) -->
<bpmn:scriptTask id="ScriptTask_InitCount" name="Initialiser compteur à 0" scriptFormat="javascript">
  <bpmn:incoming>Flow_from_Prev</bpmn:incoming>
  <bpmn:outgoing>Flow_to_Next</bpmn:outgoing>
  <bpmn:script>this.data.reformulationCount = 0</bpmn:script>
</bpmn:scriptTask>

<!-- Incrémentation après chaque tentative -->
<bpmn:scriptTask id="ScriptTask_IncrCount" name="Incrémenter compteur" scriptFormat="javascript">
  <bpmn:incoming>Flow_from_UserTask</bpmn:incoming>
  <bpmn:outgoing>Flow_to_Gateway</bpmn:outgoing>
  <bpmn:script>this.data.reformulationCount += 1</bpmn:script>
</bpmn:scriptTask>
```

Gateway de sortie de boucle lisant la variable globale :
```javascript
// Condition continuation
this.data.reformulationCount <= 2
// Condition arrêt forcé (max atteint)
this.data.reformulationCount > 2
```

> ⚠️ **La gateway doit lire `this.data.reformulationCount` directement** — PAS via `this.data.TASK_ID.result.reformulationCount` (erreur fréquente : lire la variable depuis le résultat d'une tâche au lieu du contexte global).

**Pattern complet boucle limitée :**
```
ScriptTask(init=0) → UserTask(analyze) → ScriptTask(+=1) → Gateway(<=2 ?)
  ├─ [oui] → loopback vers UserTask
  └─ [non] → EndEvent clôture forcée
```

#### D-ter. UserTask back-office — `gnspdCandidateCompanies`

Paramètre optionnel présent sur les userTasks back-office XFlow pour restreindre les entités autorisées à prendre la tâche :

```xml
<camunda:inputParameter name="gnspdCandidateCompanies" />
<!-- Laisser vide si pas de restriction, ou remplir avec les IDs des entités autorisées -->
```

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
// Données de la soumission initiale — DEUX formats possibles selon l'action
this.data.Event_X_Start.parameters.submissionData.data.champFormulaire  // ← format standard
this.data.Event_X_Start.parameters.submissionData.nomChamp               // ← format alternatif
// ⚠️ Le chemin correct se termine par .submissionData.data.champFormulaire (avec .data)
// Vérifier dans le SRS quel format utilise le formulaire Form.io du service

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

// Données reçues via receiveTask (message Kafka entrant)
// DEUX patterns selon le pool et l'émetteur :
this.data.Activity_X_RecvResub.parameters.message.champFormulaire   // ← XFlow reçoit de XPortal
this.data.Activity_P_RecvFiche.parameters.message.submission_file.file  // ← XPortal reçoit de XFlow
this.data.Activity_P_RecvFiche.parameters.message.check_state.data.state
// Pattern général : this.data.[RECV_TASK_ID].result.message.[CHAMP]
// (certains exemples utilisent .parameters.message., d'autres .result.message. — vérifier l'exemple de référence)

// Données d'une userTask XPortal envoyées vers XFlow via sendTask
// Utiliser .parameters (pas .result) pour les tâches XPortal
$this.data.Activity_P_UserTask.parameters  // ← envoi du contexte complet d'une tâche XPortal

// Configuration Odoo/API (depuis le startEvent XFlow)
this.data.Event_X_Start.parameters.configuration.ODOO.URL
this.data.Event_X_Start.parameters.configuration.DGDN.BASE_URL
this.data.Event_X_Start.parameters.configuration.DGDN.AUTH_URL

// Résultat restBuilder
this.data.Activity_X_Odoo.result.id
this.data.Activity_X_Rest.result.data.id
this.data.Activity_X_Rest.result ?? null  // avec nullish pour optional chaining

// payment_key — flag de paiement
// Initialisé à false via outputParameter du 1er restBuilder de création :
//   <camunda:outputParameter name="payment_key">false</camunda:outputParameter>
// Mis à true via executionListener event="end" sur le IntermediateCatchEvent paiement :
//   <camunda:script scriptFormat="javascript">this.data.payment_key = true</camunda:script>
this.data.payment_key == true   // condition "paiement reçu"

// gnspdSystemData — à inclure dans TOUS les restBuilders XFlow (référence applicant + recordUid)
// ${"applicant": this.data.applicant, "recordUid": this.data.recordUid}

// Opérateur nullish (toujours utiliser pour les champs optionnels)
this.data.Activity_X_Rest.result?.transactionNumber ?? null
```

### 10. Boucle de correction — Intelligence et limites

La boucle n'est **jamais** un simple retour en arrière. Elle est interactive et doit :
1. **XFlow** → Notifier le citoyen (sendNotification avec le motif)
2. **XFlow** → Envoyer l'ordre de correction au portail (sendTask avec `action: "correction"` et le motif)
3. **XFlow** → Se mettre en pause (receiveTask "attendre resoumission")
4. **XPortal** → Recevoir la commande → UserTask de correction pré-remplie (`gnspdHandlerType="publish_submission"` + `gnspdSubmissionData` conditionnel)
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

> **Duplication KMS autorisée** : Certains services (ex: DNCCP) mettent la même config KMS sur les deux startEvents. Cela est valide : XPortal envoie `$this.data.Event_P_Start.parameters` à XFlow, qui peut donc lire la config depuis `this.data.Event_P_Start.parameters.configuration.API.XXX`. Si la config n'est que sur XFlow, utiliser `this.data.Event_X_Start.parameters.configuration.API.XXX`. Mettre la config sur les deux garantit l'accès depuis n'importe quel chemin.

> **`isExecutable` — Règle définitive** : Les **deux** `<bpmn:process>` doivent être `isExecutable="true"`. XPortal process : `isExecutable="true"`. XFlow process : `isExecutable="true"`. Sans cela, Camunda 7 refuse le déploiement.

### 12. Section BPMNDiagram — Générée en Passe 2

> **IMPORTANT** : Cette section n'est PAS générée en même temps que le XML fonctionnel. Elle est produite lors de la **Passe 2** (voir "Stratégie de génération en deux passes" en début de document).

#### En Passe 1 — Placeholder vide

```xml
<bpmndi:BPMNDiagram id="BPMNDiagram_1">
  <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Collaboration_[Service]" />
</bpmndi:BPMNDiagram>
```

#### En Passe 2 — Section complète

L'agent relit le fichier, identifie tous les éléments, et génère :

```xml
<bpmndi:BPMNDiagram id="BPMNDiagram_1">
  <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Collaboration_[Service]">
    <!-- Pools : isHorizontal="true" -->
    <bpmndi:BPMNShape id="Participant_Portal_di" bpmnElement="Participant_Portal" isHorizontal="true">
      <dc:Bounds x="140" y="80" width="2970" height="500" />
    </bpmndi:BPMNShape>
    <bpmndi:BPMNShape id="Participant_Xflow_di" bpmnElement="Participant_Xflow" isHorizontal="true">
      <dc:Bounds x="140" y="650" width="2970" height="600" />
    </bpmndi:BPMNShape>

    <!-- BPMNShape pour CHAQUE élément (startEvent, endEvent, tâche, gateway, boundaryEvent, intermediateCatchEvent) -->
    <!-- Conventions de taille : StartEvent/EndEvent 36x36, Tâches 100x80, Gateway 50x50 -->

    <!-- BPMNEdge pour CHAQUE sequenceFlow -->
    <!-- BPMNEdge pour CHAQUE messageFlow (inter-pools) -->
  </bpmndi:BPMNPlane>
</bpmndi:BPMNDiagram>
```

**Checklist Passe 2** — Avant de valider, vérifier que :
- Chaque `id` d'élément du XML fonctionnel a un `BPMNShape` correspondant (`id` = `[elementId]_di`, `bpmnElement` = `[elementId]`)
- Chaque `id` de sequenceFlow a un `BPMNEdge` correspondant
- Chaque `id` de messageFlow a un `BPMNEdge` correspondant
- Les pools XPortal (y=80) et XFlow (y=650) ne se chevauchent pas
- Les éléments XPortal ont des coordonnées y entre 100 et 550
- Les éléments XFlow ont des coordonnées y entre 670 et 1220

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
      <camunda:inputParameter name="gnspdGeneratedName">Lettre d'avis ${this.data.xref}</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTemplate">24</camunda:inputParameter>
      <!-- gnspdTemplate : ID NUMÉRIQUE du template dans le CMS GNSPD (pas un nom, un entier) -->
      <camunda:inputParameter name="gnspdTempData">${
  "numero": this.data.xref,
  "dateDeTransmission": this.data.Activity_X_Agent.result.submissionData.date ?? null,
  "recepteurLettre": this.data.Event_X_Start.parameters.submissionData.data.nomOrganisme,
  "objetLettre": this.data.Activity_X_Agent.result.submissionData.objet ?? null,
  "contenu": this.data.Activity_X_Agent.result.submissionData.avis ?? null
}</camunda:inputParameter>
      <!-- ⚠️ gnspdTempData : TOUJOURS référencer this.data.XXX — JAMAIS de valeurs hardcodées -->
      <camunda:inputParameter name="gnspdPrintOptions">{'format':'A4'}</camunda:inputParameter>
      <!-- gnspdPrintOptions : {'format':'A4'} est la valeur standard -->
      <camunda:inputParameter name="gnspdGroups" />
      <camunda:inputParameter name="gnspdRoles" />
      <!-- + 8 paramètres de tâche standards -->
    </camunda:inputOutput>
  </bpmn:extensionElements>
</bpmn:serviceTask>
```

> **Usage typique** : après une userTask agent qui saisit le contenu (ex: "Analyser et proposer une réponse"), puis avant une userTask de validation/signature.
> Le résultat (`this.data.Activity_X_Generate.result`) est un objet fichier passable à `gnspdAttachments` ou `gnspdPdfFile`.

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

> **⚠️ DEUX CHAMPS DISTINCTS — NE PAS CONFONDRE :**
>
> **`gnspdStatus`** (champ de `stepNotification`) — valeurs autorisées :
> `Pending` | `PendingPeer` | `PendingPayment` | `PendingUser` | `PendingBackOffice` | `Success` | `Fail` | `WaitingForControls` | `SavedAsDraft` | `Submited` | `Terminated`
> ⛔ INVALIDES : `Submitted` (2 t), `Processing`, `Completed`, `InProgress`, `Done`
> ⚠️ `Submited` s'écrit avec **1 seul `t`** — c'est un quirk du framework, pas une faute.
>
> **`gnspdTaskStatus`** (champ des tâches userTask/sendTask/receiveTask) — valeurs autorisées :
> `Pending` | `PendingPortal` | `PendingPayment` | `PendingBackOffice` | `Review` | `Submitted` | `Rejected` | `Completed` | `Failed` | `PendingCompletion` | `PendingPublic`
> ⛔ INVALIDES pour les tâches : `PendingUser`, `Success`, `Fail`, `Submited`

> **Mapping `gnspdStatus` selon le contexte :**
>
> | Moment dans le processus | Valeur |
> |---|---|
> | Dossier reçu par XFlow (démarrage) | `Submited` |
> | En cours d'instruction back-office | `PendingBackOffice` |
> | En attente d'action citoyen | `PendingUser` |
> | En attente de paiement | `PendingPayment` |
> | Service rendu avec succès | `Success` |
> | Dossier rejeté | `Fail` |
> | Clôturé / annulé | `Terminated` |

> **⛔ `stepNotification` N'UTILISE PAS les 8 paramètres de tâche standards** (`gnspdTaskIsVisible`, `gnspdTaskStatus`, `gnspdTaskKind`, etc.). Seulement les 3 champs ci-dessous.

```xml
<bpmn:serviceTask ... camunda:modelerTemplate="tg.gouv.gnspd.stepNotification"
  camunda:type="external" camunda:topic="flow-step-notification">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdStatus">Submited</camunda:inputParameter>
      <camunda:inputParameter name="gnspdIsPortal">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdStepOrder">1</camunda:inputParameter>
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
| ExclusiveGateway utilisé comme simple merge (N entrées → 1 sortie) | Erreur validation : « ExclusiveGateway doit avoir au moins 2 flux sortants » et « sans conditions ni flux par défaut » | Ne jamais utiliser d'ExclusiveGateway pour la convergence. Connecter les flux entrants directement sur la tâche cible (une tâche BPMN accepte plusieurs `<bpmn:incoming>`) |
| `flowPortail` pour les tâches citoyen XPortal | Pattern legacy (3 usages vs 34 pour userTask) | Utiliser `userTask` avec `gnspdHandlerType` et `camunda:formKey` |
| Paiement orchestré par XPortal seul | XPortal ne peut pas recevoir le callback e-Gov | Adopter le pattern `demande-passeport` : XFlow orchestre via `intermediateCatchEvent` |
| `userTask` sans `camunda:type="external"` | Validateur : "Implementation Type vide" | Ajouter `camunda:type="external"` sur **toute** `userTask` (comme `receiveTask`) |
| `sendNotification` avec template vide quand canal activé | Validateur : "Template In-App obligatoire" | Si `gnspdNotifyInApp=true` → `gnspdNotifyTemplateInApp=TODO_TPL_INAPP_xxx` (idem Email/SMS) |
| `payment_key = true` inconditionnel dans executionListener | Branche PayKO morte (code inatteignable) | Évaluer conditionnellement : `this.data.Event_X_PayCallback.result.paymentStatus == 'paid'` |

---

## Mission finale

Chaque fichier `.bpmn` généré doit pouvoir être importé directement dans Camunda Modeler 5.42.0 et déployé sur Camunda Platform 7.17 sans modification. La génération se fait en **deux passes** :

### Après Passe 1 — Vérifier :

1. **Syntaxe XML valide** — Pas de balises non fermées, encodage UTF-8
2. **IDs uniques** — Aucun doublon dans tout le fichier
3. **Références cohérentes** — Chaque `sourceRef`, `targetRef`, `messageRef`, `processRef` pointe sur un ID existant
4. **Templates complets** — Tous les paramètres standards présents sur chaque tâche
5. **Chemins exhaustifs** — Pas de deadlock possible, tous les chemins atteignent un endEvent
6. **Placeholder bpmndi présent** — `<bpmndi:BPMNDiagram>` avec `<bpmndi:BPMNPlane ... />` vide

### Après Passe 2 — Vérifier :

7. **BPMNDiagram complet** — Chaque élément BPMN a son `BPMNShape`, chaque flux a son `BPMNEdge`
8. **Aucun élément orphelin** — Pas d'élément fonctionnel sans shape, pas de shape sans élément fonctionnel
9. **Ouverture Modeler** — Le fichier doit s'ouvrir correctement dans Camunda Modeler (pas de page blanche)
