# SERVICE REQUIREMENT SHEET (SRS)
## Autorisation d'ouverture d'établissement d'enseignement privé
### Ministère des Enseignements Primaire et Secondaire (MEPS) — Togo

| Champ | Valeur |
|---|---|
| **Fournisseur de Services (FDS)** | Ministère des Enseignements Primaire et Secondaire (MEPS) |
| **Service parent** | Direction de l'Enseignement Privé (DEP) |
| **Intégrateur en charge** | ATD |
| **Chef de projet ATD** | ATD |
| **Point focal FDS** | DEP |
| **Date de création** | 26 mars 2026 |
| **Date de dernière révision** | 26 mars 2026 (v1.0 — Version initiale) |
| **Date de validation** | _________________________________ |
| **Back-office utilisé** | Xflow (Orchestrateur ATD) |
| **Déploiement cible** | Xportal + Xflow |

---

## Historique des changements

| Version | Date | Auteur | Description des modifications |
|---|---|---|---|
| 1.0 | 26/03/2026 | ATD IA Analyst | Version initiale (Optimisation processus TO-BE) |

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

Toute personne physique ou morale souhaitant ouvrir un établissement scolaire privé au Togo (maternel, primaire ou secondaire) doit en obtenir l'autorisation auprès de la Direction de l'Enseignement Privé (DEP) du MEPS. Cet agrément confère au promoteur le droit d'opérer formellement dans le respect des programmes nationaux, des normes d'hygiène et de la qualification du personnel.

La digitalisation de ce parcours abolit les déplacements répétitifs et fastidieux de l'usager, auparavant obligatoires pour le dépôt de dossier, les relances et le paiement, qui est dorénavant intégré directement dans le portail (TMoney / Flooz / Visa). En réduisant drastiquement le délai d'examen des demandes incomplètes via des contrôles stricts dans le formulaire (Form.io) et l'information dynamique de la planification d'inspection matérielle, l'usager jouit d'une forte transparence de l'état d'avancement de sa demande. Le document final, un arrêté ministériel, est signé manuellement par les autorités. Il est ensuite remis physiquement au promoteur au guichet de la DEP, après convocation par SMS.

### 1.2. Fiche d'identité du service

