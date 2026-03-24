# PATTERNS BPMN GNSPD — Référence de wiring XML

> **Bibliothèque de snippets XML annotés.** Ce fichier remplace la lecture des 9 exemples BPMN complets (~7 800 lignes).
> Pour les détails de chaque template GNSPD (tous les inputParameters), voir **SKILL.md §4**.
> Pour le squelette de départ, utiliser **`skeleton-dual-pool.bpmn`**.
>
> Chaque snippet est un fragment valide pouvant être intégré directement dans un processus dual-pool.

---

## 0. Entête canonique + Déclaration des messages

```xml
<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions
  xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:camunda="http://camunda.org/schema/1.0/bpmn"
  xmlns:modeler="http://camunda.org/schema/modeler/1.0"
  exporter="Camunda Modeler" exporterVersion="5.42.0"
  modeler:executionPlatform="Camunda Platform"
  modeler:executionPlatformVersion="7.17.0">

  <!-- RÈGLE : messages déclarés AVANT la collaboration, JAMAIS dedans -->
  <!-- Service sans paiement : 3 messages -->
  <bpmn:message id="MSG_SERVICE_START"  name="MSG_SERVICE_START" />
  <bpmn:message id="MSG_SERVICE_RETURN" name="MSG_SERVICE_RETURN" />
  <bpmn:message id="MSG_SERVICE_RESUB"  name="MSG_SERVICE_RESUB" />

  <!-- Service PAYANT : 3 messages supplémentaires -->
  <bpmn:message id="MSG_SERVICE_PAY_ORDER"    name="MSG_SERVICE_PAY_ORDER" />    <!-- XFlow → XPortal : ordre de paiement -->
  <bpmn:message id="MSG_SERVICE_PAY_CALLBACK" name="MSG_SERVICE_PAY_CALLBACK" /> <!-- e-Gov callback → XFlow -->
  <bpmn:message id="MSG_SERVICE_PAY_CONFIRM"  name="MSG_SERVICE_PAY_CONFIRM" />  <!-- XFlow → XPortal : confirmation paiement -->
```

---

## 1. Collaboration : structure des 2 pools + messageFlows

```xml
  <bpmn:collaboration id="Collaboration_SERVICE">
    <bpmn:participant id="Participant_Portal" name="XPORTAL" processRef="Process_Portal" />
    <bpmn:participant id="Participant_Xflow"  name="XFLOW"
      processRef="Process_Xflow"
      camunda:versionTag="1.0"
      camunda:historyTimeToLive="180" />

    <!-- RÈGLE P8 : chaque SendTask a exactement UN messageFlow vers le ReceiveTask/StartEvent correspondant -->
    <!-- XPortal → XFlow (démarrage) -->
    <bpmn:messageFlow id="MF_Start"     sourceRef="Send_P_Start"   targetRef="Event_X_Start" />
    <!-- XPortal → XFlow (resoumission après correction) -->
    <bpmn:messageFlow id="MF_Resub"     sourceRef="Send_P_Resub"   targetRef="Recv_X_Resub" />
    <!-- XFlow → XPortal (retour décision : action unique) -->
    <bpmn:messageFlow id="MF_Return"    sourceRef="Send_X_Return"  targetRef="Recv_P_Return" />
    <!-- Service payant : 3 messageFlows supplémentaires -->
    <bpmn:messageFlow id="MF_PayOrder"  sourceRef="Send_X_PayOrder"   targetRef="Recv_P_PayOrder" />
    <bpmn:messageFlow id="MF_PayConfirm" sourceRef="Send_X_PayConfirm" targetRef="Recv_P_PayConfirm" />
  </bpmn:collaboration>
```

---

## 1bis. P1 — Symétrie des gateways entre pools

> **Règle** : toute décision conditionnelle (ex: duplicata oui/non, paiement requis/non) doit être **répliquée en miroir** dans les 2 pools. Chaque pool lit la même donnée source via `this.data` et prend sa propre décision. **Aucun pool ne dépend de l'autre pour son routage.**

```xml
  <!-- XPortal : gateway basée sur la donnée 'duplicata' du formulaire initial -->
  <bpmn:exclusiveGateway id="Gw_P_Duplicata" name="Duplicata ?">
    <bpmn:incoming>SF_P_Prev_GwDuplicata</bpmn:incoming>
    <bpmn:outgoing>SF_P_Dup_Oui</bpmn:outgoing>
    <bpmn:outgoing>SF_P_Dup_Non</bpmn:outgoing>
  </bpmn:exclusiveGateway>
  <bpmn:sequenceFlow id="SF_P_Dup_Oui" sourceRef="Gw_P_Duplicata" targetRef="...">
    <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">
      this.data.Event_P_Start.parameters.submissionData.duplicata == 'Oui'
    </bpmn:conditionExpression>
  </bpmn:sequenceFlow>

  <!-- XFlow : MÊME condition, MÊME donnée source, décision INDÉPENDANTE -->
  <bpmn:exclusiveGateway id="Gw_X_Duplicata" name="Duplicata ?">
    <bpmn:incoming>SF_X_Prev_GwDuplicata</bpmn:incoming>
    <bpmn:outgoing>SF_X_Dup_Oui</bpmn:outgoing>
    <bpmn:outgoing>SF_X_Dup_Non</bpmn:outgoing>
  </bpmn:exclusiveGateway>
  <bpmn:sequenceFlow id="SF_X_Dup_Oui" sourceRef="Gw_X_Duplicata" targetRef="...">
    <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">
      this.data.Event_X_Start.parameters.submissionData.duplicata == 'Oui'
    </bpmn:conditionExpression>
  </bpmn:sequenceFlow>
  <!-- Note : Event_P_Start côté XPortal, Event_X_Start côté XFlow — même donnée, accès différent -->
```

---

## 2. P2 — ReceiveTask multi-entrante (convergence sans ExclusiveGateway)

> **Règle** : plusieurs `<bpmn:incoming>` sur une seule tâche. NE PAS utiliser un ExclusiveGateway comme merge.

