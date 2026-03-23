# SERVICE REQUIREMENT SHEET
## DEMANDE DU DIPLÔME DU CFA
### Centre de Formation par Apprentissage — République Togolaise

---

| Champ | Valeur |
|---|---|
| **Fournisseur de Services (FDS)** | CFA — Centre de Formation par Apprentissage |
| **Service parent** | Direction de la Formation Professionnelle |
| **Intégrateur en charge** | [Nom de la société intégratrice] |
| **Chef de projet ATD** | [Nom du chef de projet] |
| **Point focal FDS** | [Nom du responsable côté CFA] |
| **Date de création** | 18 mars 2026 |
| **Date de dernière révision** | 18 mars 2026 (v1.1 — ajout formulaire paiement) |
| **Date de validation** | _________________________________ |
| **Back-office utilisé** | Odoo Traitement (ATD — par défaut) |
| **Déploiement cible** | Xportal + Xflow + Interface e-service CFA |

---

## Historique des changements

| Version | Date | Auteur | Description des modifications |
|---|---|---|---|
| 1.0 | 18/03/2026 | Équipe ATD | Version initiale — rédaction après analyse du formulaire principal et du processus BPMN |
| 1.1 | 18/03/2026 | Équipe ATD | Ajout du formulaire de paiement (duplicata) — sections 2.1 et 2.2 enrichies |

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

Le diplôme du CFA (Centre de Formation par Apprentissage) est un titre officiel délivré par l'État togolais attestant qu'un apprenti a réussi son examen de fin de formation professionnelle. Il constitue une preuve reconnue de qualification dans un métier donné et est exigé pour l'accès à certains emplois, la poursuite d'études supérieures ou techniques, et l'obtention de financements.

La digitalisation de ce service permet au candidat reçu de soumettre sa demande de diplôme en ligne via Xportal sans se déplacer, de suivre l'état de traitement de son dossier en temps réel, et de recevoir une notification dès que son diplôme est disponible. Un parcours spécifique est prévu pour les demandes de duplicata, avec paiement en ligne.

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
| **Coût du service** | Gratuit (demande initiale) / Payant (duplicata — montant à préciser) |
| **Langue(s)** | Français |
| **Canaux de dépôt** | Xportal (web / mobile) — Interface e-service CFA |

### 1.3. Acteurs et intervenants

Cette section liste tous les acteurs impliqués dans le cycle de vie de la demande.

| Acteur | Profil | Rôle dans le processus | Accès système | Responsabilité SLA |
|---|---|---|---|---|
| **Citoyen / Candidat** | Apprenti reçu au CFA | Soumet la demande, fournit les pièces, reçoit la notification | Xportal (lecture seule) | Évaluateur du service |
| **Agent de vérification** | Agent CFA (N1 métier) | Vérifie la conformité du dossier, lance l'instruction | Back-office — Odoo Traitement | Délai : selon SLA CFA |
| **Superviseur / Chef de service** | Responsable administratif CFA | Valide et signe le dossier après vérification | Back-office — accès complet | Délai : selon SLA CFA |
| **Système Xflow** | Orchestrateur BPMN | Routage automatique, notifications, escalades temporelles | Infrastructure ATD / CFA | Disponibilité 99,5% |
| **Admin Xportal (ATD)** | Technicien ATD | Surveillance, publication, KPIs | Administration Xportal | SLA plateforme |
| **Centre d'appel (N1)** | Agent support ATD | Assistance candidats en difficulté sur la démarche | Consultation statut uniquement | Résolution < 30 min |

---

## 2. Design du formulaire Form.io

### 2.1. Structure du formulaire

Le parcours est composé de deux formulaires Form.io distincts orchestrés par Xflow :

- **Formulaire principal (5 onglets)** : parcours commun à tous les candidats.
- **Formulaire de paiement (1 onglet, conditionnel)** : activé uniquement pour les demandes de duplicata, entre la soumission initiale et l'instruction back-office.

#### Formulaire principal — 5 onglets wizard

