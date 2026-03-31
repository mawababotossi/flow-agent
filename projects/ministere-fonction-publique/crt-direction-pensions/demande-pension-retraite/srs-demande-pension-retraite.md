# SERVICE REQUIREMENT SHEET
## DEMANDE DE MISE À LA RETRAITE ET DE LIQUIDATION DE PENSION
### Caisse de Retraite du Togo (CRT) — République Togolaise

---

| Champ | Valeur |
|---|---|
| **Fournisseur de Services (FDS)** | Caisse de Retraite du Togo (CRT) |
| **Service parent** | Direction des Pensions à la CRT — Ministère de la Fonction Publique |
| **Intégrateur en charge** | [Nom de la société intégratrice] |
| **Chef de projet ATD** | [Nom du chef de projet] |
| **Point focal FDS** | [Nom du responsable côté CRT] |
| **Date de création** | 25 mars 2026 |
| **Date de dernière révision** | 25 mars 2026 (v1.0 — version initiale) |
| **Date de validation** | _________________________________ |
| **Back-office utilisé** | Odoo Traitement (ATD — par défaut) |
| **Déploiement cible** | Xportal + Xflow + Interface e-service CRT |

---

## Historique des changements

| Version | Date | Auteur | Description des modifications |
|---|---|---|---|
| 1.0 | 25/03/2026 | Équipe ATD | Version initiale — rédaction après analyse Kobo et cartographie AS-IS/TO-BE |

---

## Table des matières