| Champ | Valeur |
|---|---|
| **Code service** | SRV-MEPS-2026-003 |
| **Nom complet** | Demande d'autorisation d'ouverture d'un établissement d'enseignement privé (préscolaire / primaire / secondaire) |
| **Catégorie** | Éducation / Entreprise |
| **Bénéficiaires** | Personnes physiques (promoteurs individuels), Personnes morales (associations, ONG, congrégations, sociétés) |
| **Fréquence estimée** | 300 demandes / an |
| **Délai standard de traitement** | 30 jours ouvrés |
| **Délai réglementaire maximum** | 6 mois |
| **Coût du service** | Payant — 40 000 FCFA (Frais de dossier et frais d'inspection unifiés) |
| **Langue(s)** | Français |
| **Canaux de dépôt** | Xportal (web / mobile) |

### 1.3. Acteurs et intervenants

| Acteur | Profil | Rôle dans le processus | Accès système | Responsabilité SLA |
|---|---|---|---|---|
| **Citoyen / Promoteur** | Usager | Renseigne le formulaire, upload les pièces justificatives, paie, accomplit les corrections demandées et se déplace pour retirer physiquement l'arrêté | Xportal | Déclencheur du service |
| **Agent Instructeur DEP** | Agent MEPS | Instruit les pièces déposées, évalue la conformité du dossier (administratif, pédagogique), signale les corrections nécessaires, et valide pour instruction terrain (inspection) | Back-office XFlow | Instruction préliminaire : 7 jours |
| **Inspecteur de visite** | Inspecteur MEPS | Effectue la visite de terrain physique. Saisit le rapport via le back-office, upload sur l'application la grille de notation de conformité | Back-office XFlow | Délai inspection (max) : 15 jours |
| **Commission Technique DEP / Directeur** | Chef de direction | Rend un avis et délibère sur l'autorisation finale de l'établissement. Valide l'arrêté ministériel | Back-office XFlow | Approbation : 5 jours ouvrés |
| **Système Xflow** | Orchestrateur BPMN | Orchestre l'ensemble du processus métier, génère dynamiquement les documents sécurisés et envoie les notifications | Infrastructure ATD / MEPS | Disponibilité 99,5% |
| **Admin Xportal (ATD)** | Technicien ATD | Audit, supervision de la fluidité et statistiques du portail | Administration Xportal | SLA plateforme ATD |
| **Centre d'appel (N1)** | Agent support | Assiste l'usager dans sa procédure en ligne de bout-en-bout | Consultation statut | Résolution < 30 min |

---

## 2. Design du formulaire Form.io

### 2.1. Structure du formulaire

Le parcours est composé de 4 formulaires Form.io distincts orchestrés par Xflow :

- **Formulaire principal (4 onglets)** : parcours commun à tous les usagers (Portail Citoyen).
- **Formulaire secondaire de Correction (2 onglets)** : activé uniquement si l'instructeur repère un document défaillant ou non conforme.
- **Formulaire Instruction Agent** : formulaire présenté à l'agent back-office pour instruire le dossier déposé par le promoteur.
- **Formulaire Visite d'inspection** : composant réservé à l'inspecteur terrain pour consigner son avis de visite.
- **Formulaire Décision Finale** : formulaire directeur.

*Le paiement se fait sur la plateforme e-Gov externe.*

#### Formulaire principal — 4 onglets wizard

| Onglet | Titre | Remarques |
|---|---|---|
| Onglet 1 | Contexte de la demande | Qualification, présentation du process, type d'enseignements (maternelle, primaire, etc.), localisation |
| Onglet 2 | Informations du promoteur | Pré-rempli via E-ID, précisions (Société, ONG, Individuel) |
| Onglet 3 | Pièces à fournir | Plans d'architecte, justificatifs bancaires, certificats sanitaires, rapports de maire, projet pédagogique... |
| Onglet 4 | Récapitulatif et soumission | Résumé non modifiable + confirmation sur l'honneur + CAPTCHA |

#### Formulaire secondaire de Correction — Conditionnel (Rejet Instructeur)

| Formulaire | Titre | Condition de déclenchement |
|---|---|---|
| formio-correction-autorisation-ecole.json | Formulaire de resoumission de pièces | Si l'instructeur DEP indique une demande de correction — déclenché par Xflow |

### 2.2. Détail des champs

#### Onglet 1 — Contexte de la demande

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `typePromoteur` | Statut juridique du promoteur | Select | Oui | Personne Physique (Individuel), Congrégation / ONG, Société | Saisie | Liste imposant certains justificatifs en Onglet 3 (RG-001) |
| `niveauEnseignement` | Niveaux d'enseignement demandés | Select (Multi) | Oui | Préscolaire, Primaire, Collège, Lycée | Saisie |  |
| `nomEtablissement` | Nom proposé de l'établissement | Texte | Oui |  | Saisie | Lettres majuscules |
| `localisationRegion` | Région d'implantation | Select | Oui |  | API | `config.apiBaseUrl`/regions |
| `localisationPrefecture` | Préfecture | Select | Oui |  | API | `config.apiBaseUrl`/prefectures |
| `localisationCommune` | Commune ou village | Select | Oui |  | API | `config.apiBaseUrl`/communes |
| `adresseEtablissement` | Localisation exacte (Quartier, Repères) | Textarea | Oui | | Saisie | |

#### Onglet 2 — Informations du promoteur

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `promNom` | Nom / Raison sociale | Texte | Oui | Verrouillé / Read-only | Profil Citoyen `config.users` | |
| `promPrenom` | Prénoms | Texte | Conditionnel | Verrouillé / Read-only | Profil Citoyen `config.users` | Requis si Personne physique |
| `promEmail` | E-mail du contact principal | Email | Oui | Verrouillé / Read-only | Profil Citoyen `config.users` | Notification |
| `promTelephone` | Téléphone joignable E-Gov | Téléphone | Oui | Verrouillé / Read-only | Profil Citoyen `config.users` | |
| `promNumIdentite` | N° Pièce identité / NIN | Texte | Oui | Verrouillé / Read-only | Profil Citoyen `config.users` | |
| `promRccm` | Registre de Commerce et de Crédit Mobilier (RCCM) | Texte | Conditionnel | | Saisie | Si typePromoteur = Société (RG-001) |

#### Onglet 3 — Pièces à fournir

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `pjDemandeManuscrite` | Demande signée adressée au Directeur | Fichier | Oui | PDF/JPG/PNG < 2 Mo | Upload | |
| `pjCasierJudiciaire` | Extrait du casier judiciaire vierge (-3 mois) | Fichier | Conditionnel | PDF/JPG/PNG < 2 Mo | Upload | Si typePromoteur = Personne Physique (RG-001) |
| `pjStatutsAsso` | Statuts ou Récépissé ONG / Société | Fichier | Conditionnel | PDF/JPG/PNG < 2 Mo | Upload | Si typePromoteur = Congrégation/ONG ou Société (RG-001) |
| `pjPlanSituation` | Plan de situation (signé technicien) | Fichier | Oui | PDF/JPG/PNG < 2 Mo | Upload | |
| `pjTitrePropriete` | Titre foncier ou bail commercial | Fichier | Oui | PDF/JPG/PNG < 2 Mo | Upload | |
| `pjAttestationSanitaire` | Attestation de conformité sanitaire | Fichier | Oui | PDF/JPG/PNG < 2 Mo | Upload | |
| `pjRapportMairie` | Rapport de la Mairie (Sécurité incendie) | Fichier | Oui | PDF/JPG/PNG < 2 Mo | Upload | |
| `pjProjetPedagogique` | Projet Pédagogique (Niveaux, effectifs, diplômes enseignants) | Fichier | Oui | PDF < 2 Mo | Upload | |
| `pjPreuveFinancement` | Preuves de capacité financière (Relevés ou attestation) | Fichier | Oui | PDF < 2 Mo | Upload | Tableau 3 ans compris visé par banque |

#### Onglet 4 — Récapitulatif et soumission

| Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques |
|---|---|---|---|---|---|---|
| `htmlRecapitulatifFinal` | N/A | HTML | N/A | Script Parseur Formulaire | Système | Injection du composant recapitulatif |
| `luEtApprouve` | Je déclare et certifie sur l'honneur que les informations et justificatifs susmentionnés sont vrais sous peine de poursuites... | Checkbox | Oui | Doit être coché | Saisie | Ignoré par le récap via `excludeKeys` |

### 2.3. Actions du formulaire (P-Studio)

| Code Action P-Studio | Condition d'activation | Configuration algorithmique |
|---|---|---|
| **Calculate Costs** | Ne sera plus déclenché sur P-Studio. Le paiement central de 40.000 (Dossier+Inspection) se fait en externe dans le flow, avant l'instruction. | N/A |
| **Publish to RabbitMQ** | Toujours actif | Routing Key: `submissions.topic` — Queue: `workflows-engine.main.queue` |

### 2.4. Configuration des environnements

#### Environnements déclarés

| Environnement | `apiBaseUrl` | `appName` |
|---|---|---|
| `development` | `https://api.education.dev.gouv.tg` | Développement |
| `sandbox` | `https://api.education.sandbox.gouv.tg` | Sandbox |
| `preproduction` | `https://api.education.preprod.gouv.tg` | Pré-production |
| `production` | `https://api.education.gouv.tg` | Production |

### 2.5. Inventaire des formulaires userTask

| # | Fichier JSON | Lane | userTask BPMN | Description | Condition |
| --- | --- | --- | --- | --- | --- |
| 1 | `formio-autorisation-ouverture-ecole-privee.json` | PORTAL | Soumission initiale | Formulaire principal (4 onglets) | Toujours |
| 2 | `formio-correction-autorisation-ouverture-ecole-privee.json` | PORTAL | Correction / Resoumission | Formulaire avec composant d'aide à la correction | Si dossier bloqué à l'instruction |
| 3 | `formio-paiement-autorisation-ouverture-ecole-privee.json` | PORTAL | Paiement | Formulaire technique pour routage vers plateforme E-Gov externe de 40.000 FCFA | Toujours |
| 4 | `formio-instruction-autorisation-ouverture-ecole-privee.json` | XFLOW | Instruction agent | Formulaire back-office de validation pour le Desk Review de l'agent. | Toujours |
| 5 | `formio-inspection-autorisation-ouverture-ecole-privee.json` | XFLOW | Visite sur site (Inspecteur) | Formulaire dynamique avec upload PV | Si dossier Conforme Instruction |
| 6 | `formio-deliberation-autorisation-ouverture-ecole-privee.json` | XFLOW | Délibération Finale | Formulaire avis de validation (Direction) | Si inspection soumise |

---

## 3. Le processus BPMN 2.0

### 3.1. Vue d'ensemble du processus TO-BE

| Champ | Valeur |
|---|---|
| **Nom du processus** | `Procédure_AutorisationOuvertureEcolePrivee_v1.0` |
| **Événement déclencheur** | Soumission du formulaire Form.io complet dans Xportal |
| **Événement de fin (succès)** | Notifications finales à l'usager, convocation et retrait physique de l'Arrêté |
| **Événement de fin (rejet)** | Envoi courrier refus de dossier avec impossibilité de corriger (motif absolu ou temps de correction X Flow écoulé). |
| **Moteur d'exécution** | Xflow (Camunda Platform 7 — GNSPD Framework) |
| **Version processus** | 1.0 |
| **Participants BPMN** | Pool XPORTAL (citoyen) + Pool XFLOW (back-office) |

### 3.2. Étapes détaillées du processus

#### Lane PORTAL — Côté Citoyen

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| 01 | Soumission Dépôt | Usager transmet son dossier form.io de manière 100% numérisée. | Citoyen | Immédiat | → Étape 02 |
| 02 | Redirection de Paiement E-Gov | L'usager est notifié de régler 40 000 FCFA unifiés. La tarification lance le module E-Gov de l'Etat. Confirmation renvoyée au BPMN. | Citoyen | 48 heures max | Si paiement OK → 03 |
| 03 | Attente Action XFlow | Une receive-task `MSG_RETURN` permet d'obtenir le routage. | Système | N/A | → `correction`, `accepte`, `rejete` |
| 04a | Résolution des corrections | User task (Activity_P_Corrections). L'usager se connecte et résout selon les instructions, télécharge les éléments manquants. | Citoyen | =< 15 jours | → 03 |
| 04b | Convocation et Retrait Physique | L'usager reçoit sa convocation et se déplace physiquement à la DEP pour retirer son arrêté. L'arrêté n'est pas téléchargeable en ligne. | Citoyen | =< 15 jours | → FIN succès |
| 04c | Notification de Refus | L'usager lit les motifs légaux pour lesquels la requête est jetée (Activity_P_Rejet). | Citoyen | Immédiat | → FIN rejet |

#### Lane XFLOW — Côté Back-office

| N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition |
|---|---|---|---|---|---|
| B01 | Démarrage Processus `MSG_SERVICE_START` | Initialisation, envoi accusé de réception automatique. | Système | Immédiat | → B02 |
| B02 | Orchestration Paiement | Lancer un signal PAIEMENT vers XPortal. Attendre callback et acquérir les fonds via la task. | Système | Immédiat | → B03 |
| B03 | Examen Préliminaire (Instruction) | User Task Instruction (formio-instruction...). Vérification pointilleuse de 100% visuel de l'étagère de dépôt documentaire. Sortie : "Conforme", "A-Corriger" ou "Rejet-Irrecevable". | Agent DEP | SLA = 7j | Si"Conforme" → B05 / Si"A-Corriger" → B04 / Si"Rejet" → B08 |
| B04 | Demande de Correction | SendTask MSG_SERVICE_RETURN=correction. Met la requête en quarantaine en attendant `MSG_SERVICE_RESUB`. Max retry count=2. | Système | 15j limités | → Attente resoumission → B03 (ou Rejet délai B08) |
| B05 | Notification Inspection / Planning | SMS de notification du besoin physique de programmer visite. | Système | Immédiat | → B06 |
| B06 | Visite d'inspection sur Site | User Task (formio-inspection...). Déplacement et remplissage de la grille, et proposition d'avis favorable ou défavorable. | Inspecteur DEP | SLA = 15j | → B07 |
| B07 | Délibération et Commission Finale | User Task (formio-deliberation...). Examen de la grille, du cahier financier, pédagogique et social. Emission de l'Ok final "Avis Favorable" / "Avis Défavorable". | Directeur / DEP | SLA = 5j | Si"Favorable" → B09 / Si"Défavorable" → B08 |
| B08 | Rejet et Clôture | Envoi via `flow-notify` du SMS/Emails de condamnation du dossier. Puis envoi de `MSG_SERVICE_RETURN=rejete` à XPortal. | Système | Immédiat | → FIN rejet |
| B09 | Signature de l'Arrêté Ministériel | User Task : Hors système, l'arrêté est rédigé et signé physiquement. L'agent indique ensuite sur Xflow que le document est prêt. | Agent DEP | SLA = 3j | → B10 |
| B10 | Convocation et Remise Physique | Envoi du SMS/Email "Arrêté disponible pour retrait". User Task : L'agent d'accueil confirme la remise physique de l'arrêté au promoteur convoqué. Envoi Kafka MSG_SERVICE_RETURN=accepte. | Agent DEP | =< 15 jours | → FIN succès |

### 3.3. Matrice des échanges inter-pools (Kafka)

#### XPortal → XFlow

| # | Message Kafka (`messageRef`) | Émetteur (SendTask) | Récepteur (ReceiveTask/StartEvent) | Payload | Condition |
| --- | --- | --- | --- | --- | --- |
| 1 | `MSG_ECOLE_START` | Soumission initiale | StartEvent XFlow | Données formulaire complet | Toujours |
| 2 | `MSG_ECOLE_RESUB` | Resoumission correction | ReceiveTask resoumission | Données corrigées | Si agent demande correction |

#### XFlow → XPortal

| # | Message Kafka (`messageRef`) | Émetteur (SendTask) | Récepteur (ReceiveTask) | Payload | Condition |
| --- | --- | --- | --- | --- | --- |
| 1 | `MSG_ECOLE_PAY_REQ` | Demande paiement | ReceiveTask paiement | Ordre d'ouverture du module "tarification" XPortal | Toujours |
| 2 | `MSG_ECOLE_PAY_CONFIRM` | Confirmation paiement | ReceiveTask confirmation | Résultat callback | Toujours |
| 3 | `MSG_ECOLE_RETURN` | SendTask `flow-send-message` (Action: correction, accepte, rejete) | ReceiveTask Action (`MSG_ECOLE_RETURN`) | Instructions dynamiques de la Gateway retour (+ Motif de correction le cas échéant) | Toujours |

#### Points de convergence

| ReceiveTask (convergence) | Pool | Entrées | Description |
| --- | --- | --- | --- |
| `MSG_ECOLE_RETURN` | PORTAL | Chemin Droit, Chemin après Correction | Ce n'est qu'avec un Message de Routing XFlow unique que XPortal déclenchera la Gateway d'état terminale ou de correction. |

#### Terminaisons du processus

| EndEvent | Pool | Condition | Notification associée |
| --- | --- | --- | --- |
| Fin succès | PORTAL | Arrêté Produit (`action=accepte`) | Notification de l'obtention de l'autorisation et livraison Arrêté. |
| Fin rejet | PORTAL | Demande Interdite (`action=rejete`) | Motifs de rejets délivrés. |

### 3.4. Flux d'escalade temporelle

| Déclencheur | Canal | Action |
|---|---|---|
| Délai correction usager dépassé (15 jours calendaires) | SMS + Email | Rejet automatique du dossier avec déclinaison à Xportal (action=rejete). |
| Indisponibilité Xflow > 15 min | Email Admin | Alerte automatique à l'Admin ATD |

---

## 4. Règles métiers

| ID | Règle métier | Description / Condition | Priorité | Étapes concernées |
|---|---|---|---|---|
| RG-001 | Typologie de pièces jointes vs Statut Juridique | Si `typePromoteur` = "Société" ou "Congrégation/ONG", le document de Statuts (pjStatutsAsso) est rendu Obligatoire. Même principe pour le Casier Judiciaire pour individu. Si manquant, blocage de la soumission. | HAUTE | Onglet 3 (Form principal) |
| RG-002 | Paiement prérequis exclusif | Le processus métier de la demande (B03) ne peut en aucun cas être enclenché avant certitude absolue (via la CallBack E-Gov) que les frais centraux de 40 000 F sont sur les caisses du Trésor/MEPS. | HAUTE | B02 (Paiement) |
| RG-003 | Délai de rattrapage (Correction) | L'usager a 15 jours calendaires maximums une fois le message `correction` de l'agent émis, pour agir. Passé ce Timer Limit Event, l'orchestrateur annule tout et refuse. | HAUTE | B04, Porta.04a |
| RG-004 | Limitation du ping-pong correctif | Le nombre de renvois d'erreurs par l'agent est bloqué techniquement à l'itérateur 2 (max Retry = 2). Si la 3ème correction n'est toujours pas valable, le dossier doit aller au rejet. | MOYENNE | B03 (Instructeur) |
| RG-005 | Obligatoire Terrain (Inspection) | L'outil Back-Office de l'Inspecteur (B06) contraint la géolocalisation ou l'envoi d'images live du Terrain avec la grille de notation pour éviter des certifications douteuses. | HAUTE | B06 (Inspection) |
| RG-006 | Archivage automatique centralisé ATD | L'arrêté, les pièces fondatrices du dossier usager complets validés devront être ségrégués dans la GED d'Etat pour des inspections quinquennales futures. | HAUTE | B10 (Fin) |

---

## 5. Intégration avec des systèmes tiers

Les intégrations suivantes sont envisagées. Elles nécessitent la signature de conventions d'échange de données entre les structures concernées.

| Système cible | Type d'intégration | Données échangées | Condition d'appel | Statut |
|---|---|---|---|---|
| Plateforme paiement E-Gov | API REST (paiement) | Montant cible unifié (40.000 FCFA) | Étape 02 - Déclenchement | À configurer |
| Plateforme SMS / Emailing GNSPD | API REST via XFlow `flow-notify` | Numéro téléphone, contenu sémantique informatif (statuts dossier). | Modification d'état B01, B04, B05, B08, B10 | Disponible |
| Base de Données Ecole Régulières (Odoo) | API interne / Ecriture via GnsPd | Données civiques du promoteur + Enregistrement de la nouvelle école et de ses attributs approuvés (localisation, type enseignement, id_arrete). | Après B09 / Acceptation Totale | À développer |

---

## 6. Notifications automatiques

| Réf. | Déclencheur | Canal | Destinataire | Message type |
|---|---|---|---|---|
| N01 | Démarrage Procédure XFlow (B01) | SMS + Email | Citoyen/Promoteur | *Votre demande pour la création de la crèche/école (réf. DOSSIER-[ULID]) a bien été réceptionnée. Vous passerez très prochainement au paiement des frais.* |
| N02 | Appel des fonds | SMS + E-mail | Citoyen | *Veuillez régler en ligne vos frais administratifs unifiés (40 000 FCFA). Délai : 48h. Lien de paiement en cours de présentation.* |
| N03 | Rejet au fond de la conformité du dossier documentaire | SMS + E-mail | Citoyen | *Votre dossier comporte des anomalies strictes, il est incomplet ou illisible. L'assistance vous demande de corriger : [MOTIF_AGENT_1]. Limite: 15j.* |
| N04 | Avis d'Organisation Inspection (Progression) | SMS + E-mail | Citoyen | *Sujet : Prévoyez une Visite – Le dossier papier ayant été qualifié avec succès, nos inspecteurs prendront prochainement contact pour leur visite.* |
| N05 | Rejet Définitif du Dossier | SMS + Email | Citoyen | *Malheureusement, face aux normes MEPS de sécurité de locaux ou du dossier Pédagogique, nous émettons formellement un avis Négatif d'interdiction d'exercice. Refus.* |
| N06 | Réussite et Convocation | SMS + Email | Citoyen | *FÉLICITATIONS ! Votre ouverture est autorisée. Veuillez vous présenter au guichet de la DEP muni de votre pièce d'identité pour le retrait physique de votre Arrêté ministériel.* |

---

## 7. KPIs du service & engagements SLA

| Indicateur | Valeur cible |
|---|---|
| **Taux de complétion** | ≥ 85% (dossiers soumis / formulaires initiés) |
| **Taux d'abandon** | ≤ 15% |
| **Délai standard de traitement** | 30 jours ouvrés cible (fort resserrement du délai physique historique) |
| **Délai réglementaire maximum** | 6 mois |
| **Taux de rejet** | ≤ 10% |
| **Note de satisfaction usager** | ≥ 4,0 / 5 |
| **Taux de résolution N1 (FCR)** | ≥ 80% |
| **Disponibilité service (Xportal/Xflow)** | ≥ 99,5% mensuel |
| **Délai notification accusé de réception** | < 5 minutes |
| **Délai de correction du contribuable avant suppression** | Max: 15 jours civils (Config Timer BPMN) |

---

## 8. Interface e-service [FDS]

En complément de Xportal, aucune interface e-service spécifiquement rattachée au MEPS en Front-End n'est actée à ce stade. Ce service s'opère pleinement depuis la vue usuelle du citoyen "Service Public E-Gov / XPortal".

---

## 9. Validations & signatures

Le présent SRS a été élaboré à l'issue des ateliers d'analyse conduits entre l'intégrateur, l'équipe ATD et les points focaux du MEPS. Il constitue la référence contractuelle pour le développement, les tests et la mise en production du service.

| | Rédigé par | Validé par (FDS) | Approuvé par (ATD) |
|---|---|---|---|
| **Qualité** | Intégrateur Externe ATD | Point focal DEP/MEPS | Chef de projet ATD |
| **Nom** | ________________________ | ________________________ | ________________________ |
| **Date** | _______________________ | _______________________ | _______________________ |
| **Signature** | __________________ | __________________ | __________________ |

---

*SRS — Demande d'autorisation d'ouverture d'un établissement d'enseignement privé | v1.0 | ATD*
