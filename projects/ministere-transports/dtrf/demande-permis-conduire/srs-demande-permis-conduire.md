# SERVICE REQUIREMENT SHEET (SRS)
## Demande et délivrance du permis de conduire
### Ministère des Transports / DTRF — République Togolaise

---

| Champ | Valeur |
|---|---|
| **Fournisseur de Services (FDS)** | Direction des Transports Routiers et Ferroviaires (DTRF) |
| **Service parent** | Ministère des Transports |
| **Intégrateur en charge** | [Nom de la société intégratrice] |
| **Chef de projet ATD** | [Nom du chef de projet] |
| **Point focal FDS** | [Nom du responsable côté DTRF] |
| **Date de création** | 30 mars 2026 |
| **Date de dernière révision** | 30 mars 2026 (v1.1 — version simplifiée : fusion paiements et automatisation) |
| **Date de validation** | _________________________________ |
| **Back-office utilisé** | Odoo Traitement (ATD — par défaut) |
| **Déploiement cible** | Xportal + Xflow |

---

## Historique des changements

| Version | Date | Auteur | Description des modifications |
|---|---|---|---|
| 1.0 | 30/03/2026 | Antigravity | Version initiale |
| 1.1 | 30/03/2026 | Antigravity | Simplification radicale : fusion des paiements, planification auto, suppression validation manuelle finale. |

---

## Table des matières