```xml
  <!-- Point de convergence XPortal : même tâche attend indifféremment
       la première soumission, la confirmation de paiement, ou un retour correction -->
  <bpmn:receiveTask id="Recv_P_Return" name="Attendre réponse XFlow"
    camunda:modelerTemplate="tg.gouv.gnspd.receiveTask"
    messageRef="MSG_SERVICE_RETURN"
    camunda:topic="flow-receive-task">
    <bpmn:incoming>SF_P_SendStart_RecvReturn</bpmn:incoming>   <!-- chemin initial (sans paiement) -->
    <bpmn:incoming>SF_P_PayConfirm_RecvReturn</bpmn:incoming>  <!-- après confirmation paiement -->
    <bpmn:incoming>SF_P_SendResub_RecvReturn</bpmn:incoming>   <!-- après resoumission correction -->
    <bpmn:outgoing>SF_P_RecvReturn_GwAction</bpmn:outgoing>
    <!-- ... inputParameters standards ... -->
  </bpmn:receiveTask>

  <!-- Même pattern côté XFlow : le même receiveTask reçoit aussi bien la soumission initiale
       que la resoumission après correction (P6) -->
  <bpmn:serviceTask id="Activity_X_OdooSearch" name="Vérifier inscription Odoo"
    camunda:modelerTemplate="tg.gouv.gnspd.odoo" camunda:topic="flow-odoo">
    <bpmn:incoming>SF_X_Start_OdooSearch</bpmn:incoming>      <!-- soumission initiale -->
    <bpmn:incoming>SF_X_RecvResub_OdooSearch</bpmn:incoming>  <!-- après resoumission (P6) -->
    <bpmn:outgoing>SF_X_OdooSearch_GwOdoo</bpmn:outgoing>
    <!-- ... inputParameters ... -->
  </bpmn:serviceTask>
```

---

## 3. P3 + P8 — Notify → Send (ordre obligatoire) + appariement messageFlow

> **Règle P3** : toujours notifier le citoyen AVANT d'envoyer le message Kafka qui change son état portail.
> **Règle P8** : chaque SendTask a un ReceiveTask correspondant dans l'autre pool.

```xml
  <!-- XFlow : notification PUIS envoi (ordre immuable) -->
  <bpmn:serviceTask id="Notif_X_Accept" name="Notifier acceptation"
    camunda:modelerTemplate="tg.gouv.gnspd.sendNotification" camunda:topic="flow-notify">
    <bpmn:incoming>SF_X_DocChain_Notif</bpmn:incoming>
    <bpmn:outgoing>SF_X_Notif_Send</bpmn:outgoing>
    <!-- gnspdNotifySendEmail, gnspdNotifySendSMS, gnspdNotifyInApp = true -->
  </bpmn:serviceTask>

  <bpmn:sendTask id="Send_X_Return" name="Envoyer réponse XPortal"
    camunda:modelerTemplate="tg.gouv.gnspd.sendMessage" camunda:topic="flow-send-message">
    <bpmn:incoming>SF_X_Notif_Send</bpmn:incoming>
    <bpmn:outgoing>SF_X_Send_End</bpmn:outgoing>
    <!-- gnspdTargetElementType = bpmn:ReceiveTask (sauf première soumission : bpmn:StartEvent) -->
    <!-- gnspdMessageRef = MSG_SERVICE_RETURN -->
    <!-- gnspdMessage = ${"action": "accepte", "reference": this.data.xref} -->
  </bpmn:sendTask>

  <!-- XPortal : ReceiveTask correspondant (P8) — déclaré dans Recv_P_Return (P2 ci-dessus) -->
```

---

## 4. P4 — Nœud de rejet DRY (plusieurs chemins → un seul endNotif)

> **Règle** : tous les chemins de rejet convergent sur UN SEUL bloc notify+send+end.
> Utiliser P2 (plusieurs `<bpmn:incoming>`) pour la convergence.

```xml
  <!-- Nœud de rejet unique : 4 sources possibles (Odoo KO, rejet agent, non-paiement, max corrections) -->
  <bpmn:serviceTask id="Notif_X_Reject" name="Notifier rejet dossier"
    camunda:modelerTemplate="tg.gouv.gnspd.sendNotification" camunda:topic="flow-notify">
    <bpmn:incoming>SF_X_OdooKO_Reject</bpmn:incoming>      <!-- non inscrit Odoo -->
    <bpmn:incoming>SF_X_AgentReject_Reject</bpmn:incoming>  <!-- rejet décision agent -->
    <bpmn:incoming>SF_X_MaxCorr_Reject</bpmn:incoming>      <!-- trop de tentatives de correction -->
    <bpmn:incoming>SF_X_NonPay_Reject</bpmn:incoming>       <!-- paiement non confirmé -->
    <bpmn:outgoing>SF_X_Reject_Send</bpmn:outgoing>
  </bpmn:serviceTask>

  <bpmn:sendTask id="Send_X_ReturnReject" name="Envoyer rejet XPortal"
    camunda:modelerTemplate="tg.gouv.gnspd.sendMessage" camunda:topic="flow-send-message">
    <bpmn:incoming>SF_X_Reject_Send</bpmn:incoming>
    <bpmn:outgoing>SF_X_ReturnReject_End</bpmn:outgoing>
    <!-- gnspdMessage = ${"action": "rejete", "motif": this.data.Activity_X_Agent.result.submissionData.motif ?? null} -->
  </bpmn:sendTask>

  <bpmn:endEvent id="End_X_Reject" name="Dossier rejeté">
    <bpmn:incoming>SF_X_ReturnReject_End</bpmn:incoming>
  </bpmn:endEvent>
```

---

## 5. XPortal complet — Machine à états (service sans paiement)

> Ce pool est quasi-identique pour tous les services sans paiement. Réutiliser directement.

