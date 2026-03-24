---
description: Digitaliser un service public - cartographie as-is, to-be, formulaire Form.io (JSON) et processus BPMN (XML)
---

<!-- ══════════════════════════════════════════════════════════════════
     NAVIGATION RAPIDE — Table des étapes, livrables et gates
     Grep: STEP:0.5, STEP:1, GATE:1, etc.
     ══════════════════════════════════════════════════════════════════ -->

<!--
| Étape      | Livrables                                      | Lectures obligatoires                                              | Gate suivante |
|------------|-------------------------------------------------|--------------------------------------------------------------------|---------------|
| STEP:0.5   | *-pipeline.yaml                                 | —                                                                  | —             |
| STEP:1     | (recueil oral/doc)                              | —                                                                  | —             |
| STEP:2     | *-as-is.md                                      | —                                                                  | —             |
| STEP:3     | *-to-be.md                                      | documentation/guide-transformation-asis-tobe.md                    | GATE:1        |
| GATE:1     | ✋ Validation périmètre (AS-IS + TO-BE + Pipeline) |                                                                 |               |
| STEP:4     | srs-*.md                                        | exemples/templates/srs-template.md, exemples/*/srs-*.md           | GATE:2        |
| GATE:2     | ✋ Validation SRS                                |                                                                    |               |
| STEP:5     | formio-*.json (principal)                       | exemples/templates/template-premium-stepintro.json,                | —             |
|            |                                                 | Guide_Integration_Formulaires_PStudio_v1.md,                       |               |
|            |                                                 | guide-validation-formio.md, exemples/*/formio-*.json               |               |
| STEP:5a    | formio-correction-*.json, formio-paiement-*.json| exemples/templates/template-paiement.json                          | —             |
| STEP:5b    | formio-instruction-*.json (+ autres userTasks)  | SRS §3.2                                                           | GATE:3a       |
| GATE:3a    | ✋ Validation Form.io                            |                                                                    |               |
| STEP:6     | bpmn-*.bpmn                                     | .agents/skills/bpmn-integrator/SKILL.md,                           | GATE:3b       |
|            |                                                 | documentation/bpmn-gnspd-documentation.md,                         |               |
|            |                                                 | documentation/guide-agent-ia-modelisateur.md,                      |               |
|            |                                                 | exemples/*/bpmn-*.bpmn                                             |               |
| GATE:3b    | ✋ Validation BPMN                               |                                                                    |               |
| STEP:6.5   | (audit cohérence inter-livrables)               | Tous les livrables produits                                        | —             |
| STEP:7     | *-tests.md, *-manuel.md                         | —                                                                  | —             |
| STEP:8     | (personnalisation)                              | —                                                                  | —             |
| STEP:8.5   | *-pv-recette.md                                 | —                                                                  | —             |
| STEP:9     | (checklist finale)                              | Tous les livrables                                                 | —             |
-->

# Workflow : Digitalisation d'un Service Public

Ce workflow guide la production complète de 4 livrables organisés selon une structure hiérarchique administrative :
`projects/{{ministère de tutelle}}/{{direction}}/{{service-public-à-digitaliser}}`

> **⛔ INTERDICTION ABSOLUE** : Le dossier `projects/` est **UNIQUEMENT** un emplacement de sortie (stockage des livrables produits). Ne JAMAIS consulter les fichiers de `projects/` comme source d'inspiration ou de référence pour produire de nouveaux livrables. Les projets existants peuvent contenir des erreurs, des patterns obsolètes ou être incomplets.
>
> **Sources de référence autorisées** : le dossier `exemples/`, les modèles dans `.agents/skills/bpmn-integrator/examples/`, les templates dans `exemples/templates/`, et les guides dans `documentation/`.
>
> **⚠️ NUANCE** : Les exemples sont des sources d'inspiration et de patterns validés, mais ne constituent pas une vérité absolue. En cas de conflit entre un exemple et les règles architecturales ou guides documentés, les règles et guides prévalent.

Les livrables obligatoires pour chaque service (Niveau 3/4) sont :
1. **Cartographie AS-IS** (Processus actuel)
2. **Cartographie TO-BE** (Processus cible)
3. **Pipeline YAML** (Contrat de service du processus cible)
4. **Fiche SRS** (Spécifications fonctionnelles)
5. **Formulaire JSON principal** (XPortal / Form.io)
6. **Formulaire JSON de correction** (si boucle de correction — conditionnel)
7. **Formulaire JSON de paiement** (si service payant — conditionnel)
8. **Formulaires JSON des userTasks** (un formulaire par userTask identifié dans le SRS — instruction agent, téléchargement, etc.)
9. **Processus BPMN XML** (XFlow / Camunda)
10. **Plan de Tests**
11. **Manuels Utilisateurs** (Citoyen et Agent)
12. **PV de Recette**

---

Le processus suit une **RÈGLE D'OR DE DÉRIVATION** :
1. **L'analyse AS-IS** est extraite du **KoboToolbox**.
2. **La cartographie TO-BE** est conçue par transformation de **l'AS-IS** (optimisation) en appliquant **scrupuleusement** le guide `documentation/guide-transformation-asis-tobe.md`.
3. **Le SRS** est rédigé à partir de la **cartographie TO-BE** (formalisation).

**INTERDICTION FORMELLE** : Ne jamais sauter d'étape. Le SRS n'est pas une numérisation du Kobo, mais la spécification technique de la cible TO-BE. Le TO-BE ne peut pas être conçu sans appliquer l'Analyse de la Valeur Ajoutée et les 10 Règles d'Or de la Modernisation.

### Mapping pour le SRS :
- **Identification** : Questions 1 à 6 (Nom, Direction, Service).
- **Contexte & Objectif** : Question 7 (Utilité concrète), Questions 9-11 (Base légale).
- **Acteurs** : Question 8 (Usagers) et Question 21 (Intervenants).
- **Processus métier** : Question 14 (Étapes citoyen) et Question 17 (Actions internes).
- **Documents & Formulaire** : Question 16 (Pièces jointes) et Questions 22-24 (Inputs/Outputs).
- **SLA & Performances** : Questions 20, 33 et 53.
- **Vision cible** : Question 45 (Interaction future).

---

## <!-- STEP:0.5 --> Étape 0.5 — Modélisation du Pipeline YAML (MANDATOIRE)

Avant de produire tout livrable industriel (BPMN, SRS, Form.io), il est **obligatoire** de formaliser le processus cible sous forme d'un pipeline YAML. Cette étape sert de "contrat de service" entre l'analyste et l'utilisateur.

### Format attendu :
```yaml
pipeline:
  - step: 1
    name: "Nom de l'étape"
    actor: "Qui agit ?"
    system: "XPortal / XFlow / Système / Communauté"
    action: "Description de l'action métier"
    inputs: [ "Champs", "Pièces" ]
    output: "Résultat attendu"
```

### Champs optionnels pour services complexes :
```yaml
  - step: 3a
    name: "Boucle de correction — PHYSIQUE"
    actor: "Citoyen"
    system: "XPortal"
    type: "humain"          # humain | système | physique
    sla: "48h"              # délai max de traitement
    retry:                  # si l'étape peut être retentée
      max: 3                # nombre max de tentatives
      timer: "P15D"         # durée ISO 8601 avant clôture automatique
    action: "..."
    inputs: [ "..." ]
    output: "..."
```

### Conventions de nommage des sous-étapes :
- Les sous-étapes d'une étape N sont numérotées `Na`, `Nb`, `Nc` (ex: `3a` = boucle de correction de l'étape 3).
- Les étapes nécessitant une présence physique obligatoire portent le suffixe `— PHYSIQUE` dans leur nom.

### Fichier STATUS.md (OBLIGATOIRE)

Dès la création du dossier projet, l'agent **DOIT** créer un fichier `STATUS.md` à la racine du dossier service (`projects/[ministère]/[direction]/[service]/STATUS.md`). Ce fichier est mis à jour **à chaque changement d'étape ou de gate**.

```markdown
# Status — [Nom du Service]

| Champ | Valeur |
|-------|--------|
| **Étape courante** | STEP:X / GATE:X — description |
| **Dernière étape complétée** | STEP:X |
| **Prochaine étape** | STEP:X — après condition |
| **Date de mise à jour** | AAAA-MM-JJ |

## Livrables produits

| Livrable | Fichier | Statut |
|----------|---------|--------|
| Pipeline YAML | `*-pipeline.yaml` | Produit / En attente / Non commencé |
| ... | ... | ... |

## Blocages / Notes
- (notes libres)
```

**Règles de mise à jour** :
- Créer le fichier dès l'étape 0.5 (en même temps que le pipeline YAML).
- Mettre à jour le statut à chaque passage de gate ou complétion d'étape.
- Ajouter chaque livrable produit au tableau au fur et à mesure.
- Consigner les blocages ou décisions importantes dans la section Notes.

---

## <!-- STEP:1 --> Étape 1 — Recueil d'informations complémentaire

Demander à l'utilisateur (ou extraire depuis les documents disponibles) :

- **Nom du service** : ex. "Demande d'assignation de fréquence radio"
- **Organisme** : ex. ARCEP, Mairie, Ministère
- **Acteurs impliqués** : citoyen/entreprise, agent guichet, chef de service, système
- **Étapes actuelles** (as-is) : liste des étapes manuelles du processus actuel
- **Pièces justificatives requises** : liste des documents à fournir
- **Champs du formulaire** : données collectées auprès du demandeur
- **Décision(s) possible(s)** : approbation, rejet, correction demandée
- **SLA / délais** : délai réglementaire de traitement
- **Canal de notification** : email, SMS, courrier

---

## <!-- STEP:2 --> Étape 2 — Cartographie AS-IS (processus actuel)

Produire un document Markdown décrivant le processus tel qu'il est aujourd'hui.

### Format attendu : `[nom-du-service]-as-is.md`

```markdown
# Cartographie AS-IS : [Nom du Service]

## Acteurs
| Acteur | Rôle |
|--------|------|
| Citoyen/Entreprise | Dépose la demande physiquement ou par courrier |
| Agent Guichet | Vérifie la conformité du dossier |
| Chef de Service | Instruit et valide la décision |
| Service Courrier | Notifie le demandeur par courrier |

## Étapes du Processus

1. **Dépôt du dossier** (Citoyen → Guichet physique)
   - Formulaire papier rempli + pièces jointes
   - Durée : 1 jour

2. **Réception et enregistrement** (Agent Guichet)
   - Vérification de complétude du dossier
   - Attribution d'un numéro de dossier manuel
   - Durée : 1-2 jours

3. **Vérification de conformité** (Agent Guichet + Chef de Service)
   - Examen des pièces justificatives
   - Durée : 5-10 jours ouvrables

4. **Instruction et décision** (Chef de Service)
   - Décision : Approbation / Rejet / Demande de compléments
   - Durée : 5-15 jours

5. **Notification** (Service Courrier)
   - Envoi du résultat par courrier postal
   - Durée : 2-5 jours

## Points de Friction Identifiés
- Déplacement physique obligatoire
- Pas de traçabilité en temps réel
- Perte de dossiers possible
- Délais longs et imprévisibles
- Pas de notification automatique
```

---

## <!-- STEP:3 --> Étape 3 — Cartographie TO-BE (processus cible)

<!-- reads_before:
  - documentation/guide-transformation-asis-tobe.md   # AVA + 10 Règles d'Or ATD
-->

> **RÈGLE MANDATOIRE (STOP AVANT DE CONTINUER) ✋** :
> Avant de concevoir le TO-BE, l'agent **DOIT OBLIGATOIREMENT** lire (outil `Read`) et appliquer strictement les principes du guide `documentation/guide-transformation-asis-tobe.md`. Le TO-BE n'est pas une simple copie numérique, il doit intégrer l'Analyse de la Valeur Ajoutée (AVA), les 10 Règles d'Or ATD (Zéro papier, e-ID automatique, paiement en ligne, BPMN asynchrone, notifications) et le Design Thinking. Produisez un TO-BE qui résout activement les frictions de l'AS-IS.
> **ATTENTION (BOUCLE DE CORRECTION)** : Le TO-BE **DOIT** expliciter formellement la boucle de resoumission (correction par le citoyen sans recréer de dossier) pour chaque cas de non-conformité. Ce comportement ne doit jamais être caché ou implicite, il fait partie du cœur du workflow d'alerte et de correction asynchrone.

Produire un document Markdown décrivant le processus digitalisé cible.

### Format attendu : `[nom-du-service]-to-be.md`

```markdown
# Cartographie TO-BE : [Nom du Service]

## Vision Générale
Digitalisation complète du service via un portail citoyen (Form.io) connecté
à un moteur de workflow (Camunda Platform 7). Le demandeur soumet en ligne,
le back-office traite via un tableau de bord, les notifications sont automatiques.

## Architecture Technique
- **Frontend / Orchestrateur Citoyen** : XPortal (Pool BPMN exécutable gérant les états d'attente usager).
- **Moteur de workflow Métier** : XFlow (Camunda Platform 7, pool de traitement).
- **Bus de messaging** : Kafka (topics `bpmn.commands`) pour la synchro inter-pools.
- **Identité** : Remplissage transparent e-ID.
- **Notifications** : Injecteurs Service Task `tg.gouv.gnspd.sendNotification`.
- **Paiement** : Plateforme de paiement e-Gov **externe** (Flooz, TMoney, Visa, Mastercard). Le paiement ne se fait **ni dans XPortal ni dans XFlow** — le citoyen est redirigé vers la plateforme externe, et la confirmation revient de manière asynchrone.

## Acteurs et Systèmes
| Acteur / Système | Rôle |
|------------------|------|
| Moteur XPortal (Citoyen) | Orchestration des écrans usager (Correction, suivi) en attente des ordres XFlow. |
| Plateforme de Paiement e-Gov | Plateforme **externe** de paiement électronique — le citoyen est redirigé hors de XPortal pour payer. |
| Moteur XFlow (Back-Office) | Orchestration métier, appels GED Odoo, validation agent. |
| Agent Back-Office | Vérification conformité via tableau de bord (GNSPD User Task). |
| Chef de Service | Validation/rejet via interface dédiée |
| Service de Notification | Email/SMS automatique |
| Service PDF | Génération du document de décision |

## Étapes Digitalisées

1. **Soumission en ligne** (Citoyen → Portail)
   - Remplissage du formulaire Form.io
   - Upload des pièces justificatives
   - Accusé de réception automatique par email
   - Durée : immédiat

2. **Réception et enregistrement automatique** (Système)
   - Création du dossier en base
   - Attribution automatique d'un numéro de suivi
   - Durée : immédiat

3. **Vérification métier et Allers-Retours (XFlow <=> XPortal)**
   - L'agent instruit le dossier via `gnspd.userTask` sur XFlow.
   - **Décision "Correction"** : XFlow publie un message Kafka `correction` vers XPortal. XPortal réveille le dossier citoyen, propose un écran form.io de resoumission (`Activity_P_Corrections`), puis renvoie le flux à XFlow.
   - **Décision "Paiement requis"** : Fonctionnement identique pour débloquer le composant de paiement portail.
   - **Décision "Conforme"** : XFlow lance l'enregistrement et notifie XPortal de l'action `accepte`.
   - Durée : 1-3 jours

4. **Instruction et décision** (Chef de Service)
   - Validation/rejet via interface back-office
   - Durée : 2-5 jours

5. **Génération du document et notification finale** (Système)
   - Génération PDF automatique
   - Notification email/SMS au demandeur
   - Téléchargement disponible sur le portail
   - Durée : immédiat

### Pattern pour sous-étapes (boucles, notifications intermédiaires)

3a. **Boucle de correction** (Citoyen → XPortal)
   - XFlow notifie le citoyen avec le motif de correction.
   - Le citoyen corrige et resoumets via son dossier existant.
   - Maximum N tentatives, au-delà rejet automatique.
   - Timer : si pas de resoumission dans X jours, clôture automatique.

### Pattern pour étapes physiques obligatoires (services hybrides)

Certains services imposent des étapes physiques par obligation légale (biométrie, examen, retrait de titre sécurisé). Ces étapes doivent :
- Porter le suffixe **`— PHYSIQUE`** dans leur titre.
- Être précédées d'une **convocation automatique par SMS/Email** (jamais de déplacement sans notification préalable).
- Avoir leur résultat **saisi dans le système** par l'agent ou l'inspecteur (capture numérique, pas papier).
- Être justifiées par une **référence légale** dans la Vision Générale.

Exemple :
4. **Relevé des données biométriques — PHYSIQUE** (Citoyen → Agent)
   - Convocation par SMS/Email après validation du dossier.
   - Capture : photo biométrique, empreintes digitales, signature.
   - L'agent enregistre les données dans XFlow.
   - Obligation légale : [référence loi/décret].
   - Durée : 1 jour (rendez-vous)

## Patterns d'orchestration inter-pools (OBLIGATOIRE)

Le TO-BE doit explicitement décrire les patterns d'interaction entre XPortal et XFlow. Ces patterns garantissent qu'aucun jeton BPMN ne se perd et que le flux est cohérent.

### P1. Symétrie des gateways
Toute décision de routage conditionnel (ex: duplicata oui/non) doit être **répliquée en miroir** dans les deux pools. Chaque pool prend sa propre décision de routage en lisant la même donnée source. Aucun pool ne dépend de l'autre pour savoir quel chemin emprunter.

### P2. Point de convergence unique (ReceiveTask multi-entrante, jamais d'ExclusiveGateway merge)
Lorsque plusieurs chemins (ex: après paiement, après correction, chemin direct) doivent converger vers la même suite du processus, utiliser un **seul ReceiveTask** (ou ServiceTask/UserTask) avec plusieurs `<bpmn:incoming>`. Cela évite la duplication de logique et garantit un seul point d'attente. **Ne jamais utiliser un ExclusiveGateway comme simple point de merge** (N entrées → 1 sortie) : le validateur exige au moins 2 flux sortants avec conditions. Les ExclusiveGateway servent uniquement à la **divergence** (1 entrée → N sorties conditionnelles).

### P3. Notification PUIS SendMessage (jamais l'inverse)
Côté XFlow, toujours envoyer la **notification citoyen** (ServiceTask `flow-notify`) AVANT le **message Kafka** (SendTask `flow-send-message`) vers XPortal. Le citoyen doit être informé avant que l'état de son dossier ne change sur le portail.

### P4. Noeud de rejet unique (DRY)
Tous les chemins de rejet (non-inscrit, rejet agent, non-paiement, etc.) doivent converger vers un **seul ServiceTask de notification de rejet** avec plusieurs entrées. Un seul template, une seule logique, pas de duplication.

### P5. Vérification système AVANT instruction agent
Toute vérification automatisable (Odoo, API tierce) doit s'exécuter **avant** la userTask agent. L'agent reçoit des données pré-vérifiées et ne fait que valider — il ne cherche pas manuellement.

### P6. Boucle de correction avec re-vérification
La boucle de correction doit revenir à la **vérification système** (Odoo/API), pas directement à l'agent. Les données corrigées sont re-vérifiées automatiquement avant de repasser par l'instruction agent.

### P7. Terminaison explicite de chaque branche
Chaque chemin alternatif du processus doit se terminer par un **EndEvent explicite**. Aucun jeton ne doit rester en suspens. Lister dans le TO-BE tous les EndEvents et leur condition.

### P8. Appariement SendTask/ReceiveTask
Chaque SendTask inter-pool doit avoir un ReceiveTask (ou StartEvent) correspondant dans l'autre pool. Aucun message orphelin. Le TO-BE doit lister tous les échanges Kafka entre les deux pools.

## Gains Attendus
- Réduction du délai de traitement de 70%
- Réduction maximale des déplacements physiques (zéro si 100% digital, minimum légal si service hybride)
- Traçabilité complète en temps réel
- Réduction des erreurs de saisie (validation formulaire)
- Archivage numérique sécurisé
```

---

## <!-- GATE:1 --> GATE 1 — Validation du périmètre ✋

> **STOP OBLIGATOIRE** : Avant de produire les livrables techniques, soumettre la cartographie AS-IS, la cartographie TO-BE et le pipeline YAML à l'utilisateur pour validation.
> L'agent ne doit **JAMAIS** passer aux étapes suivantes sans accord explicite de l'utilisateur sur le périmètre fonctionnel.
>
> **INSTRUCTION AGENT IA** : Présenter les chemins absolus des fichiers `*-pipeline.yaml`, `*-as-is.md` et `*-to-be.md` à l'utilisateur et attendre sa validation explicite avant de continuer. L'utilisateur doit pouvoir amender chaque livrable avant de passer à la suite.

---

## <!-- STEP:4 --> Étape 4 — Dossier SRS (Spécifications)

<!-- reads_before:
  - exemples/templates/srs-template.md                # Template officiel SRS (structure 9 sections)
  - exemples/*/srs-*.md                               # Exemples SRS validés (glob)
