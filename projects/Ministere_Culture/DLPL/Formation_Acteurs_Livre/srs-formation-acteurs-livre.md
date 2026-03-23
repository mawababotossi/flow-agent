# SERVICE REQUIREMENT SHEET (SRS)
## Formation des Acteurs de la Chaîne du Livre
### Direction du Livre et de la Promotion Littéraire (DLPL) — Togo

| Champ | Valeur |
|---|---|
| **Fournisseur de Services (FDS)** | Direction du Livre et de la Promotion Littéraire (DLPL) |
| **Service parent** | Ministère de la Culture et du Tourisme |
| **Intégrateur en charge** | ATD — Agence Togo Digital |
| **Chef de projet ATD** | _________________________________ |
| **Point focal FDS** | KOUTCHE Amévi — Cheffe division Édition et Promotion littéraire |
| **Date de création** | 20 mars 2026 |
| **Date de dernière révision** | 20 mars 2026 (v1.0 — Version initiale) |
| **Date de validation** | _________________________________ |
| **Back-office utilisé** | Odoo Traitement (ATD — par défaut) |
| **Déploiement cible** | Xportal + Xflow |

---

## Historique des changements

| Version | Date | Auteur | Description des modifications |
|---|---|---|---|
| 1.0 | 20/03/2026 | Agent ATD | Version initiale — digitalisation du processus de candidature à la formation |

---

## Table des matières

