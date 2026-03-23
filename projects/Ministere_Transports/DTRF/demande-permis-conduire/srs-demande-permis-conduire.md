# SERVICE REQUIREMENT SHEET (SRS)
## DEMANDE ET DÉLIVRANCE DU PERMIS DE CONDUIRE
### Direction des Transports Routiers et Ferroviaires (DTRF) — République Togolaise

---

| Champ | Valeur |
|---|---|
| **Fournisseur de Services (FDS)** | DTRF — Direction des Transports Routiers et Ferroviaires |
| **Service parent** | Ministère des Transports |
| **Intégrateur en charge** | [Nom de la société intégratrice] |
| **Chef de projet ATD** | [Nom du chef de projet] |
| **Point focal FDS** | [Nom du responsable côté DTRF] |
| **Date de création** | 21 mars 2026 |
| **Date de dernière révision** | 21 mars 2026 (v1.0 — version initiale) |
| **Date de validation** | _________________________________ |
| **Back-office utilisé** | Odoo Traitement (ATD — par défaut) |
| **Déploiement cible** | Xportal + Xflow |

---

## Historique des changements

| Version | Date | Auteur | Description des modifications |
|---|---|---|---|
| 1.0 | 21/03/2026 | Équipe ATD | Version initiale — rédaction après analyse du Kobo DTRF et cartographies AS-IS / TO-BE |

---

## Table des matières

