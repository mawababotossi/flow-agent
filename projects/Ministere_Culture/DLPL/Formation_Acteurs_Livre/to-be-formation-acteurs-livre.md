# Cartographie TO-BE : Formation des Acteurs de la Chaîne du Livre

## Vision Générale

Digitalisation complète du service de formation des acteurs de la chaîne du livre via un portail citoyen (XPortal / Form.io) connecté à un moteur de workflow BPMN (XFlow / Camunda Platform 7). Le candidat soumet sa candidature en ligne avec ses pièces justificatives, le jury évalue via un tableau de bord numérique, et les notifications sont automatiques à chaque étape. L'attestation de formation est générée en PDF sécurisé avec QR Code.

## Architecture Technique

- **Frontend / Orchestrateur Citoyen** : XPortal (Pool BPMN exécutable gérant les états d'attente usager — soumission, correction, confirmation).
- **Moteur de workflow Métier** : XFlow (Camunda Platform 7, pool de traitement back-office).
- **Bus de messaging** : Kafka (topics `bpmn.commands`) pour la synchronisation inter-pools XPortal ↔ XFlow.
- **Identité** : Pré-remplissage transparent via e-ID (`config.users` : nom, prénom, email, téléphone).
- **Notifications** : Service Task `tg.gouv.gnspd.sendNotification` (Email + SMS multicanal).
- **Génération documentaire** : Service Task de génération PDF avec QR Code anti-fraude.

## Acteurs et Systèmes

| Acteur / Système | Rôle |
|------------------|------|
| Candidat (Citoyen) | Soumet sa candidature en ligne, corrige si demandé, confirme sa participation, télécharge son attestation. |
| Moteur XPortal | Orchestration des écrans usager (soumission, correction, consultation résultats) en attente des ordres XFlow. |
| Moteur XFlow (Back-Office) | Orchestration métier : vérification conformité, évaluation jury, génération attestation. |
| Agent DLPL (Vérificateur) | Vérifie la conformité des pièces justificatives via tableau de bord GNSPD (`gnspd.userTask`). |
| Directeur DLPL / Jury | Évalue les candidatures et prend la décision de sélection via interface back-office dédiée. |
| Service de Notification | Injection automatique Email/SMS aux jalons clés (accusé de réception, correction, sélection/non-sélection, convocation, attestation). |
| Service PDF | Génération de l'attestation de formation avec QR Code anti-fraude. |

## Résolution des Frictions AS-IS

| Friction AS-IS | Remède TO-BE | Règle d'Or Appliquée |
|----------------|-------------|---------------------|
| F1 — Aucun formulaire structuré | Formulaire Form.io Wizard structuré avec validation au fil de l'eau | Règle 1 (Zéro papier) + Règle 5 (Validation au fil de l'eau) |
| F2 — Navette physique des dossiers | Flux 100% numérique via Kafka, dossier accessible depuis le tableau de bord | Règle 1 (Simplicité) + Règle 4 (Capture à la source) |
| F3 — Notification par téléphone uniquement | Notifications automatiques Email + SMS à chaque jalon | Règle 5 (Communication proactive) + Règle 6 (Transparence) |
| F4 — Aucune traçabilité pour le candidat | Numéro de suivi automatique, statut consultable sur le portail H24 | Règle 6 (Transparence totale) |
| F5 — Manque de matériel (directeur sans PC) | Tableau de bord GNSPD accessible sur navigateur mobile (responsive) | Règle 7 (Inclusivité) |
| F6 — Problèmes de connexion | Architecture asynchrone BPMN, pas de dépendance temps réel | Règle 4 (BPMN asynchrone) |
| F7 — Pas de base centrale | Base de données centralisée, historique des candidatures consultable | Règle 3 (Zéro saisie redondante) |
| F8 — Pièces variables sans guide | Formulaire conditionnel selon le profil (écrivain vs éditeur vs bibliothécaire) | Règle 5 (Validation au fil de l'eau) |
| F9 — Communication résultats par courrier | Notification automatique système → Ministère et candidats simultanément | Règle 8 (Automatisation par défaut) |
| F10 — Indisponibilité acteurs | Confirmation de participation en ligne, rappels automatiques | Règle 5 (Communication proactive) |

## Étapes Digitalisées

### 1. Soumission en ligne (Candidat → Portail XPortal)
- Le candidat se connecte au portail citoyen et accède au formulaire « Formation des acteurs de la chaîne du livre ».
- Les champs d'identité (Nom, Prénom, Email, Téléphone) sont **pré-remplis automatiquement via e-ID** et verrouillés si non vides (logique `logic` Form.io robuste).
- Le candidat sélectionne sa **catégorie d'acteur** (Écrivain en herbe, Bibliothécaire, Libraire, Éditeur, Autre).
- Des **champs conditionnels** apparaissent selon la catégorie :
  - Écrivain : « Uploadez une ébauche de texte »
  - Éditeur : « Uploadez votre catalogue ou lettre de motivation »
  - Bibliothécaire/Libraire : « Description de votre expérience »
- Le candidat uploade sa **pièce d'identité** (PDF/JPEG, max 2 Mo).
- Le **Récapitulatif Intelligent** affiche un résumé de toutes les données avant soumission.
- Case à cocher « Je certifie sur l'honneur l'exactitude des informations ».
- **Accusé de réception automatique** par Email + SMS avec numéro de suivi.
- **Durée** : immédiat.

### 2. Réception et enregistrement automatique (Système XFlow)
- Le formulaire soumis est transmis via **Kafka** (`MSG_FORM_ACT_LIVRE_START`) au moteur XFlow.
- Création automatique du dossier en base avec numéro de suivi unique.
- Notification interne aux agents DLPL (nouveau dossier à traiter).
- **Durée** : immédiat.

### 3. Vérification de conformité et Allers-Retours (XFlow ↔ XPortal)
- L'agent DLPL instruit le dossier via `gnspd.userTask` dans le tableau de bord XFlow.
- L'agent vérifie : pièce d'identité valide, échantillon d'œuvre présent et lisible, cohérence catégorie/pièce.

**Trois décisions possibles :**

- **« Correction requise »** :
  - XFlow publie un message Kafka `MSG_FORM_ACT_LIVRE_RETURN` (action = `correction`) vers XPortal.
  - XPortal réveille le dossier citoyen et propose un **écran de resoumission** (`Activity_P_Corrections`) avec le motif de correction affiché.
  - Le candidat corrige son dossier et le resoumet (XPortal envoie `MSG_FORM_ACT_LIVRE_RESUB` vers XFlow).
  - **Limite** : maximum **3 tentatives** de correction. Au-delà, rejet automatique.

- **« Rejeté »** :
  - Notification Email + SMS au candidat avec motif de rejet.
  - Fin du processus pour ce candidat.
  - XFlow envoie `MSG_FORM_ACT_LIVRE_RETURN` (action = `rejete`) vers XPortal → EndEvent.

- **« Conforme »** :
  - Le dossier passe à l'étape d'évaluation par le jury.

- **Durée** : 1-5 jours ouvrables.

### 4. Évaluation par le Jury (Directeur DLPL + Jury)
- Le Directeur accède au tableau de bord et consulte les dossiers conformes.
- Le jury évalue la qualité de l'œuvre soumise et la pertinence du profil.
- **Deux décisions possibles** :

  - **« Sélectionné »** :
    - Le dossier passe à la notification d'admission.
    - Notification Email + SMS de sélection.

  - **« Non sélectionné »** :
    - Notification Email + SMS de non-sélection avec commentaire du jury.
    - XFlow envoie `MSG_FORM_ACT_LIVRE_RETURN` (action = `rejete`) vers XPortal → EndEvent.

- **Durée** : 3-7 jours ouvrables.

### 5. Notification d'admission et convocation (Système)
- Le candidat sélectionné reçoit une **notification automatique Email + SMS** contenant :
  - Confirmation de sélection
  - Dates et lieu de la formation
  - Programme de la formation
- Le candidat peut **confirmer sa participation** via le portail (optionnel).
- **Durée** : immédiat.

### 6. Génération et délivrance de l'attestation (Post-formation)
- Après la formation, le système génère automatiquement un **PDF d'attestation** comportant :
  - Identité du participant
  - Intitulé de la formation
  - Dates de la formation
  - **QR Code anti-fraude** (Security by Design)
- Notification Email + SMS au candidat : « Votre attestation est prête ».
- L'attestation est **téléchargeable sur le portail citoyen**.
- XFlow envoie `MSG_FORM_ACT_LIVRE_RETURN` (action = `accepte`) vers XPortal → EndEvent.
- **Durée** : immédiat.

## Cartographie des Messages Kafka

| ID Message | Nom sémantique | Sens | Émetteur | Récepteur | Déclencheur |
|-----------|---------------|------|----------|-----------|-------------|
| `MSG_FORM_ACT_LIVRE_START` | Soumission initiale | XPortal → XFlow | SendTask soumission | StartEvent XFlow | Formulaire soumis par le candidat |
| `MSG_FORM_ACT_LIVRE_RETURN` | Retour XFlow | XFlow → XPortal | SendTask retour | ReceiveTask XPortal | Toute décision XFlow (correction, rejet, accepté) |
| `MSG_FORM_ACT_LIVRE_RESUB` | Resoumission | XPortal → XFlow | SendTask correction | ReceiveTask XFlow | Candidat a corrigé son dossier |

> **Note** : Pas de message `MSG_FORM_ACT_LIVRE_PAY_CONFIRM` car le service est **gratuit**.

## Gains Attendus

| Indicateur | AS-IS | TO-BE | Gain |
|-----------|-------|-------|------|
| Délai de traitement | 1-2 mois | 1-2 semaines | Réduction de 70% |
| Déplacements physiques | Oui (dépôt dossier) | Zéro | -100% |
| Traçabilité | Aucune | Temps réel (portail + notifications) | +100% |
| Notification candidats non retenus | Aucune | Email + SMS automatique | +100% |
| Support formulaire | Libre (email, papier) | Structuré (Form.io Wizard) | Standardisation complète |
| Archivage | Local + papier | Base centralisée + GED | Sécurisation et pérennité |
| Attestation | Papier | PDF avec QR Code | Anti-fraude |