-->

Produire un document Markdown structuré **en suivant impérativement le template officiel** `exemples/templates/srs-template.md`. Sauvegarder dans `projects/[ministere]/[direction]/[service]/srs-[nom-service].md`.

> **RÈGLE MANDATOIRE (STOP AVANT DE CONTINUER) ✋** :
> Avant de rédiger le SRS, l'agent **DOIT OBLIGATOIREMENT** :
> 1. Lire (outil `view_file`) le template officiel `exemples/templates/srs-template.md`. Ce template contient la structure exacte à respecter, les directives IA intégrées (`<!-- IA: ... -->`), et les conventions de nommage. Le SRS produit doit suivre la structure à 9 sections du template. Toute section non applicable doit être conservée avec la mention « Non applicable pour ce service ».
> 2. **Chercher et consulter les exemples** de SRS déjà validés situés dans le dossier `exemples/` (ex: `exemples/*/srs-*.md`) pour maîtriser le niveau d'exigence rédactionnel, la granularité des tableaux et les formulations standards.
>
> **RÈGLE** : Le SRS est produit AVANT le formulaire JSON et le BPMN. Il sert de référence technique pour guider la construction des livrables techniques. On spécifie avant de coder.

### Structure Obligatoire (9 sections — conforme au template) :

#### Section 1 : Identification du service
- **En-tête de versionnage** : FDS, Service parent, Intégrateur, Chef de projet ATD, Point focal FDS, Dates, Back-office, Déploiement cible.
- **Historique des changements** : tableau versionné.
- **§1.1 Description fonctionnelle** : 2 paragraphes (contexte institutionnel + apport digitalisation).
- **§1.2 Fiche d'identité** : code service `SRV-[SIGLE]-[AAAA]-[NNN]`, catégorie, bénéficiaires, fréquence, délai, coût, langue, canaux.
- **§1.3 Acteurs et intervenants** :
  | Acteur | Profil | Rôle dans le processus | Accès système | Responsabilité SLA |
  |--------|--------|----------------------|---------------|-------------------|
  Inclure : Citoyen, Agent(s), Superviseur, Système Xflow, Admin Xportal, Centre d'appel N1.