| Onglet | Titre | Remarques |
|---|---|---|
| Onglet 1 | Description — Qualification de la demande | Conditionne le parcours : duplicata ou demande initiale |
| Onglet 2 | Informations personnelles | Identité du candidat + personne à prévenir |
| Onglet 3 | Informations sur le centre d'examen | Région, préfecture, centre, numéro de table, spécialité, session |
| Onglet 4 | Pièces à fournir | Upload pièces — `copieDiplome` et `declarationPerte` conditionnels (duplicata) |
| Onglet 5 | Récapitulatif et soumission | Résumé non modifiable + confirmation + CAPTCHA |

#### Formulaire de paiement — Conditionnel duplicata

Ce formulaire est un composant Form.io indépendant (slug : `v1_paiement-de-la-demande-du-diplome-de-cfa`), déclenché par Xflow via une Send Task après la soumission initiale, uniquement lorsque `duplicata = Oui`. Il s'affiche dans Xportal comme une tâche utilisateur intercalée avant l'instruction back-office.

| Formulaire | Titre | Condition de déclenchement |
|---|---|---|
| Paiement | Paiement de la demande du diplôme de CFA | `duplicata = Oui` uniquement — déclenché par Xflow (étape B02) |

### 2.2. Détail des champs

#### Onglet 1 — Description (Qualification de la demande)

Cet onglet conditionne le parcours : demande initiale vs duplicata, et vérifie la réussite à l'examen.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `duplicata` | S'agit-il d'une demande de duplicata ? | Radio | Oui | Oui / Non | Saisie | Conditionne le parcours paiement (RG-001) |
| `exam` | Avez-vous réussi votre examen CFA ? | Radio | Oui | Oui / Non | Saisie | Si Non → blocage avec message explicatif (RG-002) |

#### Onglet 2 — Informations personnelles

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `nom` | Nom | Texte | Oui | Majuscules, max 60 car. | Saisie | Transformé en majuscules automatiquement |
| `prenoms` | Prénoms | Texte | Oui | Max 100 caractères | Saisie | |
| `dateNaissance` | Date de naissance | Date | Oui | DD/MM/YYYY | Saisie | Doit être ≥ 14 ans (RG-003) |
| `lieuNaissance` | Lieu de naissance | Texte | Oui | Max 80 caractères | Saisie | |
| `adresseResidence` | Adresse de résidence | Texte | Non | Max 150 caractères | Saisie | Optionnel |
| `numeroTelephone` | Numéro de téléphone | Téléphone | Oui | +228 XXXXXXXX | Saisie | Validation format E.164 |
| `eMail` | E-mail | Email | Non | Format RFC 5322 | Saisie | Pour notifications si renseigné |
| `nomPrenomsPersonneAPrevenir` | Nom et Prénoms (personne à prévenir) | Texte | Oui | Max 100 car. | Saisie | Contact d'urgence |
| `numeroTelephonePersonneAPrevenir` | Téléphone (personne à prévenir) | Téléphone | Oui | +228 XXXXXXXX | Saisie | |
| `adresseResidencePersonneAPrevenir` | Adresse (personne à prévenir) | Texte | Oui | Max 150 car. | Saisie | |

#### Onglet 3 — Informations sur le centre d'examen

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `regionExamen` | Région | Liste déroulante | Oui | Référentiel régions TG | Référentiel | Filtre les préfectures disponibles |
| `prefectureExamen` | Préfecture | Liste déroulante | Oui | Filtré par région | Référentiel | Dépend du champ `regionExamen` |
| `centreExamen` | Centre d'examen | Texte | Oui | Max 100 caractères | Saisie | Nom officiel du centre CFA |
| `numeroDeTable` | Numéro de table | Texte | Oui | Alphanum. max 20 | Saisie | Tel qu'indiqué sur la convocation |
| `specialite` | Spécialité | Liste déroulante | Oui | Référentiel métiers CFA | Référentiel | Filtre les sessions disponibles |
| `session` | Session de (Année) | Liste déroulante | Oui | AAAA | Référentiel | Années disponibles dans le système |

#### Onglet 4 — Pièces à fournir