1. [Identification du service](#1-identification-du-service)
2. [Design du formulaire Form.io](#2-design-du-formulaire-formio)
3. [Le processus BPMN 2.0](#3-le-processus-bpmn-20)
4. [Règles métiers](#4-règles-métiers)
5. [Intégration avec des systèmes tiers](#5-intégration-avec-des-systèmes-tiers)
6. [Notifications automatiques](#6-notifications-automatiques)
7. [KPIs du service & engagements SLA](#7-kpis-du-service--engagements-sla)
8. [Interface e-service [FDS]](#8-interface-e-service-fds)
9. [Validations & signatures](#9-validations--signatures)

---

## 1. Identification du service

### 1.1. Description fonctionnelle

Le permis de conduire est le titre officiel autorisant son titulaire à conduire un véhicule à moteur sur la voie publique au Togo. Il est délivré par la Direction des Transports Routiers et Ferroviaires (DTRF) après réussite aux épreuves théoriques et pratiques. Ce titre est essentiel pour la sécurité routière et constitue une pièce d'identité professionnelle pour de nombreux citoyens.

La digitalisation de ce service permet aux usagers de soumettre leur dossier de candidature en ligne sans déplacement initial vers les bureaux de la DTRF. L'usager peut suivre le statut de son dossier, recevoir ses convocations aux épreuves par SMS/Email, et payer les frais d'examen et les droits de délivrance de manière électronique. Seules les épreuves physiques de conduite et le retrait du titre sécurisé restent des étapes présentielles obligatoires.

### 1.2. Fiche d'identité du service

| Champ | Valeur |
|---|---|
| **Code service** | SRV-DTRF-2026-001 |
| **Nom complet** | Demande et délivrance du permis de conduire (catégories A / B / C / D / E) |
| **Catégorie** | Transports / Certification |
| **Bénéficiaires** | Citoyens togolais et résidents légaux (selon l'âge requis par catégorie) |
| **Fréquence estimée** | Environ 8 000 permis par an |
| **Délai standard de traitement** | 15 jours ouvrés (après succès aux épreuves) |
| **Délai réglementaire maximum** | 30 jours ouvrés |
| **Coût du service** | Inscription : 5000 FCFA | Droits de délivrance : 15000 FCFA |
| **Langue(s)** | Français |
| **Canaux de dépôt** | Xportal (web / mobile) |

### 1.3. Acteurs et intervenants

| Acteur | Profil | Rôle dans le processus | Accès système | Responsabilité SLA |
|---|---|---|---|---|
| **Citoyen** | Usager demandeur | Soumet la demande, paie en ligne, passe les épreuves, retire le titre | Xportal | N/A |
| **Agent de réception** | Agent DTRF (N1) | Vérifie la conformité numérique du dossier | Back-office Odoo | 24h pour validation initiale |
| **Inspecteur Examen** | Agent DTRF (Terrain) | Saisit les résultats des épreuves théoriques et pratiques | Interface agent mobile | Immédiat après épreuve |
| **Agent de production** | Agent DTRF (Atelier) | Lance l'impression du titre sécurisé | Système dédié connecté | 72h après validation finale |
| **Directeur DTRF** | Responsable FDS | Signe numériquement / valide la sortie du titre | Back-office (validation) | 48h |
| **Système Xflow** | Orchestrateur BPMN | Gère les flux, notifications et escalades | Infrastructure ATD | 99.5% disponibilité |

---

## 2. Design du formulaire Form.io

### 2.1. Structure du formulaire

Le parcours est composé de plusieurs formulaires Form.io orchestrés par Xflow :

- **Formulaire principal (5 onglets)** : soumission initiale de la candidature.
- **Formulaire de paiement (1 onglet)** : utilisé pour l'inscription ET pour la délivrance.
- **Formulaire de correction** : en cas de dossier non conforme.
- **Formulaire d'instruction agent** : pour la vérification back-office.

#### Formulaire principal — 5 onglets wizard

| Onglet | Titre | Remarques |
|---|---|---|
| Onglet 1 | Bienvenue & Qualification | Info Pills sur les catégories et conditions d'âge |
| Onglet 2 | Informations personnelles | Identité complète (pré-remplie e-ID) |
| Onglet 3 | Détails de la demande | Catégorie sollicitée, Auto-école de formation, Bureau de retrait |
| Onglet 4 | Pièces justificatives | Upload CNI, Acte naissance, Certificat médical, Photos |
| Onglet 5 | Récapitulatif & Soumission | Validation finale et consentement |

### 2.2. Détail des champs

#### Onglet 2 — Informations personnelles

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `nom` | Nom | Texte | Oui | Majuscules | e-ID | Verrouillé si présent |
| `prenoms` | Prénoms | Texte | Oui | | e-ID | Verrouillé si présent |
| `dateNaissance` | Date de naissance | Date | Oui | JJ/MM/AAAA | e-ID | Utilisé pour RG-003 |
| `lieuNaissance` | Lieu de naissance | Texte | Oui | | e-ID | |
| `profession` | Profession | Texte | Oui | | Saisie | |
| `adresse` | Adresse de résidence | Texte | Oui | | Saisie | |
| `telephone` | Numéro de téléphone | Téléphone | Oui | +228 | e-ID | Pour notifications |

#### Onglet 3 — Détails de la demande

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `categoriePermis` | Catégorie sollicitée | Select | Oui | A, B, C, D, E | Saisie | |
| `autoEcole` | Auto-école de formation | Select | Oui | Liste agréée | API | |
| `bureauRetrait` | Bureau de retrait souhaité | Select | Oui | Lomé, Kara, etc. | API | |

#### Onglet 4 — Pièces justificatives

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `pieceIdentite` | Copie de la pièce d'identité | Fichier | Oui | PDF/JPG < 2Mo | Upload | CNI ou Passeport |
| `acteNaissance` | Copie de l'acte de naissance | Fichier | Oui | PDF/JPG < 2Mo | Upload | |
| `certificatMedical` | Certificat médical d'aptitude | Fichier | Oui | PDF/JPG < 2Mo | Upload | Moins de 3 mois |
| `photosIdentite` | Photos d'identité (4x4) | Fichier | Oui | JPG < 1Mo | Upload | 4 photos requises |
| `attestationFormation` | Attestation de formation auto-école | Fichier | Oui | PDF/JPG < 2Mo | Upload | |

### 2.3. Actions du formulaire (P-Studio)

| Code Action P-Studio | Condition d'activation | Configuration algorithmique |
|---|---|---|
| **Calculate Costs** | Soumission initiale | Prix fixe : 20000 FCFA (Frais d'examen + Droits de délivrance fusionnés) |
| **Publish to RabbitMQ** | Toujours actif | Routing Key: `submissions.topic` |

---

## 3. Le processus BPMN 2.0

### 3.1. Vue d'ensemble du processus TO-BE

| Champ | Valeur |
|---|---|
| **Nom du processus** | `Procédure_Permis_Conduire_v1` |
| **Événement déclencheur** | Soumission dossier + Paiement inscription |
| **Événement de fin (succès)** | Remise du permis physique |
| **Moteur d'exécution** | Xflow (GNSPD Framework) |

### 3.2. Étapes détaillées du processus

#### Lane PORTAL — Côté Citoyen

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| 01 | Dépôt Candidature | Soumission du formulaire + Upload pièces | Citoyen | N/A | → 02 |
| 02 | Paiement Unique | Règlement des 20000 FCFA (Tout inclus) | Citoyen | 48h | Si payé → B01 (XFlow) |
| 03 | Choix Session Auto | Sélection immédiate de la session d'examen disponible | Système/Citoyen | Immédiat | → 04 (Physique) |
| 04 | Épreuve Code — PHYSIQUE | Examen théorique (résultat instantané) | Citoyen | 1 jour | Si succès → 05 |
| 05 | Épreuve Conduite — PHYSIQUE | Examen pratique (résultat instantané) | Citoyen | 1 jour | Si succès → B10 (XFlow) |
| 06 | Retrait Permis — PHYSIQUE | Récupération du titre au guichet après notification | Citoyen | 1 jour | FIN |

#### Lane XFLOW — Côté Back-office

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| B01 | Instruction Dossier | Vérification des pièces justificatives | Agent DTRF | 24h | Si OK → B02 |
| B02 | Validation Inscription | Activation du dossier pour les examens | Système | Immédiat | Déclenche N03 (Convocation) |
| B10 | Production Automatique | Impression du titre déclenchée dès succès conduite | Système | 72h | Déclenche N05 (Disponibilité) |

---

## 4. Règles métiers

| ID | Règle métier | Description / Condition | Priorité | Étapes concernées |
|---|---|---|---|---|
| RG-001 | Éligibilité par âge | Cat A: 16+ ans. Cat B: 18+ ans. Cat C/D: 21+ ans | HAUTE | Onglet 1 & 2 |
| RG-002 | Unicité du dossier | Un seul dossier actif par citoyen par catégorie | HAUTE | Étape 01 |
| RG-003 | Validité certificat médical | Doit être daté de moins de 3 mois à la soumission | MOYENNE | B01 Instruction |
| RG-004 | Blocage après 3 échecs | Si 3 échecs à la conduite, exiger nouvelle attestation formation | HAUTE | B04 Saisie Note |
| RG-005 | Paiement libératoire | La production ne démarre qu'après confirmation du paiement unique de 20000 FCFA effectué à l'inscription. | HAUTE | B10 Production |

---

## 5. Intégration avec des systèmes tiers

| Système cible | Type d'intégration | Données échangées | Condition d'appel | Statut |
|---|---|---|---|---|
| Plateforme Paiement e-Gov | API REST | Montant, Réf Dossier, Statut | Étape 02 | À configurer |
| Registre National Permis | API Interne | Bio-data, Catégories, Dates | Post-production | À développer |
| Service SMS/Email | API REST | Messages dynamiques | Jalons du workflow | Disponible |

---

## 6. Notifications automatiques

| Réf. | Déclencheur | Canal | Destinataire | Message type |
|---|---|---|---|---|
| N01 | Paiement Inscription OK | SMS | Usager | *Votre candidature a été validée. Votre dossier est en cours d'instruction.* |
| N02 | Correction demandée | Email | Usager | *Pièce non conforme : [Liste]. Veuillez corriger sur votre portail.* |
| N03 | Session Planifiée | SMS | Usager | *Votre session d'examen est validée : [Date] au centre [Lieu].* |
| N04 | Succès Examens | SMS | Usager | *Félicitations ! Vos examens sont validés. Votre permis est en cours de production.* |
| N05 | Permis Dispo | SMS | Usager | *Votre permis est prêt au bureau de [Lieu]. Veuillez vous munir de votre CNI pour le retrait.* |

---

## 7. KPIs du service & engagements SLA

| Indicateur | Valeur cible |
|---|---|
| **Délai instruction initiale** | < 24h ouvrées |
| **Délai production après paiement** | < 7 jours ouvrés |
| **Taux de satisfaction usager** | > 90% |

---

## 8. Interface e-service [FDS]

Le service est accessible via Xportal. Aucune interface dédiée spécifique n'est prévue à ce stade.

---

## 9. Validations & signatures

| | Rédigé par | Validé par (FDS) | Approuvé par (ATD) |
|---|---|---|---|
| **Qualité** | Intégrateur (Antigravity) | Point focal DTRF | Chef de projet ATD |
| **Nom** | ________________________ | ________________________ | ________________________ |
| **Date** | 30/03/2026 | _______________________ | _______________________ |
