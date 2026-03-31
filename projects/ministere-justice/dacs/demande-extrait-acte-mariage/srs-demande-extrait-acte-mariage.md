# SERVICE REQUIREMENT SHEET (SRS)
## DEMANDE D'EXTRAIT D'ACTE DE MARIAGE (PREMIÈRE DÉLIVRANCE ET DUPLICATA)
### Direction des Affaires Civiles et du Sceau (DACS) — Togo

---

| Champ | Valeur |
|---|---|
| **Fournisseur de Services (FDS)** | Direction des Affaires Civiles et du Sceau (DACS) |
| **Service parent** | Ministère de la Justice |
| **Intégrateur en charge** | Équipe ATD |
| **Chef de projet ATD** | ATD |
| **Point focal FDS** | Responsable DACS |
| **Date de création** | 31 mars 2026 |
| **Date de dernière révision** | 31 mars 2026 (v1.0 — Version initiale) |
| **Date de validation** | _________________________________ |
| **Back-office utilisé** | XFlow / Odoo Traitement (ATD) |
| **Déploiement cible** | Xportal + Xflow + Plateforme de paiement e-Gov |

---

## Historique des changements

| Version | Date | Auteur | Description des modifications |
|---|---|---|---|
| 1.0 | 31/03/2026 | Équipe ATD | Version initiale |

---

## Table des matières