```xml
  <bpmn:process id="Process_Portal" isExecutable="true" camunda:versionTag="1">

    <bpmn:startEvent id="Event_P_Start" name="Soumettre la demande"
      camunda:modelerTemplate="tg.gouv.gnspd.startEvent" camunda:topic="flow-start">
      <bpmn:outgoing>SF_P_Start_Send</bpmn:outgoing>
      <!-- gnspdPaymentAmount : 0 si gratuit, montant si payant -->
    </bpmn:startEvent>

    <!-- Immédiatement après soumission : envoyer au XFlow -->
    <bpmn:sendTask id="Send_P_Start" name="Soumettre dossier XFlow"
      camunda:modelerTemplate="tg.gouv.gnspd.sendMessage" camunda:topic="flow-send-message">
      <bpmn:incoming>SF_P_Start_Send</bpmn:incoming>
      <bpmn:outgoing>SF_P_SendStart_RecvReturn</bpmn:outgoing>
      <!-- gnspdTargetElementType = bpmn:StartEvent (UNIQUEMENT pour la 1ère soumission) -->
      <!-- gnspdMessageRef = MSG_SERVICE_START -->
    </bpmn:sendTask>

    <!-- Point de convergence P2 : reçoit retour XFlow (3 chemins possibles) -->
    <bpmn:receiveTask id="Recv_P_Return" name="Attendre réponse XFlow"
      camunda:modelerTemplate="tg.gouv.gnspd.receiveTask"
      messageRef="MSG_SERVICE_RETURN" camunda:topic="flow-receive-task">
      <bpmn:incoming>SF_P_SendStart_RecvReturn</bpmn:incoming>
      <bpmn:incoming>SF_P_SendResub_RecvReturn</bpmn:incoming>
      <bpmn:outgoing>SF_P_RecvReturn_GwAction</bpmn:outgoing>
    </bpmn:receiveTask>

    <!-- Gateway action unique : lit this.data.Recv_P_Return.result.data.action -->
    <bpmn:exclusiveGateway id="Gw_P_Action" name="Action XFlow ?">
      <bpmn:incoming>SF_P_RecvReturn_GwAction</bpmn:incoming>
      <bpmn:outgoing>SF_P_Action_Correction</bpmn:outgoing>
      <bpmn:outgoing>SF_P_Action_Accepte</bpmn:outgoing>
      <bpmn:outgoing>SF_P_Action_Rejete</bpmn:outgoing>
    </bpmn:exclusiveGateway>

    <!-- Branche correction : userTask de correction pré-remplie -->
    <bpmn:userTask id="Task_P_Correction" name="Corriger le dossier"
      camunda:modelerTemplate="tg.gouv.gnspd.userTask"
      camunda:formKey="[UUID_FORM_CORRECTION]"
      camunda:topic="flow-user-task">
      <bpmn:extensionElements>
        <camunda:inputOutput>
          <camunda:inputParameter name="gnspdHandlerType">publish_submission</camunda:inputParameter>
          <!-- gnspdSubmissionData : pattern conditionnel avec fallback — .submissionData.data (avec .data) -->
          <camunda:inputParameter name="gnspdSubmissionData">$(this.data.Task_P_Correction &amp;&amp; this.data.Task_P_Correction.result ? this.data.Task_P_Correction.result : this.data.Event_P_Start.parameters.submissionData.data)</camunda:inputParameter>
          <!-- gnspdSubmissionFormkey : OPTIONNEL (absent du passeport de référence) -->
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
      <bpmn:incoming>SF_P_Action_Correction</bpmn:incoming>
      <bpmn:outgoing>SF_P_Correction_Send</bpmn:outgoing>
    </bpmn:userTask>

    <bpmn:sendTask id="Send_P_Resub" name="Soumettre correction XFlow"
      camunda:modelerTemplate="tg.gouv.gnspd.sendMessage" camunda:topic="flow-send-message">
      <bpmn:incoming>SF_P_Correction_Send</bpmn:incoming>
      <bpmn:outgoing>SF_P_SendResub_RecvReturn</bpmn:outgoing>
      <!-- gnspdTargetElementType = bpmn:ReceiveTask (resoumission) -->
      <!-- gnspdMessageRef = MSG_SERVICE_RESUB -->
    </bpmn:sendTask>

    <!-- Fin acceptation -->
    <bpmn:endEvent id="End_P_Accepte" name="Demande acceptée">
      <bpmn:incoming>SF_P_Action_Accepte</bpmn:incoming>
    </bpmn:endEvent>

    <!-- Fin rejet -->
    <bpmn:endEvent id="End_P_Rejete" name="Demande rejetée">
      <bpmn:incoming>SF_P_Action_Rejete</bpmn:incoming>
    </bpmn:endEvent>

    <!-- SequenceFlows -->
    <bpmn:sequenceFlow id="SF_P_Start_Send"          sourceRef="Event_P_Start"    targetRef="Send_P_Start" />
    <bpmn:sequenceFlow id="SF_P_SendStart_RecvReturn" sourceRef="Send_P_Start"     targetRef="Recv_P_Return" />
    <bpmn:sequenceFlow id="SF_P_RecvReturn_GwAction"  sourceRef="Recv_P_Return"    targetRef="Gw_P_Action" />
    <bpmn:sequenceFlow id="SF_P_Action_Correction"    sourceRef="Gw_P_Action"      targetRef="Task_P_Correction">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">this.data.Recv_P_Return.result.data.action == "correction"</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="SF_P_Action_Accepte"       sourceRef="Gw_P_Action"      targetRef="End_P_Accepte">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">this.data.Recv_P_Return.result.data.action == "accepte"</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="SF_P_Action_Rejete"        sourceRef="Gw_P_Action"      targetRef="End_P_Rejete">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">this.data.Recv_P_Return.result.data.action == "rejete"</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="SF_P_Correction_Send"      sourceRef="Task_P_Correction" targetRef="Send_P_Resub" />
    <bpmn:sequenceFlow id="SF_P_SendResub_RecvReturn"  sourceRef="Send_P_Resub"      targetRef="Recv_P_Return" />

  </bpmn:process>
```

---

## 6. XPortal — Extension paiement (ajouter avant Recv_P_Return)

> Insérer ce bloc entre Send_P_Start et Recv_P_Return(multi-entrante) pour les services payants.

```xml
    <!-- XPortal reçoit l'ordre de paiement de XFlow -->
    <bpmn:receiveTask id="Recv_P_PayOrder" name="Recevoir ordre de paiement"
      camunda:modelerTemplate="tg.gouv.gnspd.receiveTask"
      messageRef="MSG_SERVICE_PAY_ORDER" camunda:topic="flow-receive-task">
      <bpmn:incoming>SF_P_SendStart_RecvPayOrder</bpmn:incoming>
      <bpmn:outgoing>SF_P_PayOrder_TaskPay</bpmn:outgoing>
    </bpmn:receiveTask>

    <!-- Redirection vers la plateforme e-Gov externe (tarification) -->
    <bpmn:userTask id="Task_P_Payment" name="Procéder au paiement"
      camunda:modelerTemplate="tg.gouv.gnspd.userTask" camunda:topic="flow-user-task">
      <bpmn:incoming>SF_P_PayOrder_TaskPay</bpmn:incoming>
      <bpmn:outgoing>SF_P_TaskPay_RecvConfirm</bpmn:outgoing>
      <!-- gnspdHandlerType = tarification (JAMAIS publish_submission pour le paiement) -->
    </bpmn:userTask>

    <!-- Confirmation de paiement envoyée par XFlow après callback e-Gov -->
    <bpmn:receiveTask id="Recv_P_PayConfirm" name="Recevoir confirmation paiement"
      camunda:modelerTemplate="tg.gouv.gnspd.receiveTask"
      messageRef="MSG_SERVICE_PAY_CONFIRM" camunda:topic="flow-receive-task">
      <bpmn:incoming>SF_P_TaskPay_RecvConfirm</bpmn:incoming>
      <bpmn:outgoing>SF_P_PayConfirm_RecvReturn</bpmn:outgoing>  <!-- vers Recv_P_Return (P2) -->
    </bpmn:receiveTask>
```

