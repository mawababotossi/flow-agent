# SERVICE REQUIREMENT SHEET (SRS)
## Demande d'Extrait d'Acte de Naissance
### Ministère de la Justice / DACS — République Togolaise

---

| Champ | Valeur |
|---|---|
| **Fournisseur de Services (FDS)** | Direction des Affaires Civiles et du Sceau (DACS) — Ministère de la Justice |
| **Service parent** | Ministère de la Justice |
| **Intégrateur en charge** | ATD — Agence Togo Digital |
| **Chef de projet ATD** | À renseigner |
| **Point focal FDS** | À renseigner |
| **Date de création** | 24 mars 2026 |
| **Date de dernière révision** | 24 mars 2026 (v1.0 — Version initiale) |
| **Date de validation** | _________________________________ |
| **Back-office utilisé** | XFlow (Camunda Platform 7 — GNSPD Framework) |
| **Déploiement cible** | XPortal + XFlow |

---

## Historique des changements

| Version | Date | Auteur | Description des modifications |
|---|---|---|---|
| 1.0 | 24/03/2026 | ATD | Version initiale |

---

## Table des matières

1. [Identification du service](#1-identification-du-service)
2. [Design du formulaire Form.io](#2-design-du-formulaire-formio)
3. [Le processus BPMN 2.0](#3-le-processus-bpmn-20)
4. [Règles métiers](#4-règles-métiers)
5. [Intégration avec des systèmes tiers](#5-intégration-avec-des-systèmes-tiers)
6. [Notifications automatiques](#6-notifications-automatiques)
7. [KPIs du service & engagements SLA](#7-kpis-du-service--engagements-sla)
8. [Interface e-service](#8-interface-e-service)
9. [Validations & signatures](#9-validations--signatures)

---

## 1. Identification du service

### 1.1. Description fonctionnelle

L'extrait d'acte de naissance est un document officiel délivré par l'officier d'état civil de la commune où la naissance a été enregistrée, sous la supervision de la Direction des Affaires Civiles et du Sceau (DACS) du Ministère de la Justice. Il constitue la preuve légale de l'état civil d'une personne et est requis dans de très nombreuses démarches administratives : inscription scolaire, demande de CNI ou de passeport, mariage civil, succession, accès aux droits sociaux, concours publics, demande de visa, etc. Il est délivré sous forme d'extrait avec filiation ou de copie intégrale, sur la base des registres de l'état civil tenus par chaque commune. Le service est gratuit pour la première délivrance. Le cadre légal est fixé par l'Ordonnance n°78-35 du 7 septembre 1978 portant Code de l'État Civil togolais, modifiée par décret d'application n°80-10 du 29 janvier 1980.

Dans le cadre du Plan d'Accélération de la Digitalisation (PAD) du Togo, ce service bascule vers un mode **hybride** : la soumission de la demande et le suivi du dossier se font entièrement en ligne via XPortal, tandis que le retrait de l'extrait physique signé reste obligatoire au guichet de la DACS — la signature manuscrite de l'officier d'état civil et le cachet humide étant légalement requis et non substituables par signature électronique à ce stade. Cette digitalisation élimine le premier déplacement (dépôt de dossier), supprime les rejets pour informations manquantes grâce à la validation temps réel du formulaire, et notifie automatiquement le citoyen à chaque étape de traitement, réduisant le délai moyen de traitement de 70%.

### 1.2. Fiche d'identité du service

| Champ | Valeur |
|---|---|
| **Code service** | SRV-DACS-2026-002 |
| **Nom complet** | Demande d'extrait d'acte de naissance (première délivrance et duplicata) |
| **Catégorie** | Justice — État Civil |
| **Bénéficiaires** | Toute personne physique (l'intéressé(e), un parent direct, un représentant légal mandaté) nécessitant un extrait d'acte de naissance |
| **Fréquence estimée** | ~30 000 demandes/an (national) — ~700/mois à Lomé |
| **Délai standard de traitement** | 3 jours ouvrables (TO-BE cible) |
| **Délai réglementaire maximum** | 5 jours ouvrables |
| **Coût du service** | Gratuit (première délivrance) — timbres fiscaux éventuels selon commune |
| **Langue(s)** | Français |
| **Canaux de dépôt** | XPortal (web / mobile) |
| **Canal de retrait** | Guichet physique DACS (obligation légale) |
| **Service hybride** | Oui — retrait physique obligatoire |

### 1.3. Acteurs et intervenants

| Acteur | Profil | Rôle dans le processus | Accès système | Responsabilité SLA |
|---|---|---|---|---|
| **Citoyen / Usager** | Toute personne physique (intéressé, parent, mandataire) | Soumet la demande en ligne, corrige si demandé, retire l'extrait au guichet | XPortal (portail citoyen) | Évaluateur du service |
| **Agent état civil DACS** | Agent administratif DACS habilité en état civil | Reçoit le dossier dans XFlow, consulte le registre, instruit et prépare l'extrait | XFlow (UserTask instruction) | 72h ouvrables max |
| **Chef de service DACS** | Responsable administratif DACS | Valide ou rejette la délivrance après instruction de l'agent | XFlow (UserTask validation) | 48h ouvrables max |
| **Agent de guichet DACS** | Agent affecté au guichet physique | Vérifie la pièce d'identité originale et le numéro de dossier, remet l'extrait signé | Guichet physique (hors système) | N/A |
| **Officier d'état civil** | Officier d'état civil ou délégué | Signe l'extrait et appose le cachet officiel | Guichet physique (hors système) | N/A |
| **Système XFlow** | Orchestrateur BPMN Camunda 7 | Routage automatique, notifications, escalades temporelles, gestion des états | Infrastructure ATD / DACS | Disponibilité 99,5% |
| **Admin XPortal (ATD)** | Technicien ATD | Surveillance, publication, KPIs | Administration XPortal | SLA plateforme |
| **Centre d'appel (N1)** | Agent support ATD | Assistance usagers en difficulté sur la démarche | Consultation statut uniquement | Résolution < 30 min |

---

## 2. Design du formulaire Form.io

### 2.1. Structure du formulaire

Le parcours est composé de **3 formulaires Form.io** distincts orchestrés par XFlow :

- **Formulaire principal (5 onglets)** : parcours commun à tous les usagers — soumission initiale.
- **Formulaire de correction (1 onglet, conditionnel)** : activé uniquement si l'agent demande une correction, entre l'étape d'instruction (B04) et la resoumission (B05). Slug : `formio-correction-demande-extrait-acte-naissance`.
- **Formulaire d'instruction agent (1 onglet)** : formulaire présenté à l'agent back-office XFlow pour instruire le dossier (UserTask B04). Slug : `formio-instruction-demande-extrait-acte-naissance`.
- **Formulaire de validation chef de service (1 onglet)** : formulaire présenté au chef de service pour valider ou rejeter (UserTask B07). Slug : `formio-validation-demande-extrait-acte-naissance`.

#### Formulaire principal — 5 onglets wizard

| Onglet | Clé (`key`) | Titre | Remarques |
|---|---|---|---|
| Onglet 1 | `stepIntro` | Présentation du service | Landing page premium : objet, pièces requises, étapes, délai, conditions |
| Onglet 2 | `stepIdentite` | Identité du demandeur | Champs e-ID pré-remplis et verrouillés + lien de parenté |
| Onglet 3 | `stepNaissance` | Informations sur la naissance | Date, lieu, type d'extrait demandé |
| Onglet 4 | `stepPieces` | Pièces justificatives | Upload pièce d'identité (+ procuration si mandataire) |
| Onglet 5 | `stepRecapitulatif` | Récapitulatif et soumission | Résumé non modifiable + certification sur l'honneur + CAPTCHA |

#### Formulaire de correction — Conditionnel (si correction demandée par l'agent)

Ce formulaire est un composant Form.io indépendant (slug : `formio-correction-demande-extrait-acte-naissance`), déclenché par XFlow via une SendTask après l'étape d'instruction (B04), uniquement lorsque `décision == "correction"`. Il s'affiche dans XPortal comme une tâche utilisateur intercalée.

| Formulaire | Titre | Condition de déclenchement |
|---|---|---|
| Correction | Corriger ma demande | `décision == "correction"` uniquement — déclenché par XFlow (étape B04) |

### 2.2. Détail des champs

#### Onglet 1 — Présentation du service (`stepIntro`)

Panel de type landing page premium (grille Bootstrap 8/4). Aucun champ de saisie. Contient des composants `htmlelement` richement formatés :
- **Info Pills** : avantages du service (En ligne, Gratuit, 3 jours)
- **Sidebar** : coordonnées DACS, horaires d'ouverture du guichet
- **Guide pas à pas** numéroté : Remplir → Soumettre → Attendre notification → Retirer au guichet
- **Liste des pièces requises**
- **Conditions d'éligibilité**

#### Onglet 2 — Identité du demandeur (`stepIdentite`)

Cet onglet collecte les informations du demandeur. Les champs identité sont pré-remplis depuis le profil e-ID et verrouillés dynamiquement.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `nom` | Nom de famille | `textfield` | Oui | Texte, max 100 car. | Profil Citoyen (`config.users.lastName`) | Verrouillage dynamique `logic` si non vide |
| `prenom` | Prénom(s) | `textfield` | Oui | Texte, max 100 car. | Profil Citoyen (`config.users.firstName`) | Verrouillage dynamique `logic` si non vide |
| `email` | Adresse e-mail | `email` | Oui | Format email valide | Profil Citoyen (`config.users.email`) | Verrouillage dynamique |
| `telephone` | Numéro de téléphone | `phoneNumber` | Oui | Format `228 XX XX XX XX` | Profil Citoyen (`config.users.phone`) | `inputMask: "228 99 99 99 99"`, verrouillage dynamique |
| `typePiece` | Type de pièce d'identité du demandeur | `select` | Oui | CNI / Passeport / Titre de séjour | `dataSrc: "values"` | Valeurs statiques |
| `numeroPiece` | Numéro de la pièce d'identité | `textfield` | Oui | Alphanumérique, 6–20 car. | Saisie citoyen | `validateOn: "blur"`, message custom |
| `lienParente` | Lien de parenté avec l'intéressé(e) | `select` | Oui | Moi-même / Père ou mère / Représentant légal mandaté | `dataSrc: "values"` | Conditionne l'affichage du champ procuration — RG-004 |
| `nomIntéressé` | Nom complet de l'intéressé(e) | `textfield` | Conditionnel | Texte, max 200 car. | Saisie citoyen | `customConditional: "show = (data.lienParente !== 'Moi-même');"` — RG-004 |

#### Onglet 3 — Informations sur la naissance (`stepNaissance`)

Cet onglet collecte les informations permettant à l'agent de localiser l'acte dans le registre.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `dateNaissanceInteresse` | Date de naissance de l'intéressé(e) | `datetime` | Oui | Format JJ/MM/AAAA, antérieure à J | Saisie citoyen | `enableMaxDateInput: true` avec date du jour |
| `communeNaissance` | Commune de naissance | `textfield` | Oui | Texte, max 150 car. | Saisie citoyen | Préciser la commune exacte (pas la préfecture) |
| `prefectureNaissance` | Préfecture / Région | `select` | Oui | Liste des préfectures du Togo | API (`config.apiBaseUrl/references/prefectures`) | `dataSrc: "url"` |
| `paysNaissance` | Pays de naissance | `select` | Oui | Liste des pays | API (`config.apiBaseUrl/references/pays`) | `dataSrc: "url"`, défaut : Togo |
| `numeroActe` | Numéro de l'acte (si connu) | `textfield` | Non | Numérique ou alphanumérique | Saisie citoyen | Facultatif — accélère la recherche |
| `typeExtrait` | Type d'extrait demandé | `radio` | Oui | Extrait avec filiation / Copie intégrale | `dataSrc: "values"` | — |
| `objetDemande` | Objet de la demande | `select` | Oui | Inscription scolaire / CNI/Passeport / Mariage / Visa / Succession / Autre | `dataSrc: "values"` | Valeurs statiques |
| `objetAutre` | Précisez l'objet | `textarea` | Non | Texte libre, max 300 car. | Saisie citoyen | `customConditional: "show = (data.objetDemande === 'Autre');"` |

#### Onglet 4 — Pièces justificatives (`stepPieces`)

Les fichiers sont uploadés directement dans XPortal et transmis à XFlow. Formats acceptés : PDF, JPG, PNG.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `pieceIdentite` | Copie de la pièce d'identité du demandeur | `file` | Oui | PDF/JPG/PNG — max 2 Mo | Upload citoyen | `storage: "base64"`, `multiple: false` — RG-009 |
| `procuration` | Procuration notariée (si mandataire) | `file` | Conditionnel | PDF — max 2 Mo | Upload citoyen | `customConditional: "show = (data.lienParente === 'Représentant légal mandaté');"` — RG-004 |

#### Formulaire de correction — Détail des champs

Formulaire pré-rempli avec les données de la soumission initiale. Le motif de correction (fourni par l'agent) est affiché en lecture seule. Le citoyen corrige uniquement les champs signalés.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `motifCorrection` | Motif de la correction | `htmlelement` | N/A | Texte fourni par l'agent | XFlow (lecture seule) | Affiché en bandeau d'alerte |
| `dateNaissanceInteresse` | Date de naissance corrigée | `datetime` | Oui | Format JJ/MM/AAAA | Saisie citoyen | Pré-rempli avec la valeur précédente |
| `communeNaissance` | Commune de naissance corrigée | `textfield` | Oui | Texte, max 150 car. | Saisie citoyen | Pré-rempli |
| `prefectureNaissance` | Préfecture / Région | `select` | Oui | Liste des préfectures | API | Pré-rempli |
| `numeroActe` | Numéro de l'acte (si connu) | `textfield` | Non | Alphanumérique | Saisie citoyen | Pré-rempli |
| `pieceIdentite` | Copie de la pièce d'identité | `file` | Non | PDF/JPG/PNG — max 2 Mo | Upload citoyen | Pré-rempli — remplacement optionnel |

**Propriétés techniques :**

| Propriété technique | Valeur |
|---|---|
| **Slug du formulaire** | `formio-correction-demande-extrait-acte-naissance` |
| **Version** | 1 (`locked = true`, `status = Active`) |
| **Déclencheur processus** | SendTask XFlow — étape B04 (message : `MSG_ACTENAISSANCE_RETURN` avec `action == "correction"`) |
| **Condition d'affichage** | `action == "correction"` — formulaire invisible sinon |
| **Action post-traitement** | ReceiveTask XFlow — étape B05 attend la resoumission avant de continuer |

#### Onglet 5 — Récapitulatif et soumission (`stepRecapitulatif`)

L'onglet 5 affiche un résumé de toutes les données saisies via le script d'analyse natif ATD. L'usager coche une case de confirmation. P-Studio gère nativement le bouton « Soumettre » sur le dernier panel du wizard.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `htmlRecapitulatifFinal` | N/A | `htmlelement` | N/A | Script Parseur Formulaire | Système | Injection du composant `recap_form.json` |
| `luEtApprouve` | Je déclare et certifie sur l'honneur que les informations fournies sont exactes et complètes, et reconnais que toute fausse déclaration m'expose à des poursuites | `checkbox` | Oui | Doit être coché | Saisie citoyen | Ignoré par le récap via `excludeKeys` |

### 2.3. Actions du formulaire (P-Studio)

| Code Action P-Studio | Condition d'activation | Configuration algorithmique |
|---|---|---|
| **Calculate Costs** | Non applicable (service gratuit) | N/A |
| **Publish to RabbitMQ** | Toujours actif | Routing Key: `submissions.topic` — Queue: `workflows-engine.main.queue` |

### 2.4. Configuration des environnements

Le formulaire Form.io contient un bloc `config` à la racine du JSON, déclinant les paramètres par environnement. Cette configuration est également portée par les **startEvent des deux pools BPMN** (XPortal et XFlow).

#### Environnements déclarés

| Environnement | `apiBaseUrl` | `appName` |
|---|---|---|
| `development` | `https://api.dev.gouv.tg/api/v1/admin` | Développement |
| `sandbox` | `https://api.sandbox.gouv.tg/api/v1/admin` | Sandbox |
| `preproduction` | `https://api.preprod.gouv.tg/api/v1/admin` | Pré-production |
| `production` | `https://api.gouv.tg/api/v1/admin` | Production |

> **Note** : Ce service ne nécessite pas de configuration KMS spécifique (pas d'intégration Odoo ni d'API tierce avec secrets). La configuration XFlow peut rester vide `{}` pour les 4 environnements.

#### Mapping utilisateur (`config.users`)

| Clé | Valeur | Description |
|---|---|---|
| `firstName` | `user.firstName` | Prénom de l'usager connecté |
| `lastName` | `user.lastName` | Nom de l'usager connecté |
| `fullName` | `user.fullName` | Nom complet |
| `email` | `user.email` | Adresse e-mail |
| `username` | `user.username` | Identifiant |
| `userId` | `user.userId` | ID unique |
| `accountType` | `user.accountType` | Type de compte |
| `language` | `user.language` | Langue préférée |
| `phone` | `user.phone` | Numéro de téléphone |

### 2.5. Inventaire des formulaires userTask

| # | Fichier JSON | Lane | userTask BPMN | Description | Condition |
|---|---|---|---|---|---|
| 1 | `formio-demande-extrait-acte-naissance.json` | PORTAL | Soumission initiale (StartEvent) | Formulaire principal — 5 onglets wizard | Toujours |
| 2 | `formio-correction-demande-extrait-acte-naissance.json` | PORTAL | `Task_P_Correction` | Formulaire de correction après demande de l'agent | Si boucle de correction |
| 3 | `formio-instruction-demande-extrait-acte-naissance.json` | XFLOW | `Activity_X_Instruction` | Formulaire d'instruction agent — décision + motif | Toujours |
| 4 | `formio-validation-demande-extrait-acte-naissance.json` | XFLOW | `Activity_X_Validation` | Formulaire de validation chef de service | Toujours |

---

## 3. Le processus BPMN 2.0

### 3.1. Vue d'ensemble du processus TO-BE

| Champ | Valeur |
|---|---|
| **Nom du processus** | `Procédure_DemandeExtraitActeNaissance_v1` |
| **Événement déclencheur** | Soumission du formulaire par l'usager sur XPortal |
| **Événement de fin (succès)** | Citoyen notifié que l'extrait est prêt — retrait physique au guichet DACS |
| **Événement de fin (rejet)** | Notification de rejet définitif motivé à l'usager |
| **Moteur d'exécution** | XFlow (Camunda Platform 7 — GNSPD Framework) |
| **Version processus** | 1.0 |
| **Participants BPMN** | Pool XPORTAL (`isExecutable="true"`) + Pool XFLOW (`isExecutable="false"`) — deux pools communiquant via Kafka (topic `bpmn.commands`) |

### 3.2. Étapes détaillées du processus

#### Lane PORTAL — Côté Citoyen

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| 01 | Soumettre la demande | StartEvent XPortal. Le citoyen remplit et soumet le formulaire wizard 5 onglets. Le formulaire est publié vers RabbitMQ. | Citoyen | Immédiat | → 02 |
| 02 | Soumettre le dossier vers XFlow | SendTask `tg.gouv.gnspd.sendMessage` : envoi du message `MSG_ACTENAISSANCE_START` (payload : `$this.data.Event_P_Start.parameters`) vers XFlow via Kafka destination `peer-xflow-local-sp`. `gnspdTargetElementType: bpmn:StartEvent`. | Système | Immédiat | → 03 |
| 03 | Attendre la décision XFlow | ReceiveTask multi-entrante (convergence) : attend le message `MSG_ACTENAISSANCE_RETURN` de XFlow. Reçoit les décisions : `correction`, `accepte`, `rejete`. Entrées : flux initial (02) + flux resoumission (05). | Système | Variable | → Gateway 04 |
| 04 | Gateway — Action XFlow ? | ExclusiveGateway de divergence. Lit `this.data.Recv_P_Return.result.data.action`. | Système | Immédiat | `"correction"` → 05a / `"accepte"` → FIN Accepté / `"rejete"` → FIN Rejeté |
| 05a | Corriger le dossier | UserTask `tg.gouv.gnspd.userTask` avec `gnspdHandlerType="publish_submission"` et `gnspdSubmissionData` conditionnel (fallback sur saisie initiale). `gnspdTaskStatus: PendingPortal`. Formulaire de correction pré-rempli avec le motif fourni par l'agent. `camunda:taskListener event="create"`. | Citoyen | ≤ 15 jours | → 05b |
| 05b | Resoummettre la correction vers XFlow | SendTask : envoi du message `MSG_ACTENAISSANCE_RESUB` (payload : `$this.data.Task_P_Correction.result`) vers XFlow via `peer-xflow-local-sp`. `gnspdTargetElementType: bpmn:ReceiveTask`. | Système | Immédiat | → 03 (retour boucle) |
| FIN-OK | Demande acceptée | EndEvent — le dossier a été accepté. Le citoyen est notifié séparément par email/SMS pour le retrait physique. | Système | — | FIN (succès) |
| FIN-KO | Demande rejetée | EndEvent — le dossier a été rejeté définitivement. | Système | — | FIN (rejet) |

#### Lane XFLOW — Côté Back-office

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| B01 | Réception du dossier | StartEvent message `MSG_ACTENAISSANCE_START`. Initialise le compteur de corrections : `this.data.nbCorrections = 0` (executionListener sur le flux sortant). | Système | Immédiat | → B02 |
| B02 | Status : Soumis | ServiceTask `tg.gouv.gnspd.stepNotification` : `gnspdStatus="Submited"`, `gnspdStepOrder=1`. Enregistre le démarrage du processus dans l'historique du dossier. | Système | Immédiat | → B03 |
| B03 | Notifier accusé de réception | ServiceTask `tg.gouv.gnspd.sendNotification` : email + SMS au citoyen (N01 — réf. dossier, délai traitement 3 jours). | Système | Immédiat | → B04 |
| B04 | Status : En instruction | ServiceTask `tg.gouv.gnspd.stepNotification` : `gnspdStatus="PendingBackOffice"`, `gnspdStepOrder=2`. Mise à jour du statut visible sur le portail. Entrées : flux initial (B03) + flux retour correction (compteur). | Système | Immédiat | → B05 |
| B05 | Instruire le dossier | UserTask agent `tg.gouv.gnspd.userTask` avec `gnspdHandlerType="publish_submission"`, `gnspdSubmissionFormkey="casier-judiciaire-instruction"`, `gnspdSubmissionData=$this.data.Event_X_Start.parameters.submissionData.data`, `gnspdTaskStatus="PendingBackOffice"`. L'agent consulte le registre et rend sa décision : trouvé/correction/introuvable. **Timer d'escalade non-interruptif 72h** : notification automatique au chef de service si dépassement. | Agent état civil DACS | ≤ 72h | → Gateway B06 |
| B06 | Gateway — Décision instruction ? | ExclusiveGateway. Lit `this.data.Activity_X_Instruction.result.submissionData.decision`. | Système | Immédiat | `"approve"` → B07 / `"correction"` → B09 / `"reject"` → B10 |
| B07 | Validation Chef de Service | UserTask chef `tg.gouv.gnspd.userTask` avec `gnspdHandlerType="publish_submission"`, `gnspdSubmissionFormkey="casier-judiciaire-validation"`, `gnspdSubmissionData=$this.data.Event_X_Start.parameters.submissionData.data`, `gnspdTaskStatus="PendingBackOffice"`. Le chef valide ou rejette la délivrance. | Chef de service DACS | ≤ 48h | → Gateway B08 |
| B08 | Gateway — Validation Chef OK ? | ExclusiveGateway. Lit `this.data.Activity_X_Validation.result.submissionData.decision`. | Système | Immédiat | `"oui"` → B11 / `"non"` → B10 |
| B09 | Notifier correction | ServiceTask `tg.gouv.gnspd.sendNotification` : email + SMS citoyen (N03 — motif de correction). Définit `action_portal = "correction"`. | Système | Immédiat | → B12 (Send Return) |
| B10 | Notifier rejet | ServiceTask `tg.gouv.gnspd.sendNotification` : email + SMS citoyen (N04 — motif de rejet). Définit `action_portal = "rejete"`. Entrées : rejet agent (B06) + rejet chef (B08) + nb_corrections maximal (B14). | Système | Immédiat | → B12 (Send Return) |
| B11 | Status : Succès | ServiceTask `tg.gouv.gnspd.stepNotification` : `gnspdStatus="Success"`, `gnspdStepOrder=3`. | Système | Immédiat | → Notif Ready → B12 |
| B11a | Notifier prêt pour retrait | ServiceTask `tg.gouv.gnspd.sendNotification` : email + SMS citoyen (N05 — document prêt, instructions retrait guichet). Définit `action_portal = "accepte"`. | Système | Immédiat | → B12 |
| B12 | Envoyer décision vers XPortal | SendTask `tg.gouv.gnspd.sendMessage` : envoi `MSG_ACTENAISSANCE_RETURN` (payload : `${action, reference, motif}`) vers XPortal via `ch-portail-local-sp`. `gnspdTargetElementType: bpmn:ReceiveTask`. Convergence des 3 chemins (accepte / correction / rejete). | Système | Immédiat | → Gateway B13 |
| B13 | Gateway — Fin ? | ExclusiveGateway. Lit `this.data.action_portal`. | Système | Immédiat | `"accepte"` → FIN Succès / `"rejete"` → FIN Rejet / `"correction"` → B14 |
| B14 | Attendre resoumission | ReceiveTask `MSG_ACTENAISSANCE_RESUB`. Attend la correction du citoyen. | Système | ≤ 15 jours | → B15 |
| B15 | Incrémenter compteur corrections | Incrémentation `nbCorrections += 1` via executionListener sur le flux B14→B16. | Système | Immédiat | → B16 |
| B16 | Gateway — Tentatives ? | ExclusiveGateway. Lit `this.data.nbCorrections`. | Système | Immédiat | `< 3` → B04 (retour instruction) / `>= 3` → B10 (rejet max) |
| FIN-OK | Succès | EndEvent — processus terminé avec succès. | — | — | — |
| FIN-KO | Rejet | EndEvent — processus terminé par rejet. | — | — | — |
| FIN-ESC | Escalade terminée | EndEvent — timer d'escalade 72h exécuté (branche non-interruptive). | — | — | — |

### 3.3. Matrice des échanges inter-pools (Kafka)

Tous les échanges asynchrones entre les deux pools sont listés ci-dessous.

#### XPortal → XFlow

| # | Message Kafka (`messageRef`) | Émetteur (SendTask) | Récepteur | Payload | Condition |
|---|---|---|---|---|---|
| 1 | `MSG_ACTENAISSANCE_START` | `Send_P_Start` | StartEvent XFlow (`Event_X_Start`) | `$this.data.Event_P_Start.parameters` | Toujours |
| 2 | `MSG_ACTENAISSANCE_RESUB` | `Send_P_Resub` | ReceiveTask XFlow (`Recv_X_Resub`) | `$this.data.Task_P_Correction.result` | Si correction |

#### XFlow → XPortal

| # | Message Kafka (`messageRef`) | Émetteur (SendTask) | Récepteur | Payload | Condition |
|---|---|---|---|---|---|
| 1 | `MSG_ACTENAISSANCE_RETURN` | `Send_X_Return` | ReceiveTask XPortal (`Recv_P_Return`) | `${action, reference, motif}` | Toujours (accepte / correction / rejete) |

#### Points de convergence (Pattern P2)

| ReceiveTask (convergence) | Pool | Entrées | Description |
|---|---|---|---|
| `Recv_P_Return` | PORTAL | Flux initial (Send_P_Start) + Flux resoumission (Send_P_Resub) | Point d'attente unique avant la gateway de décision XPortal |
| `Send_X_Return` | XFLOW | Flux accepté (B11a) + Flux correction (B09) + Flux rejet (B10) | Noeud de rejet/décision unique (DRY) avant le sendTask vers XPortal |
| `Step_X_Pending` (B04) | XFLOW | Flux initial (B03) + Flux retour correction (B16) | Remise en instruction après chaque correction reçue |

#### Terminaisons du processus

| EndEvent | Pool | Condition | Notification associée |
|---|---|---|---|
| `End_P_Accepte` | PORTAL | `action == "accepte"` | N05 — Document prêt pour retrait |
| `End_P_Rejete` | PORTAL | `action == "rejete"` | N04 — Rejet définitif |
| `End_X_Success` | XFLOW | `action_portal == "accepte"` | — |
| `End_X_Reject` | XFLOW | `action_portal == "rejete"` | — |
| `End_X_Escalade` | XFLOW | Timer 72h expiré (non-interruptif) | N07 — Escalade chef de service |

### 3.4. Flux d'escalade temporelle

| Déclencheur | Canal | Action |
|---|---|---|
| Délai instruction agent > 72h (BoundaryEvent non-interruptif sur B05) | Email + Dashboard XFlow | Notification automatique au chef de service (N07) |
| Délai correction citoyen > 15 jours (timer côté portail) | SMS + Email | Clôture automatique — rejet avec statut *Délai dépassé* |
| Nb corrections > 3 (Gateway B16) | SMS + Email | Rejet automatique avec motif *Nombre maximal de corrections atteint* |
| Indisponibilité XFlow > 15 min | Email Admin | Alerte automatique à l'Admin ATD |

---

## 4. Règles métiers

| ID | Règle métier | Description / Condition | Priorité | Étapes concernées |
|---|---|---|---|---|
| RG-001 | Authentification obligatoire | SI l'usager n'est pas connecté à XPortal ALORS la soumission est bloquée. Le formulaire n'est accessible qu'après authentification e-ID. | HAUTE | Onglet 1 |
| RG-002 | Verrouillage e-ID | SI les champs `nom`, `prenom`, `email`, `telephone` sont présents dans le profil e-ID ALORS ils sont pré-remplis et verrouillés dynamiquement (bloc `logic` type `Disabled`). L'usager ne peut pas les modifier manuellement. | HAUTE | Onglet 2 |
| RG-003 | Éligibilité mandataire | SI `lienParente == "Représentant légal mandaté"` ALORS le champ `nomIntéressé` est obligatoire ET le champ `procuration` (pièce jointe) devient obligatoire. Blocage sans ces éléments. | HAUTE | Onglet 2 et 4 |
| RG-004 | Conformité des pièces jointes | SI un fichier est uploadé ALORS son format doit être PDF/JPG/PNG ET sa taille < 2 Mo. Tout fichier non conforme est rejeté avec message explicite : *« Format non accepté ou fichier trop volumineux (max 2 Mo) »*. | MOYENNE | Onglet 4 |
| RG-005 | Date de naissance cohérente | SI `dateNaissanceInteresse` est postérieure à la date du jour ALORS blocage avec message : *« La date de naissance ne peut pas être dans le futur »*. | HAUTE | Onglet 3 |
| RG-006 | Une demande active par usager | SI une demande pour le même intéressé est déjà en cours de traitement ALORS la nouvelle soumission est bloquée avec message : *« Une demande est déjà en cours pour cet acte. Suivez l'état de votre dossier sur votre espace personnel »*. | HAUTE | Onglet 1 / Étape B01 |
| RG-007 | Boucle de correction limitée | SI `nbCorrections >= 3` ALORS la demande est clôturée automatiquement avec statut *Rejeté — nombre maximal de corrections atteint*. Le citoyen peut soumettre une nouvelle demande. | HAUTE | Étapes B15, B16 |
| RG-008 | Délai de resoumission correction | SI le citoyen ne resoumit pas sa correction dans les 15 jours calendaires ALORS la demande est clôturée automatiquement avec statut *Rejeté — délai dépassé*. | HAUTE | Étape 05a PORTAL |
| RG-009 | Acte introuvable — orientation TGI | SI l'agent sélectionne `decision == "reject"` avec motif *Acte introuvable* ALORS le citoyen est notifié et orienté vers la procédure de jugement supplétif au TGI. Ce cas est hors périmètre du service digital. | HAUTE | Étape B06 |
| RG-010 | Certification sur l'honneur | SI la checkbox `luEtApprouve` n'est pas cochée ALORS le bouton Soumettre reste désactivé. Tout fausse déclaration expose le citoyen à des poursuites pénales. | HAUTE | Onglet 5 |
| RG-011 | Archivage 10 ans | Tous les dossiers (acceptés et rejetés) doivent être archivés pendant 10 ans minimum conformément aux obligations légales togolaises en matière d'état civil. | HAUTE | Post-décision |
| RG-012 | Escalade automatique agent | SI l'agent ne traite pas le dossier dans les 72h ALORS une notification d'escalade est envoyée automatiquement au chef de service (BoundaryEvent non-interruptif). | HAUTE | Étape B05 |

---

## 5. Intégration avec des systèmes tiers

Les intégrations suivantes sont envisagées. Elles nécessitent la signature de conventions d'échange de données entre les structures concernées.

| Système cible | Type d'intégration | Données échangées | Condition d'appel | Statut |
|---|---|---|---|---|
| Plateforme SMS (ATD) | API REST (envoi) | Numéro téléphone, texte message, réf. dossier | À chaque changement de statut (N01–N07) | Disponible |
| Service e-mail (ATD) | API interne | Adresse email, contenu HTML, réf. dossier | À chaque changement de statut | Disponible |
| Système archivage ATD | API interne | Dossier complet (formulaire + pièces + décision) | Post-décision — Archivage automatique | Disponible |
| Registre national état civil (RNEEC) | API REST (lecture) — *futur* | Données de l'acte de naissance | Optionnel — vérification automatique si registre numérisé | À développer |
| Système identité numérique e-ID | API REST (lecture) | Nom, prénom, date de naissance, email, téléphone | Pré-remplissage formulaire à chaque connexion | Disponible |

> **Note** : L'intégration avec un registre national électronique de l'état civil (RNEEC) n'existe pas à ce jour au Togo. Lorsqu'elle sera disponible, la vérification automatique de l'acte pourra être ajoutée en ServiceTask avant l'instruction agent (étape B05), conformément au Pattern P5 (vérification système avant instruction agent).

---

## 6. Notifications automatiques

| Réf. | Déclencheur | Canal | Destinataire | Message type |
|---|---|---|---|---|
| N01 | Soumission formulaire (Étape B02) | SMS + Email | Citoyen | *Votre demande d'extrait d'acte de naissance (réf. [DOSSIER]) a bien été reçue. Délai de traitement estimé : 3 jours ouvrables. Suivez l'état de votre dossier sur XPortal.* |
| N02 | Démarrage instruction (Étape B04) | — | — | (Mise à jour silencieuse du statut portail vers PendingBackOffice — pas de notification séparée) |
| N03 | Correction demandée par l'agent (Étape B09) | SMS + Email | Citoyen | *Votre dossier (réf. [DOSSIER]) nécessite des corrections. Motif : [MOTIF_CORRECTION]. Connectez-vous à XPortal pour corriger et resoumttre votre demande. Délai : 15 jours.* |
| N04 | Rejet définitif (Étape B10) | SMS + Email | Citoyen | *Votre demande d'extrait d'acte de naissance (réf. [DOSSIER]) a été rejetée. Motif : [MOTIF_REJET]. Vous pouvez soumettre une nouvelle demande. En cas d'acte introuvable, contactez le TGI de Lomé pour une procédure de jugement supplétif.* |
| N05 | Acceptation — document prêt (Étape B11a) | SMS + Email | Citoyen | *Votre demande (réf. [DOSSIER]) a été acceptée. Votre extrait d'acte de naissance est prêt. Présentez-vous au guichet DACS (adresse : [ADRESSE_DACS]) muni de votre pièce d'identité originale et de votre numéro de dossier. Horaires : [HORAIRES].* |
| N06 | Invitation évaluation (J+1 après décision) | SMS + Email | Citoyen | *Êtes-vous satisfait(e) de votre expérience avec le service de demande d'extrait d'acte de naissance ? Donnez votre avis en 30 secondes sur XPortal.* |
| N07 | Escalade — SLA agent dépassé (Timer 72h) | Email + Dashboard | Chef de service DACS | *Escalade automatique : Le dossier [DOSSIER] n'a pas été traité dans les 72h. Intervention requise.* |

---

## 7. KPIs du service & engagements SLA

| Indicateur | Valeur cible | Mesure |
|---|---|---|
| **Délai moyen de traitement** | ≤ 3 jours ouvrables | Temps entre soumission et décision finale |
| **Délai maximum réglementaire** | 5 jours ouvrables | Délai légal à ne pas dépasser |
| **Taux de dossiers complets à la 1ère soumission** | ≥ 70% | Nb dossiers sans correction / total soumissions |
| **Taux de dossiers traités sous SLA** | ≥ 90% | Nb dossiers dans les délais / total |
| **Délai de notification après décision** | < 5 minutes | Automatique (XFlow service task) |
| **Disponibilité plateforme XPortal** | ≥ 99,5% | Monitoring ATD |
| **Taux de satisfaction usager** | ≥ 85% | Enquête NPS post-décision (N06) |
| **Taux d'adoption canal numérique** | ≥ 60% an 1 → ≥ 85% an 3 | Nb demandes en ligne / total |
| **Taux de renvoi vers TGI (acte introuvable)** | ≤ 8% | Nb rejets motif introuvable / total |

---

## 8. Interface e-service

Aucune interface e-service dédiée n'est prévue. Le service est accessible exclusivement via XPortal (portail national des services publics). Le back-office est géré via XFlow (Camunda Platform 7).

---

## 9. Validations & signatures

| Rôle | Nom | Signature | Date |
|---|---|---|---|
| **Rédigé par** (Intégrateur ATD) | À renseigner | _________________ | _________________ |
| **Validé par** (Point focal DACS) | À renseigner | _________________ | _________________ |
| **Approuvé par** (Chef de projet ATD) | À renseigner | _________________ | _________________ |