1. [Identification du service](#1-identification-du-service)
2. [Design du formulaire Form.io](#2-design-du-formulaire-formio)
3. [Le processus BPMN 2.0](#3-le-processus-bpmn-20)
4. [Règles métiers](#4-règles-métiers)
5. [Intégration avec des systèmes tiers](#5-intégration-avec-des-systèmes-tiers)
6. [Notifications automatiques](#6-notifications-automatiques)
7. [KPIs du service & engagements SLA](#7-kpis-du-service--engagements-sla)
8. [Interface e-service CRT](#8-interface-e-service-crt)
9. [Validations & signatures](#9-validations--signatures)

---

## 1. Identification du service

### 1.1. Description fonctionnelle

La liquidation de pension est un droit constitutionnel accordé à tout agent titulaire de la Fonction Publique togolaise ayant accompli au minimum 15 années de services effectifs et atteignant l'âge légal de la retraite (60 ans en règle générale, avec dérogations pour invalidité ou impossibilité permanente de service). La Caisse de Retraite du Togo (CRT), sous tutelle du Ministère de la Fonction Publique, est l'organe chargé du calcul, de la liquidation et du versement mensuel des droits à pension. Le service gère également les pensions de réversion accordées aux ayants droit (conjoint survivant, orphelins) des fonctionnaires décédés. La base légale est constituée de la Loi n°2005-003 du 23 juillet 2005 portant Statut Général de la Fonction Publique, du Décret n°2005-054 du 8 juillet 2005 portant Règlement de la CRT, et du Code des Pensions civiles et militaires (Décret n°92-142).

La digitalisation de ce service transforme radicalement l'expérience du fonctionnaire en fin de carrière : au lieu de courir 2 à 3 mois entre guichets (mairie, DRH, Ministère, banque), il soumet l'intégralité de son dossier en ligne depuis n'importe quel lieu via Xportal, grâce à un formulaire wizard guidé qui pré-remplit son identité via e-ID et l'aide à ne rien oublier grâce à une liste de contrôle interactive. La CRT instruit le dossier via un tableau de bord back-office centralisé, le calcul de pension est effectué par le liquidateur, et le titre de pension est généré en PDF et mis à disposition sur le portail. Le délai de traitement cible passe de 3-6 mois à moins de 30 jours ouvrables après réception du dossier complet.

### 1.2. Fiche d'identité du service

| Champ | Valeur |
|---|---|
| **Code service** | SRV-CRT-2026-001 |
| **Nom complet** | Demande de Mise à la Retraite et de Liquidation de Pension |
| **Catégorie** | Fonction Publique / Protection Sociale |
| **Bénéficiaires** | Agents titulaires de la FP togolaise en fin de carrière ; ayants droit (pension de réversion) |
| **Fréquence estimée** | ~1 200 nouveaux dossiers par an |
| **Délai standard de traitement** | 20 jours ouvrables (après réception du dossier complet) |
| **Délai réglementaire maximum** | [À confirmer par la CRT — délai légal cible] |
| **Coût du service** | Gratuit |
| **Langue(s)** | Français |
| **Canaux de dépôt** | Xportal (web / mobile) — Interface e-service CRT |

### 1.3. Acteurs et intervenants

| Acteur | Profil | Rôle dans le processus | Accès système | Responsabilité SLA |
|---|---|---|---|---|
| **Fonctionnaire / Ayant droit** | Agent titulaire FP ou conjoint survivant | Soumet le dossier, corrige sur demande, reçoit le titre | Xportal (lecture seule) | Évaluateur du service |
| **Liquidateur CRT** | Agent Direction des Pensions (N1 métier) | Instruit le dossier, vérifie les droits, valide le calcul | Back-office — Odoo Traitement | Délai : 10 jours ouvrables |
| **Contrôleur CRT** | Agent Direction des Pensions (N2 contrôle) | Contre-vérifie le calcul avant production du titre | Back-office — Odoo Traitement | Délai : 5 jours ouvrables |
| **Directeur Général CRT** | DG CRT | Signe le titre de pension (hybride — physique/numérique) | Tableau de bord + signature physique | Délai : 3 jours ouvrables |
| **Système Xflow** | Orchestrateur BPMN | Routage automatique, notifications, escalades temporelles | Infrastructure ATD / CRT | Disponibilité 99,5% |
| **Admin Xportal (ATD)** | Technicien ATD | Surveillance, publication, KPIs | Administration Xportal | SLA plateforme |
| **Centre d'appel (N1)** | Agent support ATD | Assistance fonctionnaires en difficulté sur la démarche | Consultation statut uniquement | Résolution < 30 min |

---

## 2. Design du formulaire Form.io

### 2.1. Structure du formulaire

Le parcours est composé de 4 formulaires Form.io distincts orchestrés par Xflow :

- **Formulaire principal (6 onglets)** : parcours de soumission citoyen, commun à toutes les catégories de demande (avec onglets conditionnels selon le type de demande).
- **Formulaire de correction (1 onglet, conditionnel)** : activé uniquement lorsque le liquidateur exige des corrections, entre l'instruction et la resoumission citoyen.
- **Formulaire d'instruction — Liquidateur CRT (userTask XFlow)** : formulaire présenté à l'agent liquidateur pour instruire le dossier, valider le calcul et rendre une décision.
- **Formulaire de contre-vérification — Contrôleur CRT (userTask XFlow)** : formulaire présenté au contrôleur pour la contre-vérification avant production du titre.

#### Formulaire principal — 6 onglets wizard

| Onglet | Titre | Remarques |
|---|---|---|
| Onglet 1 | Présentation & Qualification de la demande | Qualifie le type de demande (retraite d'office / anticipée / invalidité / réversion). Conditionne les pièces obligatoires et certains champs des onglets suivants. Affiche les conditions d'éligibilité. |
| Onglet 2 | Identité du demandeur | Identité pré-remplie via e-ID (`config.users`). Champs supplémentaires pour ayants droit (identité conjoint décédé). |
| Onglet 3 | Informations de carrière | Données de carrière (ministère, poste, dates). Saisie manuelle par le demandeur. |
| Onglet 4 | Coordonnées bancaires | Modalité de versement de la pension (virement bancaire, CCP). |
| Onglet 5 | Pièces justificatives | Upload de toutes les pièces. Champs conditionnels selon le type de demande. |
| Onglet 6 | Récapitulatif et soumission | Résumé non modifiable + déclaration sur l'honneur + CAPTCHA. |

#### Formulaire de correction — Conditionnel (décision Liquidateur = Correction requise)

Ce formulaire est un composant Form.io indépendant (slug : `v1_correction-demande-pension-retraite`), déclenché par Xflow via une Send Task après la décision de correction du liquidateur (étape B04). Il s'affiche dans Xportal comme une tâche utilisateur intercalée avant la resoumission.

| Formulaire | Titre | Condition de déclenchement |
|---|---|---|
| Correction | Correction de votre demande de pension | Décision liquidateur = `correctionRequise` — déclenché par Xflow (étape B04) |

### 2.2. Détail des champs

#### Onglet 1 — Présentation & Qualification de la demande

Cet onglet présente le service, vérifie l'éligibilité et conditionne le parcours.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `htmlIntro` | [Bloc HTML d'accueil] | HTML | N/A | Statique | Système | Présentation du service, avantages, liste de contrôle des documents à préparer |
| `typeDemande` | Type de demande | Radio | Oui | Retraite d'office (60 ans) / Retraite anticipée / Retraite pour invalidité / Pension de réversion | Saisie | Conditionne les pièces et certains champs (RG-001) |
| `confirmationEligibilite` | Je confirme remplir les conditions d'éligibilité légales pour ce type de demande | Checkbox | Oui | Doit être cochée | Saisie | Affiche un texte d'éligibilité contextuel selon `typeDemande`. Bloque si non cochée. |
| `typeAgent` | Catégorie de l'agent | Radio | Conditionnel | Fonctionnaire titulaire civil / Militaire / Agent contractuel titularisé | Saisie | Affiché si `typeDemande ≠ Pension de réversion` |

#### Onglet 2 — Identité du demandeur

Les champs marqués *Profil Citoyen* sont pré-remplis via e-ID et mis en lecture seule.

**Section A — Identité du demandeur**

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `nom` | Nom | Texte | Oui | Majuscules, max 60 car. | Profil Citoyen (`config.users`) | Lecture seule — pré-rempli e-ID |
| `prenoms` | Prénoms | Texte | Oui | Max 100 car. | Profil Citoyen (`config.users`) | Lecture seule — pré-rempli e-ID |
| `dateNaissance` | Date de naissance | Date | Oui | DD/MM/YYYY | Profil Citoyen (`config.users`) | Lecture seule — pré-rempli e-ID |
| `lieuNaissance` | Lieu de naissance | Texte | Oui | Max 80 car. | Profil Citoyen (`config.users`) | Lecture seule — pré-rempli e-ID |
| `numeroCNI` | Numéro CNI | Texte | Oui | Alphanum. | Profil Citoyen (`config.users`) | Lecture seule — pré-rempli e-ID |
| `numeroMatricule` | Numéro matricule FP | Texte | Oui | Alphanum. max 20 car. | Saisie | Non disponible dans e-ID — saisie manuelle |
| `adresseResidence` | Adresse de résidence actuelle | Texte | Oui | Max 150 car. | Saisie | |
| `numeroTelephone` | Numéro de téléphone | Téléphone | Oui | +228 XXXXXXXX | Profil Citoyen (`config.users`) | Lecture seule — pré-rempli e-ID |
| `email` | Adresse e-mail | Email | Non | Format RFC 5322 | Profil Citoyen (`config.users`) | Pré-rempli si disponible ; pour notifications |

**Section B — Identité du fonctionnaire décédé (conditionnel : `typeDemande = Pension de réversion`)**

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `nomConjointDecede` | Nom du fonctionnaire décédé | Texte | Conditionnel | Majuscules, max 60 car. | Saisie | Obligatoire si réversion (RG-002) |
| `prenomsConjointDecede` | Prénoms du fonctionnaire décédé | Texte | Conditionnel | Max 100 car. | Saisie | Obligatoire si réversion |
| `matriculeConjointDecede` | Numéro matricule du fonctionnaire décédé | Texte | Conditionnel | Alphanum. max 20 car. | Saisie | Obligatoire si réversion |
| `dateDecesConjoint` | Date de décès | Date | Conditionnel | DD/MM/YYYY | Saisie | Obligatoire si réversion |

#### Onglet 3 — Informations de carrière

| `directionService` | Direction / Service | Texte | Oui | Max 100 car. | Saisie | |
| `dernierPoste` | Dernier poste occupé | Texte | Oui | Max 100 car. | Saisie | |
| `categorieCorps` | Catégorie / Corps | Texte | Oui | Ex : A1, B2... | Saisie | |
| `derniereEchelon` | Échelon | Texte | Oui | Alphanum. | Saisie | |
| `dernierIndice` | Dernier indice salarial | Nombre | Oui | Entier positif | Saisie | Utilisé pour le calcul de pension |
| `dateEntreeFP` | Date d'entrée dans la Fonction Publique | Date | Oui | DD/MM/YYYY | Saisie | |
| `dateMiseRetraite` | Date de mise à la retraite | Date | Oui | DD/MM/YYYY | Saisie | Date effective de cessation de service |
| `nombreAnnuitesDeclarees` | Nombre d'annuités déclarées | Nombre | Oui | Entier ≥ 15 (RG-003) | Saisie | |
| `motifRetraiteAnticipee` | Motif de la demande de retraite anticipée | Zone de texte | Conditionnel | Max 500 car. | Saisie | Obligatoire si `typeDemande = Retraite anticipée ou Invalidité` (RG-004) |

#### Onglet 4 — Coordonnées bancaires

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `modePaiement` | Mode de versement de la pension | Radio | Oui | Virement bancaire / CCP (compte chèque postal) | Saisie | Conditionne les champs suivants (RG-005) |
| `nomBanque` | Nom de l'établissement bancaire | Texte | Conditionnel | Max 100 car. | Saisie | Obligatoire si `modePaiement = Virement bancaire` |
| `agenceBanque` | Agence | Texte | Conditionnel | Max 100 car. | Saisie | Obligatoire si virement bancaire |
| `ribCompte` | Numéro de compte / RIB | Texte | Conditionnel | Alphanum. max 30 car. | Saisie | Obligatoire si virement bancaire |
| `numeroCCP` | Numéro de compte CCP | Texte | Conditionnel | Numérique max 15 car. | Saisie | Obligatoire si `modePaiement = CCP` |

#### Onglet 5 — Pièces justificatives

Formats acceptés : PDF, JPG, PNG. Taille maximale : 5 Mo par fichier.

**Section A — Pièces communes à toutes les demandes (hors réversion)**

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `acteMiseRetraite` | Acte de mise à la retraite (signé par le Ministre) | Fichier | Oui | PDF < 5 Mo | Upload | Document obligatoire — signé manuscritement par le Ministre de la FP |
| `arreteNomination` | Arrêté de nomination dans la Fonction Publique | Fichier | Oui | PDF/JPG/PNG < 5 Mo | Upload | Copie certifiée conforme |
| `copieCNI` | Copie de la CNI en cours de validité | Fichier | Oui | PDF/JPG/PNG < 5 Mo | Upload | |
| `acteNaissance` | Acte de naissance | Fichier | Oui | PDF/JPG/PNG < 5 Mo | Upload | Copie certifiée conforme |
| `dernierBulletinSalaire` | Dernier bulletin de salaire | Fichier | Oui | PDF/JPG/PNG < 5 Mo | Upload | |
| `releveEtatsServices` | Relevé des états de services (DRH du Ministère) | Fichier | Oui | PDF < 5 Mo | Upload | Délivré par la DRH du Ministère d'affectation |
| `livretMariage` | Livret de mariage | Fichier | Conditionnel | PDF/JPG/PNG < 5 Mo | Upload | Obligatoire si le demandeur est marié (RG-006) |
| `actesNaissanceEnfants` | Actes de naissance des enfants à charge | Fichier | Conditionnel | PDF/JPG/PNG < 5 Mo | Upload | Obligatoire si enfants à charge déclarés |
| `certificatMedical` | Certificat médical d'aptitude / invalidité | Fichier | Conditionnel | PDF < 5 Mo | Upload | Obligatoire si `typeDemande = Retraite anticipée ou Invalidité` (RG-004) |

**Section B — Pièces spécifiques pension de réversion (conditionnel : `typeDemande = Pension de réversion`)**

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `acteDecesConjoint` | Acte de décès du fonctionnaire | Fichier | Conditionnel | PDF/JPG/PNG < 5 Mo | Upload | Obligatoire si réversion (RG-002) |
| `titrePensionConjoint` | Titre de pension du fonctionnaire décédé | Fichier | Conditionnel | PDF < 5 Mo | Upload | Si fonctionnaire était déjà pensionné |
| `acteMarriage` | Acte de mariage légalisé | Fichier | Conditionnel | PDF/JPG/PNG < 5 Mo | Upload | Obligatoire si réversion |
| `pieceIdentiteConjoint` | Pièce d'identité du conjoint survivant | Fichier | Conditionnel | PDF/JPG/PNG < 5 Mo | Upload | Obligatoire si réversion |
| `actesNaissanceOrphelins` | Actes de naissance des enfants orphelins | Fichier | Conditionnel | PDF/JPG/PNG < 5 Mo | Upload | Si pension d'orphelin demandée |
| `certificatNonRemariage` | Certificat de non-remariage | Fichier | Conditionnel | PDF < 5 Mo | Upload | Obligatoire pour le conjoint survivant (réversion) |

#### Onglet 6 — Récapitulatif et soumission

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `luEtApprouve` | Je déclare et certifie sur l'honneur que les informations contenues dans ce dossier sont correctes et exactes. Je suis conscient(e) que toute fausse déclaration m'expose à des poursuites. | Checkbox | Oui | Doit être coché | Saisie | Bloque la soumission si non coché |
| `captcha` | Vérification anti-robot | reCAPTCHA | Oui | Google reCAPTCHA v3 | Système | Score minimum : 0,5 |

#### Formulaire de correction — Détail des champs

Ce formulaire affiche le motif de correction transmis par le liquidateur et permet au demandeur de compléter ou corriger uniquement les éléments signalés.

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `htmlMotifCorrection` | Motif de la demande de correction | HTML | N/A | Injecté par Xflow | Système | Affiche le motif détaillé transmis par le liquidateur |
| `piecesCorriges` | Pièces à corriger ou compléter | Fichier (multiple) | Conditionnel | PDF/JPG/PNG < 5 Mo | Upload | Seules les pièces signalées sont demandées |
| `commentaireDemandeur` | Commentaire (facultatif) | Zone de texte | Non | Max 500 car. | Saisie | |

#### Formulaire d'instruction — Liquidateur CRT (userTask XFlow)

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `htmlResumeDossier` | Résumé du dossier | HTML | N/A | Généré par Xflow | Système | Affiche les données clés du demandeur et les pièces uploadées |
| `annuitesValidees` | Annuités validées | Nombre | Oui | Entier ≥ 0 | Saisie | Ajustable par le liquidateur |
| `indiceRetenu` | Indice retenu | Nombre | Oui | Entier positif | Saisie | |
| `montantPensionCalcule` | Montant mensuel de pension calculé (FCFA) | Nombre | Oui | Calculé automatiquement | Système | Lecture seule — calculé par le moteur (indice × annuités × taux) |
| `observationsLiquidateur` | Observations du liquidateur | Zone de texte | Non | Max 1000 car. | Saisie | Notes internes de l'agent |
| `decisionInstruction` | Décision | Radio | Oui | Conforme / Correction requise / Rejet | Saisie | Conditionne le routage du processus |
| `motifDecision` | Motif de correction ou de rejet | Zone de texte | Conditionnel | Max 500 car. | Saisie | Obligatoire si décision ≠ Conforme (RG-007) |

#### Formulaire de contre-vérification — Contrôleur CRT (userTask XFlow)

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `htmlResumeDossierControle` | Résumé dossier + calcul à vérifier | HTML | N/A | Généré par Xflow | Système | Données complètes + calcul liquidateur |
| `conformiteCalcul` | Le calcul de pension est-il exact ? | Radio | Oui | Oui / Non | Saisie | Si Non → renvoi interne au liquidateur |
| `observationsControleur` | Observations du contrôleur | Zone de texte | Non | Max 1000 car. | Saisie | |
| `decisionControle` | Décision finale | Radio | Oui | Validé / Renvoi en correction interne | Saisie | Si renvoi → retour au liquidateur sans notification citoyen |

### 2.3. Actions du formulaire (P-Studio)

| Formulaire | Action | Déclencheur | Description |
|---|---|---|---|
| Principal | `publish_submission` | Soumission | Publication du dossier vers Xflow via message Kafka |
| Principal | `gnspdSubmissionData` | Soumission (conditionnel) | Transmission des données `submissionData.data` si disponible |
| Correction | `publish_submission` | Resoumission | Renvoie le dossier corrigé vers Xflow |
| Instruction | `complete_task` | Décision liquidateur | Complète la userTask Xflow et route selon la décision |
| Contre-vérification | `complete_task` | Décision contrôleur | Complète la userTask Xflow |

### 2.4. Configuration des environnements

| Paramètre | Valeur (Portail) | Valeur (XFlow) |
|---|---|---|
| `PORTAL_BASE_URL` | https://xportal.gouv.tg | N/A |
| `ETAT_CIVIL_API_URL` | N/A | https://etatcivil.gouv.tg/api |
| `PROCESS_KEY` | `PENSION_RETRAITE` | `PENSION_RETRAITE` |

### 2.5. Inventaire des formulaires userTask

| ID BPMN | Nom de la tâche | Formulaire | Assigné à | Pool |
|---|---|---|---|---|
| `Activity_P_Corrections` | Faire les corrections | `v1_correction-demande-pension-retraite` | Demandeur | PORTAL |
| `Activity_X_Instruction` | Instruction du dossier | `v1_instruction-pension-retraite` | Liquidateur CRT | XFLOW |
| `Activity_X_Contreverification` | Contre-vérification | `v1_contreverification-pension-retraite` | Contrôleur CRT | XFLOW |

---

## 3. Le processus BPMN 2.0

### 3.1. Vue d'ensemble du processus TO-BE

| Champ | Valeur |
|---|---|
| **Nom du processus** | `Procédure_Demande_Pension_Retraite_v1` |
| **Événement déclencheur** | Soumission du formulaire par le demandeur sur Xportal |
| **Événement de fin (succès)** | Titre de pension généré, notifié et disponible en téléchargement sur le portail |
| **Événement de fin (rejet)** | Notification de rejet définitif motivé au demandeur |
| **Moteur d'exécution** | Xflow (Camunda Platform 7) |
| **Version processus** | 1.0 |
| **Participants BPMN** | PORTAL (lane citoyen) + XFLOW (lane back-office CRT) |
| **Type de service** | Gratuit — pas de sous-processus paiement |

### 3.2. Étapes détaillées du processus

#### Lane PORTAL — Côté Citoyen

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| P01 | Soumission de la demande de pension | Le demandeur remplit et soumet le formulaire depuis Xportal. Un numéro de dossier unique est généré. Le système envoie les données au back-office via message Kafka (`MSG_PENSION_START`). | Système / Citoyen | Immédiat | → Attente traitement (P02) |
| P02 | Attente de traitement back-office | Le dossier est en cours d'instruction à la CRT. Le citoyen peut consulter l'état de son dossier sur le portail. | Système | Selon SLA CRT | Si correction → P03 / Si décision finale → P04 |
| P03 | Réception demande de correction | Le citoyen reçoit un SMS/email avec le motif précis. Il accède à son dossier sur le portail et corrige les éléments signalés. | Citoyen | 15 jours calendaires (timer) | → P02 (resoumission via `MSG_PENSION_RESUB`) |
| P04 | Réception de la décision finale | Le citoyen est notifié de la décision : acceptation (titre disponible au téléchargement) ou rejet définitif motivé. | Système / Citoyen | < 5 min | → FIN |

#### Lane XFLOW — Côté Back-office CRT

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| B01 | Initialisation de la procédure | Xflow reçoit le message de démarrage. Les données du formulaire sont chargées et normalisées. Notification d'accusé de réception envoyée au demandeur. | Système | Immédiat | → B02 |
| B02 | (Étape supprimée) | | | | |
| B03 | Instruction du dossier | User Task assignée au liquidateur CRT : examen du dossier, contrôle des pièces, vérification des droits (ancienneté ≥ 15 ans, âge légal), validation ou ajustement du calcul de pension. | Liquidateur CRT | 10 jours ouvrables | Si conforme → B05 / Si correction → B04 / Si rejet → B08 |
| B04 | Notification de correction au citoyen | Send Task : envoi d'un message Kafka `MSG_PENSION_RETURN` (correction) vers le portail. Notification SMS/email au demandeur avec le motif détaillé. | Système | < 5 min | → Attente resoumission (ReceiveTask `MSG_PENSION_RESUB`) → retour B03 |
| B05 | Contre-vérification | User Task assignée au contrôleur CRT : vérification du calcul de pension et des données avant production du titre. | Contrôleur CRT | 5 jours ouvrables | Si validé → B06 / Si renvoi interne → B03 |
| B06 | Génération du projet de titre de pension | Service Task : génération automatique du projet de titre de pension en PDF (template normé ATD, données pré-remplies). | Système | Immédiat | → B07 |
| B07 | Signature du titre de pension (hybride) | User Task notifiant le DG CRT : liste des titres à signer dans le tableau de bord. Signature physique ou électronique qualifiée. Le titre signé est numérisé et versé dans le dossier. | DG CRT | 3 jours ouvrables | → B08 |
| B08 | Génération PDF final | Service Task : génération du titre de pension définitif en PDF. Mise à disposition sur le portail. Mise à jour fichier pensionnés actifs. Transmission au service comptable. | Système | Immédiat | → B09 |
| B08-R | Notification de rejet définitif | Send Task : envoi de la notification de rejet définitif via Kafka (`MSG_PENSION_FINAL`) + SMS/email au demandeur avec motif et voies de recours. | Système | < 5 min | → FIN (rejet) |
| B09 | Notification de mise à disposition | Send Task : envoi de la notification de succès via Kafka (`MSG_PENSION_FINAL`) + SMS/email au demandeur. Fin du processus back-office. | Système | < 5 min | → FIN (succès) |

### 3.3. Matrice des échanges inter-pools (Kafka)

| # | Direction | Message Kafka | Déclencheur | Contenu principal |
|---|---|---|---|---|
| 1 | PORTAL → XFLOW | `MSG_PENSION_START` | Soumission formulaire (P01) | Données formulaire complet + pièces jointes |
| 2 | XFLOW → PORTAL | `MSG_PENSION_RETURN` (correction) | Décision correction liquidateur (B04) | Motif de correction, liste des pièces à corriger |
| 3 | PORTAL → XFLOW | `MSG_PENSION_RESUB` | Resoumission citoyen (P03) | Dossier corrigé + nouvelles pièces |
| 4 | XFLOW → PORTAL | `MSG_PENSION_FINAL` (succès) | Notification mise à disposition (B09) | Lien de téléchargement titre de pension |
| 4b | XFLOW → PORTAL | `MSG_PENSION_FINAL` (rejet) | Rejet définitif (B08-R) | Motif rejet + voies de recours |

### 3.4. Flux d'escalade temporelle

| Déclencheur | Canal | Action |
|---|---|---|
| Délai instruction liquidateur dépassé (10 jours ouvrables) | Email + Dashboard | Escalade automatique vers Contrôleur / Superviseur CRT |
| Délai contre-vérification dépassé (5 jours ouvrables) | Email + Dashboard | Escalade automatique vers DG CRT |
| Délai correction citoyen dépassé (15 jours calendaires) | SMS + Email | Rejet automatique du dossier avec notification motivée |
| Délai signature DG dépassé (3 jours ouvrables) | Email + Dashboard | Rappel automatique au DG CRT |
| (Indisponibilité API supprimée) | | |

---

## 4. Règles métiers

| ID | Règle métier | Description / Condition | Priorité | Étapes concernées |
|---|---|---|---|---|
| RG-001 | Type de demande conditionne le parcours | `typeDemande` détermine les pièces obligatoires, les champs affichés dans les onglets 2, 3 et 5, et le texte de conditions d'éligibilité affiché. | HAUTE | Onglet 1, 2, 3, 5 |
| RG-002 | Pension de réversion — champs et pièces spécifiques | Si `typeDemande = Pension de réversion`, les sections B de l'onglet 2 et de l'onglet 5 deviennent obligatoires. Les champs de carrière (onglet 3) sont adaptés au fonctionnaire décédé. | HAUTE | Onglets 2, 3, 5 |
| RG-003 | Ancienneté minimale de 15 ans | Le champ `nombreAnnuitesDeclarees` doit être ≥ 15. Si inférieur, message bloquant : *« Vous devez avoir accompli au minimum 15 années de services effectifs pour bénéficier d'une pension complète. »* | HAUTE | Onglet 3, B03 |
| RG-004 | Pièces conditionnelles retraite anticipée / invalidité | Si `typeDemande = Retraite anticipée ou Invalidité`, les champs `motifRetraiteAnticipee` et `certificatMedical` deviennent obligatoires. | HAUTE | Onglets 3, 5 |
| RG-005 | Coordonnées bancaires conditionnelles | Les champs `nomBanque`, `agenceBanque`, `ribCompte` sont obligatoires si `modePaiement = Virement bancaire`. Le champ `numeroCCP` est obligatoire si `modePaiement = CCP`. | HAUTE | Onglet 4 |
| RG-006 | Livret de mariage conditionnel | Le champ `livretMariage` est obligatoire si le demandeur est marié. Une question radio de qualification sera ajoutée en début d'onglet 5. | MOYENNE | Onglet 5 |
| RG-007 | Motif obligatoire si correction ou rejet | Si `decisionInstruction ≠ Conforme`, le champ `motifDecision` du formulaire d'instruction est obligatoire. Ce motif est transmis au citoyen dans la notification. | HAUTE | Formulaire instruction, B04 |
| RG-008 | Boucle de correction limitée à 3 tentatives | Un compteur `correctionCount` est géré par Xflow. Si `correctionCount ≥ 3`, le dossier est automatiquement rejeté avec notification : *« Votre dossier a été clôturé suite au dépassement du nombre maximal de tentatives de correction. »* | HAUTE | B04, B03 |
| RG-009 | Conformité des pièces jointes | Les fichiers uploadés doivent respecter : formats PDF/JPG/PNG, taille < 5 Mo par fichier. Tout fichier non conforme génère un message d'erreur bloquant côté Form.io. | MOYENNE | Onglet 5 |
| RG-010 | Un seul dossier actif par matricule | Un demandeur identifié par son numéro matricule ne peut avoir qu'un seul dossier actif. Si un dossier est en cours, la nouvelle soumission est bloquée avec message explicatif. | HAUTE | P01, B01 |
| RG-011 | Calcul assisté de pension | Le montant mensuel est calculé par le moteur : `montantPension = dernierIndice × tauxAnnuité × annuitesValidees`. Ces variables proviennent de la saisie manuelle du liquidateur (onglet Instruction). Le montant est affiché en lecture seule ; le liquidateur peut l'ajuster avec justification. | HAUTE | B03, formulaire instruction |
| RG-012 | Archivage 30 ans | Tous les dossiers (approuvés et rejetés) doivent être archivés pendant 30 ans minimum conformément aux obligations légales pour les dossiers de pension (durée de vie du pensionné + marge). | HAUTE | Post-décision |
| RG-013 | Interconnexion état civil — détection décès | Xflow interroge l'API état civil à chaque cycle de contrôle d'existence. Si un décès est détecté, la pension est suspendue automatiquement avec notification à la CRT pour vérification. | HAUTE | Contrôle d'existence (hors scope formulaire principal) |

---

## 5. Intégration avec des systèmes tiers

| Système cible | Type d'intégration | Données échangées | Condition d'appel | Statut |
|---|---|---|---|---|
| e-ID Togo | API REST (lecture) | Profil citoyen : nom, prénoms, date/lieu naissance, CNI | Formulaire principal (onglet 2) — pré-remplissage | Disponible |
| Registre État Civil | API REST (lecture) | Numéro CNI → statut vital (vivant/décédé) | Contrôle d'existence annuel | À développer |
| Plateforme SMS | API REST (envoi) | Numéro téléphone, texte message, réf. dossier | À chaque changement de statut | Disponible |
| Plateforme Email | SMTP / API | Adresse email, contenu, réf. dossier | À chaque changement de statut | Disponible |
| Système archivage ATD | API interne | Dossier complet (formulaire + pièces + décision + titre) | Post-décision | Disponible |
| Service comptable CRT | Notification interne | Matricule pensionné, montant pension, RIB/CCP | Après signature titre (B08) | À configurer |

---

## 6. Notifications automatiques

| Réf. | Déclencheur | Canal | Destinataire | Message type |
|---|---|---|---|---|
| N01 | Soumission formulaire (P01) | SMS + Email | Demandeur | *Votre demande de pension (réf. [DOSSIER]) a bien été reçue par la CRT. Votre dossier est en cours d'instruction. Délai cible : 20 jours ouvrables.* |
| N02 | Demande de correction (B04) | SMS + Email | Demandeur | *Votre dossier [DOSSIER] nécessite une correction. Motif : [MOTIF]. Vous avez 15 jours pour corriger votre dossier sur le portail.* |
| N03 | Rejet définitif (B08-R) | SMS + Email | Demandeur | *Votre demande [DOSSIER] a été rejetée. Motif : [MOTIF]. Vous pouvez introduire un recours gracieux auprès de la CRT ou un recours contentieux dans les délais légaux.* |
| N04 | Titre de pension disponible (B09) | SMS + Email | Demandeur | *Votre titre de pension (réf. [DOSSIER]) est prêt. Vous pouvez le télécharger sur votre espace Xportal. Votre premier versement sera effectué le mois prochain.* |
| N05 | Rappel agent SLA à risque | Email + Dashboard | Liquidateur CRT | *Rappel : Le dossier [DOSSIER] doit être traité avant le [DATE_LIMITE]. Délai SLA à risque.* |
| N06 | Escalade superviseur | Email + Dashboard | Contrôleur CRT / DG CRT | *Escalade automatique : Le dossier [DOSSIER] dépasse le délai d'instruction. Action requise.* |
| N07 | Rejet automatique délai correction | SMS + Email | Demandeur | *Votre dossier [DOSSIER] a été automatiquement clôturé — délai de correction de 15 jours dépassé. Vous pouvez soumettre une nouvelle demande.* |
| N08 | Rappel contrôle d'existence (J-30) | SMS + Email | Pensionné | *Rappel : Votre attestation d'existence annuelle arrive à échéance le [DATE]. Renouvelez-la sur le portail ou dans un bureau CRT.* |
| N09 | Suspension pension (non-renouvellement) | SMS + Email | Pensionné | *Votre pension (réf. [DOSSIER]) est suspendue — attestation d'existence non renouvelée dans les délais. Contactez la CRT pour régularisation.* |
| N10 | Invitation évaluation (J+1 décision) | SMS + Email | Demandeur | *Comment s'est passée votre expérience ? Évaluez ce service en 30 secondes sur Xportal.* |

---

## 7. KPIs du service & engagements SLA

| Indicateur | Valeur cible |
|---|---|
| **Délai de traitement (dossier complet → titre signé)** | ≤ 20 jours ouvrables |
| **Taux de dossiers incomplets à la soumission** | ≤ 5 % (vs 50 % en AS-IS) |
| **Taux d'abandon formulaire** | ≤ 15 % |
| **Taux de rejet définitif** | ≤ 8 % |
| **Délai d'accusé de réception (soumission → notification)** | < 5 minutes |
| **Taux de disponibilité service (Xportal/Xflow)** | ≥ 99,5 % mensuel |
| **Note de satisfaction usager** | ≥ 4,0 / 5 |
| **Taux de résolution N1 (FCR)** | ≥ 80 % |
| **Réduction des pensions frauduleuses (décès)** | Détection automatique dans les 30 jours suivant le décès déclaré |

---

## 8. Interface e-service CRT

En complément de Xportal, une interface e-service aux couleurs de la CRT sera déployée pour faciliter l'accès des fonctionnaires en fin de carrière.

| Champ | Valeur |
|---|---|
| **URL e-service** | https://services.crt.gouv.tg/pension [À confirmer] |
| **Charte graphique** | Couleurs officielles CRT — logo, typographie, palette fournis par la CRT |
| **Fonctionnalités** | Accès direct au formulaire de demande, suivi de dossier en temps réel, téléchargement du titre de pension, espace contrôle d'existence |
| **Authentification** | Identique à Xportal (SSO ATD) |
| **Backend** | Partage du même processus Xflow — données synchronisées en temps réel |
| **Responsabilité design** | Intégrateur (en concertation avec le service communication CRT) |
| **Livrables attendus** | Maquettes HTML/CSS validées par CRT + intégration Form.io |

---

## 9. Validations & signatures

Le présent SRS a été élaboré à l'issue des ateliers d'analyse conduits entre l'intégrateur, l'équipe ATD et les points focaux de la CRT. Il constitue la référence contractuelle pour le développement, les tests et la mise en production du service.

| | Rédigé par | Validé par (FDS) | Approuvé par (ATD) |
|---|---|---|---|
| **Qualité** | Intégrateur Externe | Point focal CRT | Chef de projet ATD |
| **Nom** | ________________________ | ________________________ | ________________________ |
| **Date** | _______________________ | _______________________ | _______________________ |
| **Signature** | __________________ | __________________ | __________________ |

---

*SRS — Demande de Mise à la Retraite et de Liquidation de Pension | v1.0 | ATD — CRT*