Les fichiers sont uploadés directement dans Xportal et transmis à Xflow. Formats acceptés : PDF, JPG, PNG.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `acteDeNaissance` | Acte de naissance | Fichier | Oui | PDF/JPG/PNG < 2 Mo | Upload | Document officiel de naissance |
| `releveDeNotes` | Relevé de notes | Fichier | Oui | PDF/JPG/PNG < 2 Mo | Upload | Relevé signé par le centre |
| `copieDiplome` | Copie du diplôme | Fichier | Conditionnel | PDF/JPG/PNG < 2 Mo | Upload | Obligatoire uniquement si duplicata (RG-004) |
| `declarationPerte` | Déclaration de perte | Fichier | Conditionnel | PDF/JPG/PNG < 2 Mo | Upload | Obligatoire si duplicata (RG-005) |

#### Formulaire de paiement — Détail des champs (duplicata uniquement)

Ce formulaire est pré-rempli par Xflow. Le candidat ne saisit aucune donnée : il consulte le montant à régler et est redirigé vers la plateforme de paiement.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `html` | Texte introductif | HTML (h4) | N/A | Statique | Système | Message : *« Vous allez procéder au paiement des frais pour la demande de duplicata du diplôme du CFA qui s'élèvent à : »* |
| `serviceTitle` | Paiement de la demande du diplôme de CFA | HTML (h2) | N/A | Statique | Système | Titre affiché en h2 — non modifiable |
| `montantAPayer` | Montant à payer | Texte (désactivé) | Non | Numérique — injecté par Xflow | Xflow | Champ en lecture seule (`disabled=true`). Valeur transmise par le processus depuis le référentiel tarifaire CFA |
| `dynamicCost` | Dynamic Cost | Texte (caché) | Non | Numérique — calculé par le moteur | Xflow | Champ `hidden=true`, `clearOnHide=false`. Valeur dynamique utilisée par Xflow pour le calcul du montant final. Non visible de l'usager. |

**Propriétés techniques du formulaire de paiement :**

| Propriété technique | Valeur |
|---|---|
| **Slug du formulaire** | `v1_paiement-de-la-demande-du-diplome-de-cfa_tue-07-jan-2025` |
| **Version** | 43 (`locked = true`, `status = Active`) |
| **Groupe Form.io** | `e77adf12-f837-40ae-8d6c-01d1bb4c51b1` |
| **Déclencheur processus** | Send Task Xflow — étape B02 (message : `DIPLOMECFA_PAYMENT_REQUEST`) |
| **Condition d'affichage** | `duplicata = Oui` — formulaire invisible pour les demandes initiales |
| **Action post-paiement** | Receive Task Xflow — étape B03 attend la confirmation de paiement avant de continuer |

#### Onglet 5 — Récapitulatif et soumission

L'onglet 5 affiche un résumé non modifiable de toutes les données saisies. Le candidat coche une case de confirmation et clique sur « Soumettre ma demande ». Une notification SMS/email est envoyée avec le numéro de dossier.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `luEtApprouve` | Je déclare et certifie sur l'honneur que les informations contenues dans ce dossier sont correctes et exactes. | Checkbox | Oui | Doit être coché | Saisie | Bloque la soumission si non coché |
| `captcha` | Vérification anti-robot | reCAPTCHA | Oui | Google reCAPTCHA v3 | Système | Score minimum : 0.5 |

---

## 3. Le processus BPMN 2.0

### 3.1. Vue d'ensemble du processus TO-BE

Le processus complet est modélisé sur P-Studio (Camunda Web Modeler). Le diagramme BPMN est joint en annexe (fichier `.bpmn`). Ce tableau décrit chaque étape avec ses acteurs, délais et conditions.

| Champ | Valeur |
|---|---|
| **Nom du processus** | `Procédure_Demande_Diplome_CFA_v1` |
| **Événement déclencheur** | Soumission du formulaire par le candidat sur Xportal |
| **Événement de fin (succès)** | Notification du candidat + mise à disposition de la décision (diplôme signé) |
| **Événement de fin (rejet)** | Notification de rejet définitif motivé au candidat |
| **Moteur d'exécution** | Xflow (Camunda Cloud 8.8.0) |
| **Version processus** | 1.0 |
| **Participants BPMN** | PORTAL (lane citoyen) + XFLOW (lane back-office) |