---

## 7. XFlow — Squelette principal (Odoo → Agent → Gateway décision)

> Backbone standard d'un XFlow avec vérification Odoo avant instruction agent (P5).

```xml
  <bpmn:process id="Process_Xflow" isExecutable="true" camunda:versionTag="1">

    <!-- StartEvent : reçoit la soumission initiale depuis XPortal -->
    <bpmn:startEvent id="Event_X_Start" name="Réception dossier"
      camunda:modelerTemplate="tg.gouv.gnspd.startEvent" camunda:topic="flow-start">
      <bpmn:messageEventDefinition messageRef="MSG_SERVICE_START" />
      <bpmn:outgoing>SF_X_Start_StepNotif</bpmn:outgoing>
    </bpmn:startEvent>

    <!-- Mise à jour statut portail (optionnel mais recommandé au démarrage) -->
    <!-- ⛔ stepNotification N'UTILISE PAS les 8 champs de tâche standards — seulement ces 3 champs -->
    <bpmn:serviceTask id="StepNotif_X_Submitted" name="Mettre à jour étape (Soumis)"
      camunda:modelerTemplate="tg.gouv.gnspd.stepNotification" camunda:topic="flow-step-notification">
      <bpmn:extensionElements>
        <camunda:inputOutput>
          <camunda:inputParameter name="gnspdStatus">Submited</camunda:inputParameter><!-- UN SEUL t — quirk framework -->
          <camunda:inputParameter name="gnspdIsPortal">true</camunda:inputParameter>
          <camunda:inputParameter name="gnspdStepOrder">1</camunda:inputParameter>
        </camunda:inputOutput>
      </bpmn:extensionElements>
      <bpmn:incoming>SF_X_Start_StepNotif</bpmn:incoming>
      <bpmn:outgoing>SF_X_StepNotif_OdooSearch</bpmn:outgoing>
    </bpmn:serviceTask>

    <!-- P5 : vérification Odoo AVANT l'agent -->
    <bpmn:serviceTask id="Activity_X_OdooSearch" name="Vérifier dans Odoo"
      camunda:modelerTemplate="tg.gouv.gnspd.odoo" camunda:topic="flow-odoo">
      <bpmn:incoming>SF_X_StepNotif_OdooSearch</bpmn:incoming>
      <bpmn:incoming>SF_X_RecvResub_OdooSearch</bpmn:incoming>   <!-- P6 : resoumission revient ici -->
      <bpmn:outgoing>SF_X_OdooSearch_GwOdoo</bpmn:outgoing>
      <!-- gnspdMethod = search_read, gnspdDomain = résultat de la recherche -->
    </bpmn:serviceTask>

    <!-- Gateway Odoo : inscrit ou non -->
    <bpmn:exclusiveGateway id="Gw_X_OdooOK" name="Inscrit Odoo ?">
      <bpmn:incoming>SF_X_OdooSearch_GwOdoo</bpmn:incoming>
      <bpmn:outgoing>SF_X_OdooOK_StepNotifProcessing</bpmn:outgoing>  <!-- oui : vers instruction -->
      <bpmn:outgoing>SF_X_OdooKO_Reject</bpmn:outgoing>               <!-- non : vers P4 rejet DRY -->
    </bpmn:exclusiveGateway>

    <!-- Mise à jour statut : en cours d'instruction -->
    <bpmn:serviceTask id="StepNotif_X_Processing" name="Mettre à jour étape (Instruction)"
      camunda:modelerTemplate="tg.gouv.gnspd.stepNotification" camunda:topic="flow-step-notification">
      <bpmn:extensionElements>
        <camunda:inputOutput>
          <camunda:inputParameter name="gnspdStatus">PendingBackOffice</camunda:inputParameter>
          <camunda:inputParameter name="gnspdIsPortal">true</camunda:inputParameter>
          <camunda:inputParameter name="gnspdStepOrder">2</camunda:inputParameter>
        </camunda:inputOutput>
      </bpmn:extensionElements>
      <bpmn:incoming>SF_X_OdooOK_StepNotifProcessing</bpmn:incoming>
      <bpmn:outgoing>SF_X_StepNotif_SendAgent</bpmn:outgoing>
    </bpmn:serviceTask>

    <!-- TODO : SendTask vers XPortal si handoff visuel nécessaire (optionnel selon SRS) -->

    <!-- Instruction agent -->
    <bpmn:userTask id="Activity_X_Agent" name="Instruire le dossier"
      camunda:modelerTemplate="tg.gouv.gnspd.userTask" camunda:topic="flow-user-task">
      <bpmn:incoming>SF_X_StepNotif_SendAgent</bpmn:incoming>
      <bpmn:outgoing>SF_X_Agent_GwDecision</bpmn:outgoing>
      <!-- gnspdHandlerType = publish_submission, gnspdTaskIsVisible = false (back-office) -->
    </bpmn:userTask>

    <!-- Gateway décision agent : 3 sorties OBLIGATOIRES (P7 : jamais de deadlock) -->
    <bpmn:exclusiveGateway id="Gw_X_Decision" name="Décision agent ?">
      <bpmn:incoming>SF_X_Agent_GwDecision</bpmn:incoming>
      <bpmn:outgoing>SF_X_Decision_Approve</bpmn:outgoing>
      <bpmn:outgoing>SF_X_Decision_Correction</bpmn:outgoing>
      <bpmn:outgoing>SF_X_Decision_Reject</bpmn:outgoing>
    </bpmn:exclusiveGateway>

    <bpmn:sequenceFlow id="SF_X_Decision_Approve" sourceRef="Gw_X_Decision" targetRef="TODO_DocChainOrNotif">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">
        this.data.Activity_X_Agent.result.submissionData.decision == 'oui'
      </bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="SF_X_Decision_Correction" sourceRef="Gw_X_Decision" targetRef="Notif_X_Correction">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">
        this.data.Activity_X_Agent.result.submissionData.decision == 'correction'
      </bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="SF_X_Decision_Reject" sourceRef="Gw_X_Decision" targetRef="Notif_X_Reject">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">
        this.data.Activity_X_Agent.result.submissionData.decision == 'non'
      </bpmn:conditionExpression>
    </bpmn:sequenceFlow>

    <!-- SequenceFlows structurels -->
    <bpmn:sequenceFlow id="SF_X_Start_StepNotif"        sourceRef="Event_X_Start"          targetRef="StepNotif_X_Submitted" />
    <bpmn:sequenceFlow id="SF_X_StepNotif_OdooSearch"   sourceRef="StepNotif_X_Submitted"   targetRef="Activity_X_OdooSearch" />
    <bpmn:sequenceFlow id="SF_X_OdooSearch_GwOdoo"      sourceRef="Activity_X_OdooSearch"   targetRef="Gw_X_OdooOK" />
    <bpmn:sequenceFlow id="SF_X_OdooKO_Reject"          sourceRef="Gw_X_OdooOK"             targetRef="Notif_X_Reject">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">this.data.Activity_X_OdooSearch.result.id == null</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="SF_X_OdooOK_StepNotifProcessing" sourceRef="Gw_X_OdooOK"         targetRef="StepNotif_X_Processing">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">this.data.Activity_X_OdooSearch.result.id != null</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="SF_X_StepNotif_SendAgent"    sourceRef="StepNotif_X_Processing"  targetRef="Activity_X_Agent" />
    <bpmn:sequenceFlow id="SF_X_Agent_GwDecision"       sourceRef="Activity_X_Agent"         targetRef="Gw_X_Decision" />

  </bpmn:process>
```