1. [Identification du service](#1-identification-du-service)
2. [Design du formulaire Form.io](#2-design-du-formulaire-formio)
3. [Le processus BPMN 2.0](#3-le-processus-bpmn-20)
4. [Règles métiers](#4-règles-métiers)
5. [Intégration avec des systèmes tiers](#5-intégration-avec-des-systèmes-tiers)
6. [Notifications automatiques](#6-notifications-automatiques)
7. [KPIs du service & engagements SLA](#7-kpis-du-service--engagements-sla)
8. [Interface e-service DACS](#8-interface-e-service-dacs)
9. [Validations & signatures](#9-validations--signatures)

---

## 1. Identification du service

### 1.1. Description fonctionnelle

L'extrait d'acte de mariage est un document officiel attestant de l'union légale entre deux personnes. Il est indispensable pour de nombreuses démarches administratives (demande de passeport, succession, etc.). La délivrance est assurée par l'officier d'état civil de la commune où le mariage a été célébré. La loi togolaise impose une signature manuscrite sur le document physique.

La digitalisation permet au citoyen de soumettre sa demande en ligne, d'être pré-vérifié sur les registres numérisés ou manuels, de payer les frais éventuels en temps réel et, si désiré, de choisir une option d'expédition postale sécurisée évitant tout déplacement. L'usager a une visibilité totale sur l'avancement de son dossier grâce à XPortal.

### 1.2. Fiche d'identité du service

| Champ | Valeur |
|---|---|
| **Code service** | SRV-DACS-2026-001 |
| **Nom complet** | Demande d'extrait d'acte de mariage (première délivrance et duplicata) |
| **Catégorie** | État Civil |
| **Bénéficiaires** | Tout citoyen togolais ou étranger marié sur le territoire togolais |
| **Fréquence estimée** | 15 000 demandes par an (national) |
| **Délai standard de traitement** | 24h à 48h (si acte numérisé/facilement localisable) |
| **Délai réglementaire maximum** | 30 jours |
| **Coût du service** | Gratuit (extrait simple) / Payant (copie intégrale / recommandé postal) |
| **Langue(s)** | Français |
| **Canaux de dépôt** | Xportal (web / mobile) |

### 1.3. Acteurs et intervenants

| Acteur | Profil | Rôle dans le processus | Accès système | Responsabilité SLA |
|---|---|---|---|---|
| **Citoyen / Usager** | L'un des époux ou proche | Soumet la demande, paie en ligne, réajuste si correction | Xportal (lecture seule) | Évaluateur du service |
| **Agent d'état civil** | Agent DACS / Mairie | Instruit le dossier si acte introuvable automatiquement | Back-office — Odoo / XFlow | Délai : 72h |
| **Officier d'état civil** | Officier officiel | Imprime l'original, signe manuellement et scelle | Back-office — XFlow | Délai : SLA DACS |
| **Système Xflow** | Orchestrateur BPMN | Vérifie automatiquement l'acte avec l'API, notifie | Infrastructure ATD | Disponibilité 99,5% |
| **Admin Xportal (ATD)** | Technicien ATD | Surveillance, publication | Administration Xportal | SLA plateforme |
| **Centre d'appel (N1)** | Agent support ATD | Assistance usagers en difficulté | Consultation | Résolution < 30 min |

---

## 2. Design du formulaire Form.io

### 2.1. Structure du formulaire

Le parcours est composé de deux formulaires distincts :

- **Formulaire principal (5 onglets)** : parcours de demande initiale.
- **Formulaire de correction (Conditionnel)** : affiché dans la boucle de correction.
- **Formulaire d'instruction agent** : pour la validation back-office XFlow.

#### Formulaire principal — 5 onglets wizard

| Onglet | Titre | Remarques |
|---|---|---|
| Onglet 1 | Présentation (Qualification) | Landing Page Premium avec informations, règles et éligibilité |
| Onglet 2 | Informations des époux | Identité du demandeur (E-ID) et du conjoint |
| Onglet 3 | Informations sur le mariage | Date, lieu, centre d'état civil |
| Onglet 4 | Options & Pièces à fournir | Choix document, mode de retrait et paiement intégré |
| Onglet 5 | Récapitulatif et soumission | Résumé non modifiable + confirmation + CAPTCHA |

#### Formulaire de correction (Conditionnel)

Slug : `formio-correction-demande-extrait-acte-mariage`

Ce formulaire est un composant Form.io indépendant déclenché par Xflow via une Send Task après la soumission initiale, uniquement lorsque l'agent demande une correction.

| Formulaire | Titre | Condition de déclenchement |
|---|---|---|
| Correction | Correction de votre demande d'extrait d'acte de mariage | Déclenché par Xflow si décision agent = Correction |

### 2.2. Détail des champs

#### Onglet 1 — Présentation (Qualification)

Cet onglet de type Landing Page Premium contient des Info Pills sur le service (délais, coûts) et une Sidebar explicative. Il instruit l'utilisateur sans lui demander de saisie. Les champs sont de type `htmlelement` et `columns`.

#### Onglet 2 — Informations des époux

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `nomDemandeur` | Nom du demandeur | Texte | Oui | Lecture seule | Profil Citoyen (config.users) | Pré-rempli (e-ID) |
| `prenomDemandeur` | Prénoms du demandeur | Texte | Oui | Lecture seule | Profil Citoyen (config.users) | Pré-rempli (e-ID) |
| `telephone` | Téléphone | Téléphone | Oui | Standard E.164 | Profil Citoyen (config.users) | Pré-rempli (e-ID) |
| `qualiteDemandeur` | Qualité du demandeur | Select | Oui | Époux, Épouse, Descendant | Saisie | Liste fixe |
| `nomConjoint` | Nom du conjoint | Texte | Oui | Majuscules | Saisie | |
| `prenomConjoint` | Prénoms du conjoint | Texte | Oui | Max 100 caractères | Saisie | |

#### Onglet 3 — Informations sur le mariage

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `dateMariage` | Date de célébration | Date | Oui | < Date du jour | Saisie | |
| `communeMariage` | Commune du mariage | Select | Oui | Communes du Togo | API (config.apiBaseUrl/communes) | |
| `centreEtatCivil` | Mairie ou centre d'état civil | Select | Oui | Filtré par commune | API (config.apiBaseUrl/centres) | Détermine l'agent-cible |
| `numeroActe` | Numéro d'acte de mariage | Texte | Non | Max 20 caractères | Saisie | Optionnel |

#### Onglet 4 — Options & Pièces à fournir

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `typeDocument` | Nature du document | Radio | Oui | Extrait simple / Copie intégrale | Saisie | (RG-001) |
| `modeRetrait` | Mode de retrait | Radio | Oui | Guichet / La Poste | Saisie | (RG-002) |
| `adresseExpedition` | Adresse postale complète | Texte | Conditionnel | Max 150 caractères | Saisie | Requis si Poste (RG-002) |
| `pieceIdentite` | Pièce d'identité | Fichier | Oui | PDF/JPG/PNG < 2 Mo | Upload | |
| `livretFamille` | Copie du livret de famille | Fichier | Non | PDF/JPG/PNG < 2 Mo | Upload | |
| `montantTotal` | Montant estimé (FCFA) | Texte | Oui | Lecture seule (calcul) | Saisie | Sert pour Calculate Costs |

#### Onglet 5 — Récapitulatif et soumission

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `htmlRecapitulatifFinal` | N/A | HTML | N/A | Script Parseur | Système | Récap intelligent ATD |
| `luEtApprouve` | Je déclare et certifie sur l'honneur... | Checkbox | Oui | Doit être coché | Saisie | Exclu des données `excludeKeys` |
| `captcha` | Sécurité anti-robot | reCAPTCHA | Oui | Google v3 | Système | |

### 2.3. Actions du formulaire (P-Studio)

Le paiement éventuel s'effectue directement à la soumission pour éviter une étape BPMN conditionnelle et hachée.

| Code Action P-Studio | Condition d'activation | Configuration algorithmique |
|---|---|---|
| **Calculate Costs** | Si `montantTotal > 0` | Montant basé sur le champ `montantTotal`. Redirige vers passerelle avant complétion finale de soumission. |
| **Publish to RabbitMQ** | Toujours actif | Routing Key: `submissions.topic` — Queue: `workflows-engine.main.queue` |

### 2.4. Configuration des environnements

| Environnement | `apiBaseUrl` | `appName` |
|---|---|---|
| `development` | `https://api.dacs.dev.gouv.tg/api/v1` | Développement |
| `sandbox` | `https://api.dacs.sandbox.gouv.tg/api/v1` | Sandbox |
| `preproduction` | `https://api.dacs.preprod.gouv.tg/api/v1` | Pré-production |
| `production` | `https://api.dacs.gouv.tg/api/v1` | Production |

**Endpoints API :**
| Clé endpoint | Chemin | Usage dans le formulaire |
|---|---|---|
| `communes` | `/communes` | Liste des communes |
| `centres` | `/centres-etat-civil?commune={{data.communeMariage}}` | Centres rattachés |

### 2.5. Inventaire des formulaires userTask

| # | Fichier JSON | Lane | userTask BPMN | Description | Condition |
| --- | --- | --- | --- | --- | --- |
| 1 | `formio-demande-extrait-acte-mariage.json` | PORTAL | Soumission | Formulaire principal (5 onglets) | Toujours |
| 2 | `formio-correction-demande-extrait-acte-mariage.json`| PORTAL | Correction | Modification usager | Si erreurs notées |
| 3 | `formio-instruction-agent-etat-civil.json` | XFLOW | Instruction agent | Validation back-office | Toujours |

---

## 3. Le processus BPMN 2.0

### 3.1. Vue d'ensemble du processus TO-BE

| Champ | Valeur |
|---|---|
| **Nom du processus** | `Procedure_Extrait_Acte_Mariage_v1` |
| **Événement déclencheur** | Soumission du formulaire sur Xportal |
| **Événement de fin (succès)** | Retrait de l'acte au guichet ou expédition confirmée |
| **Événement de fin (rejet)** | Notification de rejet définitif |
| **Moteur d'exécution** | Xflow (Camunda Platform 7 — GNSPD Framework) |
| **Version processus** | 1.0 |
| **Participants BPMN** | Pool XPORTAL + Pool XFLOW |

### 3.2. Étapes détaillées du processus

#### Lane PORTAL — Côté Citoyen

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| 01 | Soumission et Paiement | L'usager remplit la demande. Le paiement est certifié avant confirmation de l'envoi MSG_START. | Système / Citoyen | Immédiat | → 02 |
| 02 | Attente vérification | Le citoyen est en attente du résultat de l'instruction dans sa boucle de resoumission. | Système / Citoyen | - | Si correction → 03 / Si décision finale → 04 |
| 03 | Réaliser la correction | L'usager a reçu une demande de changement et modifie. La soumission renvoie le dossier. | Citoyen | Max 15 j | → Retour 02 |
| 04 | Décision Finale | Notification d'acceptation (document physique prêt/expédié) ou de rejet définitif. | Système / Citoyen | Immédiat | → FIN |

#### Lane XFLOW — Côté Back-office

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| B01 | Initialisation | Xflow charge les données. Un accusé de réception est envoyé Odoo/LogiEC. | Système | Immédiat | → B02 |
| B02 | Service de vérification (Odoo) | Recherche dans la base numérique des actes de la commune choisie. | Système / Odoo | < 2 min | Trouvé → B04 / Non Trouvé → B03 |
| B03 | Recherche/Instruction Manuelle | L'agent de l'état civil recherche l'acte non numérisé et valide ou demande correction. | Agent État Civil | SLA : 48h | Conforme → B04 / Erreur → B06 / Rejet → B07 |
| B04 | Impression et Signature Officielle | L'officier certifie et signe l'acte de sa main. | Officier État Civil | SLA : 24h | → B05 |
| B05 | Notification Finale & Clôture | Envoi via SMS/Email de la convocation "Prêt" ou de la preuve d'expédition postale. Fin du token. | Système | Immédiat | → FIN (succès) |
| B06 | Sous-boucle Correction | MSG de correction envoyé à XPortal. XFlow passe en "WaitResub". | Système | < 5 min | → Attente resoumission → Retour B03 |
| B07 | Rejet définitif | Envoi de la notification de rejet définitif. | Système | < 5 min | → FIN (rejet) |

### 3.3. Matrice des échanges inter-pools (Kafka)

#### XPortal → XFlow
| # | Message Kafka (`messageRef`) | Émetteur (SendTask) | Récepteur (Start/ReceiveEvent) | Payload | Condition |
| --- | --- | --- | --- | --- | --- |
| 1 | `MSG_MARIAGE_START` | Soumission | StartEvent XFlow | Données formulaire + preuve paiement | Toujours |
| 2 | `MSG_MARIAGE_RESUB` | Resoumission citoyen | ReceiveTask resoumission | Données corrigées | Si correction demandée |

#### XFlow → XPortal
| # | Message Kafka (`messageRef`) | Émetteur (SendTask) | Récepteur (ReceiveTask) | Payload | Condition |
| --- | --- | --- | --- | --- | --- |
| 1 | `MSG_MARIAGE_CORRECT` | Notification correction | ReceiveTask correction | Motif correction | Si non conforme |
| 2 | `MSG_MARIAGE_FINAL` | Notification finale | ReceiveTask finale | Résultat (accepte/rejette) | Si décision finale |

#### Points de convergence
| ReceiveTask (convergence) | Pool | Entrées | Description |
| --- | --- | --- | --- |
| `ReceiveTask_Decision` | PORTAL | Résultats B04, B06, B07 | Porte unique d'entrée XPortal recevant les différents signaux depuis XFlow. |

#### Terminaisons du processus
| EndEvent | Pool | Condition | Notification associée |
| --- | --- | --- | --- |
| Fin succès | PORTAL | Dossier accepté | Acte Prêt / Acte Expédié |
| Fin rejet | PORTAL | Dossier rejeté | Notification de rejet |

### 3.4. Flux d'escalade temporelle

| Déclencheur | Canal | Action |
|---|---|---|
| Délai B03 instruction dépassé (7j ouvrés) | Email Dashboard | Escalade Superviseur |
| Délai correction usager dépassé (15 jours ouvrés) | SMS + Email | Rejet automatique (Timeout P15D) |

---

## 4. Règles métiers

| ID | Règle métier | Description / Condition | Priorité | Étapes concernées |
|---|---|---|---|---|
| RG-001 | Calcul tarifaire du document | Si `typeDocument` = "Copie intégrale" → Ajout de frais fixes (ex: 2000 FCFA). Extrait simple = 0. | HAUTE | Onglet 4 |
| RG-002 | Frais postaux variables | Si `modeRetrait` = "Envoi par La Poste" → Activation champ `adresseExpedition` (requis = true) et ajout des frais de livraison au total. | HAUTE | Onglet 4 |
| RG-003 | Identité sécurisée e-ID | `nomDemandeur` et `prenomDemandeur` sont en `disabled = true` et sourcés par `config.users`. Empêche la fraude documentaire. | HAUTE | Onglet 2 |
| RG-004 | Limitation tentatives de correction | L'usager a max 3 essais (`nbCorrections`). Au-delà, rejet automatique. | HAUTE | Étape 03 |
| RG-005 | Archivage longue durée | Tout acte final est loggué pendant 10 ans via système ATD. | HAUTE | Post-B05 |

---

## 5. Intégration avec des systèmes tiers

| Système cible | Type d'intégration | Données échangées | Condition d'appel | Statut |
|---|---|---|---|---|
| Plateforme Paiement e-Gov | Module Calculate Costs | Montant, référence | Soumission avec frais | À configurer |
| Odoo État Civil | API REST (recherche) | Mairie, Nom, Numero Acte | Étape B02 | À développer (selon mairie) |
| API La Poste Togo | API REST | Adresse complète du citoyen | Poste B05 (Si choix) | À configurer |
| Plateforme SMS ATD | API SMS / Email | Coordonnées et motif | Changer de statut | Disponible |

---

## 6. Notifications automatiques

| Réf. | Déclencheur | Canal | Destinataire | Message type |
|---|---|---|---|---|
| N01 | Soumission (B01) | SMS + Email | Usager | *Votre demande d'extrait d'acte de mariage [DOSSIER] est reçue.* |
| N02 | Correction (B06) | SMS + Email | Usager | *Votre demande [DOSSIER] requiert une modification : [motif]. Vous avez 15 jours.* |
| N03 | Document Prêt - Guichet (B05) | SMS + Email | Usager | *Votre acte légalisé [DOSSIER] est prêt. Présentez-vous à la mairie choisie.* |
| N04 | Document Expédié - Poste (B05)| SMS + Email | Usager | *Votre acte a été remis à La Poste. Suivi : [TRACKING].* |
| N05 | Rejet définitif (B07) | SMS + Email | Usager | *Votre demande [DOSSIER] est refusée. Motif : [motif].* |

---

## 7. KPIs du service & engagements SLA

| Indicateur | Valeur cible |
|---|---|
| **Taux de complétion des formulaires** | ≥ 85% |
| **Délai maximum d'instruction (agent)** | 48h ouvrées |
| **Délai maximum de signature (officier)** | 24h ouvrées |
| **Disponibilité service XFlow** | ≥ 99,5% |

---

## 8. Interface e-service DACS

| Champ | Valeur |
|---|---|
| **URL e-service** | https://services.dacs.gouv.tg/mariage [À confirmer] |
| **Charte graphique** | Couleurs officielles Mairie de la localité concernée |
| **Authentification** | OAUTH2 (Portail E-ID) |

---

## 9. Validations & signatures

| | Rédigé par | Validé par (FDS) | Approuvé par (ATD) |
|---|---|---|---|
| **Qualité** | Équipe ATD | Responsable DACS | Chef de Projet ATD |
| **Nom** | ________________________ | ________________________ | ________________________ |
| **Date** | _______________________ | _______________________ | _______________________ |
| **Signature** | __________________ | __________________ | __________________ |

---

*SRS — Demande d'extrait d'acte de mariage | v1.0 | ATD*