### 3.2. Étapes détaillées du processus

#### Lane PORTAL — Côté Citoyen

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| 01 | Demande de diplôme | Le candidat soumet le formulaire depuis Xportal. Un numéro de dossier unique est généré. Le système envoie immédiatement le dossier au back-office via message Kafka. | Système / Citoyen | Immédiat | → Étape 02 |
| 02 | Soumission au back-office | Xflow reçoit les données du formulaire. Un événement de démarrage est déclenché dans le processus XFLOW. La gateway « duplicata ? » est évaluée. | Système | < 5 min | Si duplicata → 03 / Sinon → 06 |
| 03 | Réception demande de paiement | Si duplicata : le citoyen reçoit une demande de paiement via notification Xportal. | Système / Citoyen | < 15 min | → Étape 04 |
| 04 | Effectuer le paiement | Le citoyen accède à l'interface de paiement et règle le montant du duplicata (paiement mobile money / carte). | Citoyen | À la demande | → Étape 05 |
| 05 | Confirmation de paiement | Xflow reçoit la confirmation de paiement depuis le système de paiement. La boucle de resoumission est rejointe. | Système | < 5 min | → Étape 06 |
| 06 | Réception notification vérif. | Le citoyen entre dans la boucle de resoumission. Il reçoit une notification indiquant si son dossier est accepté, rejeté ou si des corrections sont demandées. | Système / Citoyen | Selon traitement | Si correction → 07 / Si fin → 09 |
| 07 | Faire les corrections | Si des erreurs sont détectées, le citoyen est invité à corriger et compléter son dossier via une tâche utilisateur dédiée dans Xportal. | Citoyen | Délai citoyen | → Étape 08 |
| 08 | Envoyer la resoumission | Le dossier corrigé est renvoyé au back-office. La boucle de resoumission est réactivée. | Système | Immédiat | → Retour Étape 06 |
| 09 | Réception notification finale | Le citoyen reçoit la décision finale : acceptation (diplôme disponible) ou rejet définitif motivé. Fin du processus côté citoyen. | Système / Citoyen | < 10 min | → FIN |

#### Lane XFLOW — Côté Back-office

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| B01 | Initialisation procédure | Xflow reçoit le message de démarrage depuis Xportal. Les données du formulaire sont chargées. La gateway « duplicata ? » est évaluée immédiatement. | Système | Immédiat | Si duplicata → B02 / Sinon → B04 |
| B02 | Demande paiement (duplicata) | Xflow envoie au portail une notification de paiement avec le montant et le lien de paiement. | Système | < 5 min | → B03 |
| B03 | Attente confirmation paiement | Xflow attend la confirmation du paiement. Si le paiement est confirmé, le processus continue. Sans confirmation dans le délai imparti, rejet automatique. | Système | Délai paiement | → B04 si OK / → B08 si KO |
| B04 | Recevoir les données candidat | Script task : extraction et normalisation des données du formulaire soumis. Vérification automatique : format, cohérence, complétude. | Système | < 2 min | → B05 |
| B05 | Vérification candidat Odoo | Service task : interrogation de la base Odoo pour vérifier l'inscription du candidat et la réussite à l'examen dans la spécialité et session déclarées. | Système / Odoo | < 5 min | Si inscrit → B06 / Sinon → B08 |
| B06 | Vérification de conformité | User task assignée à l'agent CFA : examen du dossier, vérification des pièces justificatives, cohérence des informations. | Agent CFA | Selon SLA CFA | Si conforme → B07 / Si erreurs → B09 / Si rejet → B08 |
| B07 | Enregistrement candidat | Service task : enregistrement de la décision d'acceptation dans la base de données. Génération du récépissé de validation. | Système | < 2 min | → B10 |
| B08 | Envoi rejet définitif | Service task / Send task : envoi de la notification de rejet définitif au portail avec le motif détaillé. Fin du processus back-office. | Système | < 5 min | → FIN (rejet) |
| B09 | Notification correction | Send task : envoi d'une notification de correction au portail avec la liste précise des erreurs ou pièces manquantes. Le citoyen dispose d'un délai pour corriger. | Système | < 15 min | → Attente resoumission → B05 |
| B10 | Notification acceptation | Send task : envoi de la notification d'acceptation au portail. Le candidat est informé que son diplôme est en cours d'édition / disponible. | Système | < 5 min | → FIN (succès) |

