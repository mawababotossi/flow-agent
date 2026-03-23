# SERVICE REQUIREMENT SHEET (SRS)
## Demande de Carte Nationale d'Identité (CNI)
### Direction Générale de la Documentation Nationale (DGDN) — Ministère de la Sécurité et de la Protection Civile — Togo

---

| Champ | Valeur |
|---|---|
| **Fournisseur de Services (FDS)** | Ministère de la Sécurité et de la Protection Civile — Direction Générale de la Documentation Nationale (DGDN) |
| **Service parent** | Ministère de la Sécurité et de la Protection Civile |
| **Intégrateur en charge** | À renseigner |
| **Chef de projet ATD** | À renseigner |
| **Point focal FDS** | À renseigner |
| **Date de création** | 23 mars 2026 |
| **Date de dernière révision** | 23 mars 2026 (v1.0 — Version initiale) |
| **Date de validation** | _________________________________ |
| **Back-office utilisé** | Odoo Traitement (ATD — par défaut) |
| **Déploiement cible** | Xportal + Xflow |

---

## Historique des changements

| Version | Date | Auteur | Description des modifications |
|---|---|---|---|
| 1.0 | 23/03/2026 | ATD / IA | Version initiale |

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

La Carte Nationale d'Identité biométrique (CNI) est le document officiel permettant à tout citoyen togolais d'attester de son identité sur le territoire national et dans les pays de la CEDEAO. Elle est obligatoire pour l'exercice du droit de vote, l'ouverture d'un compte bancaire et de nombreuses démarches administratives. La DGDN produit et personnalise les CNI sur une chaîne sécurisée centralisée à Lomé. Les dossiers sont collectés dans les 35 Centres de Documentation (CD) répartis sur l'ensemble du territoire.

La digitalisation permet au citoyen de soumettre son dossier en ligne, de payer électroniquement, de choisir son créneau de rendez-vous biométrique, et de suivre en temps réel l'avancement de sa demande grâce aux notifications SMS/Email. **La capture biométrique (présence physique obligatoire au CD) et le retrait du titre physique restent des étapes non digitalisables** en vertu du Décret n°2010-091 du 16 juillet 2010.

### 1.2. Fiche d'identité du service

| Champ | Valeur |
|---|---|
| **Code service** | SRV-DGDN-2026-001 |
| **Nom complet** | Demande de Carte Nationale d'Identité (CNI) |
| **Catégorie** | Sécurité / Documents d'identité |
| **Bénéficiaires** | Tout citoyen togolais âgé de 15 ans et plus |
| **Fréquence estimée** | ~250 000 CNI/an |
| **Délai standard de traitement** | 15 à 30 jours ouvrables |
| **Délai procédure d'urgence** | 48 heures |
| **Coût du service** | Payant — variable selon le type de demande |
| **Langue(s)** | Français |
| **Canaux de dépôt** | Xportal (web / mobile) |

### 1.3. Tarifs par type de demande

| Type de demande | Montant |
|---|---|
| 1ère demande (majeur) | 4 000 FCFA |
| 1ère demande (mineur 15–17 ans) | 4 000 FCFA |
| Renouvellement | 4 000 FCFA |
| Duplicata (perte ou vol) | 8 000 FCFA |
| Procédure d'urgence (48h) | 20 000 FCFA |

### 1.4. Acteurs et intervenants

| Acteur | Profil | Rôle dans le processus | Accès système | Responsabilité SLA |
|---|---|---|---|---|
| **Citoyen / Demandeur** | Personne physique (majeur ou représentant légal mineur) | Soumet le dossier en ligne, paie, choisit le RDV, se présente au CD pour la capture biométrique, retire la CNI | Xportal | Évaluateur du service |
| **Agent de réception CD** | Agent DGDN (N1 métier) | Vérifie la conformité du dossier numérique, confirme le RDV biométrique | Back-office Xflow | ≤ 48h ouvrables |
| **Opérateur biométrique CD** | Agent DGDN habilité biométrie | Capte photo, empreintes, signature ; valide données biographiques dans Xflow | Back-office Xflow | Immédiat (présence citoyen) |
| **Superviseur CD** | Responsable CD | Contrôle qualité du dossier complet avant transmission à la DGDN | Back-office Xflow — accès complet | ≤ 4h ouvrables |
| **Agent DGDN (personnalisation)** | Agent DGDN central | Marque la CNI comme produite dans Xflow après impression et contrôle qualité | Back-office Xflow | Délai production |
| **Système Xflow** | Orchestrateur BPMN | Routage automatique, notifications, suivi de statut | Infrastructure ATD | Disponibilité 99,5 % |
| **Admin Xportal (ATD)** | Technicien ATD | Surveillance, publication, KPIs | Administration Xportal | SLA plateforme |