1. [Identification du service](#1-identification-du-service)
2. [Design du formulaire Form.io](#2-design-du-formulaire-formio)
3. [Le processus BPMN 2.0](#3-le-processus-bpmn-20)
4. [Règles métiers](#4-règles-métiers)
5. [Intégration avec des systèmes tiers](#5-intégration-avec-des-systèmes-tiers)
6. [Notifications automatiques](#6-notifications-automatiques)
7. [KPIs du service & engagements SLA](#7-kpis-du-service--engagements-sla)
8. [Interface e-service DLPL](#8-interface-e-service-dlpl)
9. [Validations & signatures](#9-validations--signatures)

---

## 1. Identification du service

### 1.1. Description fonctionnelle

La Direction du Livre et de la Promotion Littéraire (DLPL), rattachée au Ministère de la Culture et du Tourisme, organise des sessions de formation gratuites destinées aux acteurs de la chaîne du livre togolais (écrivains en herbe, bibliothécaires, libraires, éditeurs). Ces formations visent à renforcer les compétences des professionnels du secteur littéraire et à promouvoir la littérature togolaise. À l'issue de la formation, les participants reçoivent une attestation de formation. Aujourd'hui, le processus de candidature est entièrement manuel : les candidats déposent physiquement ou par email une pièce d'identité accompagnée d'un échantillon d'œuvre, sans formulaire structuré ni traçabilité.

La digitalisation offre aux candidats la possibilité de soumettre leur candidature 100% en ligne via le portail Xportal, avec un formulaire structuré par catégorie d'acteur (écrivain, éditeur, bibliothécaire, libraire). Le candidat bénéficie d'un accusé de réception immédiat, d'un suivi en temps réel de l'état de sa candidature (soumise, en vérification, sélectionnée, rejetée), et de notifications automatiques Email/SMS à chaque étape. L'attestation de formation est générée en PDF sécurisé (QR Code anti-fraude) et téléchargeable directement sur le portail.

### 1.2. Fiche d'identité du service

| Champ | Valeur |
|---|---|
| **Code service** | SRV-DLPL-2026-001 |
| **Nom complet** | Formation des acteurs de la chaîne du livre |
| **Catégorie** | Formation Professionnelle / Promotion Culturelle |
| **Bénéficiaires** | Écrivains en herbe, bibliothécaires, libraires, éditeurs, acteurs du livre togolais |
| **Fréquence estimée** | À renseigner par le FDS — estimation 1 à 3 sessions par an |
| **Délai standard de traitement** | 15 jours ouvrés (soumission → notification de sélection) |
| **Délai réglementaire maximum** | À renseigner par le FDS |
| **Coût du service** | Gratuit |
| **Langue(s)** | Français |
| **Canaux de dépôt** | Xportal (web / mobile) |

### 1.3. Acteurs et intervenants

| Acteur | Profil | Rôle dans le processus | Accès système | Responsabilité SLA |
|---|---|---|---|---|
| **Candidat (Citoyen)** | Citoyen togolais authentifié (e-ID) | Soumet la candidature en ligne, uploade les pièces, corrige si demandé, consulte le résultat, télécharge l'attestation | Xportal (lecture + saisie) | Correction < 72h |
| **Agent DLPL** | Agent N1 métier (Division Édition) | Vérifie la conformité du dossier (identité, pièces, cohérence catégorie/œuvre) | Back-office Odoo Traitement | Vérification ≤ 5 jours ouvrés |
| **Directeur DLPL / Jury** | Responsable administratif + Jury composé d'agents DLPL | Évalue la qualité des œuvres, sélectionne les candidats (max 35 par session) | Back-office Odoo Traitement — accès complet | Évaluation ≤ 7 jours ouvrés |
| **Système Xflow** | Orchestrateur BPMN (Camunda Platform 7) | Routage automatique, notifications, escalades temporelles, génération attestation PDF | Infrastructure ATD | Disponibilité 99,5% |
| **Admin Xportal (ATD)** | Technicien ATD | Surveillance plateforme, publication formulaire, KPIs | Administration Xportal | SLA plateforme |
| **Centre d'appel (N1)** | Agent support ATD | Assistance candidats en difficulté sur la démarche | Consultation statut uniquement | Résolution < 30 min |

---

## 2. Design du formulaire Form.io

### 2.1. Structure du formulaire

Le parcours est composé de **1 formulaire** Form.io principal orchestré par Xflow :

- **Formulaire principal (5 onglets)** : parcours adaptatif selon la catégorie d'acteur du livre.

#### Formulaire principal — 5 onglets wizard

| Onglet | Titre | Remarques |
|---|---|---|
| Onglet 1 | Présentation du service | Landing page premium — description, conditions, étapes, pièces requises |
| Onglet 2 | Identité du candidat | Pré-remplissage e-ID (nom, prénom, email) + informations personnelles |
| Onglet 3 | Profil littéraire | Catégorie d'acteur + champs conditionnels selon le profil |
| Onglet 4 | Pièces justificatives | Upload pièces — conditionnées par la catégorie d'acteur |
| Onglet 5 | Récapitulatif et soumission | Résumé non modifiable + confirmation + soumission |

### 2.2. Détail des champs

#### Onglet 1 — Présentation du service (`stepIntro`)

Panel Premium « Landing Page ». Présente le service, les conditions d'éligibilité, les profils concernés, les pièces requises par catégorie, et les étapes du processus. Utilise la grille `columns` (8/4) avec Info Pills et Sidebar DLPL.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `stylesCssSidebar` | N/A | HTML (tag `style`) | N/A | CSS inline | Statique | Styles Info Pills, Sidebar, étapes numérotées |
| `columnsIntro` | N/A | Columns (8/4) | N/A | Grille responsive | Statique | Contenu principal + sidebar fournisseur |
| `htmlPillsIntro` | N/A | HTML | N/A | — | Statique | Info Pills : Gratuit · Attestation · 100% en ligne · Max 35 candidats |
| `htmlDescService` | N/A | HTML | N/A | — | Statique | Description du service et conditions d'éligibilité |
| `htmlEtapesProcess` | N/A | HTML | N/A | — | Statique | Étapes numérotées du processus |
| `htmlAvertissement` | N/A | HTML | N/A | — | Statique | « Les pièces varient selon votre profil. Préparez votre échantillon d'œuvre. » |
| `htmlSidebarDLPL` | N/A | HTML | N/A | — | Statique | Sidebar : DLPL, contact, horaires, adresse |

---

#### Onglet 2 — Identité du candidat (`stepIdentite`)

Pré-remplissage e-ID. Verrouillage dynamique via bloc `logic` si la valeur est non vide (RG-001).

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `nom` | Nom de famille | Texte | Oui | `blur` · `minLength: 2` · `maxLength: 100` · Erreur : « Veuillez renseigner votre nom » | Profil Citoyen (`config.users.lastName`) | Verrouillage e-ID (RG-001) |
| `prenom` | Prénoms | Texte | Oui | `blur` · `minLength: 2` · `maxLength: 100` · Erreur : « Veuillez renseigner vos prénoms » | Profil Citoyen (`config.users.firstName`) | Verrouillage e-ID (RG-001) |
| `email` | Adresse e-mail | Email | Oui | `blur` · Regex Email RFC · Erreur : « Adresse e-mail invalide » | Profil Citoyen (`config.users.email`) | Verrouillage e-ID (RG-001) |
| `telephone` | Numéro de téléphone | Téléphone | Oui | `blur` · Pattern `^\+228[0-9]{8}$` · Erreur : « Format attendu : +228XXXXXXXX » | Saisie | RG-009 |
| `dateNaissance` | Date de naissance | Date | Oui | `blur` · Date ≤ aujourd'hui − 16 ans · Erreur : « Vous devez avoir au moins 16 ans » | Saisie | RG-012 |
| `lieuNaissance` | Lieu de naissance | Texte | Oui | `blur` · `minLength: 2` · `maxLength: 100` · Erreur : « Veuillez indiquer votre lieu de naissance » | Saisie | — |
| `nationalite` | Nationalité | Select | Oui | `blur` · Erreur : « Sélectionnez votre nationalité » | API (`config.apiBaseUrl/references/nationalities`) | Liste dynamique |
| `adresse` | Adresse de résidence | Texte | Non | `blur` · `maxLength: 200` | Saisie | — |
| `dernierDiplome` | Dernier diplôme obtenu | Select | Oui | `blur` · Erreur : « Sélectionnez votre diplôme » | Saisie | Valeurs : Baccalauréat, Licence, Master, Doctorat, Autre |

---

#### Onglet 3 — Profil littéraire (`stepProfil`)

Onglet adaptatif selon la catégorie d'acteur (logique conditionnelle `customConditional`). Les champs non pertinents sont masqués et nettoyés (`clearOnHide: true`).

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `categorieActeur` | Catégorie d'acteur de la chaîne du livre | Radio | Oui | Erreur : « Sélectionnez votre catégorie » | Saisie | Options : Écrivain en herbe, Bibliothécaire, Libraire, Éditeur, Autre · RG-003 / RG-004 |
| `htmlInfoCategorie` | N/A | HTML | N/A | — | Statique | Description dynamique des pièces attendues selon catégorie |
| `genreLitteraire` | Genre littéraire | Select | Conditionnel | `blur` · `clearOnHide: true` · Erreur : « Précisez votre genre littéraire » | Saisie | Visible si `categorieActeur == 'ecrivain'` · Options : Roman, Poésie, Théâtre, Nouvelle, Essai, Autre · RG-004 |
| `titreOeuvre` | Titre de l'œuvre soumise | Texte | Conditionnel | `blur` · `minLength: 2` · `maxLength: 200` · `clearOnHide: true` | Saisie | Visible si `categorieActeur == 'ecrivain'` · RG-004 |
| `descriptionExperience` | Description de votre expérience | Textarea | Conditionnel | `blur` · `minLength: 50` · `maxLength: 2000` · `clearOnHide: true` · Erreur : « Décrivez votre expérience (min. 50 car.) » | Saisie | Visible si catégorie ≠ écrivain ET ≠ éditeur · RG-004 |
| `nomMaisonEdition` | Nom de la maison d'édition | Texte | Conditionnel | `blur` · `minLength: 2` · `maxLength: 200` · `clearOnHide: true` | Saisie | Visible si `categorieActeur == 'editeur'` · RG-004 |
| `motivation` | Motivation pour la formation | Textarea | Oui | `blur` · `minLength: 50` · `maxLength: 2000` · Erreur : « Minimum 50 caractères » | Saisie | RG-010 |

---

#### Onglet 4 — Pièces justificatives (`stepPieces`)

Les fichiers sont uploadés directement dans Xportal et transmis à Xflow. Formats acceptés : PDF, JPG, PNG. Les pièces conditionnelles utilisent `clearOnHide: true`.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `fileIdentite` | Pièce d'identité valide | Fichier | Oui | PDF/JPG/PNG < 2 Mo | Upload | Obligatoire pour tous · RG-009 |
| `fileEbaucheTexte` | Ébauche de texte / manuscrit | Fichier | Conditionnel | PDF < 5 Mo · `clearOnHide: true` | Upload | Visible si `categorieActeur == 'ecrivain'` · RG-003 |
| `fileCatalogueEditeur` | Catalogue ou lettre de motivation | Fichier | Conditionnel | PDF < 5 Mo · `clearOnHide: true` | Upload | Visible si `categorieActeur == 'editeur'` · RG-003 |
| `fileJustificatifExperience` | Justificatif d'expérience | Fichier | Non | PDF/JPG < 2 Mo · `clearOnHide: true` | Upload | Visible si bibliothécaire ou libraire |

---

#### Onglet 5 — Récapitulatif et soumission (`stepRecapitulatif`)

L'onglet 5 affiche un résumé de toutes les données saisies via le script d'analyse natif ATD. L'usager coche une case de confirmation. P-Studio gère nativement le bouton « Soumettre » sur le dernier panel du wizard.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `htmlRecapitulatifFinal` | N/A | HTML | N/A | Script Parseur Formulaire | Système | Injection du composant récapitulatif intelligent · `excludeKeys: ["luEtApprouve"]` |
| `luEtApprouve` | Je certifie sur l'honneur l'exactitude des informations et m'engage à me rendre disponible si sélectionné(e). | Checkbox | Oui | Doit être coché | Saisie | Ignoré par le récap via `excludeKeys` |

### 2.3. Actions du formulaire (P-Studio)

| Code Action P-Studio | Condition d'activation | Configuration algorithmique |
|---|---|---|
| **Calculate Costs** | Non (Gratuit) | N/A — Service entièrement gratuit |
| **Publish to RabbitMQ** | Toujours actif | Routing Key: `submissions.topic` — Queue: `workflows-engine.main.queue` |

---

## 3. Le processus BPMN 2.0

### 3.1. Vue d'ensemble du processus TO-BE

Le processus complet est modélisé sur P-Studio (Camunda Web Modeler). Le diagramme BPMN est joint en annexe (fichier `.bpmn`). Ce tableau décrit chaque étape avec ses acteurs, délais et conditions.

| Champ | Valeur |
|---|---|
| **Nom du processus** | `Procedure_FormationActeursLivre_v1` |
| **Événement déclencheur** | Soumission du formulaire par le candidat sur Xportal |
| **Événement de fin (succès)** | Notification « Attestation disponible » + PDF téléchargeable sur le portail |
| **Événement de fin (rejet)** | Notification de rejet/non-sélection motivé au candidat |
| **Moteur d'exécution** | Xflow (Camunda Platform 7 — GNSPD Framework) |
| **Version processus** | 1.0 |
| **Participants BPMN** | Pool XPORTAL (candidat) + Pool XFLOW (back-office DLPL) — deux pools exécutables communiquant via Kafka |

### 3.2. Étapes détaillées du processus

#### Lane PORTAL — Côté Candidat

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| 01 | Soumission de la candidature | Le candidat remplit le formulaire Form.io (5 onglets) et uploade ses pièces justificatives. Accusé de réception automatique Email + SMS avec numéro de suivi. | Candidat (Citoyen) | Immédiat | → 02 |
| 02 | Envoi vers Xflow | Send Task : le formulaire soumis est publié via Kafka (`MSG_FORM_ACT_LIVRE_START`) vers le pool XFLOW. | Système | < 1 min | → 03 (attente) |
| 03 | Attente décision Xflow | Receive Task multi-entrante : le candidat attend la décision du back-office. XPortal reçoit `MSG_FORM_ACT_LIVRE_RETURN` avec l'action de retour. | Système | Variable | Si `action == 'correction'` → 04 · Si `action == 'rejete'` → 06 · Si `action == 'accepte'` → 06 |
| 04 | Correction du dossier | User Task : le candidat voit le motif de non-conformité et peut corriger/compléter son dossier en ligne (écran `Activity_P_Corrections`). | Candidat | ≤ 72h (timer) | → 05 |
| 05 | Resoumission vers Xflow | Send Task : le dossier corrigé est renvoyé via Kafka (`MSG_FORM_ACT_LIVRE_RESUB`) vers XFLOW. Retour à l'étape 03. | Système | < 1 min | → 03 |
| 06 | Fin du parcours candidat | End Event : le candidat reçoit la notification finale (attestation disponible au téléchargement, ou rejet/non-sélection motivé). | Système / Candidat | Immédiat | → FIN |

#### Lane XFLOW — Côté Back-office DLPL

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| B01 | Réception de la candidature | Start Event (Message) : Xflow reçoit `MSG_FORM_ACT_LIVRE_START`. Les données du formulaire sont chargées. Instance créée avec numéro de suivi. | Système | Immédiat | → B02 |
| B02 | Notification interne | Service Task (Notification) : notification aux agents DLPL qu'un nouveau dossier est à traiter. | Système | < 5 min | → B03 |
| B03 | Vérification de conformité | User Task (GNSPD `tg.gouv.gnspd.userTask`) : l'agent DLPL vérifie la conformité des pièces (identité valide, échantillon d'œuvre lisible, cohérence catégorie/pièces). Affichage des pièces jointes via `gnspdAttachments`. | Agent DLPL | ≤ 5 jours (SLA) | Si conforme → B06 · Si correction requise → B04 · Si rejeté → B05 |
| B04 | Envoi demande de correction | Send Task (`tg.gouv.gnspd.sendMessage`) : message Kafka `MSG_FORM_ACT_LIVRE_RETURN` (action = `correction`, motif saisi par l'agent). Notification Email + SMS au candidat avec motif. Incrémentation compteur `nbCorrections`. | Système | < 5 min | → B04b |
| B04b | Attente resoumission | Receive Task : Xflow attend `MSG_FORM_ACT_LIVRE_RESUB` du candidat. Boundary Timer interrompant : 72h → clôture automatique (RG-006). | Système | ≤ 72h | Si reçu → Gateway : `nbCorrections >= 3` ? → B05 (rejet auto, RG-005) / Sinon → B03 |
| B05 | Envoi rejet définitif | Send Task + Notification : Email + SMS de rejet motivé au candidat. Message Kafka `MSG_FORM_ACT_LIVRE_RETURN` (action = `rejete`) vers XPortal. | Système | < 5 min | → FIN (rejet) |
| B06 | Évaluation par le jury | User Task (GNSPD `tg.gouv.gnspd.userTask`) : le Directeur DLPL et le jury évaluent la qualité de l'œuvre et la pertinence du profil du candidat. | Directeur DLPL / Jury | ≤ 7 jours (SLA) | Si sélectionné → B07 · Si non sélectionné → B05 |
| B07 | Notification de sélection | Send Task (Notification) : Email + SMS de sélection avec dates, lieu et programme de la formation. | Système | < 5 min | → B08 |
| B08 | Génération attestation | Service Task : génération du PDF attestation de formation avec QR Code ATD anti-fraude (post-formation, déclenché par action agent). | Système | < 5 min | → B09 |
| B09 | Notification finale | Send Task : Email + SMS « Attestation disponible au téléchargement ». Message Kafka `MSG_FORM_ACT_LIVRE_RETURN` (action = `accepte`) vers XPortal. | Système | < 5 min | → FIN (succès) |

### 3.3. Flux d'escalade temporelle

| Déclencheur | Canal | Action |
|---|---|---|
| Délai vérification agent dépassé (5 jours — SLA DLPL) | Email + Dashboard | Escalade automatique vers Directeur DLPL |
| Délai évaluation jury dépassé (7 jours — SLA DLPL) | Email + Dashboard | Escalade hiérarchique |
| Délai correction candidat dépassé (72h) | SMS + Email | Clôture automatique du dossier avec notification |
| Indisponibilité Xflow > 15 min | Email Admin | Alerte automatique à l'Admin ATD |

---

## 4. Règles métiers

| ID | Règle métier | Description / Condition | Priorité | Étapes concernées |
|---|---|---|---|---|
| RG-001 | Verrouillage e-ID robuste | Les champs `nom`, `prenom`, `email` sont verrouillés via bloc `logic` dynamique (trigger : `!!(data.champ && String(data.champ).trim().length > 0)` → `disabled: true`). **JAMAIS** de `disabled: true` statique. | HAUTE | Onglet 2 formulaire |
| RG-002 | Service gratuit | Aucun paiement requis. `Calculate Costs` désactivé. Pas de formulaire secondaire de paiement. | HAUTE | Toutes étapes |
| RG-003 | Pièces conditionnelles par catégorie | Les pièces justificatives varient selon `categorieActeur` : écrivain → `fileEbaucheTexte` ; éditeur → `fileCatalogueEditeur` ; bibliothécaire/libraire → `fileJustificatifExperience`. Implémenté via `conditional` + `clearOnHide: true`. | HAUTE | Onglet 4 formulaire |
| RG-004 | Champs conditionnels par catégorie | `genreLitteraire` et `titreOeuvre` visibles si `categorieActeur == 'ecrivain'`. `nomMaisonEdition` visible si `categorieActeur == 'editeur'`. `descriptionExperience` visible si catégorie ≠ écrivain ET ≠ éditeur. | HAUTE | Onglet 3 formulaire |
| RG-005 | Rejet après 3 corrections | Si `nbCorrections >= 3`, le dossier est automatiquement rejeté. Gateway exclusive avec compteur incrémenté à chaque passage dans B04. Message bloquant : *« Votre dossier a été rejeté après 3 tentatives de correction. »* | HAUTE | Étapes B04, B04b, B05 |
| RG-006 | Délai de correction candidat | Le candidat dispose de 72h pour soumettre un dossier corrigé. Au-delà, le dossier est clôturé automatiquement avec statut *« Rejeté — délai dépassé »*. | HAUTE | Étapes 04, B04b |
| RG-007 | Zéro déplacement | La candidature est 100% en ligne. Aucun dépôt physique n'est accepté. | HAUTE | Étape 01 |
| RG-008 | Limite de 35 candidats par session | Le nombre maximum de candidats sélectionnés par session est de 35 (contrôle métier par le jury, non automatisé dans le BPMN). | MOYENNE | Étape B06 |
| RG-009 | Validation téléphone togolais | Le champ `telephone` doit suivre le pattern `^\+228[0-9]{8}$`. Message bloquant : *« Format attendu : +228 suivi de 8 chiffres. »* | HAUTE | Onglet 2 formulaire |
| RG-010 | Motivation minimale | Le champ `motivation` requiert au minimum 50 caractères. Message bloquant : *« Votre motivation doit contenir au moins 50 caractères. »* | MOYENNE | Onglet 3 formulaire |
| RG-011 | Sécurité QR Code | L'attestation de formation générée porte un QR Code ATD infalsifiable permettant la vérification en ligne. | HAUTE | Étape B08 |
| RG-012 | Âge minimum | Le candidat doit avoir au minimum 16 ans à la date de soumission. Vérification sur `dateNaissance ≤ today - 16 ans`. Message bloquant : *« Vous devez avoir au moins 16 ans. »* | HAUTE | Onglet 2 formulaire |
| RG-013 | Conformité des pièces jointes | Les fichiers uploadés doivent respecter : formats PDF/JPG/PNG, taille < 2 Mo (identité) ou < 5 Mo (œuvres). Tout fichier non conforme est rejeté avec message explicite. | MOYENNE | Onglet 4, Étape B03 |
| RG-014 | Archivage 5 ans | Tous les dossiers (sélectionnés et rejetés) doivent être archivés pendant 5 ans minimum. | HAUTE | Post-décision |

---

## 5. Intégration avec des systèmes tiers

Les intégrations suivantes sont envisagées. Elles nécessitent la signature de conventions d'échange de données entre les structures concernées.

| Système cible | Type d'intégration | Données échangées | Condition d'appel | Statut |
|---|---|---|---|---|
| Odoo Traitement (DLPL) | API interne (lecture/écriture) | Données des candidatures, statut des dossiers, attestations générées | Étapes B01-B09 — Toutes les étapes back-office | À configurer |
| Plateforme SMS | API REST (envoi) | Numéro téléphone, texte message, réf. dossier | À chaque changement de statut (N01-N09) | Disponible |
| Système archivage ATD | API interne | Dossier complet (formulaire + pièces + décision + attestation) | Post-décision — Archivage automatique | Disponible |
| Service PDF / QR Code ATD | API interne | Données candidat, modèle attestation, QR Code | Étape B08 — Génération attestation | Disponible |
| Système identité numérique (e-ID) | API REST (vérification) | Nom, Prénoms, Email | Pré-remplissage formulaire — enrichissement données | Disponible |

---

## 6. Notifications automatiques

| Réf. | Déclencheur | Canal | Destinataire | Message type |
|---|---|---|---|---|
| N01 | Soumission formulaire (Étape 01) | SMS + Email | Candidat | *Votre candidature à la formation des acteurs de la chaîne du livre (réf. [DOSSIER]) a bien été reçue. Délai de traitement : 15 jours ouvrés.* |
| N02 | Vérification KO — corrections demandées (B04) | SMS + Email | Candidat | *Votre dossier est incomplet ou comporte des erreurs. Corrections requises : [MOTIF]. Vous avez 72h pour corriger.* |
| N03 | Sélection par le jury (B07) | SMS + Email | Candidat | *Félicitations ! Vous êtes sélectionné(e) pour la formation. Dates : [DATES]. Lieu : [LIEU]. Programme : [LIEN].* |
| N04 | Non-sélection par le jury (B05) | SMS + Email | Candidat | *Votre candidature (réf. [DOSSIER]) n'a pas été retenue pour cette session. Motif : [COMMENTAIRE]. Nous vous encourageons à postuler à la prochaine session.* |
| N05 | Rejet définitif (B05 — non-conformité ou 3 corrections) | SMS + Email | Candidat | *Votre candidature (réf. [DOSSIER]) a été rejetée. Motif : [MOTIF]. Vous pouvez soumettre une nouvelle candidature lors de la prochaine session.* |
| N06 | Attestation disponible (B09) | SMS + Email | Candidat | *Votre attestation de formation est prête ! Téléchargez-la sur le portail : [LIEN]. Référence : [DOSSIER].* |
| N07 | Timeout correction (72h dépassées) | SMS + Email | Candidat | *Votre candidature (réf. [DOSSIER]) a été automatiquement clôturée faute de correction dans les 72h.* |
| N08 | Rappel agent — délai à risque (≤ 1 jour SLA) | Email + Dashboard | Agent DLPL | *Rappel : Le dossier [DOSSIER] doit être traité avant [DATE_HEURE_LIMITE].* |
| N09 | Escalade superviseur (SLA dépassé) | Email + Dashboard | Directeur DLPL | *Escalade automatique : Le dossier [DOSSIER] dépasse le délai d'instruction. Action requise.* |
| N10 | Invitation évaluation (J+1 décision) | SMS + Email | Candidat | *Êtes-vous satisfait(e) de votre expérience ? Évaluez ce service en 30 secondes sur Xportal.* |

---

## 7. KPIs du service & engagements SLA

| Indicateur | Valeur cible |
|---|---|
| **Taux de complétion** | ≥ 85% (dossiers soumis / formulaires initiés) |
| **Taux d'abandon** | ≤ 15% |
| **Délai standard de traitement** | 15 jours ouvrés (soumission → notification sélection) |
| **Délai réglementaire maximum** | À renseigner par le FDS |
| **Taux de rejet** | ≤ 10% |
| **Note de satisfaction usager** | ≥ 4,0 / 5 |
| **Taux de résolution N1 (FCR)** | ≥ 80% |
| **Disponibilité service (Xportal/Xflow)** | ≥ 99,5% mensuel |
| **Délai notification accusé de réception** | < 5 minutes |
| **Délai vérification conformité** | ≤ 5 jours ouvrés |
| **Délai évaluation jury** | ≤ 7 jours ouvrés |

---

## 8. Interface e-service DLPL

Aucune interface e-service dédiée n'est prévue pour ce service. Le service est accessible exclusivement via Xportal (web et mobile). La DLPL pourra ultérieurement demander le développement d'une interface aux couleurs de la Direction si le volume de candidatures le justifie.

---

## 9. Validations & signatures

Le présent SRS a été élaboré à l'issue des ateliers d'analyse conduits entre l'intégrateur, l'équipe ATD et les points focaux de la DLPL. Il constitue la référence contractuelle pour le développement, les tests et la mise en production du service.

| | Rédigé par | Validé par (FDS) | Approuvé par (ATD) |
|---|---|---|---|
| **Qualité** | Intégrateur ATD | Point focal DLPL | Chef de projet ATD |
| **Nom** | ________________________ | ________________________ | ________________________ |
| **Date** | _______________________ | _______________________ | _______________________ |
| **Signature** | __________________ | __________________ | __________________ |

---

*SRS — Formation des Acteurs de la Chaîne du Livre | v1.0 | ATD*