---

## 8. XFlow — Boucle de correction complète (P6)

> La correction revient à la **vérification Odoo** (P5), pas directement à l'agent.

```xml
    <!-- Notification correction (P3 : notify AVANT send) -->
    <bpmn:serviceTask id="Notif_X_Correction" name="Notifier correction requise"
      camunda:modelerTemplate="tg.gouv.gnspd.sendNotification" camunda:topic="flow-notify">
      <bpmn:incoming>SF_X_Decision_Correction</bpmn:incoming>
      <bpmn:outgoing>SF_X_NotifCorr_Send</bpmn:outgoing>
      <!-- gnspdNotifyContentEmail = ${"record_id": this.data.xref, "reason": this.data.Activity_X_Agent.result.submissionData.motif ?? ""} -->
    </bpmn:serviceTask>

    <bpmn:sendTask id="Send_X_Correction" name="Envoyer ordre correction XPortal"
      camunda:modelerTemplate="tg.gouv.gnspd.sendMessage" camunda:topic="flow-send-message">
      <bpmn:incoming>SF_X_NotifCorr_Send</bpmn:incoming>
      <bpmn:outgoing>SF_X_SendCorr_RecvResub</bpmn:outgoing>
      <!-- gnspdMessage = ${"action": "correction", "motif": this.data.Activity_X_Agent.result.submissionData.motif ?? null, "reference": this.data.xref} -->
      <!-- gnspdMessageRef = MSG_SERVICE_RETURN -->
    </bpmn:sendTask>

    <!-- XFlow attend la resoumission (compteur anti-boucle infinie) -->
    <bpmn:receiveTask id="Recv_X_Resub" name="Attendre resoumission"
      camunda:modelerTemplate="tg.gouv.gnspd.receiveTask"
      messageRef="MSG_SERVICE_RESUB" camunda:topic="flow-receive-task">
      <bpmn:incoming>SF_X_SendCorr_RecvResub</bpmn:incoming>
      <bpmn:outgoing>SF_X_RecvResub_GwCounter</bpmn:outgoing>
    </bpmn:receiveTask>

    <!-- Gateway compteur : évite la boucle infinie -->
    <bpmn:exclusiveGateway id="Gw_X_Counter" name="Nb corrections ?">
      <bpmn:incoming>SF_X_RecvResub_GwCounter</bpmn:incoming>
      <bpmn:outgoing>SF_X_Counter_OdooSearch</bpmn:outgoing>   <!-- < 3 : vers re-vérification Odoo -->
      <bpmn:outgoing>SF_X_Counter_MaxReject</bpmn:outgoing>    <!-- >= 3 : vers rejet DRY (P4) -->
    </bpmn:exclusiveGateway>

    <bpmn:sequenceFlow id="SF_X_Counter_OdooSearch" sourceRef="Gw_X_Counter" targetRef="Activity_X_OdooSearch">
      <!-- P6 : RETOUR à la vérification Odoo, PAS directement à l'agent -->
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">this.data.nbCorrections &lt; 3</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="SF_X_Counter_MaxReject" sourceRef="Gw_X_Counter" targetRef="Notif_X_Reject">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">this.data.nbCorrections &gt;= 3</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="SF_X_RecvResub_OdooSearch" sourceRef="Gw_X_Counter" targetRef="Activity_X_OdooSearch" />
    <bpmn:sequenceFlow id="SF_X_NotifCorr_Send"       sourceRef="Notif_X_Correction" targetRef="Send_X_Correction" />
    <bpmn:sequenceFlow id="SF_X_SendCorr_RecvResub"   sourceRef="Send_X_Correction"  targetRef="Recv_X_Resub" />
    <bpmn:sequenceFlow id="SF_X_RecvResub_GwCounter"  sourceRef="Recv_X_Resub"        targetRef="Gw_X_Counter" />
```

---

## 9. XFlow — Chaîne documentaire complète

> Ordre obligatoire : generateTemplate → generateUrlQrcode → pdfImage → certSign/signServer → stepNotification → notify → send