---

## 2. Design du formulaire Form.io

### 2.1. Structure des formulaires

Le parcours est composé de 2 formulaires Form.io distincts :

- **Formulaire principal (6 onglets wizard)** : parcours complet de soumission.
- **Formulaire de correction (2 onglets wizard, conditionnel)** : activé uniquement si l'agent demande une correction.

#### Formulaire principal — 6 onglets wizard

| Onglet | Titre | Remarques |
|---|---|---|
| Onglet 1 | Bienvenue | Landing page Premium — présentation du service, tarifs, étapes, avertissement biométrique |
| Onglet 2 | Type de demande | Sélection du type + calcul automatique du montant |
| Onglet 3 | Informations personnelles | Données e-ID pré-remplies + compléments (dont mineur si applicable) |
| Onglet 4 | Pièces justificatives | Uploads conditionnels selon le type de demande |
| Onglet 5 | Rendez-vous biométrique | Sélection Centre de Documentation + date + créneau souhaités |
| Onglet 6 | Récapitulatif et soumission | Résumé + montant + déclaration sur l'honneur + bouton submit |

#### Formulaire de correction — 2 onglets wizard

| Onglet | Titre | Remarques |
|---|---|---|
| Onglet 1 | Correction du dossier | Affichage du motif de correction + uploads conditionnels (pièces à corriger) + commentaire |
| Onglet 2 | Récapitulatif et resoumission | Résumé + certification + bouton submit |

### 2.2. Champs clés du formulaire principal

| Clé | Type | Description | Obligatoire |
|---|---|---|---|
| `typedemande` | select | Type de demande | Oui |
| `montantPaiement` | hidden (calculé) | Montant automatique selon typedemande | Auto |
| `nom` | textfield | Nom de famille (pré-rempli e-ID) | Oui |
| `prenom` | textfield | Prénom(s) (pré-rempli e-ID) | Oui |
| `dateNaissance` | datetime | Date de naissance | Oui |
| `lieuNaissance` | textfield | Lieu de naissance | Oui |
| `nationalite` | textfield | Nationalité (pré-rempli "Togolaise") | Oui |
| `adresseResidence` | textarea | Adresse de résidence actuelle | Oui |
| `email` | email | Email (pré-rempli e-ID) | Oui |
| `telephone` | phoneNumber | Téléphone (pré-rempli e-ID) | Oui |
| `nomPere` | textfield | Nom du père (conditionnel : 1ère demande) | Conditonnel |
| `nomMere` | textfield | Nom de la mère (conditionnel : 1ère demande) | Conditionnel |
| `nomMineur` | textfield | Nom du mineur (conditionnel : mineur) | Conditionnel |
| `prenomMineur` | textfield | Prénom(s) du mineur | Conditionnel |
| `dateNaissanceMineur` | datetime | Date de naissance du mineur | Conditionnel |
| `acteDeNaissance` | file | Acte de naissance (1ère demande, duplicata) | Conditionnel |
| `ancienneCni` | file | Ancienne CNI (renouvellement) | Conditionnel |
| `declarationPerte` | file | Déclaration perte/vol police ou gendarmerie | Conditionnel |
| `cniRepresentantLegal` | file | CNI représentant légal (mineur) | Conditionnel |
| `centreDocumentation` | select | Centre de Documentation choisi | Oui |
| `dateRdvSouhaite` | datetime | Date souhaitée pour le RDV biométrique | Oui |
| `creneauRdv` | select | Créneau horaire souhaité | Oui |
| `declaration` | checkbox | Déclaration sur l'honneur | Oui |

### 2.3. Logique de calcul du montant (hidden field)

```javascript
var t = data.typedemande;
if (t == 'duplicata') { value = 8000; }
else if (t == 'urgence') { value = 20000; }
else { value = 4000; }
```