1. [Identification du service](#1-identification-du-service)
2. [Design du formulaire Form.io](#2-design-du-formulaire-formio)
3. [Le processus BPMN 2.0](#3-le-processus-bpmn-20)
4. [Règles métiers](#4-règles-métiers)
5. [Intégration avec des systèmes tiers](#5-intégration-avec-des-systèmes-tiers)
6. [Notifications automatiques](#6-notifications-automatiques)
7. [KPIs du service & engagements SLA](#7-kpis-du-service--engagements-sla)
8. [Interface e-service DTRF](#8-interface-e-service-dtrf)
9. [Validations & signatures](#9-validations--signatures)

---

## 1. Identification du service

### 1.1. Description fonctionnelle

Le permis de conduire est le titre officiel autorisant son titulaire à conduire un véhicule à moteur sur la voie publique au Togo. Régi par la loi n°2004-003 du 24 janvier 2004 relative à la sécurité routière, il est délivré par la DTRF après réussite aux épreuves théoriques (code de la route, QCM 40 questions, seuil 35/40) et pratiques (circuit + route, notée sur 20, seuil 10/20). Le titre se décline en catégories A (moto), B (voiture), C/D (poids lourds, bus) et E (remorque), chacune soumise à des conditions d'âge et de pré-requis spécifiques.

La digitalisation de ce service permet au candidat de soumettre son dossier d'inscription en ligne via Xportal, de payer les frais électroniquement (Flooz, TMoney, Visa, Mastercard), et de suivre l'avancement de son dossier en temps réel. Il reçoit des notifications automatiques à chaque jalon (accusé de réception, convocation biométrie, convocation examen, résultats, disponibilité du permis). Seuls le relevé biométrique, les épreuves physiques et le retrait du titre sécurisé nécessitent un déplacement.

### 1.2. Fiche d'identité du service

| Champ | Valeur |
|---|---|
| **Code service** | SRV-DTRF-2026-001 |
| **Nom complet** | Demande et délivrance du permis de conduire (catégories A / B / C / D / E) |
| **Catégorie** | Transport / Sécurité Routière |
| **Bénéficiaires** | Citoyens togolais ou résidents légaux remplissant les conditions d'âge par catégorie |
| **Fréquence estimée** | ~8 000 permis délivrés par an (~1 000/mois) |
| **Délai standard de traitement** | 5 jours ouvrés (vérification conformité + inscription examen) |
| **Délai réglementaire maximum** | [À renseigner par la DTRF] |
| **Coût du service** | Payant — Inscription examen : 5 000 FCFA / Délivrance : 15 000 FCFA / Duplicata : 15 000 FCFA |
| **Langue(s)** | Français |
| **Canaux de dépôt** | Xportal (web / mobile) |

### 1.3. Acteurs et intervenants

| Acteur | Profil | Rôle dans le processus | Accès système | Responsabilité SLA |
|---|---|---|---|---|
| **Citoyen / Candidat** | Candidat au permis de conduire | Soumet la demande en ligne, paie, se présente aux épreuves physiques et au relevé biométrique, retire le permis | Xportal (lecture seule) | Évaluateur du service |
| **Agent de réception DTRF** | Agent DTRF (N1 métier) | Vérifie la conformité du dossier, effectue le relevé biométrique, inscrit aux sessions d'examen | Back-office — Odoo Traitement | Délai : selon SLA DTRF |
| **Inspecteur code DTRF** | Inspecteur examen théorique | Surveille l'épreuve QCM, saisit les résultats dans XFlow | Back-office — saisie résultats | Saisie résultats jour même |
| **Inspecteur conduite DTRF** | Inspecteur assermenté épreuve pratique | Évalue la conduite, saisit les résultats dans XFlow | Back-office — saisie résultats | Saisie résultats jour même |
| **Chef de service DTRF** | Responsable administratif DTRF | Valide la délivrance du permis, approuve la production du titre | Back-office — accès complet | Délai : selon SLA DTRF |
| **Système Xflow** | Orchestrateur BPMN | Routage automatique, notifications, escalades temporelles, calcul montants | Infrastructure ATD | Disponibilité 99,5% |
| **Admin Xportal (ATD)** | Technicien ATD | Surveillance, publication, KPIs | Administration Xportal | SLA plateforme |
| **Centre d'appel (N1)** | Agent support ATD | Assistance candidats en difficulté sur la démarche | Consultation statut uniquement | Résolution < 30 min |

---

## 2. Design du formulaire Form.io

### 2.1. Structure du formulaire

Le parcours est composé de deux formulaires Form.io distincts orchestrés par Xflow :

- **Formulaire principal (6 onglets)** : parcours commun à tous les candidats (première inscription et duplicata).
- **Formulaire de correction (1 onglet, conditionnel)** : activé uniquement lorsque l'agent demande des corrections, entre la vérification de conformité et la reprise d'instruction.

#### Formulaire principal — 6 onglets wizard

| Onglet | Titre | Remarques |
|---|---|---|
| Onglet 1 | Présentation — Qualification de la demande | Landing page premium + sélection type de demande (inscription / duplicata) et catégorie |
| Onglet 2 | Informations personnelles | Identité du candidat (e-ID pré-remplie) + coordonnées |
| Onglet 3 | Informations sur la formation | Auto-école, catégorie, lieu de retrait souhaité |
| Onglet 4 | Pièces à fournir | Upload pièces justificatives — conditionnelles selon type de demande |
| Onglet 5 | Paiement | Calcul automatique du montant selon type de demande |
| Onglet 6 | Récapitulatif et soumission | Résumé non modifiable + confirmation |

#### Formulaire de correction — Conditionnel (non-conformité dossier)

Ce formulaire est un composant Form.io indépendant (slug : `correction-permis-conduire`), déclenché par Xflow via une Send Task après la vérification de conformité, uniquement lorsque l'agent demande des corrections. Il s'affiche dans Xportal comme une tâche utilisateur intercalée.

| Formulaire | Titre | Condition de déclenchement |
|---|---|---|
| Correction dossier | Corrections requises — Permis de conduire | `decision == "correction"` uniquement — déclenché par Xflow (étape B05) |

### 2.2. Détail des champs

#### Onglet 1 — Présentation — Qualification de la demande

Landing page premium avec grille Bootstrap (columns 8/4), Info Pills (avantages du service : zéro déplacement pour le dépôt, paiement en ligne, suivi temps réel), Sidebar DTRF (adresse, horaires, contacts), guide pas à pas numéroté.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `typeDemande` | Type de demande | Radio | Oui | `premiereInscription` / `duplicata` | Saisie | Conditionne l'affichage des pièces (Onglet 4) et le montant (Onglet 5). RG-001 |
| `categoriePermis` | Catégorie de permis demandée | Select | Oui | A / B / C / D / E | Saisie | Conditionne l'âge minimum requis. RG-002 |

#### Onglet 2 — Informations personnelles

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `nom` | Nom de famille | Texte | Oui | Lecture seule dynamique (logic e-ID) | Profil Citoyen (`config.users.lastName`) | Verrouillé si e-ID non vide. RG-003 |
| `prenom` | Prénom(s) | Texte | Oui | Lecture seule dynamique (logic e-ID) | Profil Citoyen (`config.users.firstName`) | Verrouillé si e-ID non vide. RG-003 |
| `dateNaissance` | Date de naissance | Date | Oui | Format JJ/MM/AAAA. Validation âge minimum selon catégorie. `validateOn: blur` | Saisie | Message custom : *« Vous devez avoir au moins [N] ans pour la catégorie [X] »*. RG-002 |
| `lieuNaissance` | Lieu de naissance | Texte | Oui | Min 2 caractères. `validateOn: blur` | Saisie | |
| `nationalite` | Nationalité | Select | Oui | Liste dynamique | API (`config.apiBaseUrl/references/nationalities`) | |
| `sexe` | Sexe | Radio | Oui | `masculin` / `feminin` | Saisie | |
| `telephone` | Numéro de téléphone | Téléphone | Oui | Regex : `^(\+228)?[0-9]{8}$`. `validateOn: blur` | Profil Citoyen (`config.users.phone`) | Message custom : *« Format attendu : +228XXXXXXXX ou 8 chiffres »*. Verrouillé si e-ID non vide |
| `email` | Adresse email | Email | Oui | Format email standard. `validateOn: blur` | Profil Citoyen (`config.users.email`) | Verrouillé si e-ID non vide |
| `adresseResidence` | Adresse de résidence | Texte | Oui | Min 5 caractères. `validateOn: blur` | Saisie | |
| `ville` | Ville / Commune | Select | Oui | Liste dynamique | API (`config.apiBaseUrl/references/cities`) | |
| `region` | Région | Select | Oui | Liste dynamique | API (`config.apiBaseUrl/references/regions`) | |

#### Onglet 3 — Informations sur la formation

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `nomAutoEcole` | Nom de l'auto-école | Texte | Conditionnel | Min 3 caractères. `validateOn: blur` | Saisie | Obligatoire si `typeDemande == premiereInscription`. Masqué si duplicata. RG-004 |
| `villeAutoEcole` | Ville de l'auto-école | Select | Conditionnel | Liste dynamique | API (`config.apiBaseUrl/references/cities`) | Obligatoire si `typeDemande == premiereInscription` |
| `numeroAttestation` | Numéro d'attestation de formation | Texte | Conditionnel | Alphanumérique. `validateOn: blur` | Saisie | Obligatoire si `typeDemande == premiereInscription`. RG-004 |
| `lieuRetraitSouhaite` | Bureau de retrait souhaité | Select | Oui | Lomé / Kara / Atakpamé / Sokodé / Dapaong | Saisie | Lieu où le candidat souhaite retirer son permis physique |
| `permisExistant` | Possédez-vous déjà un permis ? | Radio | Conditionnel | `oui` / `non` | Saisie | Affiché si `categoriePermis` == C, D ou E. RG-005 |
| `numeroPermisExistant` | Numéro du permis existant | Texte | Conditionnel | Alphanumérique. `validateOn: blur` | Saisie | Obligatoire si `permisExistant == oui`. RG-005 |

#### Onglet 4 — Pièces à fournir

Les fichiers sont uploadés directement dans Xportal et transmis à Xflow. Formats acceptés : PDF, JPG, PNG. Taille maximale : 2 Mo par fichier.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `pieceIdentite` | Copie de la pièce d'identité nationale ou passeport | Fichier | Oui | PDF/JPG/PNG < 2 Mo | Upload | En cours de validité |
| `acteNaissance` | Copie de l'acte de naissance | Fichier | Oui | PDF/JPG/PNG < 2 Mo | Upload | |
| `certificatMedical` | Certificat médical d'aptitude à la conduite | Fichier | Conditionnel | PDF/JPG/PNG < 2 Mo | Upload | Obligatoire si `typeDemande == premiereInscription`. Daté de moins de 3 mois. RG-006 |
| `attestationFormation` | Attestation de formation de l'auto-école agréée | Fichier | Conditionnel | PDF/JPG/PNG < 2 Mo | Upload | Obligatoire si `typeDemande == premiereInscription`. RG-004 |
| `photosIdentite` | Photos d'identité (4x4 cm) | Fichier | Oui | JPG/PNG < 2 Mo. Multiple (4 fichiers) | Upload | 4 photos format 4x4 cm |
| `declarationPerte` | Déclaration de perte ou de vol (police/gendarmerie) | Fichier | Conditionnel | PDF/JPG/PNG < 2 Mo | Upload | Obligatoire si `typeDemande == duplicata`. Original requis. RG-007 |
| `copiePermisPerdu` | Copie du permis perdu (si disponible) | Fichier | Non | PDF/JPG/PNG < 2 Mo | Upload | Facultatif. Affiché si `typeDemande == duplicata` |

#### Onglet 5 — Paiement

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `montantPaiement` | Montant à payer | Texte (caché) | N/A | Calculé automatiquement. Si `typeDemande == premiereInscription` → 20 000 FCFA (5 000 inscription + 15 000 délivrance). Si `typeDemande == duplicata` → 15 000 FCFA. | Système (Calculate Costs) | Champ caché, utilisé par l'action Calculate Costs. RG-008 |
| `recapMontant` | Récapitulatif du montant | HTML | N/A | Affiche le détail du calcul | Système | Composant HTML de présentation du montant |

#### Formulaire de correction — Détail des champs

Ce formulaire est déclenché par XFlow lorsque l'agent demande des corrections. Il affiche le motif de correction et permet au citoyen de reuploader les pièces non conformes.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `motifCorrection` | Motif de la demande de correction | HTML | N/A | Lecture seule | Système (Xflow) | Pré-rempli par l'agent via Xflow |
| `pieceCorrigee1` | Pièce corrigée | Fichier | Oui | PDF/JPG/PNG < 2 Mo | Upload | Le candidat uploade les pièces corrigées |
| `commentaireCandidat` | Commentaire (optionnel) | Texte (zone) | Non | Max 500 caractères | Saisie | |

**Propriétés techniques :**

| Propriété technique | Valeur |
|---|---|
| **Slug du formulaire** | `correction-permis-conduire` |
| **Version** | 1 (`locked = true`, `status = Active`) |
| **Déclencheur processus** | Send Task Xflow — étape B05 (message : `MSG_PC_CORRECTION`) |
| **Condition d'affichage** | `decision == "correction"` — formulaire invisible sinon |
| **Action post-traitement** | Receive Task Xflow — étape B06 attend resoumission avant de continuer |

#### Onglet 6 — Récapitulatif et soumission

L'onglet 6 affiche un résumé de toutes les données saisies via le script d'analyse natif ATD. L'usager coche une case de confirmation. P-Studio gère nativement le bouton « Soumettre » sur le dernier panel du wizard.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `htmlRecapitulatifFinal` | N/A | HTML | N/A | Script Parseur Formulaire | Système | Injection du composant Récapitulatif Intelligent |
| `luEtApprouve` | Je déclare et certifie sur l'honneur que les informations fournies sont exactes et complètes. | Checkbox | Oui | Doit être coché | Saisie | Ignoré par le récap via `excludeKeys` |

### 2.3. Actions du formulaire (P-Studio)

Les actions suivantes sont pré-configurées sur la soumission du formulaire P-Studio :

| Code Action P-Studio | Condition d'activation | Configuration algorithmique |
|---|---|---|
| **Calculate Costs** | Toujours actif | Champ dynamique : Si `typeDemande == "premiereInscription"` → 20 000 FCFA (5 000 + 15 000). Si `typeDemande == "duplicata"` → 15 000 FCFA. |
| **Publish to RabbitMQ** | Toujours actif | Routing Key: `submissions.topic` — Queue: `workflows-engine.main.queue` |

---

## 3. Le processus BPMN 2.0

### 3.1. Vue d'ensemble du processus TO-BE

| Champ | Valeur |
|---|---|
| **Nom du processus** | `Procedure_DemandePermisConduire_v1` |
| **Événement déclencheur** | Soumission du formulaire par le candidat sur Xportal |
| **Événement de fin (succès)** | Notification au candidat que le permis est prêt au retrait + clôture du dossier |
| **Événement de fin (rejet)** | Notification de rejet définitif motivé au candidat |
| **Moteur d'exécution** | Xflow (Camunda Platform 7 — GNSPD Framework) |
| **Version processus** | 1.0 |
| **Participants BPMN** | Pool XPORTAL (citoyen) + Pool XFLOW (back-office) — deux pools exécutables communiquant via Kafka |

### 3.2. Étapes détaillées du processus

#### Lane PORTAL — Côté Citoyen

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| 01 | Soumission de la demande | Le candidat remplit le formulaire wizard (6 onglets), uploade les pièces, paie en ligne et soumet. Le système génère un numéro de suivi. | Citoyen | Immédiat | → 02 |
| 02 | Accusé de réception | XPortal envoie un accusé de réception automatique par SMS + Email avec le numéro de suivi et le délai estimé. | Système | < 5 min | → 03 (envoi vers XFlow) |
| 03 | Envoi du dossier à XFlow | Send Task : le dossier complet est transmis à XFlow via Kafka (message `MSG_PC_START`). | Système | Immédiat | → 04 |
| 04 | Attente décision back-office | Receive Task multi-entrante : XPortal attend la décision de XFlow. Les actions possibles sont : `correction`, `biometrie`, `convocation_code`, `resultat_code`, `convocation_pratique`, `resultat_pratique`, `accepte`, `rejete`. | Système | Variable | Gateway action → 05/06/07/08/09 |
| 05 | Correction du dossier | Si `action == correction` : affichage du formulaire de correction avec le motif de l'agent. Le candidat corrige et resoumets. Send Task : resoumission vers XFlow (`MSG_PC_RESUB`). Retour → 04. | Citoyen | ≤ 15 jours | → 04 (boucle) |
| 06 | Convocation biométrie | Si `action == biometrie` : affichage de la convocation (date, lieu, heure) pour le relevé biométrique. | Système | Immédiat | → 04 (attente prochaine action) |
| 07 | Résultats examen théorique | Si `action == resultat_code` : affichage du résultat du code de la route (note, succès/échec). | Système | Immédiat | → 04 |
| 08 | Résultats examen pratique | Si `action == resultat_pratique` : affichage du résultat de l'épreuve pratique (note, succès/échec). | Système | Immédiat | → 04 |
| 09 | Notification finale | Si `action == accepte` : notification que le permis est prêt au retrait au bureau choisi. Si `action == rejete` : notification de rejet avec motif. | Système | < 5 min | → FIN |

#### Lane XFLOW — Côté Back-office

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| B01 | Initialisation procédure | Xflow reçoit le message de démarrage depuis Xportal (`MSG_PC_START`). Les données du formulaire et les pièces jointes sont chargées. Vérification du paiement confirmé. | Système | Immédiat | → B02 |
| B02 | Vérification paiement | Gateway : le paiement est-il confirmé ? Si oui → B03. Si non → B14 (rejet). | Système | Immédiat | Si payé → B03 / Si non payé → B14 |
| B03 | Recevoir les données candidat | Script Task : extraction et normalisation des données du formulaire soumis. Vérification automatique des formats, cohérence et complétude. | Système | < 2 min | → B04 |
| B04 | Vérification de conformité | User Task assignée à l'agent DTRF : examen du dossier, vérification des pièces justificatives (authenticité, lisibilité, validité). | Agent DTRF | Selon SLA DTRF | Si conforme → B06 / Si corrections → B05 / Si rejet → B14 |
| B05 | Notification correction | Send Task : envoi d'une notification de correction au portail avec le motif détaillé (`MSG_PC_CORRECTION`). Incrémentation du compteur `nbCorrections`. Si `nbCorrections > 3` → B14 (rejet automatique). | Système | < 15 min | → Attente resoumission (B06) |
| B06 | Réception resoumission | Receive Task : attend la resoumission du candidat (`MSG_PC_RESUB`). Timer boundary event : si pas de resoumission sous 15 jours → B14 (rejet automatique). | Système | ≤ 15 jours | → B04 (retour vérification) |
| B07 | Convocation biométrie | Send Task : envoi d'une convocation biométrique au candidat via XPortal (`MSG_PC_BIOMETRIE`). Notification SMS/Email avec date, lieu et heure du rendez-vous. | Système | < 5 min | → B08 |
| B08 | Relevé biométrique | User Task assignée à l'agent DTRF : capture des données biométriques (photo, empreintes, signature) lors de la présence physique du candidat. Enregistrement dans le système. | Agent DTRF | 1 jour | → B09 |
| B09 | Inscription session code | User Task : l'agent inscrit le candidat à la prochaine session d'examen du code. Send Task de convocation au candidat via XPortal (`MSG_PC_CONVOC_CODE`). | Agent DTRF | 1-2 jours | → B10 |
| B10 | Saisie résultats code | User Task assignée à l'inspecteur code : saisie de la note du QCM (sur 40). Gateway : si note ≥ 35 → B11. Si note < 35 → notification échec au candidat (retour B09 pour réinscription ou B14 si 3 échecs consécutifs). | Inspecteur code DTRF | Jour de session | Si ≥ 35/40 → B11 / Si < 35/40 → réinscription ou B14 |
| B11 | Inscription session pratique | User Task : inscription automatique à la prochaine session d'épreuve pratique. Send Task de convocation au candidat (`MSG_PC_CONVOC_PRATIQUE`). | Agent DTRF | 1-2 jours | → B12 |
| B12 | Saisie résultats pratique | User Task assignée à l'inspecteur conduite : saisie de la note (sur 20, grille normalisée). Gateway : si note ≥ 10 → B13. Si note < 10 → notification échec (réinscription ou formation 5h si 3 échecs consécutifs). | Inspecteur conduite DTRF | Jour de session | Si ≥ 10/20 → B13 / Si < 10/20 → réinscription ou B14 |
| B13 | Validation et production permis | User Task chef de service : validation finale du dossier complet. Service Task : lancement de la production du titre sécurisé (carte plastifiée avec photo biométrique, QR Code ATD). Archivage GED Odoo. | Chef de service DTRF | 2-5 jours | → B15 |
| B14 | Envoi rejet définitif | Send Task : envoi de la notification de rejet définitif au portail avec le motif détaillé (`MSG_PC_REJETE`). Archivage du dossier. | Système | < 5 min | → FIN (rejet) |
| B15 | Notification permis prêt | Send Task : envoi de la notification au portail indiquant que le permis est prêt au retrait (`MSG_PC_ACCEPTE`). SMS + Email au candidat avec le lieu de retrait choisi. | Système | < 5 min | → FIN (succès) |

### 3.3. Flux d'escalade temporelle

| Déclencheur | Canal | Action |
|---|---|---|
| Délai instruction agent dépassé (SLA DTRF > 48h) | Email + Dashboard | Escalade automatique vers chef de service DTRF |
| Délai correction candidat dépassé (15 jours ouvrés) | SMS + Email | Rejet automatique du dossier avec notification |
| Nombre maximum de corrections dépassé (> 3 tentatives) | SMS + Email | Rejet automatique avec notification |
| Délai paiement non confirmé | SMS + Email | Annulation automatique de la demande |
| 3 échecs consécutifs épreuve pratique | SMS + Email | Exigence formation complémentaire 5h avant réinscription |
| Indisponibilité Xflow > 15 min | Email Admin | Alerte automatique à l'Admin ATD |

---

## 4. Règles métiers

| ID | Règle métier | Description / Condition | Priorité | Étapes concernées |
|---|---|---|---|---|
| RG-001 | Type de demande obligatoire | Si `typeDemande` est vide → blocage avec message : *« Veuillez sélectionner le type de demande (première inscription ou duplicata) »* | HAUTE | Onglet 1 formulaire |
| RG-002 | Âge minimum par catégorie | Si `categoriePermis == "A"` et âge < 16 ans → blocage. Si `categoriePermis == "B"` et âge < 18 ans → blocage. Si `categoriePermis` ∈ {C, D, E} et âge < 21 ans → blocage. Message : *« Vous devez avoir au moins [N] ans pour la catégorie [X] »* | HAUTE | Onglet 2 formulaire |
| RG-003 | Verrouillage e-ID | Si `config.users.lastName` est non vide et non constitué uniquement d'espaces → les champs `nom`, `prenom`, `telephone`, `email` sont verrouillés en lecture seule via bloc `logic` (property `disabled = true`). L'usager garde la main si l'e-ID remonte une valeur vide ou corrompue. | HAUTE | Onglet 2 formulaire |
| RG-004 | Pièces conditionnelles première inscription | Si `typeDemande == "premiereInscription"` → les champs `certificatMedical`, `attestationFormation`, `nomAutoEcole`, `numeroAttestation` passent obligatoires dynamiquement. | HAUTE | Onglets 3-4 formulaire |
| RG-005 | Pré-requis permis B pour catégories C/D/E | Si `categoriePermis` ∈ {C, D, E} → le champ `permisExistant` est affiché et doit être `oui`. Le champ `numeroPermisExistant` devient obligatoire. Message si non : *« Un permis de catégorie B est requis pour demander les catégories C, D ou E »* | HAUTE | Onglet 3 formulaire |
| RG-006 | Validité certificat médical | Le certificat médical doit être daté de moins de 3 mois à la date de soumission. Vérification par l'agent lors de l'instruction (B04). | HAUTE | Onglet 4, Étape B04 |
| RG-007 | Pièces conditionnelles duplicata | Si `typeDemande == "duplicata"` → le champ `declarationPerte` passe obligatoire. Les champs de formation (auto-école, attestation) sont masqués. | HAUTE | Onglets 3-4 formulaire |
| RG-008 | Paiement préalable obligatoire | Le processus d'instruction ne démarre qu'après confirmation effective du paiement. Montant calculé automatiquement : première inscription = 20 000 FCFA, duplicata = 15 000 FCFA. | HAUTE | Onglet 5, Étapes B01-B02 |
| RG-009 | Conformité des pièces jointes | Les fichiers uploadés doivent respecter : formats PDF/JPG/PNG, taille < 2 Mo par fichier. Tout fichier non conforme est rejeté avec message explicite : *« Le fichier dépasse 2 Mo ou n'est pas au format accepté (PDF, JPG, PNG) »* | MOYENNE | Onglet 4, Étape B03 |
| RG-010 | Limite boucle de correction | Le candidat dispose de 3 tentatives maximum pour corriger son dossier. Au-delà, rejet automatique avec notification : *« Votre dossier a été rejeté après 3 tentatives de correction infructueuses »* | HAUTE | Étapes B05-B06 |
| RG-011 | Délai de correction candidat | Le candidat dispose de 15 jours ouvrés pour soumettre un dossier corrigé. Au-delà, le dossier est clôturé automatiquement avec statut *« Rejeté — délai dépassé »* | HAUTE | Étapes 05, B06 |
| RG-012 | Une demande active par candidat | Un candidat identifié par son numéro de pièce d'identité ne peut avoir qu'une seule demande en cours. Si une demande est active, bloquer la nouvelle soumission. | HAUTE | Étape 01 |
| RG-013 | Seuil épreuve théorique | Le candidat doit obtenir au minimum 35/40 au QCM du code de la route pour être admis à l'épreuve pratique. | HAUTE | Étape B10 |
| RG-014 | Seuil épreuve pratique | Le candidat doit obtenir au minimum 10/20 à l'épreuve pratique (circuit + route) pour être admis à la délivrance. | HAUTE | Étape B12 |
| RG-015 | Formation complémentaire après 3 échecs pratique | Après 3 échecs consécutifs à l'épreuve pratique, le système exige une attestation de formation complémentaire de 5h avant toute nouvelle inscription. | HAUTE | Étape B12 |
| RG-016 | Archivage 10 ans | Tous les dossiers (approuvés et rejetés) doivent être archivés pendant 10 ans minimum conformément aux obligations légales togolaises. | HAUTE | Post-décision |
| RG-017 | Durée de validité du permis | Le permis délivré a une validité de 10 ans (catégories A et B) ou 5 ans (catégories C, D, E). Cette information est inscrite sur le titre. | MOYENNE | Étape B13 |

---

## 5. Intégration avec des systèmes tiers

Les intégrations suivantes sont envisagées. Elles nécessitent la signature de conventions d'échange de données entre les structures concernées.

| Système cible | Type d'intégration | Données échangées | Condition d'appel | Statut |
|---|---|---|---|---|
| Système biométrique DTRF | API interne | Photo, empreintes digitales, signature du candidat | Étape B08 — Relevé biométrique | À configurer |
| Plateforme paiement e-Gov | API REST (paiement) | Montant, référence dossier, statut paiement (Flooz, TMoney, Visa, MC) | Étape B02 — Vérification paiement | À configurer |
| Plateforme SMS ATD | API REST (envoi) | Numéro téléphone, texte message, réf. dossier | À chaque changement de statut | Disponible |
| Plateforme Email ATD | API REST (envoi) | Adresse email, objet, corps message, réf. dossier | À chaque changement de statut | Disponible |
| GED Odoo (archivage) | API interne | Dossier complet (formulaire + pièces + décision + données biométriques) | Post-décision — Archivage automatique | Disponible |
| Base de données nationale des permis | API interne (lecture/écriture) | Données du permis, numéro, catégorie, validité, titulaire | Étape B13 — Enregistrement permis | À développer |
| Système identité numérique (e-ID) | API REST (vérification) | NOM, PRÉNOMS, DATE NAISSANCE, NUMÉRO CNI | Pré-remplissage formulaire | Disponible |

---

## 6. Notifications automatiques

| Réf. | Déclencheur | Canal | Destinataire | Message type |
|---|---|---|---|---|
| N01 | Soumission formulaire (Étape 01) | SMS + Email | Candidat | *Votre demande de permis de conduire (réf. [DOSSIER]) a bien été reçue. Paiement confirmé : [montant] FCFA. Délai de traitement : 5 jours ouvrés.* |
| N02 | Corrections demandées (B05) | SMS + Email | Candidat | *Votre dossier (réf. [DOSSIER]) est incomplet ou comporte des erreurs. Corrections requises : [motif]. Vous avez 15 jours pour corriger.* |
| N03 | Dossier conforme — convocation biométrie (B07) | SMS + Email | Candidat | *Votre dossier est conforme. Vous êtes convoqué(e) le [date] à [heure] au bureau DTRF de [lieu] pour le relevé de vos données biométriques.* |
| N04 | Convocation examen code (B09) | SMS + Email | Candidat | *Vous êtes inscrit(e) à la session d'examen du code de la route du [date] à [heure] au centre de [lieu]. Présentez-vous avec votre pièce d'identité.* |
| N05 | Résultat code — succès (B10) | SMS + Email | Candidat | *Félicitations ! Vous avez obtenu [note]/40 au code de la route. Vous serez convoqué(e) prochainement pour l'épreuve pratique.* |
| N06 | Résultat code — échec (B10) | SMS + Email | Candidat | *Votre résultat au code de la route : [note]/40 (seuil requis : 35/40). Vous pouvez vous réinscrire à la prochaine session.* |
| N07 | Convocation épreuve pratique (B11) | SMS + Email | Candidat | *Vous êtes inscrit(e) à l'épreuve pratique de conduite du [date] à [heure] au centre de [lieu].* |
| N08 | Résultat pratique — succès (B12) | SMS + Email | Candidat | *Félicitations ! Vous avez obtenu [note]/20 à l'épreuve pratique. Votre permis est en cours de production.* |
| N09 | Résultat pratique — échec (B12) | SMS + Email | Candidat | *Votre résultat à l'épreuve pratique : [note]/20 (seuil requis : 10/20). Vous pouvez vous réinscrire à la prochaine session.* |
| N10 | Permis prêt au retrait (B15) | SMS + Email | Candidat | *Votre permis de conduire (réf. [DOSSIER]) est prêt. Retirez-le au bureau DTRF de [lieu_retrait] muni de votre pièce d'identité.* |
| N11 | Rejet définitif (B14) | SMS + Email | Candidat | *Votre demande de permis (réf. [DOSSIER]) a été rejetée. Motif : [motif_rejet]. Vous pouvez soumettre une nouvelle demande.* |
| N12 | Rappel agent — délai à risque | Email + Dashboard | Agent DTRF | *Rappel : Le dossier [DOSSIER] doit être traité avant [date_heure_limite].* |
| N13 | Escalade superviseur | Email + Dashboard | Chef de service DTRF | *Escalade automatique : Le dossier [DOSSIER] dépasse le délai d'instruction (48h). Action requise.* |
| N14 | Invitation évaluation (J+1 retrait) | SMS + Email | Candidat | *Êtes-vous satisfait(e) de votre expérience ? Évaluez ce service en 30 secondes sur Xportal.* |

---

## 7. KPIs du service & engagements SLA

| Indicateur | Valeur cible |
|---|---|
| **Taux de complétion** | ≥ 85% (dossiers soumis / formulaires initiés) |
| **Taux d'abandon** | ≤ 15% |
| **Délai standard de traitement** (vérification conformité) | 5 jours ouvrés |
| **Délai réglementaire maximum** | [À renseigner par la DTRF] |
| **Délai de production du permis** (post-validation) | ≤ 5 jours ouvrés |
| **Taux de rejet au dépôt** | ≤ 10% (vs 20% en AS-IS) |
| **Taux de réussite code** | ~65% (statistique métier) |
| **Taux de réussite pratique** | ~75% (statistique métier) |
| **Note de satisfaction usager** | ≥ 4,0 / 5 |
| **Taux de résolution N1 (FCR)** | ≥ 80% |
| **Disponibilité service (Xportal/Xflow)** | ≥ 99,5% mensuel |
| **Délai notification accusé de réception** | < 5 minutes |
| **Délai notification résultats examens** | < 30 minutes (après saisie inspecteur) |

---

## 8. Interface e-service DTRF

Aucune interface e-service dédiée n'est prévue pour ce service. Le service est accessible exclusivement via Xportal. La DTRF n'ayant pas de portail web dédié, l'ensemble du parcours citoyen (soumission, suivi, notifications) est centralisé sur la plateforme Xportal de l'ATD.

---

## 9. Validations & signatures

Le présent SRS a été élaboré à l'issue des ateliers d'analyse conduits entre l'intégrateur, l'équipe ATD et les points focaux de la DTRF. Il constitue la référence contractuelle pour le développement, les tests et la mise en production du service.

| | Rédigé par | Validé par (FDS) | Approuvé par (ATD) |
|---|---|---|---|
| **Qualité** | Intégrateur Externe | Point focal DTRF | Chef de projet ATD |
| **Nom** | ________________________ | ________________________ | ________________________ |
| **Date** | _______________________ | _______________________ | _______________________ |
| **Signature** | __________________ | __________________ | __________________ |

---

*SRS — Demande et Délivrance du Permis de Conduire | v1.0 | ATD*