```xml
    <bpmn:serviceTask id="Doc_X_Generate" name="Générer le document"
      camunda:modelerTemplate="tg.gouv.gnspd.generateTemplate" camunda:topic="flow-generate-template">
      <bpmn:incoming>SF_X_Approve_Generate</bpmn:incoming>
      <bpmn:outgoing>SF_X_Generate_Qrcode</bpmn:outgoing>
      <!-- gnspdGeneratedName = "diplome-${this.data.xref}.pdf" -->
      <!-- gnspdTemplate = TEMPLATE_ID (ULID du template GED) -->
    </bpmn:serviceTask>

    <bpmn:serviceTask id="Doc_X_Qrcode" name="Générer QR code vérification"
      camunda:modelerTemplate="tg.gouv.gnspd.generateUrlQrcode" camunda:topic="flow-generate-url-qrcode">
      <bpmn:incoming>SF_X_Generate_Qrcode</bpmn:incoming>
      <bpmn:outgoing>SF_X_Qrcode_PdfImage</bpmn:outgoing>
      <!-- gnspdUrl = $(this.data.Event_X_Start.parameters.configuration.PORTAL.BASE_URL + '/verify/' + this.data.xref) -->
    </bpmn:serviceTask>

    <bpmn:serviceTask id="Doc_X_PdfImage" name="Apposer QR sur document"
      camunda:modelerTemplate="tg.gouv.gnspd.pdfImage" camunda:topic="flow-pdf-image">
      <bpmn:incoming>SF_X_Qrcode_PdfImage</bpmn:incoming>
      <bpmn:outgoing>SF_X_PdfImage_Sign</bpmn:outgoing>
      <!-- gnspdPdfFile = $this.data.Doc_X_Generate.result -->
      <!-- gnspdImage = $this.data.Doc_X_Qrcode.result -->
    </bpmn:serviceTask>

    <bpmn:serviceTask id="Doc_X_Sign" name="Signer le document (E-Cert)"
      camunda:modelerTemplate="tg.gouv.gnspd.certSign" camunda:topic="flow-cert-sign">
      <bpmn:incoming>SF_X_PdfImage_Sign</bpmn:incoming>
      <bpmn:outgoing>SF_X_Sign_StepNotifSuccess</bpmn:outgoing>
    </bpmn:serviceTask>

    <bpmn:serviceTask id="StepNotif_X_Success" name="Mettre à jour étape (Succès)"
      camunda:modelerTemplate="tg.gouv.gnspd.stepNotification" camunda:topic="flow-step-notification">
      <bpmn:extensionElements>
        <camunda:inputOutput>
          <camunda:inputParameter name="gnspdStatus">Success</camunda:inputParameter>
          <camunda:inputParameter name="gnspdIsPortal">true</camunda:inputParameter>
          <camunda:inputParameter name="gnspdStepOrder">3</camunda:inputParameter>
        </camunda:inputOutput>
      </bpmn:extensionElements>
      <bpmn:incoming>SF_X_Sign_StepNotifSuccess</bpmn:incoming>
      <bpmn:outgoing>SF_X_StepNotifSuccess_Notif</bpmn:outgoing>
    </bpmn:serviceTask>

    <!-- P3 : notify AVANT send -->
    <bpmn:serviceTask id="Notif_X_Accept" name="Notifier document disponible"
      camunda:modelerTemplate="tg.gouv.gnspd.sendNotification" camunda:topic="flow-notify">
      <bpmn:incoming>SF_X_StepNotifSuccess_Notif</bpmn:incoming>
      <bpmn:outgoing>SF_X_Notif_SendAccept</bpmn:outgoing>
    </bpmn:serviceTask>

    <bpmn:sendTask id="Send_X_Return" name="Envoyer acceptation XPortal"
      camunda:modelerTemplate="tg.gouv.gnspd.sendMessage" camunda:topic="flow-send-message">
      <bpmn:incoming>SF_X_Notif_SendAccept</bpmn:incoming>
      <bpmn:outgoing>SF_X_SendAccept_End</bpmn:outgoing>
      <!-- gnspdMessage = ${"action": "accepte", "reference": this.data.xref} -->
      <!-- gnspdMessageRef = MSG_SERVICE_RETURN -->
    </bpmn:sendTask>

    <bpmn:endEvent id="End_X_Success" name="Document délivré"
      camunda:modelerTemplate="tg.gouv.gnspd.endEvent" camunda:topic="flow-end-event">
      <bpmn:incoming>SF_X_SendAccept_End</bpmn:incoming>
    </bpmn:endEvent>

    <bpmn:sequenceFlow id="SF_X_Generate_Qrcode"        sourceRef="Doc_X_Generate"        targetRef="Doc_X_Qrcode" />
    <bpmn:sequenceFlow id="SF_X_Qrcode_PdfImage"        sourceRef="Doc_X_Qrcode"           targetRef="Doc_X_PdfImage" />
    <bpmn:sequenceFlow id="SF_X_PdfImage_Sign"          sourceRef="Doc_X_PdfImage"         targetRef="Doc_X_Sign" />
    <bpmn:sequenceFlow id="SF_X_Sign_StepNotifSuccess"  sourceRef="Doc_X_Sign"             targetRef="StepNotif_X_Success" />
    <bpmn:sequenceFlow id="SF_X_StepNotifSuccess_Notif" sourceRef="StepNotif_X_Success"    targetRef="Notif_X_Accept" />
    <bpmn:sequenceFlow id="SF_X_Notif_SendAccept"       sourceRef="Notif_X_Accept"         targetRef="Send_X_Return" />
    <bpmn:sequenceFlow id="SF_X_SendAccept_End"         sourceRef="Send_X_Return"           targetRef="End_X_Success" />
```

---

## 10. XFlow — Cycle de paiement (service payant)

> XFlow orchestre le paiement : reçoit le callback e-Gov via `intermediateCatchEvent`.
> XPortal ne traite jamais le callback e-Gov directement.