### 3.3. Flux d'escalade temporelle

Les escalades automatiques suivantes sont configurées dans Xflow :

| Déclencheur | Canal | Action |
|---|---|---|
| Délai instruction agent dépassé (SLA CFA) | Email + Dashboard | Escalade automatique vers superviseur CFA |
| Délai correction citoyen dépassé (5 jours ouvrés) | SMS + Email | Rejet automatique du dossier avec notification |
| Délai paiement duplicata dépassé | SMS + Email | Annulation automatique de la demande |
| Indisponibilité Xflow > 15 min | Email Admin | Alerte automatique à l'Admin ATD |

---

## 4. Règles métiers

| ID | Règle métier | Description / Condition | Priorité | Étapes concernées |
|---|---|---|---|---|
| RG-001 | Parcours duplicata | Si `duplicata = Oui` → activation du sous-parcours paiement avant instruction. Les pièces `copieDiplome` et `declarationPerte` deviennent obligatoires. | HAUTE | Étape 01, B01, B02 |
| RG-002 | Réussite à l'examen obligatoire | Si `exam = Non` → blocage immédiat de la soumission avec message : *« Vous devez avoir réussi votre examen CFA pour déposer cette demande. »* | HAUTE | Onglet 1 formulaire |
| RG-003 | Âge minimum du candidat | Le candidat doit avoir au moins 14 ans à la date de soumission. Vérification sur le champ `dateNaissance`. Message bloquant si non respecté. | HAUTE | Onglet 2 formulaire |
| RG-004 | Pièces duplicata conditionnelles | Si `duplicata = Oui`, les champs `copieDiplome` et `declarationPerte` passent obligatoires (`requis = true` dynamiquement). | HAUTE | Onglet 4 formulaire |
| RG-005 | Vérification Odoo obligatoire | Le numéro de table, la spécialité et la session doivent correspondre à un candidat inscrit et reçu dans la base Odoo du CFA. | HAUTE | Étape B05 |
| RG-006 | Une demande active par candidat | Un candidat identifié par son numéro de table ne peut avoir qu'une seule demande en cours. Si une demande est active, bloquer la nouvelle soumission. | HAUTE | Étape 01 |
| RG-007 | Délai de correction citoyen | Le candidat dispose de 5 jours ouvrés pour soumettre un dossier corrigé. Au-delà, le dossier est clôturé automatiquement avec statut *« Rejeté — délai dépassé »*. | HAUTE | Étapes 07-08, B09 |
| RG-008 | Paiement duplicata préalable | Le processus d'instruction ne démarre qu'après confirmation effective du paiement pour les demandes de duplicata. | HAUTE | Étapes B02-B03 |
| RG-009 | Conformité des pièces jointes | Les fichiers uploadés doivent respecter : formats PDF/JPG/PNG, taille < 2 Mo par fichier. Tout fichier non conforme est rejeté avec message explicite. | MOYENNE | Onglet 4, Étape B04 |
| RG-010 | Archivage 10 ans | Tous les dossiers (approuvés et rejetés) doivent être archivés pendant 10 ans minimum conformément aux obligations légales togolaises. | HAUTE | Post-décision |

---

## 5. Intégration avec des systèmes tiers

Les intégrations suivantes sont envisagées. Elles nécessitent la signature de conventions d'échange de données entre les structures concernées.