---

## 3. Le processus BPMN 2.0

### 3.1. Vue d'ensemble

Le processus se compose de 2 pools communicants via Kafka :

| Pool | Process ID | Rôle |
|---|---|---|
| **XPortal** | `Process_Portal` | Machine à états côté citoyen |
| **XFlow** | `Process_Xflow` | Orchestration back-office CD + DGDN |

### 3.2. Messages Kafka inter-pools

| Message | Direction | Déclencheur |
|---|---|---|
| `MSG_CNI_START` | XPortal → XFlow | Soumission initiale (avant paiement) |
| `MSG_CNI_PAY_ORDER` | XFlow → XPortal | XFlow commande le paiement au portail |
| `MSG_CNI_PAY_CALLBACK` | Externe → XFlow | Callback de la plateforme e-Gov |
| `MSG_CNI_PAY_CONFIRM` | XFlow → XPortal | Paiement validé |
| `MSG_CNI_RETURN` | XFlow → XPortal | Retour XFlow (correction / rdv_confirme / dispo / rejete) |
| `MSG_CNI_RESUB` | XPortal → XFlow | Resoumission après correction |

### 3.3. Éléments BPMN — Pool XPortal

| ID | Type | Nom | Rôle |
|---|---|---|---|
| `Event_P_Start` | StartEvent | Soumission de la demande de CNI | Point d'entrée portail |
| `Activity_P_SendBO` | SendTask | Envoi du dossier au back-office | Envoie MSG_CNI_START via Kafka |
| `Activity_P_RcvPayOrder` | ReceiveTask | Attente ordre de paiement | Reçoit MSG_CNI_PAY_ORDER |
| `Activity_P_Payment` | UserTask | Paiement des frais | Redirection vers plateforme e-Gov externe |
| `Activity_P_RcvPayConfirm` | ReceiveTask | Attente confirmation paiement | Reçoit MSG_CNI_PAY_CONFIRM |
| `Activity_P_Receive` | ReceiveTask | Attente retour XFlow | Reçoit MSG_CNI_RETURN (point d'attente central) |
| `Gateway_P_Action` | ExclusiveGateway | Quelle action ? | Route sur `result.data.action` |
| `Activity_P_RdvInfo` | UserTask | RDV biométrique confirmé | Affiche les infos RDV au citoyen, retourne à Activity_P_Receive |
| `Activity_P_Correction` | UserTask | Correction du dossier | Formulaire de correction |
| `Activity_P_SendResub` | SendTask | Envoi de la resoumission | Envoie MSG_CNI_RESUB via Kafka |
| `Event_P_End` | EndEvent | Fin | Fin du processus portail |

### 3.4. Éléments BPMN — Pool XFlow

| ID | Type | Nom | Rôle |
|---|---|---|---|
| `Event_X_Start` | StartEvent (Message) | Réception de la demande CNI | Déclenché par MSG_CNI_START |
| `Activity_X_StepSubmitted` | ServiceTask | Marquer dossier soumis | stepNotification — status: Submitted |
| `Activity_X_NotifAR` | ServiceTask | Accusé de réception SMS/Email | Notification AR avec numéro de dossier |
| `Activity_X_SendPayOrder` | SendTask | Envoyer ordre de paiement | Envoie MSG_CNI_PAY_ORDER |
| `Event_X_PayCallback` | IntermediateCatchEvent | Callback paiement | Reçoit MSG_CNI_PAY_CALLBACK de la plateforme e-Gov |
| `Activity_X_SendPayConfirm` | SendTask | Confirmer paiement | Envoie MSG_CNI_PAY_CONFIRM |
| `Activity_X_Conformite` | UserTask | Vérification de conformité (Agent CD) | Décision : conforme / correction / rejet |
| `Gateway_X_Conformite` | ExclusiveGateway | Décision conformité ? | Route sur `result.submissionData.decision` |
| `Activity_X_StepCorrection` | ServiceTask | Mettre en correction | stepNotification |
| `Activity_X_NotifCorrection` | ServiceTask | Notifier correction SMS/Email | Notification avec motif |
| `Activity_X_SendCorrection` | SendTask | Envoyer demande correction | MSG_CNI_RETURN action: "correction" |
| `Activity_X_WaitResub` | ReceiveTask | Attendre resoumission | Reçoit MSG_CNI_RESUB |
| `Activity_X_ConfirmRdv` | UserTask | Confirmer le RDV biométrique | Agent CD confirme/reprogramme le créneau |
| `Activity_X_NotifRdv` | ServiceTask | Notifier RDV SMS/Email | Notification avec détails RDV |
| `Activity_X_SendRdvConfirm` | SendTask | Envoyer confirmation RDV | MSG_CNI_RETURN action: "rdv_confirme" |
| `Activity_X_Biometrique` | UserTask | Enregistrement capture biométrique | Opérateur CD valide la capture |
| `Activity_X_Superviseur` | UserTask | Validation superviseur CD | Décision : valide / correction / rejet |
| `Gateway_X_Superviseur` | ExclusiveGateway | Décision superviseur ? | Route sur `result.submissionData.decision` |
| `Activity_X_TransmissionDGDN` | ServiceTask | Transmission lot à la DGDN | Transmission sécurisée VPN |
| `Activity_X_ProductionDGDN` | UserTask | Marquer production CNI terminée | Agent DGDN confirme la production |
| `Activity_X_OdooArchive` | ServiceTask | Archivage GED Odoo | Archivage numérique du dossier |
| `Activity_X_StepCompleted` | ServiceTask | Marquer CNI disponible | stepNotification — status: PendingCompletion |
| `Activity_X_NotifDispo` | ServiceTask | Notifier disponibilité SMS/Email | Notification avec lieu de retrait |
| `Activity_X_SendDispo` | SendTask | Clôturer le portail | MSG_CNI_RETURN action: "dispo" |
| `Event_X_End` | EndEvent | Fin | Fin du processus XFlow (succès) |
| `Activity_X_StepRejet` | ServiceTask | Marquer dossier rejeté | stepNotification — status: Rejected |
| `Activity_X_NotifRejet` | ServiceTask | Notifier rejet SMS/Email | Notification avec motif |
| `Activity_X_SendRejet` | SendTask | Signaler le rejet au portail | MSG_CNI_RETURN action: "rejete" |
| `Event_X_EndRejet` | EndEvent | Fin — Rejet | Fin du processus XFlow (rejet) |

### 3.5. Gateway XPortal — conditions de routage

| Condition | Cible |
|---|---|
| `this.data.Activity_P_Receive.result.data.action == "correction"` | `Activity_P_Correction` |
| `this.data.Activity_P_Receive.result.data.action == "rdv_confirme"` | `Activity_P_RdvInfo` |
| `this.data.Activity_P_Receive.result.data.action == "dispo"` | `Event_P_End` |
| `this.data.Activity_P_Receive.result.data.action == "rejete"` | `Event_P_End` |

### 3.6. Gateway XFlow — Conformité

| Condition | Cible |
|---|---|
| `this.data.Activity_X_Conformite.result.submissionData.decision == 'conforme'` | `Activity_X_ConfirmRdv` |
| `this.data.Activity_X_Conformite.result.submissionData.decision == 'correction'` | `Activity_X_StepCorrection` |
| `this.data.Activity_X_Conformite.result.submissionData.decision == 'rejet'` | `Activity_X_StepRejet` |

### 3.7. Gateway XFlow — Superviseur CD

| Condition | Cible |
|---|---|
| `this.data.Activity_X_Superviseur.result.submissionData.decision == 'valide'` | `Activity_X_TransmissionDGDN` |
| `this.data.Activity_X_Superviseur.result.submissionData.decision == 'correction'` | `Activity_X_Biometrique` |
| `this.data.Activity_X_Superviseur.result.submissionData.decision == 'rejete'` | `Activity_X_StepRejet` |

---

## 4. Règles métiers

### 4.1. Boucle de correction

| Paramètre | Valeur |
|---|---|
| Nombre maximum de tentatives | 3 |
| Délai maximum de resoumission | 15 jours (P15D) |
| Action si délai dépassé | Clôture automatique → `MSG_CNI_RETURN` action: "rejete" |
| Action si max tentatives dépassé | Rejet automatique → `MSG_CNI_RETURN` action: "rejete" |

### 4.2. Calcul du montant

| Type de demande | Montant |
|---|---|
| premiere_demande | 4 000 FCFA |
| premiere_demande_mineur | 4 000 FCFA |
| renouvellement | 4 000 FCFA |
| duplicata | 8 000 FCFA |
| urgence | 20 000 FCFA |

Le montant est calculé automatiquement dans le formulaire Form.io (champ `montantPaiement` hidden) et transmis à XFlow dans `submissionData.montantPaiement`.

### 4.3. Pièces justificatives conditionnelles

| Type de demande | Pièces requises |
|---|---|
| 1ère demande (majeur) | Acte de naissance |
| 1ère demande (mineur) | Acte de naissance + CNI représentant légal + informations mineur |
| Renouvellement | Ancienne CNI |
| Duplicata | Déclaration perte/vol (police ou gendarmerie) + Acte de naissance |
| Urgence | Même pièces que le type correspondant + motif d'urgence |

### 4.4. Rendez-vous biométrique

- Le citoyen choisit son Centre de Documentation, la date souhaitée et le créneau horaire dans le formulaire.
- L'agent CD dispose de **24h ouvrables** pour confirmer ou reprogrammer le RDV dans XFlow.
- La confirmation est envoyée au citoyen par SMS/Email et affichée dans XPortal (statut "RDV confirmé").
- En cas de procédure d'urgence, le RDV est planifié dans les 24h.

### 4.5. Production DGDN

- Délai standard : 15 à 30 jours ouvrables après transmission.
- Délai urgence : 48h après transmission.
- L'agent DGDN marque la production comme terminée dans XFlow une fois la CNI imprimée, contrôlée et disponible au CD.

---

## 5. Intégration avec des systèmes tiers

### 5.1. GED Odoo

| Paramètre | Valeur |
|---|---|
| **Template BPMN** | `tg.gouv.gnspd.odoo` |
| **Task ID** | `Activity_X_OdooArchive` |
| **Modèle Odoo** | `ged.document` |
| **Méthode** | `create` |
| **Données archivées** | `from_portal`, `folder_number`, `nom`, `prenom`, `typedemande`, `numeroCni` |
| **Déclencheur** | Après confirmation de production par l'agent DGDN (`Activity_X_ProductionDGDN`) |

### 5.2. Plateforme de paiement e-Gov externe

| Paramètre | Valeur |
|---|---|
| **Méthodes acceptées** | Flooz, TMoney, Visa, Mastercard |
| **Montant** | Variable (4 000 / 8 000 / 20 000 FCFA selon le type) |
| **Flux** | XFlow → MSG_CNI_PAY_ORDER → XPortal (redirection) → Plateforme externe → Callback → XFlow (MSG_CNI_PAY_CALLBACK) → MSG_CNI_PAY_CONFIRM → XPortal |
| **SLA paiement** | 30 minutes — si non confirmé, annulation automatique |

---

## 6. Notifications automatiques

| Étape | Canal | Destinataire | Contenu |
|---|---|---|---|
| **AR — Dossier reçu** | SMS + Email + In-App | Citoyen | Numéro de dossier, délai de vérification |
| **RDV biométrique confirmé** | SMS + Email + In-App | Citoyen | Lieu (CD), date, heure, documents à apporter |
| **Correction demandée** | SMS + Email + In-App | Citoyen | Motif de correction, pièces à fournir |
| **CNI disponible** | SMS + Email + In-App | Citoyen | Lieu de retrait, documents à présenter (récépissé + pièce d'identité) |
| **Rejet définitif** | SMS + Email | Citoyen | Motif de rejet |

### 6.1. Jalons de notification

```
Soumission → [AR] → Paiement → Vérification → [RDV confirmé] → Capture bio
→ Transmission DGDN → [En production] → [CNI disponible] → Retrait
```

---

## 7. KPIs du service & engagements SLA

### 7.1. SLA par étape

| Étape | Acteur responsable | SLA |
|---|---|---|
| Vérification de conformité + confirmation RDV | Agent CD | ≤ 48h ouvrables |
| Enregistrement capture biométrique | Opérateur CD | Jour du RDV |
| Validation superviseur CD | Superviseur CD | ≤ 4h ouvrables |
| Transmission à la DGDN | Système | ≤ 24h après validation |
| Production CNI (standard) | DGDN | 15 à 30 jours ouvrables |
| Production CNI (urgence) | DGDN | 48 heures |

### 7.2. KPIs cibles

| KPI | Cible | Baseline AS-IS |
|---|---|---|
| Taux de dossiers complets à la 1ère soumission | ≥ 90 % | ~85 % |
| Délai de confirmation RDV | ≤ 48h | Non mesuré |
| Taux de notification SMS envoyées | 100 % | ~40 % (partiel) |
| Délai moyen de traitement standard | ≤ 20 jours ouvrables | 15–30 jours |
| Satisfaction citoyen (CSAT) | ≥ 4/5 | Non mesuré |
| Taux de CNI non réclamées | ≤ 5 % | Non mesuré (problème signalé) |

---

## 8. Interface e-service

### 8.1. Formulaire principal (XPortal)

**Clé Form.io :** `01FORM_DEMANDE_CNI`
**URL de déploiement :** `/demande-carte-nationale-identite`
**Fichier source :** `formio-demande-carte-nationale-identite.json`

### 8.2. Formulaire de correction (XPortal)

**Clé Form.io :** `01FORM_CORRECTION_CNI`
**URL de déploiement :** `/correction-carte-nationale-identite`
**Fichier source :** `formio-correction-carte-nationale-identite.json`

### 8.3. Données pré-remplies via e-ID

| Champ formulaire | Source e-ID |
|---|---|
| `nom` | `config.users.lastName` |
| `prenom` | `config.users.firstName` |
| `email` | `config.users.email` |
| `telephone` | `config.users.phone` |

---

## 9. Validations & signatures

### 9.1. Validations côté citoyen (Form.io)

| Validation | Type | Règle |
|---|---|---|
| Champs obligatoires | Required | Tous les champs marqués Oui dans la section 2.2 |
| Format email | Pattern | `^[^@\s]+@[^@\s]+\.[^@\s]+$` |
| Taille fichiers | Max size | 2 Mo par fichier |
| Format fichiers | File type | PDF, JPG, PNG uniquement |
| Date RDV | Min date | Date du jour minimum, weekends désactivés |
| Déclaration sur l'honneur | Checkbox required | Obligatoire pour la soumission |

### 9.2. Validations back-office (XFlow)

| Validation | Acteur | Critères |
|---|---|---|
| Conformité du dossier | Agent de réception CD | Authenticité et lisibilité des pièces, concordance des informations, validité de la déclaration de perte (duplicata) |
| Données biométriques | Opérateur biométrique | Qualité photo, empreintes lisibles (10 doigts), concordance données biographiques |
| Contrôle qualité final | Superviseur CD | Complétude du dossier, qualité biométrique, absence d'anomalie |

### 9.3. Contraintes légales

| Élément | Statut | Base légale |
|---|---|---|
| Capture biométrique en présentiel | **PHYSIQUE OBLIGATOIRE** | Décret n°2010-091 du 16 juillet 2010 |
| Remise du titre physique | **PHYSIQUE OBLIGATOIRE** | Loi n°98-004 du 11 février 1998 |
| Signature du registre de délivrance | **PHYSIQUE OBLIGATOIRE** | Arrêté n°014/MSP du 12 mars 2015 |

---

## Annexes

### A. Fichiers liés

| Fichier | Description |
|---|---|
| `bpmn-demande-carte-nationale-identite.bpmn` | BPMN 2.0 exécutable (XPortal + XFlow) |
| `demande-carte-nationale-identite-pipeline.yaml` | Pipeline structuré (input générateur BPMN) |
| `formio-demande-carte-nationale-identite.json` | Formulaire principal Form.io |
| `formio-correction-carte-nationale-identite.json` | Formulaire de correction Form.io |
| `demande-carte-nationale-identite-as-is.md` | Cartographie AS-IS du processus |
| `demande-carte-nationale-identite-to-be.md` | Cartographie TO-BE du processus |

### B. Centres de Documentation

35 Centres de Documentation répartis sur le territoire national (1 par préfecture + plusieurs à Lomé). La liste complète est intégrée dans le formulaire Form.io (`centreDocumentation` select).

### C. Identifiant de la CNI biométrique

Le numéro de CNI (`numeroCni`) est assigné par la DGDN lors de la production et transmis via XFlow (`Activity_X_ProductionDGDN.result.submissionData.numeroCni`). Il est archivé dans la GED Odoo.