```xml
    <!-- XFlow envoie l'ordre de paiement au portail (avant instruction agent) -->
    <bpmn:sendTask id="Send_X_PayOrder" name="Ordonner paiement XPortal"
      camunda:modelerTemplate="tg.gouv.gnspd.sendMessage" camunda:topic="flow-send-message">
      <bpmn:incoming>SF_X_Odoo_PayOrder</bpmn:incoming>
      <bpmn:outgoing>SF_X_PayOrder_CatchCallback</bpmn:outgoing>
      <!-- gnspdMessageRef = MSG_SERVICE_PAY_ORDER -->
      <!-- gnspdMessage = ${"action": "paiement_requis", "montant": this.data.Event_X_Start.parameters.paymentAmount} -->
    </bpmn:sendTask>

    <!-- XFlow se bloque ici jusqu'à réception du callback e-Gov -->
    <bpmn:intermediateCatchEvent id="Event_X_PayCallback" name="Recevoir callback paiement e-Gov">
      <bpmn:extensionElements>
        <camunda:executionListener event="end">
          <camunda:script scriptFormat="javascript">this.data.payment_key = true</camunda:script>
        </camunda:executionListener>
      </bpmn:extensionElements>
      <bpmn:incoming>SF_X_PayOrder_CatchCallback</bpmn:incoming>
      <bpmn:outgoing>SF_X_Callback_GwPay</bpmn:outgoing>
      <bpmn:messageEventDefinition messageRef="MSG_SERVICE_PAY_CALLBACK" />
    </bpmn:intermediateCatchEvent>

    <!-- Gateway : paiement confirmé ou non -->
    <bpmn:exclusiveGateway id="Gw_X_PayOK" name="Paiement OK ?">
      <bpmn:incoming>SF_X_Callback_GwPay</bpmn:incoming>
      <bpmn:outgoing>SF_X_PayOK_SendConfirm</bpmn:outgoing>  <!-- confirmé -->
      <bpmn:outgoing>SF_X_PayKO_Reject</bpmn:outgoing>       <!-- non confirmé → rejet DRY (P4) -->
    </bpmn:exclusiveGateway>

    <bpmn:sendTask id="Send_X_PayConfirm" name="Confirmer paiement XPortal"
      camunda:modelerTemplate="tg.gouv.gnspd.sendMessage" camunda:topic="flow-send-message">
      <bpmn:incoming>SF_X_PayOK_SendConfirm</bpmn:incoming>
      <bpmn:outgoing>SF_X_PayConfirm_Agent</bpmn:outgoing>   <!-- vers instruction agent -->
      <!-- gnspdMessageRef = MSG_SERVICE_PAY_CONFIRM -->
      <!-- gnspdMessage = ${"action": "paiement_confirme", "reference": this.data.xref} -->
    </bpmn:sendTask>

    <bpmn:sequenceFlow id="SF_X_PayOrder_CatchCallback" sourceRef="Send_X_PayOrder"    targetRef="Event_X_PayCallback" />
    <bpmn:sequenceFlow id="SF_X_Callback_GwPay"         sourceRef="Event_X_PayCallback" targetRef="Gw_X_PayOK" />
    <bpmn:sequenceFlow id="SF_X_PayOK_SendConfirm"      sourceRef="Gw_X_PayOK"          targetRef="Send_X_PayConfirm">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">this.data.payment_key == true</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="SF_X_PayKO_Reject"           sourceRef="Gw_X_PayOK"          targetRef="Notif_X_Reject">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">this.data.payment_key != true</bpmn:conditionExpression>
    </bpmn:sequenceFlow>
```

---

## 11. XFlow — Boundary timer non-interrompant + EndEvent (P7)

> Un boundary timer non-interrompant crée un **jeton parallèle** qui DOIT se terminer sur un EndEvent explicite.
> Ne pas laisser ce jeton sans chemin de sortie (erreur "élément sans flux sortant").

```xml
    <!-- Timer non-interrompant sur la userTask agent : déclenche l'escalade SLA -->
    <!-- ⚠️ PAS de camunda:type ni camunda:topic sur bpmn:boundaryEvent — sinon "non atteignable depuis les startEvents" -->
    <bpmn:boundaryEvent id="BoundaryTimer_X_Agent"
      cancelActivity="false"
      attachedToRef="Activity_X_Agent">
      <bpmn:outgoing>SF_X_Timer_NotifEscalade</bpmn:outgoing>
      <bpmn:timerEventDefinition id="TimerDef_X_Agent">
        <bpmn:timeDuration xsi:type="bpmn:tFormalExpression">PT72H</bpmn:timeDuration>
      </bpmn:timerEventDefinition>
    </bpmn:boundaryEvent>

    <!-- Notification escalade SLA (jeton parallèle) -->
    <bpmn:serviceTask id="Activity_X_NotifEscalade" name="Notifier escalade SLA"
      camunda:type="external" camunda:topic="flow-notify">
      <bpmn:incoming>SF_X_Timer_NotifEscalade</bpmn:incoming>
      <bpmn:outgoing>SF_X_NotifEscalade_End</bpmn:outgoing>  <!-- P7 : OBLIGATOIRE -->
    </bpmn:serviceTask>

    <!-- P7 : EndEvent explicite pour le jeton du boundary timer -->
    <bpmn:endEvent id="End_X_Escalade" name="Fin escalade SLA">
      <bpmn:incoming>SF_X_NotifEscalade_End</bpmn:incoming>
    </bpmn:endEvent>

    <bpmn:sequenceFlow id="SF_X_Timer_NotifEscalade"  sourceRef="BoundaryTimer_X_Agent"    targetRef="Activity_X_NotifEscalade" />
    <bpmn:sequenceFlow id="SF_X_NotifEscalade_End"    sourceRef="Activity_X_NotifEscalade"  targetRef="End_X_Escalade" />
```

---

## 12. XFlow — ScriptTask compteur de boucle (alternative au boundary timer)

> Quand la boucle doit s'arrêter après N tentatives (correction, reformulation) sans délai temporel.
> Alternative au boundary timer : contrôle explicite par compteur de variables.

