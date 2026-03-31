# SERVICE REQUIREMENT SHEET
## DEMANDE DU DIPLÔME DU CFA
### Centre de Formation par Apprentissage — République Togolaise

---

| Champ | Valeur |
|---|---|
| **Fournisseur de Services (FDS)** | CFA — Centre de Formation par Apprentissage |
| **Service parent** | Direction de la Formation Professionnelle — METFP |
| **Intégrateur en charge** | [Nom de la société intégratrice] |
| **Chef de projet ATD** | [Nom du chef de projet] |
| **Point focal FDS** | [Nom du responsable côté CFA] |
| **Date de création** | 28 mars 2026 |
| **Date de dernière révision** | 28 mars 2026 (v1.0 — Version initiale) |
| **Date de validation** | _________________________________ |
| **Back-office utilisé** | Odoo Traitement (ATD — par défaut) |
| **Déploiement cible** | Xportal + Xflow + Interface e-service CFA |

---

## Historique des changements

| Version | Date | Auteur | Description des modifications |
|---|---|---|---|
| 1.0 | 28/03/2026 | Équipe ATD | Version initiale — rédaction après analyse Kobo et cartographies AS-IS / TO-BE |

---

## Table des matières

1. [Identification du service](#1-identification-du-service)
2. [Design du formulaire Form.io](#2-design-du-formulaire-formio)
3. [Le processus BPMN 2.0](#3-le-processus-bpmn-20)
4. [Règles métiers](#4-règles-métiers)
5. [Intégration avec des systèmes tiers](#5-intégration-avec-des-systèmes-tiers)
6. [Notifications automatiques](#6-notifications-automatiques)
7. [KPIs du service & engagements SLA](#7-kpis-du-service--engagements-sla)
8. [Interface e-service CFA](#8-interface-e-service-cfa)
9. [Validations & signatures](#9-validations--signatures)

---

## 1. Identification du service

### 1.1. Description fonctionnelle

Le diplôme du CFA (Centre de Formation par Apprentissage) est un titre officiel délivré par l'État togolais attestant qu'un apprenti a réussi son examen de fin de formation professionnelle. Il constitue une preuve reconnue de qualification dans un métier donné et est exigé pour l'accès à certains emplois, la poursuite d'études supérieures ou techniques, et l'obtention de financements. Ce document est délivré par la Direction des examens, concours et certifications du METFP.

La digitalisation de ce service permet au candidat reçu de soumettre sa demande de diplôme en ligne via Xportal, sans se déplacer, de suivre l'état de traitement de son dossier en temps réel, et de recevoir des notifications automatiques à chaque étape clé. Un parcours spécifique est prévu pour les demandes de duplicata, avec paiement en ligne sur la plateforme e-Gov externe.

### 1.2. Fiche d'identité du service

| Champ | Valeur |
|---|---|
| **Code service** | SRV-CFA-2026-001 |
| **Nom complet** | Demande du Diplôme du Centre de Formation par Apprentissage |
| **Catégorie** | Formation Professionnelle / Certification |
| **Bénéficiaires** | Candidats reçus à l'examen du CFA (citoyens togolais) |
| **Fréquence estimée** | [À renseigner par le FDS — estimation sessions annuelles] |
| **Délai standard de traitement** | [À renseigner par le CFA — délai cible en jours ouvrés] |
| **Délai réglementaire maximum** | [À renseigner par le FDS] |
| **Coût du service** | Gratuit (demande initiale) / Payant (duplicata — montant à préciser par le FDS) |
| **Langue(s)** | Français |
| **Canaux de dépôt** | Xportal (web / mobile) — Interface e-service CFA |

### 1.3. Acteurs et intervenants

| Acteur | Profil | Rôle dans le processus | Accès système | Responsabilité SLA |
|---|---|---|---|---|
| **Citoyen / Candidat** | Apprenti reçu à l'examen CFA | Soumet la demande, fournit les pièces, paie si duplicata, corrige si demandé, retire le diplôme | Xportal (formulaire + suivi) | Évaluateur du service |
| **Agent de vérification** | Agent CFA (N1 métier) | Vérifie la conformité du dossier, instruit la demande | Back-office Odoo | Selon SLA CFA |
| **Superviseur / Chef de service** | Responsable administratif CFA | Reçoit les escalades hors délai, valide en second niveau | Back-office — accès complet | Selon SLA CFA |
| **Système Xflow** | Orchestrateur BPMN | Routage automatique, notifications, timers d'escalade | Infrastructure ATD / CFA | Disponibilité ≥ 99,5% |
| **Admin Xportal (ATD)** | Technicien ATD | Surveillance, publication des formulaires, suivi KPIs | Administration Xportal | SLA plateforme |
| **Centre d'appel (N1)** | Agent support ATD | Assistance candidats en difficulté sur la démarche | Consultation statut uniquement | Résolution < 30 min |

---

## 2. Design du formulaire Form.io

### 2.1. Structure du formulaire

Le parcours est composé de **trois formulaires Form.io distincts** orchestrés par Xflow :

- **Formulaire principal (5 onglets)** : parcours commun à tous les candidats — soumission initiale.
- **Formulaire de paiement (conditionnel)** : activé uniquement pour les demandes de duplicata, entre la soumission initiale et l'instruction back-office.
- **Formulaire de correction** : activé lorsque l'agent demande des corrections — boucle de resoumission sans nouveau dossier.

#### Formulaire principal — 5 onglets Wizard

| Onglet | Titre | Remarques |
|---|---|---|
| Onglet 1 | Description — Qualification de la demande | Conditionne le parcours : duplicata ou demande initiale — bloquant si examen non réussi |
| Onglet 2 | Informations personnelles | Identité du candidat + personne à prévenir |
| Onglet 3 | Informations sur le centre d'examen | Région, préfecture, centre, numéro de table, spécialité, session |
| Onglet 4 | Pièces à fournir | Upload pièces — `copieDiplome` et `declarationPerte` conditionnels (duplicata) |
| Onglet 5 | Récapitulatif et soumission | Résumé non modifiable + confirmation + reCAPTCHA |

#### Formulaire de paiement — Conditionnel duplicata

| Formulaire | Slug | Condition de déclenchement |
|---|---|---|
| Paiement | `v1_paiement-de-la-demande-du-diplome-de-cfa` | `duplicata = Oui` — déclenché par Send Task Xflow (B02) |

#### Formulaire de correction — Boucle de resoumission

| Formulaire | Slug | Condition de déclenchement |
|---|---|---|
| Correction | `v1_correction-de-la-demande-du-diplome-de-cfa` | Déclenché par Send Task Xflow (B07) — si anomalies détectées |

### 2.2. Détail des champs

#### Onglet 1 — Description (Qualification de la demande)

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `duplicata` | S'agit-il d'une demande de duplicata ? | Radio | Oui | Oui / Non | Saisie | Conditionne le parcours paiement (RG-001) |
| `exam` | Avez-vous réussi votre examen CFA ? | Radio | Oui | Oui / Non | Saisie | Si Non → blocage avec message explicatif (RG-002) |

#### Onglet 2 — Informations personnelles

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `nom` | Nom | Texte | Oui | Majuscules, max 60 car. | e-ID / Saisie | Pré-rempli si disponible via e-ID — transformé en majuscules |
| `prenoms` | Prénoms | Texte | Oui | Max 100 caractères | e-ID / Saisie | Pré-rempli si disponible via e-ID |
| `dateNaissance` | Date de naissance | Date | Oui | DD/MM/YYYY | e-ID / Saisie | Doit être ≥ 14 ans (RG-003) |
| `lieuNaissance` | Lieu de naissance | Texte | Oui | Max 80 caractères | Saisie | |
| `adresseResidence` | Adresse de résidence | Texte | Non | Max 150 caractères | Saisie | Optionnel |
| `numeroTelephone` | Numéro de téléphone | Téléphone | Oui | +228 XXXXXXXX | e-ID / Saisie | Validation format E.164 — utilisé pour les notifications |
| `eMail` | E-mail | Email | Non | Format RFC 5322 | Saisie | Pour notifications e-mail si renseigné |
| `nomPrenomsPersonneAPrevenir` | Nom et Prénoms (personne à prévenir) | Texte | Oui | Max 100 car. | Saisie | Contact d'urgence |
| `numeroTelephonePersonneAPrevenir` | Téléphone (personne à prévenir) | Téléphone | Oui | +228 XXXXXXXX | Saisie | |
| `adresseResidencePersonneAPrevenir` | Adresse (personne à prévenir) | Texte | Oui | Max 150 car. | Saisie | |

#### Onglet 3 — Informations sur le centre d'examen

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `regionExamen` | Région | Select | Oui | Référentiel régions TG | Référentiel | Filtre les préfectures disponibles (dépendance en cascade) |
| `prefectureExamen` | Préfecture | Select | Oui | Filtré par `regionExamen` | Référentiel | Dépend du champ `regionExamen` |
| `centreExamen` | Centre d'examen | Texte | Oui | Max 100 caractères | Saisie | Nom officiel du centre CFA |
| `numeroDeTable` | Numéro de table | Texte | Oui | Alphanum. max 20 car. | Saisie | Tel qu'indiqué sur la convocation |
| `specialite` | Spécialité | Select | Oui | Référentiel métiers CFA | Référentiel | Filtre les sessions disponibles |
| `session` | Session de (Année) | Select | Oui | AAAA | Référentiel | Années disponibles dans le système |

#### Onglet 4 — Pièces à fournir

Formats acceptés : PDF, JPG, PNG. Taille maximale : 2 Mo par fichier.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Remarques |
|---|---|---|---|---|---|
| `acteDeNaissance` | Acte de naissance (copie légalisée) | Fichier | Oui | PDF/JPG/PNG ≤ 2 Mo | Document officiel de naissance |
| `releveDeNotes` | Relevé de notes de l'examen CFA | Fichier | Oui | PDF/JPG/PNG ≤ 2 Mo | Relevé signé par le centre |
| `copieDiplome` | Copie du diplôme original | Fichier | Conditionnel | PDF/JPG/PNG ≤ 2 Mo | Obligatoire uniquement si `duplicata = Oui` (RG-004) |
| `declarationPerte` | Déclaration de perte | Fichier | Conditionnel | PDF/JPG/PNG ≤ 2 Mo | Obligatoire si `duplicata = Oui` (RG-004) |

#### Onglet 5 — Récapitulatif et soumission

| Nom du champ | Libellé affiché | Type | Obligatoire | Remarques |
|---|---|---|---|---|
| `luEtApprouve` | Je déclare et certifie sur l'honneur que les informations contenues dans ce dossier sont correctes et exactes. | Checkbox | Oui | Bloque la soumission si non coché |
| `captcha` | Vérification anti-robot | reCAPTCHA | Oui | Google reCAPTCHA v3 — score minimum 0.5 |

#### Formulaire de paiement — Détail des champs

Ce formulaire est pré-rempli par Xflow. Le candidat ne saisit aucune donnée : il consulte le montant à régler et est redirigé vers la plateforme e-Gov externe.

| Nom du champ | Libellé affiché | Type | Obligatoire | Remarques |
|---|---|---|---|---|
| `html` | Texte introductif | HTML (h4) | N/A | *« Vous allez procéder au paiement des frais pour la demande de duplicata du diplôme du CFA qui s'élèvent à : »* |
| `serviceTitle` | Paiement de la demande du diplôme de CFA | HTML (h2) | N/A | Titre affiché — non modifiable |
| `montantAPayer` | Montant à payer | Texte (désactivé) | Non | Injecté par Xflow depuis référentiel tarifaire — `disabled=true` |
| `dynamicCost` | Dynamic Cost | Texte (caché) | Non | `hidden=true`, `clearOnHide=false` — valeur dynamique pour calcul moteur |

**Propriétés techniques du formulaire de paiement :**

| Propriété | Valeur |
|---|---|
| **Slug** | `v1_paiement-de-la-demande-du-diplome-de-cfa` |
| **Déclencheur** | Send Task Xflow — étape B02 (message : `DIPLOMECFA_PAYMENT_REQUEST`) |
| **Condition** | `duplicata = Oui` uniquement |
| **Action post-paiement** | Receive Task B03 — attend la confirmation asynchrone de la plateforme e-Gov |

#### Formulaire de correction — Détail des champs

Le formulaire de correction reprend les champs du formulaire principal dont la correction est demandée, en mode édition. Les champs non concernés par la correction sont désactivés (`disabled`).

| Nom du champ | Libellé affiché | Type | Obligatoire | Remarques |
|---|---|---|---|---|
| `correctionInstructions` | Instructions de correction | HTML | N/A | Bloc HTML injecté par Xflow — liste précise des corrections demandées par l'agent |
| *(champs identiques au formulaire principal)* | — | — | Selon champ | Seuls les champs concernés par la correction sont actifs |

**Propriétés techniques du formulaire de correction :**

| Propriété | Valeur |
|---|---|
| **Slug** | `v1_correction-de-la-demande-du-diplome-de-cfa` |
| **Déclencheur** | Send Task Xflow — étape B07 |
| **Condition** | Anomalies détectées lors de l'instruction (B06) |
| **Action post-correction** | Resoumission → réintègre le cycle B04 sans nouveau dossier |

### 2.3. Actions du formulaire (P-Studio)

| Action | Déclencheur | Description |
|---|---|---|
| **Calculate Costs** | `duplicata = Oui` à l'onglet 1 | Interroge le référentiel tarifaire CFA et injecte le montant dans `montantAPayer` |
| **Submit** | Clic « Soumettre ma demande » | Publie le dossier dans Xflow via le topic Kafka `bpmn.commands` |
| **Save Draft** | Navigation entre onglets | Sauvegarde automatique du brouillon à chaque changement d'onglet |

### 2.4. Configuration des environnements

| Paramètre | Valeur |
|---|---|
| **Groupe Form.io principal** | [À renseigner — groupe dédié CFA] |
| **Groupe Form.io paiement** | [À renseigner] |
| **Groupe Form.io correction** | [À renseigner] |
| **Topic Kafka** | `bpmn.commands` |
| **Message de démarrage Xflow** | `DIPLOMECFA_START` |
| **Message de paiement** | `DIPLOMECFA_PAYMENT_REQUEST` |
| **Message de correction** | `DIPLOMECFA_CORRECTION_REQUEST` |

### 2.5. Inventaire des formulaires userTask

| Formulaire | Slug | Type | Acteur | Étape BPMN |
|---|---|---|---|---|
| Formulaire principal | `v1_demande-du-diplome-de-cfa` | Soumission initiale | Citoyen | C01 |
| Formulaire paiement | `v1_paiement-de-la-demande-du-diplome-de-cfa` | UserTask paiement | Citoyen | B02 |
| Formulaire correction | `v1_correction-de-la-demande-du-diplome-de-cfa` | UserTask correction | Citoyen | B07 |
| Formulaire instruction agent | `v1_instruction-demande-du-diplome-de-cfa` | UserTask back-office | Agent CFA | B06 |

---

## 3. Le processus BPMN 2.0

### 3.1. Vue d'ensemble du processus TO-BE

| Champ | Valeur |
|---|---|
| **Nom du processus** | `Procédure_Demande_Diplome_CFA_v1` |
| **Événement déclencheur** | Soumission du formulaire par le candidat sur Xportal |
| **Événement de fin (succès)** | Notification d'acceptation + diplôme disponible au retrait |
| **Événement de fin (rejet)** | Notification de rejet définitif motivé au candidat |
| **Moteur d'exécution** | Xflow (Camunda Platform 7) |
| **Version processus** | 1.0 |
| **Pools BPMN** | `Process_Portal` (XPortal — isExecutable=true) + `Process_Xflow` (XFlow — isExecutable=true) |

### 3.2. Étapes détaillées du processus

#### Pool PORTAL — Côté Citoyen

| N° | Nom de l'étape | Type BPMN | Description | Acteur | Résultat / Condition |
|---|---|---|---|---|---|
| C01 | Demande de diplôme CFA | StartEvent (Message) | Le candidat soumet le formulaire depuis Xportal. Un numéro de dossier unique est généré. Notification SMS/e-mail de réception envoyée. | Citoyen | → Envoi message Kafka vers Xflow |
| C02 | Réception demande de paiement | ReceiveTask | Si duplicata : le citoyen reçoit une notification de paiement via Xportal. | Système | → C03 si `duplicata = Oui` |
| C03 | Effectuer le paiement | UserTask | Le citoyen accède au formulaire de paiement et est redirigé vers la plateforme e-Gov externe (Flooz, TMoney, Visa, Mastercard). | Citoyen | → Confirmation asynchrone → C04 |
| C04 | Réception notification vérification | ReceiveTask | Le citoyen reçoit une notification de statut : en cours / correction requise / décision finale. | Système | Si correction → C05 / Si fin → C06 |
| C05 | Faire les corrections | UserTask | Le citoyen accède au formulaire de correction dans Xportal, modifie les données ou pièces et resoumet. Timer : 5 jours ouvrés (P5D). | Citoyen | → Resoumission → Retour C04 |
| C06 | Réception notification finale | ReceiveTask | Le citoyen reçoit la décision finale : acceptation ou rejet définitif avec motif. | Système | → EndEvent |

#### Pool XFLOW — Côté Back-Office

| N° | Nom de l'étape | Type BPMN | Description | Acteur | Résultat / Condition |
|---|---|---|---|---|---|
| B01 | Initialisation procédure | StartEvent (Message) | Xflow reçoit le message `DIPLOMECFA_START` depuis Xportal. Chargement des données. Gateway `duplicata ?` évaluée. | Système | Si `duplicata = Oui` → B02 / Sinon → B04 |
| B02 | Demande paiement (duplicata) | SendTask | Xflow envoie au portail la demande de paiement avec montant (référentiel tarifaire). Message : `DIPLOMECFA_PAYMENT_REQUEST`. | Système | → B03 |
| B03 | Attente confirmation paiement | ReceiveTask | Attente asynchrone de la confirmation e-Gov. Timer : P2D. Si délai dépassé → annulation + notification. | Système | Paiement OK → B04 / Délai dépassé → B09 |
| B04 | Extraction et normalisation données | ScriptTask | Extraction et normalisation des données du formulaire. Vérification automatique : format, cohérence, complétude. | Système | → B05 |
| B05 | Vérification candidat Odoo | ServiceTask | Interrogation API Odoo : vérification inscription du candidat, réussite à l'examen, spécialité et session déclarées. | Système + Odoo | Inscrit et reçu → B06 / Non trouvé → B09 |
| B06 | Instruction du dossier | UserTask | User task assignée à l'agent CFA : examen du dossier, vérification des pièces, cohérence. Interface Odoo. `camunda:formKey` : `v1_instruction-demande-du-diplome-de-cfa`. SLA : selon CFA. | Agent CFA | Conforme → B08 / Corrections → B07 / Rejet → B09 |
| B07 | Notification correction | SendTask | Envoi de la notification de correction au portail avec liste précise des corrections. Message : `DIPLOMECFA_CORRECTION_REQUEST`. Timer citoyen : P5D. | Système | → Attente resoumission → Retour B04 |
| B08 | Enregistrement décision | ServiceTask | Enregistrement de la décision d'acceptation. Génération du récépissé de validation. | Système | → B10 |
| B09 | Envoi rejet définitif | SendTask | Notification de rejet définitif avec motif détaillé. Message vers portail + SMS + e-mail. | Système | → EndEvent (rejet) |
| B10 | Notification acceptation | SendTask | Notification d'acceptation au portail. Diplôme en cours d'édition / disponible au retrait. | Système | → EndEvent (succès) |

### 3.3. Matrice des échanges inter-pools (Kafka)

| Message | Émetteur | Récepteur | Déclencheur | Topic |
|---|---|---|---|---|
| `DIPLOMECFA_START` | XPortal (C01) | XFlow (B01) | Soumission formulaire | `bpmn.commands` |
| `DIPLOMECFA_PAYMENT_REQUEST` | XFlow (B02) | XPortal (C02) | `duplicata = Oui` | `bpmn.commands` |
| `DIPLOMECFA_PAYMENT_CONFIRM` | Plateforme e-Gov | XFlow (B03) | Paiement effectué | `bpmn.commands` |
| `DIPLOMECFA_CORRECTION_REQUEST` | XFlow (B07) | XPortal (C04) | Anomalies instruction | `bpmn.commands` |
| `DIPLOMECFA_RESUBMIT` | XPortal (C05) | XFlow (B04) | Resoumission citoyen | `bpmn.commands` |
| `DIPLOMECFA_ACCEPTED` | XFlow (B10) | XPortal (C06) | Décision acceptation | `bpmn.commands` |
| `DIPLOMECFA_REJECTED` | XFlow (B09) | XPortal (C06) | Décision rejet | `bpmn.commands` |

### 3.4. Flux d'escalade temporelle

| Déclencheur | Timer | Canal | Action |
|---|---|---|---|
| Délai instruction agent dépassé | Selon SLA CFA | Email + Dashboard Odoo | Escalade automatique vers superviseur CFA |
| Délai correction citoyen dépassé | P5D (5 jours ouvrés) | SMS + Email | Rejet automatique — statut `Rejeté — délai dépassé` |
| Délai confirmation paiement dépassé | P2D (48h) | SMS + Email | Annulation automatique de la demande |
| Indisponibilité Xflow > 15 min | P0015M | Email Admin | Alerte automatique Admin ATD |

---

## 4. Règles métiers

| ID | Règle | Description / Condition | Priorité | Étapes concernées |
|---|---|---|---|---|
| RG-001 | Parcours duplicata | Si `duplicata = Oui` → activation du sous-parcours paiement. Les pièces `copieDiplome` et `declarationPerte` deviennent obligatoires. | HAUTE | C01, B01, B02 |
| RG-002 | Réussite examen obligatoire | Si `exam = Non` → blocage immédiat de la soumission avec message : *« Vous devez avoir réussi votre examen CFA pour déposer cette demande. »* | HAUTE | Onglet 1 formulaire |
| RG-003 | Âge minimum du candidat | Le candidat doit avoir au moins 14 ans à la date de soumission. Vérification sur `dateNaissance`. Message bloquant si non respecté. | HAUTE | Onglet 2 formulaire |
| RG-004 | Pièces duplicata conditionnelles | Si `duplicata = Oui`, les champs `copieDiplome` et `declarationPerte` passent obligatoires dynamiquement (`required = true`). | HAUTE | Onglet 4 formulaire |
| RG-005 | Vérification Odoo obligatoire | Le numéro de table, la spécialité et la session doivent correspondre à un candidat inscrit et reçu dans la base Odoo du CFA. | HAUTE | B05 |
| RG-006 | Une demande active par candidat | Un candidat identifié par son numéro de table ne peut avoir qu'une seule demande active en cours. Bloquer la nouvelle soumission avec message explicatif. | HAUTE | C01 |
| RG-007 | Délai correction citoyen | Le candidat dispose de 5 jours ouvrés pour soumettre un dossier corrigé. Au-delà → dossier clôturé automatiquement (statut : *Rejeté — délai dépassé*). | HAUTE | C05, B07 |
| RG-008 | Paiement duplicata préalable | Le processus d'instruction ne démarre qu'après confirmation effective du paiement pour les demandes de duplicata. | HAUTE | B02, B03 |
| RG-009 | Conformité pièces jointes | Formats acceptés : PDF/JPG/PNG. Taille max : 2 Mo par fichier. Tout fichier non conforme est rejeté avec message explicite. | MOYENNE | Onglet 4, B04 |
| RG-010 | Maximum 3 itérations correction | Le dossier peut être corrigé et renvoyé au maximum 3 fois. À la 3e anomalie consécutive → rejet définitif. | HAUTE | Boucle B07 → B04 |
| RG-011 | Archivage 10 ans | Tous les dossiers (approuvés et rejetés) doivent être archivés pendant 10 ans minimum conformément aux obligations légales togolaises. | HAUTE | Post-décision |

---

## 5. Intégration avec des systèmes tiers

| Système cible | Type d'intégration | Données échangées | Condition d'appel | Statut |
|---|---|---|---|---|
| **Base Odoo CFA** | API interne (lecture) | Numéro de table, spécialité, session, résultat examen | Étape B05 — Vérification inscription | Disponible |
| **Plateforme e-Gov (paiement)** | API REST (redirect + callback) | Montant, référence dossier, statut paiement | Étape B02 — Duplicata uniquement | À configurer |
| **Plateforme SMS / Email** | API REST (envoi) | Numéro de téléphone, e-mail, texte message, référence dossier | À chaque changement de statut | Disponible |
| **Système archivage ATD** | API interne | Dossier complet (formulaire + pièces + décision) | Post-décision — archivage automatique | Disponible |
| **e-ID Togo** | API REST (vérification — optionnel) | Nom, Prénoms, Date de naissance | Pré-remplissage formulaire citoyen | À développer |

---

## 6. Notifications automatiques

| Réf. | Déclencheur | Canal | Destinataire | Message type |
|---|---|---|---|---|
| N01 | Soumission formulaire (C01) | SMS + Email | Candidat | *Votre demande de diplôme CFA (réf. [DOSSIER]) a bien été reçue. Délai de traitement : [X] jours ouvrés.* |
| N02 | Demande de paiement — duplicata (B02) | SMS + Notification XPortal | Candidat | *Une demande de paiement de [MONTANT] FCFA a été générée pour votre demande de duplicata [DOSSIER]. Rendez-vous sur votre espace Xportal.* |
| N03 | Confirmation paiement reçu (B03) | SMS | Candidat | *Votre paiement a été confirmé. Votre dossier est en cours d'instruction.* |
| N04 | Corrections demandées (B07) | SMS + Email + Notification XPortal | Candidat | *Votre dossier [DOSSIER] nécessite des corrections. Corrections requises : [liste]. Vous avez 5 jours ouvrés pour soumettre.* |
| N05 | Resoumission reçue (C05) | SMS | Candidat | *Votre dossier corrigé [DOSSIER] a bien été reçu. Traitement en cours.* |
| N06 | Décision d'acceptation (B10) | SMS + Email | Candidat | *Votre demande [DOSSIER] a été acceptée. Votre diplôme est en cours de préparation. Vous serez notifié(e) pour le retrait.* |
| N07 | Rejet définitif (B09) | SMS + Email | Candidat | *Votre demande [DOSSIER] a été rejetée. Motif : [MOTIF]. Vous pouvez soumettre une nouvelle demande après correction.* |
| N08 | Rappel agent — délai à risque | Email + Dashboard Odoo | Agent CFA | *Rappel : Le dossier [DOSSIER] doit être traité avant [DATE_LIMITE].* |
| N09 | Escalade superviseur | Email + Dashboard Odoo | Superviseur CFA | *Escalade automatique : Le dossier [DOSSIER] dépasse le délai d'instruction. Action requise.* |
| N10 | Invitation évaluation (J+1 décision) | SMS + Email | Candidat | *Êtes-vous satisfait(e) de votre expérience ? Évaluez ce service en 30 secondes sur Xportal.* |

---

## 7. KPIs du service & engagements SLA

| Indicateur | Valeur cible |
|---|---|
| **Taux de complétion formulaire** | ≥ 85% (dossiers soumis / formulaires initiés) |
| **Taux d'abandon** | ≤ 15% |
| **Délai standard de traitement** | [À renseigner par le CFA — objectif en jours ouvrés] |
| **Délai réglementaire maximum** | [À renseigner par le FDS] |
| **Délai notification accusé de réception** | < 5 minutes après soumission |
| **Délai vérification automatique Odoo** | < 5 minutes |
| **Taux de rejet** | ≤ 10% |
| **Taux de dossiers nécessitant correction** | ≤ 20% |
| **Note de satisfaction usager** | ≥ 4,0 / 5 |
| **Taux de résolution N1 (FCR)** | ≥ 80% |
| **Disponibilité plateforme** | ≥ 99,5% mensuel |
| **Délai correction citoyen** | Max 5 jours ouvrés (RG-007) |
| **Délai confirmation paiement** | Max 48h (RG-008) |

---

## 8. Interface e-service CFA

En complément de Xportal, une interface e-service aux couleurs du CFA sera développée et déployée sur un domaine dédié. Cette interface est visuellement indépendante de Xportal mais techniquement interconnectée.

| Champ | Valeur |
|---|---|
| **URL e-service** | https://services.cfa.gouv.tg/diplome [À confirmer avec le FDS] |
| **Charte graphique** | Couleurs officielles CFA — logo, typographie, palette fournis par le FDS |
| **Fonctionnalités** | Accès direct au formulaire, suivi de dossier, notifications statut, FAQ |
| **Authentification** | Identique à Xportal (SSO ATD) |
| **Backend** | Partage du même processus Xflow — données synchronisées en temps réel |
| **Responsabilité design** | Intégrateur (en concertation avec le service communication CFA) |
| **Livrables attendus** | Maquettes HTML/CSS validées par CFA + intégration Form.io |

---

## 9. Validations & signatures

Le présent SRS a été élaboré à l'issue des ateliers d'analyse conduits entre l'intégrateur, l'équipe ATD et les points focaux du CFA. Il constitue la référence contractuelle pour le développement, les tests et la mise en production du service.

| | Rédigé par | Validé par (FDS) | Approuvé par (ATD) |
|---|---|---|---|
| **Qualité** | Intégrateur Externe | Point focal CFA | Chef de projet ATD |
| **Nom** | ________________________ | ________________________ | ________________________ |
| **Date** | _______________________ | _______________________ | _______________________ |
| **Signature** | __________________ | __________________ | __________________ |

---

*SRS — Demande du Diplôme du CFA | v1.0 | ATD — 28/03/2026*