| Système cible | Type d'intégration | Données échangées | Condition d'appel | Statut |
|---|---|---|---|---|
| Base Odoo CFA | API interne (lecture) | Numéro table, spécialité, session, résultat | Étape B05 — Vérification inscription | Disponible |
| Plateforme paiement | API REST (paiement) | Montant, référence dossier, statut paiement | Étape B02 — Déclenchement paiement duplicata | À configurer |
| Plateforme SMS | API REST (envoi) | Numéro téléphone, texte message, réf. dossier | À chaque changement de statut | Disponible |
| Système archivage ATD | API interne | Dossier complet (formulaire + pièces + décision) | Post-décision — Archivage automatique | Disponible |
| eID Togo (optionnel) | API REST (vérification) | NOM, PRÉNOMS, DATE NAISSANCE | Optionnel — enrichissement données | À développer |

---

## 6. Notifications automatiques

| Réf. | Déclencheur | Canal | Destinataire | Message type |
|---|---|---|---|---|
| N01 | Soumission formulaire (Étape 01) | SMS + Email | Candidat | *Votre demande de diplôme CFA (réf. [DOSSIER]) a bien été reçue. Délai de traitement : [X] jours ouvrés.* |
| N02 | Vérification KO — corrections demandées | SMS + Email | Candidat | *Votre dossier est incomplet ou comporte des erreurs. Corrections requises : [liste]. Vous avez 5 jours ouvrés.* |
| N03 | Demande de paiement (duplicata — B02) | SMS + Email | Candidat | *Une demande de paiement de [montant] FCFA a été générée pour votre demande de duplicata [DOSSIER]. Lien : [URL]* |
| N04 | Confirmation paiement reçu | SMS | Candidat | *Votre paiement a été confirmé. Votre dossier est en cours d'instruction.* |
| N05 | Décision d'acceptation (B10) | SMS + Email | Candidat | *Votre demande [DOSSIER] a été acceptée. Votre diplôme est en cours de préparation. Vous serez notifié(e) pour le retrait.* |
| N06 | Rejet définitif (B08) | SMS + Email | Candidat | *Votre demande [DOSSIER] a été rejetée. Motif : [motif_rejet]. Vous pouvez soumettre une nouvelle demande.* |
| N07 | Rappel agent — délai à risque | Email + Dashboard | Agent CFA | *Rappel : Le dossier [DOSSIER] doit être traité avant [date_heure_limite].* |
| N08 | Escalade superviseur | Email + Dashboard | Superviseur CFA | *Escalade automatique : Le dossier [DOSSIER] dépasse le délai d'instruction. Action requise.* |
| N09 | Invitation évaluation (J+1 décision) | SMS + Email | Candidat | *Êtes-vous satisfait(e) de votre expérience ? Évaluez ce service en 30 secondes sur Xportal.* |

---

## 7. KPIs du service & engagements SLA

| Indicateur | Valeur cible |
|---|---|
| **Taux de complétion** | ≥ 85% (dossiers soumis / formulaires initiés) |
| **Taux d'abandon** | ≤ 15% |
| **Délai standard de traitement** | [À renseigner par le CFA — objectif en jours ouvrés] |
| **Délai réglementaire maximum** | [À renseigner par le FDS] |
| **Taux de rejet** | ≤ 10% |
| **Note de satisfaction usager** | ≥ 4,0 / 5 |
| **Taux de résolution N1 (FCR)** | ≥ 80% |
| **Disponibilité service (Xportal/Xflow)** | ≥ 99,5% mensuel |
| **Délai notification accusé de réception** | < 5 minutes |
| **Délai traitement vérification Odoo** | < 5 minutes (automatique) |

---

## 8. Interface e-service CFA

En complément de Xportal, une interface e-service aux couleurs du CFA sera développée et déployée. Cette interface est visuellement indépendante de Xportal mais techniquement interconnectée.

| Champ | Valeur |
|---|---|
| **URL e-service** | https://services.cfa.gouv.tg/diplome [À confirmer] |
| **Charte graphique** | Couleurs officielles CFA — logo, typographie, palette fournis par le FDS |
| **Fonctionnalités** | Accès direct au formulaire, suivi de dossier, notifications statut |
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

*SRS — Demande du Diplôme du CFA | v1.1 | ATD*