```xml
    <!-- 1. Initialisation à 0 (une seule fois, en entrée de process ou après conformité) -->
    <bpmn:scriptTask id="ScriptTask_InitCount" name="Initialiser compteur reformulations à 0"
      scriptFormat="javascript">
      <bpmn:incoming>SF_X_Prev_Init</bpmn:incoming>
      <bpmn:outgoing>SF_X_Init_Analyze</bpmn:outgoing>
      <bpmn:script>this.data.reformulationCount = 0</bpmn:script>
    </bpmn:scriptTask>

    <!-- 2. Tâche agent (analyse, proposition de réponse...) -->
    <bpmn:userTask id="Activity_X_Analyze" name="Analyser et proposer une réponse" ... />

    <!-- 3. Incrémentation APRÈS la tâche agent -->
    <bpmn:scriptTask id="ScriptTask_IncrCount" name="Incrémenter compteur reformulations"
      scriptFormat="javascript">
      <bpmn:incoming>SF_X_Analyze_Incr</bpmn:incoming>
      <bpmn:outgoing>SF_X_Incr_GwValidate</bpmn:outgoing>
      <bpmn:script>this.data.reformulationCount += 1</bpmn:script>
    </bpmn:scriptTask>

    <!-- 4. Validation par le chef / superviseur -->
    <bpmn:userTask id="Activity_X_Validate" name="Valider et signer la réponse" ... />

    <!-- 5. Gateway : validé ou reformulation ? -->
    <bpmn:exclusiveGateway id="Gw_X_Validated" name="Validé ?">
      <bpmn:incoming>SF_X_Validate_Gw</bpmn:incoming>
      <bpmn:outgoing>SF_X_Validated_Yes</bpmn:outgoing>
      <bpmn:outgoing>SF_X_Validated_No</bpmn:outgoing>
    </bpmn:exclusiveGateway>
    <!-- Condition validation : this.data.Activity_X_Validate.result.decision == 'oui' -->
    <!-- Condition reformulation : this.data.Activity_X_Validate.result.decision == 'non' -->

    <!-- 6. Gateway de limite (après validation NON) -->
    <bpmn:exclusiveGateway id="Gw_X_CountLimit" name="Reformulations ≤ 2 ?">
      <bpmn:incoming>SF_X_Validated_No</bpmn:incoming>
      <bpmn:outgoing>SF_X_Count_Continue</bpmn:outgoing>
      <bpmn:outgoing>SF_X_Count_Max</bpmn:outgoing>
    </bpmn:exclusiveGateway>
    <bpmn:sequenceFlow id="SF_X_Count_Continue" sourceRef="Gw_X_CountLimit" targetRef="Activity_X_Analyze">
      <!-- ⚠️ Lire la VARIABLE GLOBALE, pas this.data.TASK.result.reformulationCount -->
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">
        this.data.reformulationCount &lt;= 2
      </bpmn:conditionExpression>
    </bpmn:sequenceFlow>
    <bpmn:sequenceFlow id="SF_X_Count_Max" sourceRef="Gw_X_CountLimit" targetRef="End_X_Cloture">
      <bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">
        this.data.reformulationCount &gt; 2
      </bpmn:conditionExpression>
    </bpmn:sequenceFlow>
```

---

## 13. BPMNDiagram — Grille de coordonnées de référence

> Grille standard ATD. Adapter les x selon le nombre de tâches (pas de 160px entre tâches).

```
Pool XPortal  : y=80,  hauteur=500  → centre des tâches y≈180 (événements) / y≈220 (tâches)
Pool XFlow    : y=650, hauteur=600  → centre des tâches y≈730 (événements) / y≈770 (tâches)

Progression horizontale : StartEvent x=210, puis +160px par tâche/gateway
StartEvent/EndEvent : 36x36
Tâche (serviceTask, userTask, sendTask, receiveTask) : 100x80
Gateway (exclusiveGateway) : 50x50
```

```xml
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Collaboration_SERVICE">

      <bpmndi:BPMNShape id="Participant_Portal_di" bpmnElement="Participant_Portal" isHorizontal="true">
        <dc:Bounds x="140" y="80" width="2970" height="500" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="Participant_Xflow_di" bpmnElement="Participant_Xflow" isHorizontal="true">
        <dc:Bounds x="140" y="650" width="2970" height="600" />
      </bpmndi:BPMNShape>

      <!-- StartEvent (Pool Portal) : x=210, y=312 (centré dans pool 500h) -->
      <bpmndi:BPMNShape id="Event_P_Start_di" bpmnElement="Event_P_Start">
        <dc:Bounds x="210" y="312" width="36" height="36" />
      </bpmndi:BPMNShape>

      <!-- StartEvent (Pool XFlow) : x=210, y=912 (centré dans pool 600h) -->
      <bpmndi:BPMNShape id="Event_X_Start_di" bpmnElement="Event_X_Start">
        <dc:Bounds x="210" y="912" width="36" height="36" />
      </bpmndi:BPMNShape>

      <!-- MessageFlow inter-pool : waypoints du bas du SendTask vers le haut du StartEvent/ReceiveTask -->
      <bpmndi:BPMNEdge id="MF_Start_di" bpmnElement="MF_Start">
        <di:waypoint x="[SendTask_cx]" y="[SendTask_bottom]" />
        <di:waypoint x="[StartEvent_cx]" y="[StartEvent_top]" />
      </bpmndi:BPMNEdge>

    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>
```

---

## Checklist avant livraison

- [ ] P8 : chaque `<bpmn:message>` a exactement 1 SendTask et 1 ReceiveTask/StartEvent référents
- [ ] P7 : chaque branche (approve, reject, correction, escalade timer) atteint un EndEvent
- [ ] P2 : aucun ExclusiveGateway utilisé comme merge (N→1) — vérifier que tous les EG ont ≥2 outgoing
- [ ] P3 : dans chaque chemin, la sendNotification précède le sendTask inter-pool
- [ ] Tous les `conditionExpression` ont `language="javascript"` (sans typo `javscript`)
- [ ] Tous les `conditionExpression` utilisent `this.data.` (sans `$`) — le `$` est réservé aux `inputParameter`
- [ ] `gnspdStatus` (stepNotification) : `Submited` (1 t!), `PendingBackOffice`, `PendingUser`, `PendingPayment`, `Success`, `Fail`, `Terminated` — ⛔ pas `Submitted`, `Completed`, `Processing`
- [ ] `gnspdTaskStatus` (userTask/sendTask) : `Pending`, `PendingPortal`, `PendingPayment`, `PendingBackOffice`, `Completed`, `Rejected` — ⛔ pas `PendingUser`, `Success`, `Submited`
- [ ] stepNotification : seulement `gnspdStatus` + `gnspdIsPortal` + `gnspdStepOrder` — ⛔ pas les 8 champs de tâche
- [ ] BPMNDiagram : tous les éléments ont un Shape et tous les flux ont un Edge
- [ ] Pool XPortal : `isExecutable="true"` sur participant ET process. Pool XFlow : `isExecutable="true"` sur participant, `isExecutable="false"` sur process.
- [ ] Aucun namespace `zeebe:`
- [ ] `boundaryEvent` timer : pas de `camunda:type` ni `camunda:topic` sur l'élément — `timerEventDefinition` avec `id`, `timeDuration` avec `xsi:type="bpmn:tFormalExpression"`
- [ ] Correction XPortal : `gnspdHandlerType="publish_submission"` + `gnspdSubmissionData` conditionnel avec `.submissionData.data` (avec `.data`). Pattern : `$(this.data.TASK && this.data.TASK.result ? this.data.TASK.result : this.data.EVENT.parameters.submissionData.data)`
- [ ] RestBuilders XFlow : inclure `gnspdSystemData=${"applicant": this.data.applicant, "recordUid": this.data.recordUid}` sur tous
- [ ] `gnspdTargetElementType` : `bpmn:StartEvent` pour la sendTask initiale seulement, `bpmn:ReceiveTask` pour toutes les autres
