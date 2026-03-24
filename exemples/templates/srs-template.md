# SERVICE REQUIREMENT SHEET (SRS)
## [NOM DU SERVICE]
### [Organisation / Entité — Pays]

> **INSTRUCTIONS POUR L'IA :**
> Ce fichier est un template SRS structuré. Pour générer un SRS complet, remplace chaque balise `[...]` par les informations du service concerné. Les sections marquées `<!-- IA: ... -->` contiennent des directives contextuelles à suivre. Supprime toutes les directives et commentaires `<!-- ... -->` dans le document final produit.
>
> **Niveaux de priorité des règles métiers :** HAUTE / MOYENNE / BASSE
> **Statuts d'intégration possibles :** Disponible / À configurer / À développer / Déprécié
> **Types de champs Form.io :** Texte, Date, Téléphone, Email, Radio, Checkbox, Select, Fichier, HTML, reCAPTCHA
> **Niveau PREMIUM :** Pour atteindre l'excellence ATD, suivez scrupuleusement les instructions `<!-- IA Premium: ... -->` qui exigent un haut niveau de détail technique et visuel.

---

| Champ | Valeur |
|---|---|
| **Fournisseur de Services (FDS)** | [Nom de l'organisation fournissant le service] |
| **Service parent** | [Direction ou ministère de rattachement] |
| **Intégrateur en charge** | [Nom de la société intégratrice] |
| **Chef de projet ATD** | [Nom du chef de projet] |
| **Point focal FDS** | [Nom du responsable côté FDS] |
| **Date de création** | [JJ mois AAAA] |
| **Date de dernière révision** | [JJ mois AAAA] (v[X.Y] — [description courte de la révision]) |
| **Date de validation** | _________________________________ |
| **Back-office utilisé** | [Ex : Odoo Traitement (ATD — par défaut)] |
| **Déploiement cible** | [Ex : Xportal + Xflow + Interface e-service [FDS]] |

---

## Historique des changements

<!-- IA: Ajoute une ligne par version. La v1.0 correspond à la version initiale. Incrémente le mineur (1.1, 1.2…) pour les ajouts/corrections sans changement structurel majeur, le majeur (2.0…) pour les refonte. -->

| Version | Date | Auteur | Description des modifications |
|---|---|---|---|
| 1.0 | [JJ/MM/AAAA] | [Équipe / Auteur] | Version initiale |
| 1.1 | [JJ/MM/AAAA] | [Équipe / Auteur] | [Description des modifications] |

---

## Table des matières

1. [Identification du service](#1-identification-du-service)
   - 1.1. [Description fonctionnelle](#11-description-fonctionnelle)
   - 1.2. [Fiche d'identité du service](#12-fiche-didentité-du-service)
   - 1.3. [Acteurs et intervenants](#13-acteurs-et-intervenants)
2. [Design du formulaire Form.io](#2-design-du-formulaire-formio)
   - 2.1. [Structure du formulaire](#21-structure-du-formulaire)
   - 2.2. [Détail des champs](#22-détail-des-champs)
   - 2.3. [Actions du formulaire (P-Studio)](#23-actions-du-formulaire-p-studio)
   - 2.4. [Configuration des environnements](#24-configuration-des-environnements)
   - 2.5. [Inventaire des formulaires userTask](#25-inventaire-des-formulaires-usertask)
3. [Le processus BPMN 2.0](#3-le-processus-bpmn-20)
   - 3.1. [Vue d'ensemble du processus TO-BE](#31-vue-densemble-du-processus-to-be)
   - 3.2. [Étapes détaillées du processus](#32-étapes-détaillées-du-processus)
   - 3.3. [Matrice des échanges inter-pools (Kafka)](#33-matrice-des-échanges-inter-pools-kafka)
   - 3.4. [Flux d'escalade temporelle](#34-flux-descalade-temporelle)
4. [Règles métiers](#4-règles-métiers)
5. [Intégration avec des systèmes tiers](#5-intégration-avec-des-systèmes-tiers)
6. [Notifications automatiques](#6-notifications-automatiques)
7. [KPIs du service & engagements SLA](#7-kpis-du-service--engagements-sla)
8. [Interface e-service [FDS]](#8-interface-e-service-fds)
9. [Validations & signatures](#9-validations--signatures)

---

## 1. Identification du service

### 1.1. Description fonctionnelle

<!-- IA: Rédige 2 paragraphes. Le premier décrit le service dans son contexte institutionnel (nature du titre/document délivré, valeur légale, à qui il est destiné, pourquoi il est nécessaire). Le second décrit ce que la digitalisation apporte concrètement à l'usager (soumettre en ligne, suivre, recevoir notification, parcours spécifique éventuel). -->

[Description du service dans son contexte institutionnel et légal.]

[Apport de la digitalisation pour l'usager : soumission en ligne, suivi en temps réel, notifications, parcours spécifiques éventuels.]

### 1.2. Fiche d'identité du service

<!-- IA: Le code service suit le pattern SRV-[SIGLE_FDS]-[ANNÉE]-[NNN]. -->

| Champ | Valeur |
|---|---|
| **Code service** | SRV-[SIGLE]-[AAAA]-[NNN] |
| **Nom complet** | [Intitulé complet et officiel du service] |
| **Catégorie** | [Ex : Formation Professionnelle / Certification] |
| **Bénéficiaires** | [Profil des usagers cibles] |
| **Fréquence estimée** | [À renseigner par le FDS — estimation sessions annuelles] |
| **Délai standard de traitement** | [À renseigner par le FDS — délai cible en jours ouvrés] |
| **Délai réglementaire maximum** | [À renseigner par le FDS] |
| **Coût du service** | [Gratuit / Payant — préciser montant ou conditions] |
| **Langue(s)** | [Ex : Français] |
| **Canaux de dépôt** | [Ex : Xportal (web / mobile) — Interface e-service [FDS]] |

### 1.3. Acteurs et intervenants

<!-- IA: Liste tous les acteurs humains ET systèmes impliqués. Pour chaque acteur, précise son profil, son rôle, son accès système et sa responsabilité SLA. Ne pas omettre le système Xflow ni l'Admin Xportal. -->

| Acteur | Profil | Rôle dans le processus | Accès système | Responsabilité SLA |
|---|---|---|---|---|
| **Citoyen / Usager** | [Profil de l'usager] | Soumet la demande, fournit les pièces, reçoit la notification | Xportal (lecture seule) | Évaluateur du service |
| **Agent de vérification** | Agent [FDS] (N1 métier) | Vérifie la conformité du dossier, lance l'instruction | Back-office — [Système back-office] | Délai : selon SLA [FDS] |
| **Superviseur / Chef de service** | Responsable administratif [FDS] | Valide et signe le dossier après vérification | Back-office — accès complet | Délai : selon SLA [FDS] |
| **Système Xflow** | Orchestrateur BPMN | Routage automatique, notifications, escalades temporelles | Infrastructure ATD / [FDS] | Disponibilité 99,5% |
| **Admin Xportal (ATD)** | Technicien ATD | Surveillance, publication, KPIs | Administration Xportal | SLA plateforme |
| **Centre d'appel (N1)** | Agent support ATD | Assistance usagers en difficulté sur la démarche | Consultation statut uniquement | Résolution < 30 min |

---

## 2. Design du formulaire Form.io

### 2.1. Structure du formulaire
<!-- IA Premium: L'onglet 1 (stepIntro) doit être décrit comme une véritable "Landing Page" Premium. Spécifiez l'utilisation de grilles Bootstrap (columns 8/4), d'Info Pills stylisées pour les avantages du service, d'une Sidebar pour les informations du FDS, et d'un guide "pas à pas" numéroté. -->

<!-- IA: Décris TOUS les formulaires qui composent le parcours. Chaque userTask du BPMN (côté PORTAL et XFLOW) qui nécessite un formulaire doit être listé ici. Inclure : formulaire principal, formulaires conditionnels (correction, paiement), et formulaires des userTasks agent (instruction, validation, etc.). -->

Le parcours est composé de [N] formulaire(s) Form.io distinct(s) orchestré(s) par Xflow :

- **Formulaire principal ([N] onglets)** : parcours commun à tous les usagers.
- **[Formulaire secondaire, si applicable] ([N] onglet(s), conditionnel)** : activé uniquement si [condition], entre [étape X] et [étape Y].
- **[Formulaire d'instruction agent, si applicable]** : formulaire présenté à l'agent back-office pour instruire le dossier (userTask côté XFLOW).
- **[Autres formulaires userTask]** : un formulaire par userTask identifiée dans le processus BPMN (section 3.2).

#### Formulaire principal — [N] onglets wizard

<!-- IA: Adapte le nombre d'onglets au service. L'onglet 1 qualifie toujours la demande (type, éligibilité). Le dernier onglet est toujours le récapitulatif + soumission + CAPTCHA. -->

| Onglet | Titre | Remarques |
|---|---|---|
| Onglet 1 | [Titre — ex : Qualification de la demande] | [Conditionne le parcours / vérifie l'éligibilité] |
| Onglet 2 | [Titre — ex : Informations personnelles] | [Description courte du contenu] |
| Onglet 3 | [Titre — ex : Informations sur le dossier] | [Description courte du contenu] |
| Onglet 4 | [Titre — ex : Pièces à fournir] | [Upload pièces — préciser les conditionnels éventuels] |
| Onglet 5 | Récapitulatif et soumission | Résumé non modifiable + confirmation + CAPTCHA |

#### [Formulaire secondaire — si applicable] — Conditionnel [condition]

<!-- IA: Si aucun formulaire secondaire n'existe, supprime cette sous-section. Sinon, précise le slug Form.io, la condition de déclenchement et l'étape BPMN associée. -->

Ce formulaire est un composant Form.io indépendant (slug : `[slug-du-formulaire]`), déclenché par Xflow via une Send Task après [étape déclencheur], uniquement lorsque `[condition]`. Il s'affiche dans Xportal comme une tâche utilisateur intercalée avant [étape suivante].

| Formulaire | Titre | Condition de déclenchement |
|---|---|---|
| [Nom] | [Titre affiché] | `[condition]` uniquement — déclenché par Xflow (étape [BXX]) |

### 2.2. Détail des champs

<!-- IA: Pour chaque onglet, liste tous les champs avec leurs propriétés complètes. 
Colonnes obligatoires : Nom du champ (camelCase), Libellé affiché, Type, Obligatoire (Oui/Non/Conditionnel), Format/Règle, Source, Remarques.
**Conventions P-Studio strictes :**
- Données citoyen (e-ID/Compte) : Source = `Profil Citoyen (config.users)` | Règle = `Lecture seule (statique ou dynamique via bloc logic)`.
- Listes dynamiques (Pays, etc.) : Source = `API (config.apiBaseUrl/...)`.
Précise les règles métiers applicables (RG-XXX) dans la colonne Remarques. -->

#### Onglet 1 — [Titre de l'onglet 1]

[Description de l'onglet et de sa logique de qualification.]

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `[nomChamp]` | [Libellé] | [Type] | [Oui/Non/Conditionnel] | [Format/Règle] | [Source] | [Remarques + RG-XXX] |

#### Onglet 2 — [Titre de l'onglet 2]

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `[nomChamp]` | [Libellé] | [Type] | [Oui/Non] | [Format/Règle] | [Source] | [Remarques] |

#### Onglet 3 — [Titre de l'onglet 3]

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `[nomChamp]` | [Libellé] | [Type] | [Oui/Non] | [Format/Règle] | [Source] | [Remarques] |

#### Onglet 4 — Pièces à fournir

<!-- IA: Liste toutes les pièces justificatives. Précise systématiquement le format accepté (PDF/JPG/PNG), la taille maximale, et si la pièce est conditionnelle (avec référence à la règle métier RG-XXX). -->

Les fichiers sont uploadés directement dans Xportal et transmis à Xflow. Formats acceptés : PDF, JPG, PNG.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `[nomPiece]` | [Libellé] | Fichier | [Oui/Conditionnel] | PDF/JPG/PNG < 2 Mo | Upload | [Obligatoire si condition — RG-XXX] |

#### [Formulaire secondaire — Détail des champs, si applicable]

<!-- IA: Décris les champs du formulaire secondaire (ex : paiement). Précise les champs pré-remplis par Xflow (lecture seule ou cachés) et les propriétés techniques du formulaire. -->

[Description du formulaire secondaire et de son mode de fonctionnement.]

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `[nomChamp]` | [Libellé] | [Type] | [N/A/Non] | [Statique/Numérique] | [Système/Xflow] | [Description comportement] |

**Propriétés techniques :**

| Propriété technique | Valeur |
|---|---|
| **Slug du formulaire** | `[slug-du-formulaire]` |
| **Version** | [N] (`locked = true`, `status = Active`) |
| **Groupe Form.io** | `[UUID]` |
| **Déclencheur processus** | Send Task Xflow — étape [BXX] (message : `[NOM_MESSAGE_XFLOW]`) |
| **Condition d'affichage** | `[condition]` — formulaire invisible sinon |
| **Action post-traitement** | Receive Task Xflow — étape [BXX] attend [événement] avant de continuer |

#### Onglet [N] — Récapitulatif et soumission

<!-- IA: Cet onglet est standardisé. Il comprend toujours : un composant HTML récapitulatif intelligent, une checkbox de certification sur l'honneur, et un CAPTCHA Google reCAPTCHA v3. -->

L'onglet [N] affiche un résumé de toutes les données saisies via le script d'analyse natif ATD. L'usager coche une case de confirmation. P-Studio gère nativement le bouton « Soumettre » sur le dernier panel du wizard.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `htmlRecapitulatifFinal` | N/A | HTML | N/A | Script Parseur Formulaire | Système | Injection du composant `recap_form.json` |
| `luEtApprouve` | Je déclare et certifie sur l'honneur que les informations... | Checkbox | Oui | Doit être coché | Saisie | Ignoré par le récap via `excludeKeys` |

### 2.3. Actions du formulaire (P-Studio)

<!-- IA: Documente ici la tarification et le routage applicatif. "Publish to RabbitMQ" est obligatoire pour tout formulaire P-Studio. "Calculate Costs" n'est présent que si payant. Précise si le montant est "Prix fixe" ou "Champ dynamique". -->

Les actions suivantes sont pré-configurées sur la soumission du formulaire P-Studio pour permettre son ingurgitation par le moteur XFlow / RabbitMQ :

| Code Action P-Studio | Condition d'activation | Configuration algorithmique |
|---|---|---|
| **Calculate Costs** | [Toujours actif / Non (Gratuit)] | [N/A / Prix fixe : XXX FCFA / Champ dynamique : *data.nomChamp * tarif*] |
| **Publish to RabbitMQ** | Toujours actif | Routing Key: `submissions.topic` — Queue: `workflows-engine.main.queue` |

### 2.4. Configuration des environnements

<!-- IA: Cette sous-section documente le bloc `config` du formulaire Form.io. Elle décrit les URLs API, les endpoints et le mapping utilisateur pour chaque environnement. Cette même configuration sera répliquée dans les startEvent des deux pools BPMN (XPortal et XFlow). -->

Le formulaire Form.io contient un bloc `config` à la racine du JSON, déclinant les paramètres par environnement. Cette configuration est également portée par les **startEvent des deux pools BPMN** (XPortal et XFlow) sous forme d'`inputParameter` nommés `development`, `sandbox`, `preproduction` et `production`.

#### Environnements déclarés

| Environnement | `apiBaseUrl` | `appName` |
|---|---|---|
| `development` | `https://api.[service].dev.gouv.tg` | Développement |
| `sandbox` | `https://api.[service].sandbox.gouv.tg` | Sandbox |
| `preproduction` | `https://api.[service].preprod.gouv.tg` | Pré-production |
| `production` | `https://api.[service].gouv.tg` | Production |

#### Endpoints API (par environnement)

<!-- IA: Liste ici tous les endpoints API consommés par le formulaire (listes déroulantes, données de référence, etc.). Chaque endpoint est identique dans tous les environnements, seule la baseUrl change. -->

| Clé endpoint | Chemin | Usage dans le formulaire |
|---|---|---|
| `[nomEndpoint1]` | `/api/v1/[ressource]` | [Description : liste déroulante de X, données de Y...] |
| `[nomEndpoint2]` | `/api/v1/[ressource]` | [Description] |

#### Mapping utilisateur (`config.users`)

Le mapping e-ID est identique dans tous les environnements :

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

<!-- IA: Cette sous-section recense TOUS les formulaires Form.io nécessaires au processus. Chaque userTask du BPMN (lanes PORTAL et XFLOW) qui présente un formulaire à un utilisateur (citoyen ou agent) doit être listée ici. Le BPMN référencera chaque formulaire via camunda:formKey. -->

Le tableau ci-dessous liste l'ensemble des formulaires Form.io à produire pour ce service. Chaque `userTask` du processus BPMN nécessitant une interaction formulaire est associée à un fichier JSON distinct.

| # | Fichier JSON | Lane | userTask BPMN | Description | Condition |
| --- | --- | --- | --- | --- | --- |
| 1 | `formio-[nom-service].json` | PORTAL | Soumission initiale | Formulaire principal — [N] onglets wizard | Toujours |
| 2 | `formio-correction-[nom-service].json` | PORTAL | Correction / Resoumission | Formulaire de correction après rejet partiel | Si boucle de correction |
| 3 | `formio-paiement-[nom-service].json` | PORTAL | Paiement | Formulaire de paiement | Si service payant |
| 4 | `formio-instruction-[nom-service].json` | XFLOW | Instruction agent | Formulaire d'instruction back-office | Toujours |
| [N] | `formio-[action]-[nom-service].json` | [PORTAL/XFLOW] | [Nom de la userTask] | [Description] | [Condition] |

---

## 3. Le processus BPMN 2.0

### 3.1. Vue d'ensemble du processus TO-BE

<!-- IA: Le processus est modélisé sur P-Studio (Camunda Web Modeler). Indique les métadonnées du processus. Le nom du processus suit le pattern : Procédure_[NomService]_v[N]. -->

Le processus complet est modélisé sur P-Studio (Camunda Web Modeler). Le diagramme BPMN est joint en annexe (fichier `.bpmn`). Ce tableau décrit chaque étape avec ses acteurs, délais et conditions.

| Champ | Valeur |
|---|---|
| **Nom du processus** | `Procédure_[NomService]_v[N]` |
| **Événement déclencheur** | Soumission du formulaire par l'usager sur Xportal |
| **Événement de fin (succès)** | [Description de la fin heureuse — ex : notification + mise à disposition du document] |
| **Événement de fin (rejet)** | Notification de rejet définitif motivé à l'usager |
| **Moteur d'exécution** | Xflow (Camunda Platform 7 — GNSPD Framework) |
| **Version processus** | [N.N] |
| **Participants BPMN** | Pool XPORTAL (citoyen) + Pool XFLOW (back-office) — deux pools exécutables communiquant via Kafka |

### 3.2. Étapes détaillées du processus

<!-- IA: 
- La lane PORTAL décrit ce que vit l'usager côté Xportal (numérotation : 01, 02, 03…).
- La lane XFLOW décrit les traitements back-office (numérotation : B01, B02, B03…).
- Chaque étape doit avoir : un numéro, un nom, une description complète, l'acteur, le délai, et le résultat/condition (liens vers étapes suivantes).
- Si le service a un sous-parcours conditionnel (ex : paiement), les étapes correspondantes sont numérotées séquentiellement et clairement conditionnées.
- Utilise les types de tâches BPMN standard : Script task, Service task, User task, Send task, Receive task, Gateway. -->

#### Lane PORTAL — Côté Citoyen

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| 01 | [Nom] | [Description détaillée de l'action et du déclencheur.] | Système / Citoyen | Immédiat | → Étape 02 |
| 02 | [Nom] | [Description.] | Système | < [N] min | [Si condition → XX / Sinon → XX] |
| 03 | [Nom] | [Description.] | [Acteur] | [Délai] | → Étape 04 |
| 04 | [Nom] | [Description.] | [Acteur] | [Délai] | → Étape 05 |
| 05 | [Nom — notification finale] | [L'usager reçoit la décision finale.] | Système / Citoyen | < [N] min | → FIN |

#### Lane XFLOW — Côté Back-office

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| B01 | Initialisation procédure | Xflow reçoit le message de démarrage depuis Xportal. Les données du formulaire sont chargées. [La gateway '[condition] ?' est évaluée immédiatement.] | Système | Immédiat | [Si condition → B02 / Sinon → B0X] |
| B02 | [Nom] | [Description.] | [Acteur] | < [N] min | → B0X |
| B03 | [Nom] | [Description.] | [Acteur] | [Délai] | [→ B0X si OK / → B0X si KO] |
| B04 | Recevoir les données usager | Script task : extraction et normalisation des données du formulaire soumis. Vérification automatique : format, cohérence, complétude. | Système | < 2 min | → B05 |
| B05 | Vérification [système tiers] | Service task : interrogation de [base/système] pour vérifier [condition métier]. | Système / [Système tiers] | < 5 min | Si valide → B06 / Sinon → B0X |
| B06 | Vérification de conformité | User task assignée à l'agent [FDS] : examen du dossier, vérification des pièces justificatives, cohérence des informations. | Agent [FDS] | Selon SLA [FDS] | Si conforme → B07 / Si erreurs → B09 / Si rejet → B08 |
| B07 | Enregistrement décision | Service task : enregistrement de la décision d'acceptation dans la base de données. Génération du récépissé de validation. | Système | < 2 min | → B10 |
| B08 | Envoi rejet définitif | Service task / Send task : envoi de la notification de rejet définitif au portail avec le motif détaillé. Fin du processus back-office. | Système | < 5 min | → FIN (rejet) |
| B09 | Notification correction | Send task : envoi d'une notification de correction au portail avec la liste précise des erreurs ou pièces manquantes. L'usager dispose d'un délai pour corriger. | Système | < 15 min | → Attente resoumission → B05 |
| B10 | Notification acceptation | Send task : envoi de la notification d'acceptation au portail. L'usager est informé que [document/décision] est en cours d'édition / disponible. | Système | < 5 min | → FIN (succès) |

### 3.3. Matrice des échanges inter-pools (Kafka)

<!-- IA: Cette sous-section est OBLIGATOIRE. Elle recense tous les messages Kafka échangés entre XPortal et XFlow. Chaque SendTask doit avoir un ReceiveTask correspondant. Vérifier qu'aucun message n'est orphelin. Les patterns P1-P8 du TO-BE doivent être reflétés ici. -->

Tous les échanges asynchrones entre les deux pools sont listés ci-dessous. Chaque message correspond à un couple SendTask/ReceiveTask (ou StartEvent) appariés.

#### XPortal → XFlow

| # | Message Kafka (`messageRef`) | Émetteur (SendTask) | Récepteur (ReceiveTask/StartEvent) | Payload | Condition |
| --- | --- | --- | --- | --- | --- |
| 1 | `MSG_[SERVICE]_START` | Soumission initiale | StartEvent XFlow | Données formulaire complet | Toujours |
| 2 | `MSG_[SERVICE]_RESUB` | Resoumission correction | ReceiveTask resoumission | Données corrigées | Si correction |

#### XFlow → XPortal

| # | Message Kafka (`messageRef`) | Émetteur (SendTask) | Récepteur (ReceiveTask) | Payload | Condition |
| --- | --- | --- | --- | --- | --- |
| 1 | `MSG_[SERVICE]_PAY_REQ` | Demande paiement | ReceiveTask paiement | Signal paiement | Si payant |
| 2 | `MSG_[SERVICE]_PAY_CONFIRM` | Confirmation paiement | ReceiveTask confirmation | Résultat paiement | Si payant |
| 3 | `MSG_[SERVICE]_VERIFY` | Notification vérification | ReceiveTask vérification | Résultat agent | Toujours |
| 4 | `MSG_[SERVICE]_CORRECT` | Notification correction | ReceiveTask correction | Motif correction | Si non conforme |
| 5 | `MSG_[SERVICE]_FINAL` | Notification finale | ReceiveTask finale | Résultat final | Si conforme |

#### Points de convergence

<!-- IA: Identifier ici les ReceiveTask multi-entrantes (pattern P2). Ce sont les noeuds qui reçoivent des jetons de plusieurs chemins différents. -->

| ReceiveTask (convergence) | Pool | Entrées | Description |
| --- | --- | --- | --- |
| [Nom du ReceiveTask] | PORTAL | [Chemin 1, Chemin 2, Chemin 3] | [Point de convergence avant la gateway de décision] |

#### Terminaisons du processus

<!-- IA: Lister tous les EndEvents des deux pools (pattern P7). Chaque branche alternative doit se terminer explicitement. -->

| EndEvent | Pool | Condition | Notification associée |
| --- | --- | --- | --- |
| Fin succès | PORTAL | Dossier accepté | Notification finale + document disponible |
| Fin rejet | PORTAL | Dossier rejeté | Notification de rejet |
| [Autres EndEvents] | [Pool] | [Condition] | [Notification] |

### 3.4. Flux d'escalade temporelle

<!-- IA: Liste toutes les escalades temporelles configurées dans Xflow. Il y en a au moins 4 types standards : dépassement SLA agent, délai correction citoyen, délai paiement (si applicable), indisponibilité Xflow. -->

Les escalades automatiques suivantes sont configurées dans Xflow :

| Déclencheur | Canal | Action |
|---|---|---|
| Délai instruction agent dépassé (SLA [FDS]) | Email + Dashboard | Escalade automatique vers superviseur [FDS] |
| Délai correction usager dépassé ([N] jours ouvrés) | SMS + Email | Rejet automatique du dossier avec notification |
| [Délai paiement dépassé — si applicable] | SMS + Email | Annulation automatique de la demande |
| Indisponibilité Xflow > 15 min | Email Admin | Alerte automatique à l'Admin ATD |

---

## 4. Règles métiers
<!-- IA Premium: Chaque règle doit être atomique et numérotée RG-XXX. Utilisez impérativement la syntaxe : "SI [condition technique] ALORS [action/blocage]". Ne tolérez aucune règle vague. Mentionnez explicitement le verrouillage e-ID (statique ou dynamique). -->

<!-- IA: 
- Numérote les règles RG-001, RG-002, etc.
- Chaque règle doit avoir un ID unique, un nom court, une description précise avec la condition SI/ALORS, une priorité (HAUTE/MOYENNE/BASSE) et les étapes/onglets concernés.
- Les règles de priorité HAUTE bloquent le processus si violées.
- Règles incontournables à toujours inclure : éligibilité usager, âge minimum le cas échéant, unicité de la demande, conformité des pièces jointes, archivage légal. -->

| ID | Règle métier | Description / Condition | Priorité | Étapes concernées |
|---|---|---|---|---|
| RG-001 | [Nom de la règle] | Si `[condition]` → [action / blocage / activation]. | HAUTE | [Onglet X / Étape BXX] |
| RG-002 | [Nom de la règle] | Si `[condition]` → blocage avec message : *« [Message affiché à l'usager] »* | HAUTE | [Onglet X formulaire] |
| RG-003 | Âge minimum | L'usager doit avoir au moins [N] ans à la date de soumission. Vérification sur le champ `dateNaissance`. Message bloquant si non respecté. | HAUTE | Onglet [N] formulaire |
| RG-004 | [Pièces conditionnelles] | Si `[condition]`, les champs `[nomChamp]` et `[nomChamp]` passent obligatoires (`requis = true` dynamiquement). | HAUTE | Onglet [N] formulaire |
| RG-005 | Vérification [système] obligatoire | [Champs clés] doivent correspondre à [condition dans le système tiers]. | HAUTE | Étape B05 |
| RG-006 | Une demande active par usager | Un usager identifié par [identifiant unique] ne peut avoir qu'une seule demande en cours. Si une demande est active, bloquer la nouvelle soumission. | HAUTE | Étape 01 |
| RG-007 | Délai de correction usager | L'usager dispose de [N] jours ouvrés pour soumettre un dossier corrigé. Au-delà, le dossier est clôturé automatiquement avec statut *« Rejeté — délai dépassé »*. | HAUTE | Étapes [XX-XX], B09 |
| RG-008 | [Paiement préalable — si applicable] | Le processus d'instruction ne démarre qu'après confirmation effective du paiement. | HAUTE | Étapes [BXX-BXX] |
| RG-009 | Conformité des pièces jointes | Les fichiers uploadés doivent respecter : formats PDF/JPG/PNG, taille < 2 Mo par fichier. Tout fichier non conforme est rejeté avec message explicite. | MOYENNE | Onglet [N], Étape B04 |
| RG-010 | Archivage [N] ans | Tous les dossiers (approuvés et rejetés) doivent être archivés pendant [N] ans minimum conformément aux obligations légales [pays]. | HAUTE | Post-décision |

---

## 5. Intégration avec des systèmes tiers

<!-- IA: Liste tous les systèmes externes avec lesquels le service interagit. Précise le type d'intégration (API REST, API interne, etc.), les données échangées, la condition d'appel et le statut de disponibilité. Mentionne toujours que des conventions d'échange de données sont nécessaires. -->

Les intégrations suivantes sont envisagées. Elles nécessitent la signature de conventions d'échange de données entre les structures concernées.

| Système cible | Type d'intégration | Données échangées | Condition d'appel | Statut |
|---|---|---|---|---|
| [Système back-office FDS] | API interne (lecture) | [Champs clés échangés] | Étape B05 — Vérification [condition] | Disponible |
| [Plateforme paiement — si applicable] | API REST (paiement) | Montant, référence dossier, statut paiement | Étape B02 — Déclenchement paiement | À configurer |
| Plateforme SMS | API REST (envoi) | Numéro téléphone, texte message, réf. dossier | À chaque changement de statut | Disponible |
| Système archivage ATD | API interne | Dossier complet (formulaire + pièces + décision) | Post-décision — Archivage automatique | Disponible |
| [Système identité numérique — optionnel] | API REST (vérification) | NOM, PRÉNOMS, DATE NAISSANCE | Optionnel — enrichissement données | À développer |

---

## 6. Notifications automatiques

<!-- IA: 
- Numérote les notifications N01, N02, etc.
- Toujours inclure : accusé de réception (soumission), corrections demandées, décision d'acceptation, rejet définitif, invitation à évaluer (J+1).
- Ajouter selon le service : demande de paiement, confirmation paiement, rappel agent, escalade superviseur.
- Les messages types doivent contenir les variables dynamiques entre crochets : [DOSSIER], [montant], [liste], [motif_rejet], etc. -->

| Réf. | Déclencheur | Canal | Destinataire | Message type |
|---|---|---|---|---|
| N01 | Soumission formulaire (Étape 01) | SMS + Email | Usager | *Votre demande [NOM_SERVICE] (réf. [DOSSIER]) a bien été reçue. Délai de traitement : [X] jours ouvrés.* |
| N02 | Vérification KO — corrections demandées | SMS + Email | Usager | *Votre dossier est incomplet ou comporte des erreurs. Corrections requises : [liste]. Vous avez [N] jours ouvrés.* |
| N03 | [Demande de paiement — si applicable] | SMS + Email | Usager | *Une demande de paiement de [montant] FCFA a été générée pour votre demande [DOSSIER]. Lien : [URL]* |
| N04 | [Confirmation paiement reçu — si applicable] | SMS | Usager | *Votre paiement a été confirmé. Votre dossier est en cours d'instruction.* |
| N05 | Décision d'acceptation (B10) | SMS + Email | Usager | *Votre demande [DOSSIER] a été acceptée. [Description de la suite — ex : votre document est en cours de préparation]. Vous serez notifié(e) [condition de retrait/disponibilité].* |
| N06 | Rejet définitif (B08) | SMS + Email | Usager | *Votre demande [DOSSIER] a été rejetée. Motif : [motif_rejet]. Vous pouvez soumettre une nouvelle demande.* |
| N07 | Rappel agent — délai à risque | Email + Dashboard | Agent [FDS] | *Rappel : Le dossier [DOSSIER] doit être traité avant [date_heure_limite].* |
| N08 | Escalade superviseur | Email + Dashboard | Superviseur [FDS] | *Escalade automatique : Le dossier [DOSSIER] dépasse le délai d'instruction. Action requise.* |
| N09 | Invitation évaluation (J+1 décision) | SMS + Email | Usager | *Êtes-vous satisfait(e) de votre expérience ? Évaluez ce service en 30 secondes sur Xportal.* |

---

## 7. KPIs du service & engagements SLA

<!-- IA: Les valeurs cibles standards de la plateforme ATD sont indiquées. Remplace uniquement les valeurs spécifiques au service ([À renseigner par...]) par les données fournies. Ne modifie pas les valeurs techniques standards (disponibilité, délais système). -->

| Indicateur | Valeur cible |
|---|---|
| **Taux de complétion** | ≥ 85% (dossiers soumis / formulaires initiés) |
| **Taux d'abandon** | ≤ 15% |
| **Délai standard de traitement** | [À renseigner par le FDS — objectif en jours ouvrés] |
| **Délai réglementaire maximum** | [À renseigner par le FDS] |
| **Taux de rejet** | ≤ 10% |
| **Note de satisfaction usager** | ≥ 4,0 / 5 |
| **Taux de résolution N1 (FCR)** | ≥ 80% |
| **Disponibilité service (Xportal/Xflow)** | ≥ 99,5% mensuel |
| **Délai notification accusé de réception** | < 5 minutes |
| **Délai traitement vérification [système tiers]** | < 5 minutes (automatique) |

---

## 8. Interface e-service [FDS]

<!-- IA: Cette section décrit l'interface dédiée au FDS, visuellement indépendante de Xportal mais techniquement connectée au même backend Xflow. L'URL suit le pattern services.[domaine_fds]/[service]. Si aucune interface e-service dédiée n'est prévue, remplace cette section par une note explicative et supprime les champs inapplicables. -->

En complément de Xportal, une interface e-service aux couleurs du [FDS] sera développée et déployée. Cette interface est visuellement indépendante de Xportal mais techniquement interconnectée.

| Champ | Valeur |
|---|---|
| **URL e-service** | https://services.[domaine_fds]/[service] [À confirmer] |
| **Charte graphique** | Couleurs officielles [FDS] — logo, typographie, palette fournis par le FDS |
| **Fonctionnalités** | Accès direct au formulaire, suivi de dossier, notifications statut |
| **Authentification** | Identique à Xportal (SSO ATD) |
| **Backend** | Partage du même processus Xflow — données synchronisées en temps réel |
| **Responsabilité design** | Intégrateur (en concertation avec le service communication [FDS]) |
| **Livrables attendus** | Maquettes HTML/CSS validées par [FDS] + intégration Form.io |

---

## 9. Validations & signatures

<!-- IA: Cette section est standardisée et ne se modifie pas, sauf les qualités des signataires si elles diffèrent du standard (Intégrateur Externe, Point focal FDS, Chef de projet ATD). -->

Le présent SRS a été élaboré à l'issue des ateliers d'analyse conduits entre l'intégrateur, l'équipe ATD et les points focaux du [FDS]. Il constitue la référence contractuelle pour le développement, les tests et la mise en production du service.

| | Rédigé par | Validé par (FDS) | Approuvé par (ATD) |
|---|---|---|---|
| **Qualité** | Intégrateur Externe | Point focal [FDS] | Chef de projet ATD |
| **Nom** | ________________________ | ________________________ | ________________________ |
| **Date** | _______________________ | _______________________ | _______________________ |
| **Signature** | __________________ | __________________ | __________________ |

---

*SRS — [Nom du Service] | v[X.Y] | ATD*