#### Section 2 : Design du formulaire Form.io
- **§2.1 Structure du formulaire** : tableau des onglets du wizard.
- **§2.2 Détail des champs** : UN TABLEAU DISTINCT par onglet. Colonnes : `Nom du champ | Libellé affiché | Type | Obligatoire | Format / Règle | Source | Remarques`.
  *L'agent IA DOIT spécifier systématiquement les sources e-ID (`config.users`), les appels API dynamiques, les règles de validation (blur, regex, messages custom), et tracer `htmlRecapitulatifFinal`.*
- **§2.3 Actions du formulaire (P-Studio)** : tableau des actions (`Calculate Costs` si payant, `Publish to RabbitMQ` obligatoire).

#### Section 3 : Le processus BPMN 2.0
- **§3.1 Vue d'ensemble** : fiche d'identité du processus.
- **§3.2 Étapes détaillées** : **DEUX TABLEAUX DISTINCTS** :
  - **Lane PORTAL** (côté citoyen) : numérotation `01, 02, 03…`
  - **Lane XFLOW** (côté back-office) : numérotation `B01, B02, B03…`
  Colonnes : `N° | Nom de l'étape | Description | Acteur | Délai | Résultat / Condition`.
- **§3.3 Flux d'escalade temporelle** : tableau des escalades automatiques.

#### Section 4 : Règles métiers
- Numérotation `RG-001, RG-002…`
- Colonnes : `ID | Règle métier | Description / Condition | Priorité (HAUTE/MOYENNE/BASSE) | Étapes concernées`
- Règles incontournables : éligibilité, pièces conditionnelles, verrouillage e-ID, boucle de correction, archivage.

#### Section 5 : Intégration avec des systèmes tiers
- Colonnes : `Système cible | Type d'intégration | Données échangées | Condition d'appel | Statut`
- Inclure : back-office FDS, paiement (si applicable), SMS, archivage ATD, identité numérique.

#### Section 6 : Notifications automatiques
- Numérotation `N01, N02…`
- Colonnes : `Réf. | Déclencheur | Canal | Destinataire | Message type`
- Obligatoires : accusé de réception, corrections, acceptation, rejet, invitation évaluation (J+1), escalade.

#### Section 7 : KPIs du service & engagements SLA
- Indicateurs standards ATD + valeurs spécifiques au service.

#### Section 8 : Interface e-service [FDS]
- URL, charte graphique, fonctionnalités, authentification, backend, responsabilité design.
- Si non applicable : « Aucune interface e-service dédiée n'est prévue. Le service est accessible exclusivement via Xportal. »

#### Section 9 : Validations & signatures
- Tableau standardisé : Rédigé par (Intégrateur), Validé par (FDS), Approuvé par (ATD).

---

## <!-- GATE:2 --> GATE 2 — Validation des spécifications ✋

> **STOP OBLIGATOIRE** : Soumettre le SRS complet à l'utilisateur pour validation avant de produire le JSON et le BPMN.
> Vérifier en particulier : la matrice des champs, les règles de gestion, et l'algorithme Calculate Costs.
>
> **INSTRUCTION AGENT IA** : Présenter le chemin absolu du fichier `srs-*.md` produit à l'utilisateur et attendre sa validation explicite avant de continuer.

---

## <!-- STEP:5 --> Étape 5 — Formulaire Form.io (JSON P-Studio)

