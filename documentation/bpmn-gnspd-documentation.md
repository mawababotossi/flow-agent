# Documentation de Modélisation BPMN — Projet ATD / GNSPD

**Plateforme :** Camunda Platform 7.17  
**Contexte :** Programme de Digitalisation des Services Publics — Agence Togo Digital  
**Statut :** Référence vivante extraite par analyse des artefacts réels du projet  

---

## Table des matières

1. [Architecture générale](#1-architecture-générale)
2. [Structure obligatoire d'un fichier BPMN](#2-structure-obligatoire-dun-fichier-bpmn)
3. [Catalogue Officiel des Composants GNSPD](#3-catalogue-officiel-des-composants-gnspd)
4. [Catalogue complet des templates GNSPD (Détails techniques)](#4-catalogue-complet-des-templates-gnspd-détails-techniques)
4. [Patterns de communication inter-pools (Kafka)](#4-patterns-de-communication-inter-pools-kafka)
5. [Accès aux données — Grammaire `this.data`](#5-accès-aux-données--grammaire-thisdata)
6. [Patterns de processus récurrents](#6-patterns-de-processus-récurrents)
7. [Conditions JavaScript — Référentiel des expressions](#7-conditions-javascript--référentiel-des-expressions)
8. [Intégrations systèmes tiers](#8-intégrations-systèmes-tiers)
9. [Configuration multi-environnement (KMS)](#9-configuration-multi-environnement-kms)
10. [Règles de modélisation graphique (BPMNDiagram)](#10-règles-de-modélisation-graphique-bpmndiagram)
11. [Checklist qualité d'un fichier BPMN](#11-checklist-qualité-dun-fichier-bpmn)
12. [Anti-patterns constatés dans les fichiers du projet](#12-anti-patterns-constatés-dans-les-fichiers-du-projet)

---

## 1. Architecture générale

### 1.1 Vue d'ensemble

L'architecture GNSPD repose sur deux moteurs BPMN distincts communiquant de manière **asynchrone via Kafka** :

```
┌─────────────────────────────────────────────────────────────┐
│                     CITOYEN (Browser)                        │
└──────────────────────────┬──────────────────────────────────┘
                           │ Formulaire Form.io (P-Studio)
┌──────────────────────────▼──────────────────────────────────┐
│  XPORTAL — Pool Portail Citoyen (isExecutable="true")        │
│  • Machine à états pilotée par les messages de XFlow         │
│  • Gère : paiement, corrections, affichage statuts           │
│  • Données : this.data.[StartEvent_ID].parameters.XXX        │
└──────────────────────────┬──────────────────────────────────┘
                           │ Kafka topic: bpmn.commands
┌──────────────────────────▼──────────────────────────────────┐
│  XFLOW — Pool Back-Office (isExecutable="true")              │
│  • Orchestration métier                                       │
│  • Gère : instruction, Odoo, REST tiers, notifications        │
│  • Données : this.data.[StartEvent_ID].parameters.XXX        │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
       Odoo ERP      API REST Tiers    GED / PDF
```

### 1.2 Déclaration des namespaces (obligatoire)

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
  id="Definitions_[ServiceCode]"
  targetNamespace="http://bpmn.io/schema/bpmn"
  exporter="Camunda Modeler"
  exporterVersion="5.42.0"
  modeler:executionPlatform="Camunda Platform"
  modeler:executionPlatformVersion="7.17.0">
```

> **INTERDIT** : Ne jamais utiliser `xmlns:zeebe:` — ATD tourne exclusivement sur Camunda Platform 7.

---

## 2. Structure obligatoire d'un fichier BPMN

### 2.1 Squelette global

```xml
<bpmn:definitions ...>

  <!-- 1. Messages globaux (un par échange inter-pools) -->
  <bpmn:message id="MSG_[NOM]" name="MSG_[NOM]" />

  <!-- 2. Collaboration (conteneur des deux pools) -->
  <bpmn:collaboration id="Collaboration_[Service]">
    <bpmn:participant id="Participant_Portal" name="XPORTAL"
      processRef="Process_Portal" />
    <bpmn:participant id="Participant_Xflow" name="XFLOW"
      processRef="Process_Xflow"
      camunda:versionTag="1.0"
      camunda:historyTimeToLive="180" />
    <bpmn:messageFlow id="MF01" sourceRef="[SendTask_ID]" targetRef="[ReceiveTask_ID]" />
    <!-- ... autres messageFlows ... -->
  </bpmn:collaboration>

  <!-- 3. Processus XPortal -->
  <bpmn:process id="Process_Portal" name="[Nom_Service]_Portal_v1"
    isExecutable="true" camunda:versionTag="1">
    <!-- ... éléments portail ... -->
  </bpmn:process>

  <!-- 4. Processus XFlow -->
  <bpmn:process id="Process_Xflow" name="[Nom_Service]_Xflow_v1"
    isExecutable="true" camunda:versionTag="1">
    <!-- ... éléments xflow ... -->
  </bpmn:process>

  <!-- 5. Diagramme graphique -->
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane bpmnElement="Collaboration_[Service]">
      <!-- Shapes et Edges pour tous les éléments -->
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>

</bpmn:definitions>
```

### 2.2 Déclaration des messages

Chaque échange Kafka entre les deux pools nécessite un message global déclaré **avant** la collaboration. La convention de nommage observée dans le projet est :

| Sens | Convention de nom | Exemple |
|------|------------------|---------|
| Portail → XFlow (soumission initiale) | `[SERVICE]_START_XFLOW` | `DIPLOMECFA_START_XFLOW` |
| XFlow → Portail (retour générique) | `Message_CFA_Return` | `Message_CFA_Return` |
| XFlow → Portail (demande paiement) | `MSG_PAY_REQ` ou UUID | `Message_1sr0g5o` |
| Portail → XFlow (confirmation paiement) | `MSG_PAY_CONFIRM` | `Message_CFA_PayConfirm` |
| XFlow → Portail (correction) | `MSG_CORRECTION` | `Message_3bnu1fk` |
| Portail → XFlow (resoumission) | `MSG_RESUBMIT` | `Message_CFA_Resub` |
| XFlow → Portail (acceptation) | `MSG_ACCEPT` | `Message_0eohd8p` |
| XFlow → Portail (rejet) | `MSG_REJECT` | `Message_0eohd8p` (peut être mutualisé) |

> **Bonne pratique expert-2** : Utiliser un message de retour unique (`Message_CFA_Return`) avec un champ `action` dans le payload pour distinguer les cas (`paiement_requis`, `correction`, `accepte`, `rejete`). Cela simplifie le XPortal en un point d'attente unique.

## 3. Catalogue Officiel des Composants GNSPD

Voici la liste des 29 composants techniques disponibles dans l'écosystème GNSPD / ATD pour la modélisation des processus. Ces identifiants doivent être utilisés dans les SRS et configurés dans Camunda via l'attribut `camunda:modelerTemplate`.

| Nom du Composant | Identifiant Technique (`tg.gouv.gnspd.*`) | Type BPMN | Description |
|---|---|---|---|
| Début | `startEvent` | StartEvent | Point d'entrée, porte la configuration KMS. |
| endEvent | `endEvent` | EndEvent | Point de sortie finale du processus. |
| userTask | `userTask` | UserTask | Tâche humaine (Citoyen ou Agent). |
| manualTask | `manualTask` | ManualTask | Action manuelle hors système. |
| receiveTask | `receiveTask` | ReceiveTask | Attente d'un message Kafka asynchrone. |
| Envoyer un message | `sendMessage` | SendTask | Envoi d'un message Kafka asynchrone. |
| Sub Process | `subProcess` | SubProcess | Conteneur de sous-processus. |
| Requête XMLRPC vers Odoo | `odoo` | ServiceTask | Intégration ERP Odoo (search, create, write). |
| Transfert Rest | `restBuilder` | ServiceTask | Client API REST avancé (Bearer Token). |
| Exécuter une requête http | `requestHttp` | ServiceTask | Client HTTP simple. |
| Envoyer une notification | `sendNotification` | ServiceTask | Envoi SMS, Email, In-App. |
| Modification de l'état | `stepNotification` | ServiceTask | Mise à jour du fil d'ariane citoyen. |
| signature E-Cert | `certSign` | ServiceTask | Signature électronique certifiée. |
| Signature SignServer | `signServer` | ServiceTask | Signature via serveur dédié. |
| Enregistrement DB | `dbSave` | ServiceTask | Sauvegarde directe en base de données. |
| Générer un fichier Docx | `generateTemplateDocx` | ServiceTask | Génération Word à partir d'un template. |
| Générer un fichier | `generateTemplate` | ServiceTask | Génération de fichier (HTML/PDF). |
| Apposer image sur PDF | `pdfImage` | ServiceTask | Insertion de photo/signature dans un PDF. |
| Générer QR Code URL | `generateUrlQrcode` | ServiceTask | Création de QR Code securisé. |
| Générer un voucher | `generateVoucher` | ServiceTask | Création de bordereau de voyage. |
| Télécharger un reçu | `receiptDownload` | ServiceTask | Mise à disposition du reçu de paiement. |
| Générer UUID | `uuidGeneration` | ServiceTask | Identifiant unique technique. |
| Calcul Mathématique | `mathOperation` | ServiceTask | Opérations arithmétiques sur variables. |
| Business Rule Task | `bussinessRuleTask` | BusinessRuleTask | Moteur de règles DMN. |
| Script Task | `scriptTask` | ScriptTask | Exécution de code JavaScript. |
| Fonction | `function` | ServiceTask | Appel de logique métier serverless. |
| Programme Agenda | `agendaEvent` | ServiceTask | Gestion de rendez-vous / calendrier. |
| Registre GouvTG | `registrationRegistreGouvTGTgvcs` | ServiceTask | Inscription au registre officiel TGVCS. |
| Form.io Portail | `flowPortail` | ServiceTask | Logique spécifique aux formulaires XPortal. |

---

## 4. Catalogue complet des templates GNSPD (Détails techniques)

### 3.1 `tg.gouv.gnspd.startEvent`

Utilisé au démarrage de **chaque pool** (portail ET xflow). Embarque la configuration multi-environnement.

**Attributs de la balise :**
```xml
<bpmn:startEvent id="Event_P_Start" name="Soumission de la demande"
  camunda:modelerTemplate="tg.gouv.gnspd.startEvent"
  camunda:formKey=""
  camunda:type="external"
  camunda:topic="flow-start">
```

**Paramètres obligatoires (extensionElements) :**

```xml
<camunda:inputOutput>
  <!-- Identification -->
  <camunda:inputParameter name="gnspdStepName">Début</camunda:inputParameter>
  <camunda:inputParameter name="gnspdDescription">Description fonctionnelle</camunda:inputParameter>
  <camunda:inputParameter name="gnspdPriority">10</camunda:inputParameter>
  <camunda:inputParameter name="gnspdExecution">PORTAIL</camunda:inputParameter>

  <!-- Paiement (0 si pas de paiement immédiat) -->
  <camunda:inputParameter name="gnspdPaymentAmount">0</camunda:inputParameter>
  <camunda:inputParameter name="gnspdCalculationOperator">ADDITION</camunda:inputParameter>
  <camunda:inputParameter name="gnspdCalculationVar1" />
  <camunda:inputParameter name="gnspdCalculationVar2" />

  <!-- Visibilité dans le tableau de bord citoyen -->
  <camunda:inputParameter name="gnspdTaskIsVisible">false</camunda:inputParameter>
  <camunda:inputParameter name="gnspdTaskLabel" />
  <camunda:inputParameter name="gnspdTaskStatus">Pending</camunda:inputParameter>
  <camunda:inputParameter name="gnspdTaskOrder" />
  <camunda:inputParameter name="gnspdTaskKind">citizen</camunda:inputParameter>
  <camunda:inputParameter name="gnspdCostVariable" />
  <camunda:inputParameter name="gnspdCostTotal" />
  <camunda:inputParameter name="gnspdCostUnitaire" />

  <!-- Configuration multi-environnement (objets JSON) -->
  <camunda:inputParameter name="development">{}</camunda:inputParameter>
  <camunda:inputParameter name="sandbox">{ "ODOO": { ... }, "GED": { ... } }</camunda:inputParameter>
  <camunda:inputParameter name="preproduction">{ ... }</camunda:inputParameter>
  <camunda:inputParameter name="production">{ ... }</camunda:inputParameter>
</camunda:inputOutput>
```

> **Règle** : Le startEvent de **XPortal** porte la configuration complète (ODOO, GED, DGDN...). Le startEvent de **XFlow** peut avoir des environnements vides `{}` car il hérite de la config passée dans le message initial.

---

### 3.2 `tg.gouv.gnspd.sendMessage`

Utilisé pour tout envoi Kafka inter-pools (SendTask). Le topic est toujours `bpmn.commands`.

```xml
<bpmn:sendTask id="Activity_P_SendBO" name="Envoi au back-office"
  camunda:modelerTemplate="tg.gouv.gnspd.sendMessage"
  camunda:type="external"
  camunda:topic="flow-send-message">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <!-- Infrastructure Kafka -->
      <camunda:inputParameter name="gnspdKafkaTopic">bpmn.commands</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTargetElementType">bpmn:StartEvent</camunda:inputParameter>
      <!-- bpmn:StartEvent | bpmn:ReceiveTask selon la cible -->

      <!-- Routage -->
      <camunda:inputParameter name="gnspdMessageDestination">peer-xflow-local-sp</camunda:inputParameter>
      <!-- peer-xflow-service-public-sandbox | ch-portail-service-public-sandbox -->

      <camunda:inputParameter name="gnspdMessageRef">MSG_[NOM]</camunda:inputParameter>
      <!-- ID du message global déclaré à la racine -->

      <!-- Payload (expression JavaScript) -->
      <camunda:inputParameter name="gnspdMessage">$this.data.Event_P_Start.parameters</camunda:inputParameter>

      <!-- Paramètres de tâche (toujours présents) -->
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

**Destinations Kafka observées dans le projet :**

| Environnement | Portail → XFlow | XFlow → Portail |
|--------------|-----------------|-----------------|
| local/sp | `peer-xflow-local-sp` | `ch-portail-local-sp` |
| local/gforce | `peer-xflow-local-gforce` | `ch-portail-local-gforce` |
| sandbox/service-public | `peer-xflow-service-public-sandbox` | `ch-portail-service-public-sandbox` |
| ONG (ancienne convention) | `peer_xflow` | *(non observé)* |

> **Bonne pratique** : La destination doit être un paramètre de configuration, pas une valeur en dur. Les noms d'environnement varient par déploiement.

---

### 3.3 `tg.gouv.gnspd.receiveTask`

Utilisé pour attendre un message Kafka entrant. Référence obligatoire à un `<bpmn:message>` global.

```xml
<bpmn:receiveTask id="Activity_P_Receive" name="Attendre le retour"
  camunda:modelerTemplate="tg.gouv.gnspd.receiveTask"
  messageRef="Message_CFA_Return"
  camunda:type="external"
  camunda:topic="flow-receive-task">
  <bpmn:extensionElements>
    <camunda:inputOutput>
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
```

> **Pattern expert-2** : Une seule `receiveTask` avec plusieurs `<bpmn:incoming>` (soumission initiale, paiement, correction) centralise l'attente XPortal. Une gateway exclusive en sortie route selon `result.data.action`.

---

### 3.4 `tg.gouv.gnspd.userTask`

Utilisé côté **XPortal** (écran citoyen : paiement, correction) et côté **XFlow** (tableau de bord agent).

```xml
<bpmn:userTask id="Activity_X_Agent" name="Vérification de conformité (B06)"
  camunda:modelerTemplate="tg.gouv.gnspd.userTask"
  camunda:formKey="01KJEFHW22ST49KFASWA048QGY"
  camunda:type="external"
  camunda:topic="flow-user-task">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdTaskDescription">Description métier de la tâche</camunda:inputParameter>
      <camunda:inputParameter name="gnspdHandlerType">publish_submission</camunda:inputParameter>
      <!-- publish_submission : renvoie le résultat de la tâche dans le payload -->

      <!-- Formulaire affiché à l'agent/citoyen -->
      <camunda:inputParameter name="gnspdSubmissionFormkey">demande-du-diplome-du-cfa</camunda:inputParameter>

      <!-- Données pré-remplies dans le formulaire -->
      <camunda:inputParameter name="gnspdSubmissionData">$this.data.Event_X_Start.parameters.submissionData</camunda:inputParameter>

      <!-- Pièces jointes mappées depuis la soumission initiale -->
      <camunda:inputParameter name="gnspdAttachments">${
  "acteDeNaissance": this.data.Event_X_Start.parameters.submissionData.acteDeNaissance ?? null,
  "releveDeNotes": this.data.Event_X_Start.parameters.submissionData.releveDeNotes ?? null
}</camunda:inputParameter>

      <!-- Visibilité dans le tableau de bord -->
      <camunda:inputParameter name="gnspdTaskIsVisible">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskLabel">Vérification conformité CFA</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskStatus">Pending</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskOrder">1</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskKind">citizen</camunda:inputParameter>
      <camunda:inputParameter name="gnspdCandidateCompanies" />
      <camunda:inputParameter name="gnspdCostVariable">dynamicCost</camunda:inputParameter>
      <camunda:inputParameter name="gnspdCostTotal" />
      <camunda:inputParameter name="gnspdCostUnitaire" />
      <camunda:inputParameter name="gnspdFormSetting" />
    </camunda:inputOutput>
  </bpmn:extensionElements>
```

**Paramètres clés :**

| Paramètre | Valeur | Usage |
|-----------|--------|-------|
| `gnspdTaskIsVisible` | `true` | Rend la tâche visible dans le suivi citoyen |
| `gnspdTaskOrder` | `1`, `2`, `3`... | Ordre d'affichage dans le fil d'avancement |
| `gnspdTaskKind` | `citizen` | Type de tâche (toujours `citizen` dans les artefacts observés) |
| `gnspdHandlerType` | `publish_submission` | Active le renvoi du résultat dans le processus |
| `gnspdCostVariable` | `dynamicCost` | Lien avec le calcul de coût du formulaire |
| `gnspdFormSetting` | Expression JS | Injecte des données contextuelles dans l'affichage du formulaire de correction |

---

### 3.5 `tg.gouv.gnspd.sendNotification`

Utilisé exclusivement dans **XFlow** pour déclencher SMS, Email et notifications in-app.

```xml
<bpmn:serviceTask id="Activity_X_NotifAR" name="Notifier l'accusé de réception"
  camunda:modelerTemplate="tg.gouv.gnspd.sendNotification"
  camunda:type="external"
  camunda:topic="flow-notify">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <!-- Email -->
      <camunda:inputParameter name="gnspdNotifySendEmail">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyEmail">$this.data.applicant.email</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyTemplateEmail">01KHBXDFGV1NTPHAR80ZSWEZXH</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyContentEmail">${"record_id": this.data.xref}</camunda:inputParameter>

      <!-- SMS -->
      <camunda:inputParameter name="gnspdNotifySendSMS">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyPhone">$this.data.applicant.phone</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyTemplateSMS">01KHBXF5B8B8WH9QFDZP607F5M</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyContentSMS">${"record_id": this.data.xref}</camunda:inputParameter>

      <!-- In-App -->
      <camunda:inputParameter name="gnspdNotifyInApp">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyTemplateInApp">01KHBXFNJPJT5WZ3K0W9BBDF3N</camunda:inputParameter>
      <camunda:inputParameter name="gnspdNotifyContentInApp">${"record_id": this.data.xref}</camunda:inputParameter>

      <!-- Pièce jointe (optionnel) -->
      <camunda:inputParameter name="gnspdNotifyAttachment" />

      <!-- Paramètres de tâche standard -->
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
```

**IDs de templates de notification (extraits du projet) :**

| Usage | Template ID |
|-------|-------------|
| Email générique | `01KHBXDFGV1NTPHAR80ZSWEZXH` |
| SMS générique | `01KHBXF5B8B8WH9QFDZP607F5M` |
| In-App paiement | `01KHBXFNJPJT5WZ3K0W9BBDF3N` |
| In-App correction | `01KHBX6AEWCBG136176D2GMZM3` |

---

### 3.6 `tg.gouv.gnspd.odoo`

Intégration directe à l'ERP Odoo via le worker `flow-odoo`.

```xml
<bpmn:serviceTask id="Activity_X_Odoo" name="Vérification candidat Odoo"
  camunda:modelerTemplate="tg.gouv.gnspd.odoo"
  camunda:type="external"
  camunda:topic="flow-odoo">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <!-- Connexion (lue depuis la configuration du startEvent) -->
      <camunda:inputParameter name="gnspdUrl">$this.data.Event_X_Start.parameters.configuration.ODOO.URL</camunda:inputParameter>
      <camunda:inputParameter name="gnspdDb">$this.data.Event_X_Start.parameters.configuration.ODOO.DB</camunda:inputParameter>
      <camunda:inputParameter name="gnspdPort">$this.data.Event_X_Start.parameters.configuration.ODOO.PORT</camunda:inputParameter>
      <camunda:inputParameter name="gnspdUsername">$this.data.Event_X_Start.parameters.configuration.ODOO.SECRET_USERNAME</camunda:inputParameter>
      <camunda:inputParameter name="gnspdPassword">$this.data.Event_X_Start.parameters.configuration.ODOO.SECRET_PASSWORD</camunda:inputParameter>

      <!-- Requête Odoo -->
      <camunda:inputParameter name="gnspdModel">exam.inscription</camunda:inputParameter>
      <camunda:inputParameter name="gnspdMethod">search_read</camunda:inputParameter>
      <!-- Méthodes : search_read | create | write | unlink -->

      <!-- Filtre de recherche (domain) -->
      <camunda:inputParameter name="gnspdDomain">${"table_number_without_space": this.data.Event_X_Start.parameters.submissionData.numeroDeTable}</camunda:inputParameter>

      <!-- Champs à retourner (null = tous) -->
      <camunda:inputParameter name="gnspdFields" />

      <!-- Pour create/write : données à envoyer -->
      <camunda:inputParameter name="gnspdParams">${
  "inscription_id": this.data.Activity_X_Odoo.result.id,
  "from_portal": "true",
  "folder_number": this.data.xref
}</camunda:inputParameter>

      <!-- Pour la génération de rapport PDF -->
      <camunda:inputParameter name="gnspdReportModel" />
      <camunda:inputParameter name="gnspdReportData">{}</camunda:inputParameter>
      <camunda:inputParameter name="gnspdReportType">docx</camunda:inputParameter>

      <!-- Paramètres de tâche standard -->
      <camunda:inputParameter name="gnspdTaskIsVisible">false</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskStatus">Pending</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskKind">citizen</camunda:inputParameter>
      <camunda:inputParameter name="gnspdOptions" />
      <camunda:inputParameter name="gnspdRestFeedback" />
      <camunda:inputParameter name="gnspdRestFeedbackSchema" />
      <camunda:inputParameter name="gnspdRecordId" />
    </camunda:inputOutput>
  </bpmn:extensionElements>
```

---

### 3.7 `tg.gouv.gnspd.restBuilder`

Utilisé pour appeler des **APIs REST tierces** (DGDN pour les passeports, etc.). Supporte l'authentification Bearer Token.

```xml
<bpmn:serviceTask id="Activity_X_RestCall" name="Envoie au backend de la DGDN"
  camunda:modelerTemplate="tg.gouv.gnspd.restBuilder"
  camunda:type="external"
  camunda:topic="flow-rest-builder">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <!-- Authentification -->
      <camunda:inputParameter name="gnspdRestType">bearerToken</camunda:inputParameter>
      <camunda:inputParameter name="gnspdRestAuthUrl">$this.data.Event_X_Start.parameters.configuration.DGDN.AUTH_URL</camunda:inputParameter>
      <camunda:inputParameter name="gnspdRestUser">$this.data.Event_X_Start.parameters.configuration.DGDN.SECRET_USERNAME</camunda:inputParameter>
      <camunda:inputParameter name="gnspdRestPassword">$this.data.Event_X_Start.parameters.configuration.DGDN.SECRET_PASSWORD</camunda:inputParameter>

      <!-- Requête HTTP -->
      <camunda:inputParameter name="gnspdRestMethod">POST</camunda:inputParameter>
      <!-- GET | POST | PUT | PATCH -->
      <camunda:inputParameter name="gnspdRestDataUrl">$(this.data.Event_X_Start.parameters.configuration.DGDN.BASE_URL + '/api/passeport/demandes')</camunda:inputParameter>
      <camunda:inputParameter name="gnspdContentType">application/json</camunda:inputParameter>
      <!-- application/json | application/merge-patch+json -->

      <!-- Données envoyées -->
      <camunda:inputParameter name="gnspdRestSendData">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdIsCustomData">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdDataFormat">JSON</camunda:inputParameter>
      <camunda:inputParameter name="gnspdSingleVariableKey">${
  "application_type": this.data.Event_X_Start.parameters.submissionData.data.typeDemande,
  "applicant_id": this.data.applicant.id
}</camunda:inputParameter>

      <!-- Fichier (pour upload) -->
      <camunda:inputParameter name="gnspdRestFile">false</camunda:inputParameter>
      <camunda:inputParameter name="gnspdRestTag">UPLOAD</camunda:inputParameter>
      <camunda:inputParameter name="gnspdRestStreamName">Document.pdf</camunda:inputParameter>

      <!-- Timeout (ms) -->
      <camunda:inputParameter name="gnspdTimeOutValue">120000</camunda:inputParameter>

      <!-- Contexte système (toujours présent) -->
      <camunda:inputParameter name="gnspdSystemData">${"applicant": this.data.applicant, "recordUid": this.data.recordUid}</camunda:inputParameter>

      <!-- Paramètres de tâche standard -->
      <camunda:inputParameter name="gnspdTaskIsVisible">false</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskStatus">Pending</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskKind">citizen</camunda:inputParameter>
      <camunda:inputParameter name="gnspdIsFormat">false</camunda:inputParameter>
    </camunda:inputOutput>
  </bpmn:extensionElements>
```

---

### 3.8 `tg.gouv.gnspd.endEvent`

Doit être appliqué aux End Events **XFlow** principaux (acceptation, rejet).

```xml
<bpmn:endEvent id="Event_X_EndSuccess" name="Fin succès"
  camunda:modelerTemplate="tg.gouv.gnspd.endEvent"
  camunda:type="external"
  camunda:topic="flow-end-event">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:inputParameter name="gnspdTaskIsVisible">true</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskLabel" />
      <camunda:inputParameter name="gnspdTaskStatus">Pending</camunda:inputParameter>
      <camunda:inputParameter name="gnspdTaskOrder" />
      <camunda:inputParameter name="gnspdTaskKind">citizen</camunda:inputParameter>
      <camunda:inputParameter name="gnspdCostVariable" />
      <camunda:inputParameter name="gnspdCostTotal" />
      <camunda:inputParameter name="gnspdCostUnitaire" />
    </camunda:inputOutput>
  </bpmn:extensionElements>
```

---

## 4. Patterns de communication inter-pools (Kafka)

### 4.1 Pattern 1 — Soumission initiale (Portail → XFlow)

```
[XPortal] StartEvent → SendTask(peer-xflow) → receiveTask (attend retour)
                                    ↓ Kafka
[XFlow]   StartEvent(flow-start) → ...traitement...
```

```xml
<!-- XPortal : envoi au démarrage -->
<camunda:inputParameter name="gnspdTargetElementType">bpmn:StartEvent</camunda:inputParameter>
<camunda:inputParameter name="gnspdMessageDestination">peer-xflow-local-sp</camunda:inputParameter>
<camunda:inputParameter name="gnspdMessage">$this.data.Event_P_Start.parameters</camunda:inputParameter>

<!-- XFlow : réception -->
<!-- Le startEvent déclenché par le message Kafka porte l'ID du message comme corrélation -->
```

### 4.2 Pattern 2 — Retour XFlow vers Portail (message de commande)

```
[XFlow]  ...décision... → sendTask(ch-portail, action="correction") → receiveTask
                                    ↓ Kafka
[XPortal] receiveTask → gateway(action?) → userTask(correction citoyen)
```

**Payload recommandé (pattern expert-2, le plus propre) :**
```javascript
${
  "action": "correction",
  "motif": this.data.Activity_X_Agent.result.submissionData.motif ?? null,
  "reference": this.data.xref
}
```

**Conditions côté Portail :**
```javascript
// Paiement requis
$this.data.Activity_P_Receive.result.data.action == "paiement_requis"
// Correction
$this.data.Activity_P_Receive.result.data.action == "correction"
// Acceptation
$this.data.Activity_P_Receive.result.data.action == "accepte"
// Rejet
$this.data.Activity_P_Receive.result.data.action == "rejete"
```

### 4.3 Pattern 3 — Confirmation de paiement (Portail → XFlow)

```
[XPortal] receiveTask(autorisation paiement) → userTask(paiement citoyen)
          → sendTask(peer-xflow, paymentStatus="confirmed")
                              ↓ Kafka
[XFlow]   intermediateCatchEvent(Message_PAY) → gateway(paiement OK?)
```

### 4.4 Pattern 4 — Resoumission après correction

```
[XPortal] receiveTask(correction) → userTask(correction citoyen) 
          → sendTask(peer-xflow, resoumission)
                              ↓ Kafka
[XFlow]   receiveTask(resoumission) → retour sur userTask agent (boucle)
```

---

## 5. Accès aux données — Grammaire `this.data`

### 5.1 Structure générale

La variable `this.data` est le contexte d'exécution GNSPD. Elle accumule les résultats de chaque tâche terminée, indexés par l'**ID XML de l'élément BPMN**.

```javascript
// Données de la soumission initiale (depuis le startEvent XFlow)
this.data.Event_X_Start.parameters.submissionData.data.champFormulaire

// Données de l'applicant (profil citoyen, disponible globalement)
this.data.applicant.email
this.data.applicant.phone

// Référence unique du dossier
this.data.xref
this.data.recordUid

// Résultat d'une userTask agent
this.data.Activity_X_Agent.result.submissionData.decision
this.data.Activity_X_Agent.result.submissionData.motif

// Message reçu dans une receiveTask XPortal
this.data.Activity_P_Receive.result.data.action

// Données d'un message Kafka reçu (via receiveTask XFlow)
this.data.Activity_P_Resubmit.parameters.message.submissionData.champCorrige

// Résultat d'une tâche Odoo
this.data.Activity_X_Odoo.result.id
this.data.Activity_X_Odoo.result.inscrit

// Configuration injectée par le startEvent (pour les appels systèmes)
this.data.Event_X_Start.parameters.configuration.ODOO.URL
this.data.Event_X_Start.parameters.configuration.DGDN.BASE_URL
```

### 5.2 Opérateur nullish `??`

Utiliser systématiquement `??` pour les champs optionnels :
```javascript
this.data.Activity_P_Payment.result.data.paymentRef ?? null
this.data.Event_X_Start.parameters.submissionData.duplicata ?? 'Non'
```

### 5.3 Différence `this.data` vs `$this.data`

Les deux formes sont observées dans les artefacts. La forme avec `$` est la plus robuste dans les `conditionExpression` (expression évaluée en contexte GNSPD). Les deux fonctionnent, mais la cohérence au sein d'un fichier est recommandée.

---

## 6. Patterns de processus récurrents

### 6.1 Pattern : Processus avec paiement conditionnel (diplôme duplicata)

```
XFlow:
StartEvent → Gateway(duplicata?) 
  → OUI : Notification → SendTask(autorisation paiement) → IntermediateCatch(confirmation)
         → SendTask(confirmation portail) → UserTask agent (vérification)
  → NON : directement → UserTask agent (vérification)
→ Gateway(décision agent?)
  → Conforme : Odoo(create) → Notification → SendTask(accepte) → EndEvent
  → Correction : Notification → SendTask(correction) → receiveTask(resoumission) → retour vérification
  → Rejet : Notification → SendTask(rejet) → EndEvent
```

### 6.2 Pattern : Machine à états XPortal (expert-2)

Approche recommandée — XPortal comme automate à état minimal :

```
StartEvent → SendTask(→XFlow) → receiveTask(Multi-entrants: initial+paiement+correction)
→ Gateway(action?)
  → paiement_requis : userTask(paiement) → SendTask(confirm paiement) → ↑ receiveTask
  → correction : userTask(corrections) → SendTask(resoumission) → ↑ receiveTask
  → accepte : EndEvent(Succès)
  → rejete : EndEvent(Rejet)
```

L'avantage de cette approche est la **réutilisabilité** : la `receiveTask` est multi-entrante, la gateway décide du parcours sans multiplier les points d'attente.

### 6.3 Pattern : Machine à états XPortal (expert-1)

Approche distribuée — chaque retour XFlow déclenche une branche dédiée. Plus verbeux mais plus explicite pour les processus complexes.

```
StartEvent → SendTask → InclusiveGateway(boucle) 
  → receiveTask(résultat vérif) → Gateway → correction | succès | rejet
     → [correction] receiveTask(ordre correction) → userTask → SendTask(resoumission) → ↑ gateway
```

### 6.4 Pattern : Intégration REST tierce (passeport/DGDN)

Quand le back-office n'est pas Odoo mais une API tierce :

```
XFlow:
StartEvent → restBuilder(POST /api/demandes) → Gateway(insertion OK?)
  → OK: Polling loop via restBuilder(GET /api/etat) → Gateway(état?)
         → validated : restBuilder(GET /api/fiche.pdf) → SendTask(→portail fiche)
         → processing : ... attendre
         → disallowed : Notification rejet → EndEvent
```

---

## 7. Conditions JavaScript — Référentiel des expressions

Toutes les conditions doivent être déclarées avec `language="javascript"`.

```xml
<bpmn:conditionExpression xsi:type="bpmn:tFormalExpression" language="javascript">
  EXPRESSION
</bpmn:conditionExpression>
```

### 7.1 Conditions sur décision agent

```javascript
// Décision binaire (oui/non)
this.data.Activity_X_Agent.result.submissionData.decision == 'oui'
this.data.Activity_X_Agent.result.submissionData.decision == 'non'

// Décision avec correction
this.data.Activity_X_Agent.result.submissionData.decision == 'oui' 
  && this.data.Activity_X_Agent.result.submissionData.hasCorrections == 'oui'

// Décision acceptée sans correction
this.data.Activity_X_Agent.result.submissionData.hasCorrections == 'non' 
  && this.data.Activity_X_Agent.result.submissionData.decision == 'oui'
```

### 7.2 Conditions sur action de retour XFlow

```javascript
$this.data.Activity_P_Receive.result.data.action == "paiement_requis"
$this.data.Activity_P_Receive.result.data.action == "correction"
$this.data.Activity_P_Receive.result.data.action == "accepte"
$this.data.Activity_P_Receive.result.data.action == "rejete"
```

### 7.3 Conditions sur données formulaire

```javascript
// Champ radio duplicata
this.data.Event_X_Start.parameters.submissionData.duplicata == 'Oui'
this.data.Event_X_Start.parameters.submissionData.duplicata == 'Non'
// Ou avec $
$this.data.Event_X_Start.parameters.submissionData.data.duplicata == "Oui"
```

### 7.4 Conditions sur résultats systèmes

```javascript
// Odoo : enregistrement trouvé
this.data.Activity_X_Odoo.result.id != null
this.data.Activity_X_Odoo.result.id == null

// Odoo : inscrit (champ booléen)
$this.data.Activity_X_Odoo.result.data.inscrit == true

// REST : état de traitement
this.data.Activity_X_RestPoll.result.data.state == 'validated'
this.data.Activity_X_RestPoll.result.data.state == 'disallowed'
this.data.Activity_X_RestPoll.result.data.state != 'validated' 
  && this.data.Activity_X_RestPoll.result.data.state != 'disallowed'

// Paiement confirmé
$this.data.Activity_X_RecvPay.result.data.paymentStatus == "confirmed"
$this.data.Activity_X_RecvPay.result.data.paymentStatus != "confirmed"
```

### 7.5 Conditions sur état REST (passeport)

```javascript
// Via message reçu (receiveTask)
this.data.Activity_P_Recv.parameters.message.check_state.data.state == 'disallowed'
this.data.Activity_P_Recv.parameters.message.check_state.data.state == 'validated'
```

> **ATTENTION** : Toujours vérifier l'orthographe de l'attribut `language="javascript"` (erreur fréquente : "javscript" sans 'a').

---

## 8. Intégrations systèmes tiers

### 8.1 Odoo ERP

| Paramètre | Valeur type |
|-----------|-------------|
| `gnspdModel` | `exam.inscription` / `exam.demande` / `res.partner` |
| `gnspdMethod` | `search_read` (lecture) / `create` (création) / `write` (mise à jour) |
| `gnspdDomain` | Filtre JSON : `${"table_number": this.data.X.submissionData.numero}` |
| `gnspdParams` | Données pour create/write |
| `gnspdRecordId` | ID Odoo de l'enregistrement cible (pour write) |
| `gnspdReportType` | `docx` (pour génération de rapport) |

### 8.2 GED (Gestion Electronique de Documents)

La GED est accessible via l'API GED avec une clé API KMS :

```json
"GED": {
  "BASE_URL": "https://ged.gouv.tg",
  "SECRET_API_KEY": "{dbkms:CFA_GED_API_KEY_PROD}"
}
```

### 8.3 API REST tierce (DGDN — passeport)

Modèle complet : authentification bearerToken → POST création → polling GET état → GET récupération PDF.

---

## 9. Configuration multi-environnement (KMS)

### 9.1 Structure JSON standard

Injectée dans le startEvent XFlow :

```json
{
  "ODOO": {
    "URL": "https://[service]-odoo.sandbox.gouv.tg",
    "PORT": "",
    "DB": "@{cfa}",
    "SECRET_USERNAME": "{dbkms:CFA_ODOO_USERNAME}",
    "SECRET_PASSWORD": "{dbkms:CFA_ODOO_PASSWORD}"
  },
  "GED": {
    "BASE_URL": "https://ged.sandbox.gouv.tg",
    "SECRET_API_KEY": "{dbkms:CFA_GED_API_KEY_SANDBOX}"
  },
  "NOTIFICATIONS": {
    "SMTP_HOST": "smtp.sandbox.gouv.tg",
    "SECRET_SMTP_PASSWORD": "{dbkms:CFA_SMTP_PASSWORD_SANDBOX}"
  }
}
```

### 9.2 Conventions de nommage KMS

Format : `{dbkms:[SERVICE]_[COMPOSANT]_[ENV_OPTIONNEL]}`

Exemples observés :
- `{dbkms:CFA_ODOO_USERNAME}`
- `{dbkms:CFA_ODOO_PASSWORD}`
- `{dbkms:CFA_GED_API_KEY_SANDBOX}`
- `{dbkms:SECRET_USERNAME}` (passeport — convention moins précise)

### 9.3 DB Odoo avec template

La valeur `"DB": "@{cfa}"` utilise un mécanisme de template de l'environnement d'exécution (le `@{}` est résolu au runtime).

### 9.4 Quatre environnements obligatoires

Toujours déclarer les quatre clés : `development`, `sandbox`, `preproduction`, `production`. Si un environnement n'a pas de config spécifique, mettre `{}`.

---

## 10. Règles de modélisation graphique (BPMNDiagram)

La section `<bpmndi:BPMNDiagram>` est **obligatoire**. Sans elle, le BPMN s'ouvre dans Camunda Modeler sans positionnement visuel.

### 10.1 Dimensions des pools (repères visuels)

| Pool | Largeur recommandée | Hauteur |
|------|--------------------:|--------:|
| XPortal | 2800–3000 px | 500–700 px |
| XFlow | 2800–3000 px | 500–700 px |

Les deux pools sont positionnés verticalement, XPortal en haut (y=80), XFlow en bas (y=800).

### 10.2 Dimensions des formes

| Élément | Largeur | Hauteur |
|---------|--------:|--------:|
| StartEvent / EndEvent | 36 | 36 |
| SendTask / receiveTask / userTask / serviceTask | 100 | 80 |
| Gateway | 50 | 50 |
| IntermediateCatchEvent | 36 | 36 |

### 10.3 MessageFlow DI

Chaque `messageFlow` déclaré dans la collaboration doit avoir son `BPMNEdge` dans le diagramme :

```xml
<bpmndi:BPMNEdge id="MF01_di" bpmnElement="MF01">
  <di:waypoint x="400" y="540" />
  <di:waypoint x="400" y="800" />
</bpmndi:BPMNEdge>
```

---

## 11. Checklist qualité d'un fichier BPMN

### Structure globale
- [ ] Namespace `camunda:` présent. Aucun `zeebe:`.
- [ ] `exporter="Camunda Modeler"` et `exporterVersion="5.42.0"`.
- [ ] `modeler:executionPlatformVersion="7.17.0"`.
- [ ] Tous les messages Kafka déclarés à la racine via `<bpmn:message>`.
- [ ] Section `<bpmn:collaboration>` avec les deux participants.
- [ ] Tous les `<bpmn:messageFlow>` référencent des éléments existants.

### Pools et processus
- [ ] **Les deux pools sont `isExecutable="true"`**.
- [ ] XFlow a `camunda:versionTag` et `camunda:historyTimeToLive`.
- [ ] Chaque processus a au moins un startEvent et un endEvent.
- [ ] Les `id` de tous les éléments sont uniques dans le fichier.

### Templates GNSPD
- [ ] Chaque tâche interactive a `camunda:modelerTemplate`.
- [ ] Les `camunda:type="external"` et `camunda:topic` correspondent au template.
- [ ] Tous les paramètres de tâche standards sont présents (`gnspdTaskIsVisible`, `gnspdTaskStatus`, etc.).
- [ ] Le startEvent XFlow embarque la configuration KMS des 4 environnements.

### Gateways et conditions
- [ ] Toutes les conditions sont en JavaScript (`language="javascript"` sans faute de frappe).
- [ ] Chaque gateway exclusive a une condition par sortie.
- [ ] Un chemin par défaut est prévu pour les cas imprévus (rejet ou erreur).
- [ ] Pas de deadlock possible (tous les chemins atteignent un endEvent).

### Boucle de correction
- [ ] La boucle correction est modélisée des deux côtés (XFlow et XPortal).
- [ ] La receiveTask "attendre resoumission" a sa receive task correspondante côté Portail.
- [ ] Le payload de correction inclut le motif.

### Graphique (BPMNDiagram)
- [ ] Section `<bpmndi:BPMNDiagram>` présente.
- [ ] Tous les éléments BPMN ont un `BPMNShape` ou `BPMNEdge` correspondant.
- [ ] Les `messageFlow` ont leurs `BPMNEdge`.

---

## 12. Anti-patterns constatés dans les fichiers du projet

### 12.1 Pools non exécutables (acte-etat-civil, certification-ONG)

**Problème** : `isExecutable` absent ou `false` sur l'un ou les deux pools.  
**Impact** : Camunda 7 refuse de déployer le processus.  
**Correction** : Ajouter `isExecutable="true"` sur les deux `<bpmn:process>`.

### 12.2 Nommage des messages non sémantique (expert-1)

**Problème** : `<bpmn:message name="Message_35c51dc" />` — le nom est l'ID généré automatiquement.  
**Impact** : Impossible à maintenir, corrélation aléatoire avec Kafka.  
**Correction** : Utiliser des noms fonctionnels comme `PAYMENT_CONFIRMATION`, `CORRECTION_REQUEST`.

### 12.3 Faute de frappe dans `language` (expert-1)

**Problème** : `language="javscript"` (sans le 'a').  
**Impact** : Camunda ignore la condition, le token peut se bloquer.  
**Correction** : Toujours `language="javascript"`.

### 12.4 Champ `numeroTable` absent du formulaire mais utilisé dans le BPMN (diplome-cfa)

**Problème** : Le BPMN référence `this.data.numeroTable` mais ce champ n'existe pas dans le JSON Form.io.  
**Impact** : La requête Odoo échoue systématiquement.  
**Règle générale** : Chaque variable `this.data.XXX` doit correspondre à un champ du formulaire ou à une sortie d'une tâche précédente.

### 12.5 Absence du chemin "Rejet" sur la gateway de décision (diplome-cfa)

**Problème** : Gateway avec seulement `APPROUVE` et `CORRECTION`, pas de `REJETE`.  
**Impact** : Token bloqué si l'agent choisit un rejet.  
**Règle** : Toute gateway de décision agent doit avoir au minimum 3 sorties : Approuvé, Correction, Rejeté.

### 12.6 Paiement non orchestré dans le BPMN (diplome-cfa)

**Problème** : Le montant est calculé dans le formulaire mais aucun échange de confirmation de paiement n'existe dans le BPMN.  
**Impact** : Des dossiers peuvent être soumis sans paiement réel.  
**Règle** : Tout service payant doit implémenter le cycle complet : autorisation → paiement citoyen → confirmation → réception XFlow.

### 12.7 Section BPMNDiagram incomplète (diplome-cfa, acte-etat-civil)

**Problème** : Seulement quelques `BPMNShape` positionnés sur la vingtaine d'éléments.  
**Impact** : Camunda Modeler affiche un diagramme vide et inutilisable.  
**Règle** : Chaque élément BPMN (shape ou flow) doit avoir ses coordonnées DI.

### 12.8 Boucle de correction infinie sans limite (diplome-cfa, expert-1)

**Problème** : La boucle correction → resoumission n'a pas de compteur de tentatives.  
**Impact** : Un dossier peut rester bloqué indéfiniment.  
**Correction recommandée** : Incrémenter une variable `nbCorrections` à chaque passage, ajouter un boundary timer event ou une condition de sortie après N itérations.