<!-- reads_before:
  - exemples/templates/template-premium-stepintro.json # Template stepIntro premium (Landing Page)
  - documentation/Guide_Integration_Formulaires_PStudio_v1.md  # Guide P-Studio complet (Récapitulatif Intelligent inclus)
  - documentation/guide-validation-formio.md           # Référentiel validation Form.io
  - exemples/*/formio-*.json                           # Exemples formulaires validés (glob)
-->

Produire le schéma JSON du formulaire. Sauvegarder dans `projects/[ministere]/[direction]/[service]/formio-[nom-service].json`.

> **CONFORMITÉ P-STUDIO ABSOLUE REQUISE**
> Vous devez impérativement respecter les règles de `Guide_Integration_Formulaires_PStudio_v1.md`, du `guide-integration-formulaires.md` (qui contient le code source du Récapitulatif Intelligent) et du `guide-validation-formio.md` (référentiel complet des mécanismes de validation Form.io).
> **De plus, vous DEVEZ obligatoirement chercher et consulter les exemples de formulaires JSON** situés dans le dossier `exemples/` (ex: `exemples/*/formio-*.json`) afin de calquer leur niveau de finition (grilles, classes CSS, gestion avancée des erreurs, i18n).

- **STRUCTURE RACINE (CRITIQUE)** : Le fichier JSON **DOIT IMPÉRATIVEMENT** avoir à sa racine toutes les métadonnées (telles que `title`, `name`, `type`, `display`, `i18n`, `config`, `components`...) ainsi qu'un tableau `"actions": [ ... ]` (pour les appels externes). **AUCUN** wrapper `"content": {}` ni `"settings": {}` ne doit être utilisé.
- **ACTIONS RABBITMQ** : Le tableau `"actions"` à la racine doit contenir la configuration de publication vers RabbitMQ de P-Studio pour transmettre la soumission au moteur BPMN. Le topic canonique est `"submissions.topic"` (Routing Key) avec la queue `"workflows-engine.main.queue"`.
- **PREMIER PANEL (INTRO) - DESIGN PREMIUM** : Le premier panel **DOIT** avoir `key: "stepIntro"`. Il **DOIT OBLIGATOIREMENT** être conçu comme une "Landing Page" Premium en utilisant le système de grille (`columns`) et des composants HTML/CSS riches (Info Pills, Sidebar, Étapes, Avertissement). Ne répondez jamais avec un texte simple. Utilisez comme référence complète : `exemples/templates/template-premium-stepintro.json`. **Ne PAS ajouter de bouton Submit** : P-Studio gère nativement le bouton d'amorce "Commencer" dans l'en-tête natif.
- **CONFIG & I18N** : Les blocs `config` (avec ses 4 environnements) et `i18n` (avec le dict `"en"`) **DOIVENT** être déclarés à la racine du JSON.
- **RÉCAPITULATIF** : Le dernier panel **DOIT** inclure le composant "Récapitulatif Intelligent" (`htmlelement` avec son parseur JS, copié depuis `guide-integration-formulaires.md` §3.2) suivi de la case à cocher de consentement (exclue via `excludeKeys`). **Ne PAS ajouter de bouton Submit** : P-Studio gère nativement le bouton "Soumettre" sur le dernier panel du wizard.
- **PRÉ-REMPLISSAGE DYNAMIQUE (LOGIC)** : Les champs liés à l'utilisateur doivent utiliser `"defaultValue": "{{ config.users.XXX }}"`. **INTERDICTION ABSOLUE** de mettre l'attribut statique `"disabled": true`. L'agent IA **DOIT** injecter un bloc `logic` Form.io pour verrouiller le champ (Action `property`, `disabled = true`) UNIQUEMENT si sa valeur n'est pas vide. Le trigger JavaScript doit être **robuste** et gérer les cas limites (chaîne vide, espaces, null) :
  ```javascript
  // Trigger robuste pour verrouillage e-ID
  result = !!(data.nomChamp && String(data.nomChamp).trim().length > 0);
  ```
  L'usager garde ainsi la main si l'e-ID remonte une donnée corrompue, vide ou constituée uniquement d'espaces.
- **LISTES REST** : Toute liste géographique ou technique (pays, devises) est requêtée via `"dataSrc": "url"` sur `{{ config.apiBaseUrl }}/references/XXX`.
- **VALIDATION DES CHAMPS ET RÉFLEXION IA (CRITIQUE)** : L'agent IA **DOIT OBLIGATOIREMENT** réfléchir intensément sur les types de validation pertinents et leurs raisons profondes avant de générer le code du formulaire. Il faut systématiquement appliquer `"validateOn": "blur"` pour l'UX, instancier des messages d'erreur personnalisés (dictionnaire `"errors"`), et prévoir des vérifications de type Regex (`pattern`), Javascript ou JSONLogic si justifié métier.

### Template JSON de base (P-Studio Ready) :

```json
{
  "title": "[Nom du Service]",
  "name": "[nomServiceCamelCase]",
  "path": "[nom-service-slug]",
  "type": "form",
  "display": "wizard",
  "i18n": {
    "en": {
      "Présentation (Qualification)": "Presentation",
      "Informations personnelles": "Personal details",
      "Commencer": "Start",
      "Soumettre la demande": "Submit request"
    }
  },
  "config": {
    "sandbox": {
      "apiBaseUrl": "https://api.sandbox.gouv.tg/api/v1/admin",
      "appName": "Sandbox",
      "users": { "firstName": "user.firstName", "lastName": "user.lastName", "email": "user.email" }
    },
    "production": {
      "apiBaseUrl": "https://api.gouv.tg/api/v1/admin",
      "appName": "Production",
      "users": { "firstName": "user.firstName", "lastName": "user.lastName", "email": "user.email" }
    },
    "preproduction": {
      "apiBaseUrl": "https://api.preprod.gouv.tg/api/v1/admin",
      "appName": "Pré-production",
      "users": { "firstName": "user.firstName", "lastName": "user.lastName", "email": "user.email" }
    },
    "development": {
      "apiBaseUrl": "https://api.dev.gouv.tg/api/v1/admin",
      "appName": "Développement",
      "users": { "firstName": "user.firstName", "lastName": "user.lastName", "email": "user.email" }
    }
  },
  "components": [
      {
        "type": "panel",
        "title": "Présentation (Qualification)",
        "key": "stepIntro",
        "components": [
          { "type": "htmlelement", "key": "stylesCssSidebar", "tag": "style", "content": "/* Inline CSS pour Sidebar et Info Pills... */" },
          { 
            "type": "columns", 
            "key": "columnsIntro",
            "columns": [
              {
                "width": 8,
                "components": [
                  { "type": "htmlelement", "tag": "div", "content": "<!-- Info Pills, Description, Conditions, Etapes -->" }
                ]
              },
              {
                "width": 4,
                "components": [
                  { "type": "htmlelement", "tag": "div", "content": "<!-- Sidebar Fournisseur -->" }
                ]
              }
            ]
          }
        ]
      },
      {
        "type": "panel",
        "title": "Informations personnelles",
        "key": "stepIdentite",
        "components": [ ... ]
      },
      {
        "type": "panel",
        "title": "Récapitulatif et soumission",
        "key": "stepRecapitulatif",
        "components": [
           { /* Insérez ici l'Object JSON htmlelement du Récapitulatif Intelligent depuis guide-integration-formulaires.md §3.2 */ },
           { "type": "checkbox", "label": "Je certifie sur l'honneur...", "key": "luEtApprouve", "validate": {"required": true} }
        ]
      }
  ],
  "actions": [
    {
      "name": "publishToRabbitMQ",
      "type": "rabbitmq",
      "topic": "submissions.topic",
      "payload": "{{ submission.data }}"
    }
  ]
}
```

---

## <!-- STEP:5a --> Étape 5a — Formulaires intermédiaires (conditionnels)

<!-- reads_before:
  - exemples/templates/template-paiement.json          # Template formulaire paiement (Calculate Costs)
  - exemples/*/formio-paiement-*.json                  # Exemples formulaires paiement (glob)
  - exemples/*/formio-correction-*.json                # Exemples formulaires correction (glob, si disponibles)
-->

En plus du formulaire principal, certains services nécessitent des **formulaires intermédiaires** autonomes, pilotés par XFlow via Kafka. Il existe deux types de formulaires intermédiaires, chacun avec sa propre structure :

- **Formulaire de correction** : Utilise la même structure racine que le formulaire principal (`title`, `name`, `path`, `type`, `display`, `i18n`, `config`, `components`, `actions` en tableau avec `publishToRabbitMQ`).
- **Formulaire de paiement** : Utilise la même structure racine (`title`, `name`, `path`, `type`, `display`, `i18n`, `config`) mais avec `actions` en **objet** contenant l'action `calculate-costs`. Voir le skill `formio-integrator` section 12.2 et le template `exemples/templates/template-paiement.json`.

### Formulaire de correction (`formio-correction-[nom-service].json`)

**Condition** : Obligatoire si le processus comporte une boucle de correction (décision "Correction nécessaire" par l'agent).

**Pattern standard** :
- **Panel 1 — Corrections requises** :
  - Bandeau d'alerte HTML (`htmlelement`) informant le citoyen que des corrections sont demandées.
  - Affichage dynamique du motif de l'agent (`htmlelement` avec `calculateValue` lisant `data.motifAgent`).
  - Champs hidden injectés par XFlow : `motifAgent` (texte du motif), `numeroDossier` (référence du dossier), `nbCorrections` (compteur de tentatives).
  - Compteur de tentatives restantes (`htmlelement` avec calcul `3 - nbCorrections`, couleur rouge si dernière tentative).
  - Upload de pièce(s) corrigée(s) (`file`, `storage: "base64"`, `multiple: true`, formats `.pdf,.jpg,.jpeg,.png`, max 2MB).
  - Commentaire optionnel (`textarea`, `maxLength: 500`).
- **Panel 2 — Récapitulatif et resoumission** :
  - Récapitulatif Intelligent (même composant `htmlelement` que le formulaire principal).
  - Case de certification (`checkbox`, `key: "luEtApprouve"`, `required: true`).

### Formulaire de paiement (`formio-paiement-[nom-service].json`)

**Condition** : Obligatoire si le service est payant.

> **ATTENTION** — Le formulaire de paiement partage la même structure racine (`title`, `name`, `path`, `config`, `i18n`, `components`) mais **diffère sur `actions`** (objet au lieu de tableau) et sur `display` (`"form"` au lieu de `"wizard"`). L'agent **DOIT** consulter les exemples validés et le skill `formio-integrator` section 12.2.

**Différences structurelles clés par rapport au formulaire principal** :
- `display: "form"` (page unique, pas wizard) — sauf cas complexe.
- `title`, `name`, `path`, `config`, `i18n` sont **présents** à la racine (même structure que les autres formulaires).
- `actions` est un **objet** (pas un tableau) avec la clé `"calculate-costs"` — c'est la différence principale.
- Pas de `settings: {}` à la racine (inutile).

**Composants standards** :
- `serviceTitle` (`htmlelement`, h2) : titre du service.
- Texte explicatif du paiement (`htmlelement` ou `content`).
- `montantAPayer` (`textfield`, `disabled: true`) : montant affiché, rempli par l'action Calculate Costs.
- `dynamicCost` (`textfield`, `hidden: true`, `clearOnHide: false`) : variable technique pour Calculate Costs.
- `dejaPaye` (`textfield`, `hidden: true`, `clearOnHide: false`, `defaultValue: "OUI"`) : flag de paiement.

**Action Calculate Costs** :
```json
"actions": {
  "calculate-costs": {
    "name": "calculate-costs",
    "method": ["create"],
    "handler": [{ "method": "before", "name": "Calculate Costs" }],
    "settings": {
      "serviceId": "[identifiant-du-service]",
      "pricingMode": "fixed",
      "defaultPrice": 0,
      "quantityField": "",
      "applyTax": false,
      "fixedPrice": 15000
    },
    "enabled": true
  }
}
```

**Modes de tarification** :
- `"fixed"` : Montant fixe (`fixedPrice`). Cas majoritaire.
- `"dynamic"` : Montant calculé à partir d'un champ (`quantityField`).

---

## <!-- STEP:5b --> Étape 5b — Formulaires des userTasks (instruction agent, téléchargement, etc.)

<!-- reads_before:
  - [SRS produit à l'étape 4] §3.2                    # Tableaux BPMN (lanes PORTAL + XFLOW) pour identifier les userTasks
  - exemples/*/formio-instruction-*.json               # Exemples formulaires instruction agent (glob, si disponibles)
-->

Chaque `userTask` identifiée dans le SRS (section 3.2, Lanes PORTAL et XFLOW) qui nécessite un formulaire **DOIT** avoir son propre fichier JSON Form.io. L'agent DOIT parcourir le SRS pour identifier toutes les `userTask` et produire un formulaire pour chacune.

### Identification des formulaires à produire

À partir de la section 3.2 du SRS, lister toutes les `userTask` des deux lanes :

| Lane | userTask (SRS) | Type de formulaire | Fichier JSON |
| ------ | --------------- | ------------------- | ------------- |
| PORTAL | Soumission initiale | Formulaire principal (déjà produit à l'étape 5) | `formio-[nom-service].json` |
| PORTAL | Correction / Resoumission | Formulaire de correction (déjà produit à l'étape 5a) | `formio-correction-[nom-service].json` |
| PORTAL | Paiement | Formulaire de paiement (déjà produit à l'étape 5a) | `formio-paiement-[nom-service].json` |
| XFLOW | Instruction agent | Formulaire d'instruction | `formio-instruction-[nom-service].json` |
| PORTAL / XFLOW | [Autres userTasks] | Selon le besoin métier | `formio-[action]-[nom-service].json` |

### Convention de nommage

`formio-[action]-[nom-service].json` où `[action]` décrit le rôle de la userTask (ex: `instruction`, `validation`, `verification`, `telechargement`).

### Règles de génération

1. **Chaque userTask avec `camunda:formKey`** dans le BPMN doit pointer vers un formulaire JSON existant.
2. Les formulaires des userTasks agent (côté XFLOW) suivent la même structure racine Form.io (`title`, `name`, `path`, `type`, `display`, `i18n`, `config`, `components`, `actions`) que les autres formulaires.
3. Le contenu des champs est dérivé du SRS : les informations que l'agent doit consulter, les décisions qu'il peut prendre, les pièces justificatives à vérifier.
4. L'agent **DOIT** consulter le skill `formio-integrator` et les exemples dans `exemples/` pour respecter les standards Form.io ATD.

---

## <!-- STEP:6 --> Étape 6 — Processus BPMN (XML)

<!-- reads_before:
  - .agents/skills/bpmn-integrator/SKILL.md            # Skill BPMN complet (templates GNSPD, patterns, anti-patterns)
  - documentation/bpmn-gnspd-documentation.md          # Documentation technique GNSPD
  - documentation/guide-agent-ia-modelisateur.md       # Guide opérationnel modélisation BPMN
  - exemples/*/bpmn-*.bpmn                             # Exemples BPMN validés (glob)
-->

Produire le fichier BPMN 2.0 compatible Camunda Platform 7 (GNSPD). Sauvegarder dans `projects/[ministere]/[direction]/[service]/bpmn-[nom-service].bpmn`.

### Règles de génération (Normes Camunda 7 / GNSPD Framework)

> **RÈGLE MANDATOIRE (STOP AVANT DE CONTINUER) ✋** :
> Avant de générer le fichier XML, l'agent **DOIT IMPÉRATIVEMENT** :
> 1. Lire le skill d'intégration BPMN dédié (`skills/bpmn-integrator/SKILL.md`) ainsi que la documentation de référence (`bpmn-gnspd-documentation.md`) et le guide opérationnel (`guide-agent-ia-modelisateur.md`).
> 2. **Chercher et consulter les exemples de processus BPMN** situés dans le dossier `exemples/` (ex: `exemples/*/bpmn-*.bpmn`) afin de s'imprégner de l'orchestration des tâches, des règles de modélisation ATD et du niveau de qualité attendu.
>
> Ces documents contiennent toutes les règles critiques : architecture XPortal/XFlow à deux pools exécutables, catalogue complet des templates GNSPD avec leurs paramètres exacts, patterns de communication Kafka, grammaire `this.data`, configuration KMS multi-environnement, et anti-patterns interdits. Le non-respect de ces règles entraînera un échec en production.

#### A. Dix questions métier à répondre AVANT de modéliser

L'agent doit répondre à ces 10 questions à partir du SRS validé avant d'écrire une seule ligne de XML :

| # | Question | Impact sur le BPMN |
|---|----------|-------------------|
| 1 | Le service est-il payant ? Dans quels cas ? | Paiement sur plateforme **externe** (pas dans XPortal/XFlow) — redirection + confirmation asynchrone |
| 2 | Quelles pièces justificatives sont requises ? | `gnspdAttachments` dans la userTask agent |
| 3 | Quelles décisions l'agent peut-il prendre ? | Nombre de sorties de la gateway de décision (min. 3) |
| 4 | Y a-t-il une vérification dans Odoo ? Quel modèle ? Quel champ ? | Template `tg.gouv.gnspd.odoo` + domain |
| 5 | Y a-t-il une API REST tierce à appeler ? | Template `tg.gouv.gnspd.restBuilder` |
| 6 | Quels canaux de notification ? (Email / SMS / In-App) | Paramètres `gnspdNotifySendEmail/SMS/InApp` |
| 7 | La boucle de correction est-elle possible ? Combien de fois max. ? | receiveTask resoumission + limite de boucle |
| 8 | Quel est le code fonctionnel du service ? | Convention de nommage des messages et IDs |
| 9 | Quels systèmes tiers configurer en KMS ? (ODOO, GED, API…) | Bloc configuration du startEvent XFlow |
| 10 | L'architecture XPortal est-elle simple (pattern expert-2) ou distribuée (expert-1) ? | Structure du pool XPortal |

#### B. Déclarer les messages Kafka AVANT d'écrire le XML

Lister tous les échanges inter-pools et les déclarer à la racine du fichier BPMN, **avant** la balise `<bpmn:collaboration>` :

```xml
<!-- Convention : MSG_[SERVICE]_[ACTION] en majuscules — jamais d'UUID généré automatiquement -->
<bpmn:message id="MSG_SERVICE_START"       name="MSG_SERVICE_START" />
<bpmn:message id="MSG_SERVICE_RETURN"      name="MSG_SERVICE_RETURN" />
<bpmn:message id="MSG_SERVICE_PAY_CONFIRM" name="MSG_SERVICE_PAY_CONFIRM" />  <!-- si payant -->
<bpmn:message id="MSG_SERVICE_RESUB"       name="MSG_SERVICE_RESUB" />         <!-- si correction -->
```

#### C. Pattern XPortal recommandé (machine à états — expert-2)

Utiliser par défaut le pattern **receiveTask unique multi-entrante** avec une **gateway action unique**. Ce pattern est plus maintenable et extensible que le pattern distribué.

**IMPORTANT — Templates côté XPortal** : Les tâches citoyen utilisent le template `tg.gouv.gnspd.userTask` (et **non** `tg.gouv.gnspd.flowPortail`). Chaque `userTask` citoyen possède :
- `camunda:formKey="[ULID_FORM]"` — identifiant du formulaire Form.io
- `gnspdHandlerType` — type d'interaction (voir table ci-dessous)
- `gnspdTaskIsVisible=true` — rend la tâche visible côté portail

| `gnspdHandlerType` | Usage | Exemple |
|---------------------|-------|---------|
| `publish_submission` | Afficher un formulaire Form.io (soumission initiale ou correction) | Formulaire de demande, formulaire de correction |
| `tarification` | Rediriger vers la **plateforme de paiement e-Gov externe** | Paiement des frais de service |
| `download_files` | Proposer un téléchargement de fichier au citoyen | Téléchargement d'un récépissé |

**Pattern du startEvent XPortal** : Le `startEvent` porte `camunda:formKey="[ULID]"` (formulaire initial) et `gnspdPaymentAmount` (montant du paiement si applicable).

```text
StartEvent(formKey=ULID, paymentAmount=N)
    ↓
SendTask(→XFlow MSG_START)                        ← envoi immédiat au back-office
    ↓
┌── BLOC PAIEMENT (si service payant) ────────────────────────────┐
│ ReceiveTask(MSG_PAY_ORDER)                ← XFlow ordonne       │
│     ↓                                                           │
│ UserTask(tarification, formKey=ULID_PAY)  ← redirige e-Gov     │
│     ↓                                                           │
│ ReceiveTask(MSG_PAY_CONFIRM)              ← XFlow confirme      │
└─────────────────────────────────────────────────────────────────┘
    ↓
ReceiveTask(multi-entrant MSG_RETURN) ←──────────────────────────┐
    ↓                                                             │
Gateway(action ?)                                                 │
    correction | accepte | rejete                                  │
         ↓         ↓         ↓                                    │
   UserTask(fix,  EndEvent  EndEvent                               │
   publish_submission,                                             │
   formKey=ULID_CORRECTION)                                        │
         ↓                                                        │
   SendTask(→XFlow MSG_RESUB) ──────────────────────────────────►┘
```

**Pattern XFlow correspondant (orchestration back-office)** :

```text
StartEvent(KMS config)
    ↓
StepNotification(Submited)                    ← marque dossier soumis
    ↓
SendNotification(tricanal)                    ← accusé de réception
    ↓
┌── BLOC PAIEMENT (si service payant) ────────────────────────────┐
│ SendTask(MSG_PAY_ORDER → XPortal)         ← ordonne le paiement │
│     ↓                                                           │
│ IntermediateCatchEvent(MSG_PAY_CALLBACK)  ← callback e-Gov      │
│     executionListener: payment_key = true                        │
│     ↓                                                           │
│ SendTask(MSG_PAY_CONFIRM → XPortal)       ← confirme paiement   │
└─────────────────────────────────────────────────────────────────┘
    ↓
UserTask(Conformité agent) ←─────────────────────────────────────┐
    ↓                                                             │
Gateway(décision ?)                                               │
    conforme | correction | rejet                                  │
       ↓          ↓           ↓                                   │
  Instruction  StepCorr    StepRejet                               │
       ↓       NotifCorr   NotifRejet                              │
     Chef      SendCorr    SendRejet(MSG_RETURN action:rejete)     │
       ↓    (MSG_RETURN      ↓                                    │
  Gateway     action:corr)  EndEvent                               │
  valide|corr|rejet  ↓                                            │
    ↓    ↓    ↓   WaitResub(MSG_RESUB) ─────────────────────────►┘
  Odoo  ↩Instr ↓StepRejet
    ↓
  StepCompleted → NotifDispo → SendTermine(MSG_RETURN action:accepte) → EndEvent
```

**PATTERN PAIEMENT (obligatoire si service payant)** — Adopter le pattern `demande-passeport.bpmn` :

Le paiement est **orchestré par XFlow**, jamais par XPortal seul. Le flux est :

1. **XPortal** envoie le dossier à **XFlow** dès la soumission (avant le paiement).
2. **XFlow** crée la demande dans le système tiers (restBuilder), puis envoie un message à XPortal demandant au citoyen de payer (`sendMessage` → XPortal `receiveTask`).
3. **XPortal** affiche la `userTask(tarification)` au citoyen, qui est redirigé vers la plateforme e-Gov externe.
4. La plateforme e-Gov envoie un **callback à XFlow** (via `intermediateCatchEvent` avec `payment_key = true`).
5. **XFlow** traite les infos de paiement (restBuilder PUT vers le système tiers), puis envoie une confirmation à XPortal (`sendMessage` → XPortal `receiveTask`).
6. **XPortal** débloque le citoyen et continue le flux.

Ce pattern garantit que **XFlow reste le maître du flux de paiement** : il reçoit le callback, valide, logue, et confirme. XPortal ne fait que présenter l'écran de paiement.

#### D. Règles de génération complémentaires

- Sauvegarder impérativement dans l'extension `.bpmn`.
- Le XML comportera TOUJOURS la section graphique `<bpmndi:BPMNDiagram>` complète (toutes les formes et tous les edges, y compris les messageFlows).
- Le startEvent **XFlow** porte la configuration KMS complète des 4 environnements (`development`, `sandbox`, `preproduction`, `production`). Le startEvent **XPortal** peut avoir des blocs `{}` vides.
- **DISTINCTION IMPORTANTE** : Le `config` du JSON Form.io (URLs API publiques + mapping `config.users` pour e-ID) est **totalement distinct** du bloc KMS du startEvent XFlow (secrets systèmes tiers : Odoo, GED, APIs avec syntaxe `{dbkms:SERVICE_COMPOSANT}`). Ne pas confondre les deux.
- Chaque tâche avec un `camunda:modelerTemplate` doit contenir les 8 paramètres standards : `gnspdTaskIsVisible`, `gnspdTaskLabel`, `gnspdTaskStatus`, `gnspdTaskOrder`, `gnspdTaskKind`, `gnspdCostVariable`, `gnspdCostTotal`, `gnspdCostUnitaire`.

---

## <!-- GATE:3a --> GATE 3a — Validation des formulaires Form.io ✋

> **STOP OBLIGATOIRE** : Soumettre le(s) formulaire(s) JSON à l'utilisateur pour validation technique **avant** de lancer la génération du BPMN.
> Vérifier la conformité P-Studio du JSON principal et des formulaires intermédiaires (correction, paiement si applicable).
>
> **INSTRUCTION AGENT IA** : Présenter les chemins absolus des fichiers `formio-*.json` produits à l'utilisateur et attendre sa validation explicite avant de continuer.

---

## <!-- GATE:3b --> GATE 3b — Validation du processus BPMN ✋

> **STOP OBLIGATOIRE** : Soumettre le fichier BPMN à l'utilisateur pour validation technique.
> Vérifier la validité du BPMN (structure, messages Kafka, templates GNSPD, gateways, BPMNDiagram) avant de passer aux livrables d'accompagnement.
>
> **INSTRUCTION AGENT IA** : Présenter le chemin absolu du fichier `bpmn-*.bpmn` produit à l'utilisateur et attendre sa validation explicite avant de continuer.

---

## <!-- STEP:6.5 --> Étape 6.5 — Audit de cohérence inter-livrables

Avant de passer aux livrables d'accompagnement, l'agent **DOIT** vérifier la cohérence croisée entre tous les livrables produits :

### Checklist de cohérence

**Form.io ↔ BPMN** :
- [ ] Chaque `key` Form.io référencée dans le BPMN via `this.data.key` existe effectivement dans le JSON.
- [ ] Les champs hidden du formulaire de correction (`motifAgent`, `numeroDossier`, `nbCorrections`) correspondent aux variables injectées par XFlow.
- [ ] Si un formulaire de paiement existe, les champs hidden (`montantAPayer`, `referencePaiement`) correspondent aux variables calculées côté XFlow.

**Pipeline YAML ↔ SRS** :
- [ ] Chaque étape du pipeline YAML est couverte par une ligne dans les tableaux BPMN du SRS (Lane PORTAL ou Lane XFLOW).
- [ ] Les acteurs du pipeline correspondent aux acteurs de la matrice SRS.

**SRS ↔ Form.io** :
- [ ] Chaque champ listé dans la section 2.2 du SRS (tableau des champs) existe dans le JSON avec la même `key`.
- [ ] Les types de composants correspondent (textfield, select, file, etc.).
- [ ] Les règles de validation décrites dans le SRS sont implémentées dans le JSON.

**SRS ↔ BPMN** :
- [ ] Le nombre de notifications documentées dans le SRS (section 6) correspond au nombre de `sendNotification` dans le BPMN.
- [ ] Les règles de gestion (RG) liées aux gateways sont implémentées comme conditions JavaScript dans le BPMN.

**TO-BE ↔ Pipeline** :
- [ ] Chaque étape du TO-BE a un step correspondant dans le pipeline YAML.
- [ ] Les acteurs et systèmes sont cohérents entre les deux documents.

---

## <!-- STEP:7 --> Étape 7 — Plan de Tests et Manuel Utilisateur

### Plan de Tests (`[nom-service]-tests.md`)
- Scénarios de tests nominaux (cas où tout se passe bien).
- Scénarios de tests alternatifs (erreurs, rejets).
- **Cas limites obligatoires formulaire** : fichier trop volumineux, année hors bornes, double soumission, timeout paiement, champs e-ID vides.
- **Cas limites BPMN obligatoires** :
  - Rejet définitif par l'agent (le chemin de rejet doit atteindre un endEvent, pas un deadlock).
  - Condition JavaScript retournant `null` ou `undefined` sur une gateway (vérifier qu'aucun chemin n'est bloqué).
  - Dépassement du SLA d'instruction (le timer boundary event déclenche bien l'escalade).
  - Citoyen ne resoumettant pas dans le délai imparti (le timer boundary event clôt le dossier).
  - Paiement échoué ou abandonné (le processus revient à un état cohérent ou clôt le dossier).
  - Dépassement du nombre maximum de corrections (le compteur `nbCorrections` déclenche bien le rejet automatique).
  - Echec de connexion Odoo (l'error boundary event est déclenché et le dossier notifié).
- Critères d'acceptation.
- Matrice de couverture (chaque RG doit être couverte par au moins un test).

### Manuel Utilisateur (`[nom-service]-manuel.md`)
- Guide pas à pas avec captures d'écran des formulaires.
- Explication des statuts de la demande.
- **Section Agent** : Procédure de validation/rejet en back-office.

---

## <!-- STEP:8 --> Étape 8 — Personnalisation et adaptation

Après avoir généré les livrables techniques avec les templates ci-dessus, adapter :

### Pour le formulaire Form.io
- Ajouter les champs métier spécifiques au service (ex. pour fréquences radio : bande de fréquence, puissance, zone géographique)
- Ajouter les validations métier (ex. format SIRET, format numéro de licence)
- Ajouter la logique conditionnelle (`conditional`) si certains champs dépendent d'autres
- Adapter les sections de pièces justificatives selon la liste réglementaire

### Pour le BPMN
- Renommer les participants avec le nom réel de l'organisme.
- Ajouter des lanes (swimlanes) si plusieurs services internes traitent le dossier.
- **Ajouter un boundary timer event (non-interrompant) sur la userTask d'instruction agent** pour déclencher une escalade automatique si le SLA (ex. 48h) est dépassé.
- **Ajouter un boundary timer event sur la receiveTask "attendre resoumission"** pour clore automatiquement le dossier si le citoyen ne répond pas dans le délai imparti.
- Adapter les noms des tâches au vocabulaire métier de l'organisme.
- Ajouter des error boundary events pour les cas d'exception (timeout API Odoo, échec REST tiers).
- **Si le service dispose d'une API REST tierce** (hors Odoo) : configurer les appels via le template `tg.gouv.gnspd.restBuilder` avec authentification `bearerToken` et les URLs dans le bloc KMS du startEvent XFlow.
- **Limiter explicitement la boucle de correction** : incrémenter une variable `nbCorrections` à chaque passage et ajouter une condition de sortie (ex. rejet automatique après 3 tentatives infructueuses).

---

## <!-- STEP:8.5 --> Étape 8.5 — PV de Recette (`[nom-service]-pv-recette.md`)

Produire le procès-verbal de recette fonctionnelle qui formalise la validation du service.

### Structure :
- **Référence du service** : Nom, code, version.
- **Environnement de test** : URL, date, participants.
- **Résultats des tests** : Matrice des scénarios exécutés (Pass/Fail) avec référence au plan de tests.
- **Anomalies résiduelles** : Liste des défauts connus acceptés.
- **Décision** : Recette validée / Recette conditionnelle / Recette refusée.
- **Signatures** : Intégrateur, Point focal FDS, Chef de projet ATD.

---

## <!-- STEP:9 --> Étape 9 — Contrôle qualité des livrables (Checklist finale)

Avant de livrer, vérifier chaque livrable :

### Checklist AS-IS / TO-BE
- [ ] Tous les acteurs sont identifiés
- [ ] Les durées de chaque étape sont indiquées
- [ ] Les points de friction as-is sont listés
- [ ] Les gains attendus to-be sont quantifiés
- [ ] Les technologies cibles sont spécifiées

### Checklist Form.io JSON
- [ ] JSON valide (pas d'erreurs de syntaxe)
- [ ] La structure JSON racine est **plate** : `title`, `name`, `path`, `type`, `display`, `i18n`, `config`, `components` et `actions` sont déclarés directement à la racine. **AUCUN** wrapper `settings` ni `content` ne doit être utilisé. Le tableau `actions` contient la configuration RabbitMQ (`topic: "submissions.topic"`).
- [ ] Le bloc `config` contient les 4 environnements (`development`, `sandbox`, `preproduction`, `production`) avec la même structure `users`.
- [ ] Le bloc `i18n` est présent à la racine du JSON avec les traductions anglaises de tous les textes visibles.
- [ ] Toutes les `key` sont uniques et en camelCase.
- [ ] Les champs obligatoires ont `"validate": {"required": true}` et une stratégie de validation poussée (Blur, règles métier, messages custom) a été appliquée suite à réflexion préalable de l'agent.
- [ ] `"validateOn": "blur"` est défini sur tous les champs de saisie.
- [ ] Les messages d'erreur sont personnalisés via le dictionnaire `"errors"` (pas les messages système génériques).
- [ ] Le verrouillage des champs pré-remplis (e-ID) utilise la méthode dynamique robuste (propriété `logic` avec trigger `!!(data.champ && String(data.champ).trim().length > 0)` conditionnant `disabled: true`). **JAMAIS** de `"disabled": true` statique.
- [ ] Le `startButton` du premier panel (`stepIntro`) a bien l'action `submit`. **Aucun autre bouton** de navigation ou de soumission n'est ajouté manuellement (P-Studio les fournit nativement).
- [ ] Le composant de "Récapitulatif Intelligent" (`htmlelement`) est présent juste avant la case "Lu et approuvé" (qui est présente dans ses `excludeKeys`).
- [ ] Toutes les listes (pays, devises, régions...) utilisent `"dataSrc": "url"` avec `{{ config.apiBaseUrl }}/references/XXX`. **Aucune donnée en dur**.
- [ ] Les composants `file` ont le bon libellé de pièce justificative.
- [ ] Le `display` est adapté (wizard pour formulaires multi-étapes).

### Checklist BPMN XML

**Structure et namespaces**
- [ ] Le namespace `xmlns:camunda="http://camunda.org/schema/1.0/bpmn"` est déclaré. **Aucun** namespace `zeebe:` n'est présent (ATD = Camunda Platform 7, jamais Camunda 8).
- [ ] `exporter="Camunda Modeler"`, `exporterVersion="5.42.0"`, `modeler:executionPlatformVersion="7.17.0"` sont déclarés.
- [ ] Les deux pools (XPORTAL et XFLOW) sont déclarés `isExecutable="true"` dans leurs `<bpmn:process>` respectifs.
- [ ] Le pool XFlow porte `camunda:versionTag="1.0"` et `camunda:historyTimeToLive="180"`.

**Messages Kafka**
- [ ] Tous les messages Kafka sont déclarés via `<bpmn:message>` à la racine, **avant** la balise `<bpmn:collaboration>`.
- [ ] Les noms de messages sont **sémantiques** (`MSG_SERVICE_ACTION` en majuscules), jamais des UUIDs générés automatiquement (`Message_35c51dc`).
- [ ] Chaque `<bpmn:message>` déclaré est effectivement utilisé par exactement un émetteur (sendTask ou startEvent) et un récepteur (receiveTask ou intermediateCatchEvent).
- [ ] Tous les `messageFlow` dans la collaboration référencent des éléments existants et ont leurs coordonnées DI dans le BPMNDiagram.

**Templates GNSPD et paramètres**
- [ ] Toutes les tâches interactives déclarent un `camunda:modelerTemplate` GNSPD (`tg.gouv.gnspd.userTask`, `tg.gouv.gnspd.sendMessage`, `tg.gouv.gnspd.receiveTask`, `tg.gouv.gnspd.sendNotification`, `tg.gouv.gnspd.odoo`, `tg.gouv.gnspd.restBuilder`, `tg.gouv.gnspd.endEvent`).
- [ ] **TOUTES** les tâches techniques (User, Service, Send, Receive) utilisent `camunda:type="external"` avec un `camunda:topic` valide (`flow-start`, `flow-send-message`, `flow-receive-task`, `flow-user-task`, `flow-notify`, `flow-odoo`, `flow-rest-builder`, `flow-end-event`). **Exception : `bpmn:boundaryEvent` timer — PAS de `camunda:type` ni `camunda:topic` sur l'élément boundary lui-même.**
- [ ] Le pool XFlow a `isExecutable="true"` sur le **participant** et `isExecutable="false"` sur le **process**. Le pool XPortal a `isExecutable="true"` sur les deux.
- [ ] Chaque tâche avec un `camunda:modelerTemplate` contient les **8 paramètres standards** : `gnspdTaskIsVisible`, `gnspdTaskLabel`, `gnspdTaskStatus` (ex: `Pending`, `PendingPortal`), `gnspdTaskOrder`, `gnspdTaskKind`, `gnspdCostVariable`, `gnspdCostTotal`, `gnspdCostUnitaire`. **Exception : `tg.gouv.gnspd.stepNotification` n'utilise PAS ces 8 champs** — seulement `gnspdStatus`, `gnspdIsPortal`, `gnspdStepOrder` (voir section SKILL.md §P).
- [ ] Les tâches de notification (`flow-notify`) ont **au moins un canal active** (`gnspdNotifySendEmail`, `gnspdNotifySendSMS` ou `gnspdNotifySendInApp` à `true`).

**Tâches citoyen XPortal (userTask, pas flowPortail)**
- [ ] Les tâches citoyen côté XPortal utilisent `tg.gouv.gnspd.userTask` (`bpmn:userTask`) avec `camunda:formKey="[ULID]"` et `gnspdHandlerType` — et **non** `tg.gouv.gnspd.flowPortail` (pattern legacy).
- [ ] Le `startEvent` XPortal porte `camunda:formKey="[ULID]"` (formulaire initial) et `gnspdPaymentAmount` (montant si service payant).
- [ ] Chaque `userTask` citoyen de soumission ou d'instruction agent a un `gnspdHandlerType` correct : `publish_submission` (formulaire), `tarification` (paiement), ou `download_files` (téléchargement).
- [ ] La tâche de correction côté **XPortal** utilise `gnspdHandlerType="publish_submission"` avec `gnspdSubmissionData` **conditionnel** : `$(this.data.TASK_ID && this.data.TASK_ID.result ? this.data.TASK_ID.result : this.data.EVENT_START.parameters.submissionData.data)`. Le chemin des données initiales se termine par `.submissionData.data` (avec `.data`). `gnspdSubmissionFormkey` est optionnel.

**Configuration KMS**
- [ ] Le startEvent **XFlow** embarque la configuration KMS des 4 environnements (`development`, `sandbox`, `preproduction`, `production`) avec les blocs JSON des systèmes tiers (ODOO, GED, API…).
- [ ] Les secrets sont référencés via la syntaxe KMS `{dbkms:[SERVICE]_[COMPOSANT]}`, jamais en clair.
- [ ] Les URLs de connexion Odoo/API sont lues depuis `this.data.Event_X_Start.parameters.configuration.SYSTEME.CLE`, jamais codées en dur.

**Gateways et conditions**
- [ ] Les événements de messages (`Start`/`Catch`) référencent l'`id` d'un `<bpmn:message>` global existant.
- [ ] Toutes les conditions de séquenceFlow sont en JavaScript (`language="javascript"` — vérifier l'orthographe, sans faute de frappe).
- [ ] **Toute gateway de décision agent possède au minimum 3 sorties : Approuvé, Correction, Rejeté.** Une gateway à 2 sorties sans chemin de rejet crée un deadlock systématique.
- [ ] Chaque gateway exclusive a une condition par sortie ; aucun chemin ne peut rester sans condition satisfaite (pas de deadlock possible).
- [ ] **Aucun ExclusiveGateway n'est utilisé comme simple point de merge** (N entrées → 1 sortie). Pour la convergence, connecter les flux directement sur la tâche cible via plusieurs `<bpmn:incoming>`. Les ExclusiveGateway servent uniquement à la divergence (1 entrée → N sorties avec conditions).

**Paiement (pattern demande-passeport obligatoire)**

- [ ] Le paiement est orchestré par **XFlow** (pattern `demande-passeport.bpmn`) — XPortal ne gère jamais le callback de paiement directement.
- [ ] **XFlow** : un `intermediateCatchEvent` (messageEventDefinition) attend le callback de la plateforme e-Gov et positionne `payment_key = true` via un executionListener.
- [ ] **XFlow** : un `restBuilder` (PUT) envoie les informations de paiement au système tiers après réception du callback.
- [ ] **XFlow** : un `sendMessage` envoie la confirmation de paiement à XPortal (`receiveTask` côté XPortal).
- [ ] **XPortal** : une `userTask` avec `gnspdHandlerType="tarification"` affiche l'écran de paiement au citoyen.
- [ ] **XPortal** : un `receiveTask` attend la confirmation de paiement envoyée par XFlow (pas directement par la plateforme e-Gov).
- [ ] Le `startEvent` XPortal déclare `gnspdPaymentAmount` avec le montant correct.
- [ ] Le dossier est envoyé à XFlow **avant** le paiement (XFlow orchestre la séquence).

**Boucle de correction**
- [ ] La boucle correction est modélisée des deux côtés (XFlow envoie l'ordre, XPortal le reçoit et affiche l'écran de correction).
- [ ] La boucle de correction possède une **limite explicite** (compteur de tentatives ou boundary timer event). Une boucle infinie sans issue est interdite.
- [ ] Le payload de correction inclut le motif saisi par l'agent (`motif` dans `gnspdNotifyContent` et dans le message Kafka).

**Intégrité structurelle**
- [ ] Tous les `id` sont uniques dans le fichier.
- [ ] Tous les `sequenceFlow` ont `sourceRef` et `targetRef` valides pointant vers des éléments existants.
- [ ] Chaque pool a au moins un startEvent et un endEvent.
- [ ] Tous les chemins possibles depuis chaque startEvent atteignent un endEvent (pas de branche orpheline).

**Graphique (BPMNDiagram)**
- [ ] La section `<bpmndi:BPMNDiagram>` est présente et **complète** : chaque élément BPMN (shape ou flow) a ses coordonnées DI, y compris tous les messageFlows.
- [ ] Les deux pools ont des `BPMNShape` avec `isHorizontal="true"` et des dimensions cohérentes.

**Anti-patterns BPMN interdits**

| Anti-pattern | Conséquence | Correction |
|-------------|-------------|------------|
| `isExecutable="false"` sur un pool | Camunda refuse le déploiement | `isExecutable="true"` sur les 2 pools |
| Gateway décision à 2 sorties sans rejet | Deadlock si l'agent rejette | Ajouter systématiquement la sortie Rejeté |
| `language="javscript"` (typo sans 'a') | Condition ignorée par le moteur | Toujours vérifier l'orthographe |
| Paiement calculé côté form seulement | Dossiers non payés soumis | Implémenter le cycle complet dans le BPMN |
| `flowPortail` pour les tâches citoyen XPortal | Pattern legacy, absent des exemples de référence | Utiliser `userTask` avec `gnspdHandlerType` et `camunda:formKey` |
| `this.data.champInexistant` | Requête Odoo échoue silencieusement | Vérifier la cohérence form ↔ BPMN |
| Messages nommés par UUID auto (`Message_35c51dc`) | Impossible à maintenir | Noms fonctionnels `MSG_SERVICE_ACTION` |
| BPMNDiagram vide ou incomplet | Diagramme inutilisable dans Camunda Modeler | Coordonnées DI pour tous les éléments |
| Boucle correction sans limite | Instance bloquée indéfiniment | Compteur + condition de sortie |
| ExclusiveGateway utilisé comme simple merge (N entrées → 1 sortie) | Erreur validation : « ExclusiveGateway doit avoir au moins 2 flux sortants » | Ne jamais utiliser d'ExclusiveGateway pour la convergence. Connecter les flux entrants directement sur la tâche cible (une tâche accepte plusieurs `<bpmn:incoming>`) |
| Namespace `zeebe:` présent | Incompatible Camunda Platform 7 | Supprimer, utiliser uniquement `camunda:` |
| `$this.data.` dans les `conditionExpression` | Erreur de validation P-Studio | Toujours utiliser `this.data.` (sans préfixe `$`) dans les expressions de condition des `sequenceFlow`. Le préfixe `$` est réservé aux `inputParameter` (ex: `gnspdMessage`, `gnspdSubmissionData`) |
| `camunda:topic` sur un `bpmn:boundaryEvent` timer | L'élément devient "non atteignable depuis les startEvents" — le validateur GNSPD le traite comme un service externe | Ne **jamais** ajouter `camunda:type` ni `camunda:topic` sur l'élément `bpmn:boundaryEvent` lui-même. Utiliser `timerEventDefinition` avec un `id` et `timeDuration xsi:type="bpmn:tFormalExpression"` |
| `gnspdSubmissionData` pointant vers un champ inexistant dans le formulaire | "Le champ X référencé n'existe dans aucun formulaire" | Utiliser le pattern conditionnel avec `.submissionData.data` : `$(this.data.TASK && this.data.TASK.result ? this.data.TASK.result : this.data.EVENT_START.parameters.submissionData.data)` |
| `gnspdTempData` avec valeurs hardcodées | Document généré avec données fictives en production | Toujours référencer `this.data.XXX.result.submissionData.YYY` — jamais de chaînes littérales comme `"12345"` ou `"2026-03-23"` |
| Compteur de boucle : condition lit `this.data.TASK.result.reformulationCount` | Variable non trouvée ou toujours 0 | Lire la variable globale directement : `this.data.reformulationCount` (modifiée par le scriptTask, pas par la tâche) |
| `bpmn:receiveTask` sans `camunda:modelerTemplate` | Le worker GNSPD ne prend pas la tâche | Toujours ajouter `camunda:modelerTemplate="tg.gouv.gnspd.receiveTask"` + `camunda:type="external"` + `camunda:topic="flow-receive-task"` |
| Destinations Kafka inversées (ch-portail-* pour XPortal→XFlow) | Les messages ne sont jamais reçus | XPortal→XFlow : `peer-xflow-*` ; XFlow→XPortal : `ch-portail-*` — ne jamais inverser |

---

À la fin de ce workflow, tous les fichiers suivants doivent exister **de manière centralisée et hiérarchisée au sein du dossier de projet** (`projects/[ministere]/[direction]/[service]/`) :

| Fichier | Description |
|---------|-------------|
| `[nom-service]-pipeline.yaml` | Pipeline du processus cible |
| `[nom-service]-as-is.md` | Cartographie du processus actuel |
| `[nom-service]-to-be.md` | Cartographie du processus cible digitalisé |
| `srs-[nom-service].md` | Fiche SRS (Spécifications fonctionnelles) |
| `formio-[nom-service].json` | Schéma Form.io du formulaire principal |
| `formio-correction-[nom-service].json` | Formulaire de correction (si boucle de correction) |
| `formio-paiement-[nom-service].json` | Formulaire de paiement (si service payant) |
| `bpmn-[nom-service].bpmn` | Processus BPMN 2.0 Camunda Platform 7 (GNSPD) |
| `[nom-service]-tests.md` | Plan de tests complet |
| `[nom-service]-manuel.md` | Manuel utilisateur (citoyen/agent) |
| `[nom-service]-pv-recette.md` | PV de recette (si applicable) |
