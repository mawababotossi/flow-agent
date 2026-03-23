# Guide Méthodologique de Transformation AS-IS vers TO-BE (Standard ATD)

Ce guide détaille la démarche intellectuelle, la logique de modélisation et les standards de l'Agence Togo Digital (ATD) pour passer d'une cartographie de l'existant (AS-IS) à une cartographie cible (TO-BE) dans le cadre du Plan d'Accélération de la Digitalisation (PAD).

---

## 1. Principes Fondamentaux de la Transformation

La digitalisation ne consiste pas à numériser un formulaire papier (scanner un PDF), mais à **repenser intégralement le processus métier** en exploitant les capacités du numérique (Niveau 3 et 4 de la maturité digitale ATD). L'approche repose sur les piliers suivants :

1.  **Guichet Unique Citoyen (XPortal)** : Le citoyen ne se déplace plus pour déposer ou récupérer de l'information. L'interface doit être asynchrone, accessible H24, et réactive sur mobile (Mobile-First).
2.  **Principe du "Dites-le-nous une fois"** : L'usager ne doit jamais resaisir une information déjà connue de l'État (Identité E-ID pré-remplie, Numéro d'immatriculation, etc.).
3.  **Traitement Back-Office Centralisé (XFlow & Odoo)** : Toutes les décisions, vérifications et validations doivent être orchestrées par le moteur BPMN (Camunda Platform 7) et historisées dans le back-office pour une traçabilité totale.
4.  **Interopérabilité (API-First)** : L'authentification, les paiements, l'envoi de notifications (SMS/Email) et l'accès aux registres nationaux sous-jacents se font via des appels d'API standardisés via Kafka.
5.  **Sécurisation par conception (Security by Design)** : Les documents finaux délivrés (Attestations, Diplômes, Certificats) doivent intégrer des mécanismes anti-fraude (QR Code infalsifiable à minima).

---

## 2. Étape 1 : Comprendre le Besoin à travers l'AS-IS (La Source de Vérité)

La cartographie AS-IS ne s'invente pas. Elle découle de l'enquête métier (souvent via **KoboToolbox** ou les fiches d'entretiens des directions métiers).

### Grille d'Analyse du Questionnaire Métier (Kobo)
L'analyste doit extraire du fichier source (`fichier_kobo_pour_srs.csv`) les éléments suivants :

| Thème Kobo | Outils d'Analyse (Quoi extraire ?) |
| :--- | :--- |
| **Q1 à Q13 : Identité du Service** | Définir précisément le nom officiel, le rôle, l'éligibilité légale et l'encadrement réglementaire du service. |
| **Q14 à Q16 : Parcours Demandeur (Input)** | Lister toutes les pièces que le citoyen fournit aujourd'hui. Dépister les champs (Nom, Adresse, Motivations...) cachés dans ces pièces (Ex : Si formulaire papier → le transformer en champs numériques). |
| **Q17 à Q19 : Parcours Agent (Output)** | Identifier les étapes de validation (Contrôle niveau 1, Signature, Cachet, Transmission). Où se trouvent les goulots d'étranglement physiques ? |
| **Q20, Q29-33 : Volumes & SLA** | Récupérer le délai de traitement moyen (AS-IS), les pics d'activité et la volumétrie annuelle pour calibrer les KPIs cibles du TO-BE. |
| **Q36 : Tarification** | Si le service est payant, l'architecture cible doit inclure une brique e-paiement (Flooz / TMoney / Visa / Mastercard). |
| **Q37-43 : Points de Friction** | Les "douleurs" (falsification, déplacements inutiles aux guichets, pertes de dossiers papier) dictent directement les automatisations à prévoir dans le TO-BE. |

### Livrable de sortie AS-IS
Le document `nom-service-as-is.md` doit clairement illustrer :
-   Les acteurs en jeu et leur rôle exact.
-   Les étapes séquentielles manuelles.
-   La liste brute des points de friction validés.

---

## 3. Étape 2 : Conception de la Cartographie Cible (Le TO-BE)

L'ingénierie du TO-BE consiste à "casser" l'AS-IS en appliquant des "remèdes digitaux" aux points de friction, en alignant les étapes sur les technologies P-Studio (Form.io + Camunda 7 GNSPD).

### 3.1. Méthodes d'Analyse Avancées pour l'Analyse

Pour un TO-BE performant, l'analyste doit utiliser des outils de diagnostic :

#### A. Analyse de la Valeur Ajoutée (AVA)
Chaque étape de l'AS-IS doit être classée :
1.  **Valeur Ajoutée Citoyen (VAC)** : Bénéfice direct à l'usager. *À optimiser.*
2.  **Valeur Ajoutée Business/Légale (VAB)** : Nécessaire pour la conformité. *À automatiser.*
3.  **Sans Valeur Ajoutée (SVA)** : Bureaucratie, attentes, doublons. *À supprimer radicalement.*

#### B. La Méthode des "5 Pourquoi"
Face à un blocage, posez la question "Pourquoi ?" 5 fois pour identifier la cause racine (Ex: manque d'accès au registre, signature physique attendue) et proposez une solution technologique.

### 3.2. Règles de passage (AS-IS → TO-BE)

#### Règle 1 : Éliminer la Poursuite Papier
*   **AS-IS** : L'usager remplit un formulaire Cerfa, joint des photocopies et se rend au guichet.
*   **TO-BE** : Formulaire dynamique 100% en ligne (Form.io Wizard). Pièces jointes transformées en Upload (`file maxSize: 2MB`, `pdf/jpeg`).

#### Règle 2 : L'État Civil Automatique
*   **AS-IS** : L'agent vérifie manuellement l'identité via la copie de la CNI.
*   **TO-BE** : Pré-remplissage via e-ID (`{{ user.firstName }}`). Plus de saisie manuelle bloquante. Les champs "Nom", "Prénom", "Téléphone" sont extraits de `config.users` avec un bloc `logic` de type "Disabled" si existants.

#### Règle 3 : Paiement Sans Contact
*   **AS-IS** : L'usager paie en espèces à la caisse de la direction.
*   **TO-BE** : Composant de calcul caché (`montantPaiement`). Déclenchement de l'action système `Calculate Costs` et module de paiement e-Gov avant transmission du dossier.

#### Règle 4 : Orchestration BPMN Asynchrone
*   **AS-IS** : Un dossier passe de main en main (bureau de l'instructeur → signature du chef). Processus opaque pour l'usager.
*   **TO-BE** : XFlow (Camunda 7) gère l'état du dossier et communique avec XPortal via Kafka. Chacun possède son pool exécutable.

#### Règle 5 : Communication Proactive
*   **AS-IS** : Le citoyen appelle ou revient vérifier si son document est prêt (Allers-retours inutiles).
*   **TO-BE** : Injection de Service Tasks `flow-notify`. Notifications SMS/Email automatiques aux jalons clés (Réception de la Demande, Demande de Correction, Validation/Document Prêt).

#### Règle 6 : Sécurisation et Génération Automatique
*   **AS-IS** : Le directeur signe manuellement un parchemin physique, risque de falsification.
*   **TO-BE** : Service Task `flow-generate-template`. Production d'un PDF normé, validé numériquement et intégrité prouvée par un QR Code centralisé ATD.

### Livrable de sortie TO-BE
Le document `nom-service-to-be.md` doit inclure :
-   La vision globale de la cible (L'expérience numérique).
-   La nouvelle architecture technique (XPortal, XFlow / API locales, Odoo).
-   Les étapes "Digital-First" clarifiées (De la soumission citoyen à la mise à disposition).
-   La cartographie explicite des gains (Finis les déplacements X fois, fin du cash, traçabilité temps réel).

---

## 4. Les 10 Règles d'Or de la Modernisation (ATD)

1.  **Simplicité Radicale** : Si une étape n'est pas justifiée par la loi ou un bénéfice citoyen, supprimez-la.
2.  **Parallélisation** : Ne faites pas attendre une vérification si elle peut être faite en même temps qu'une autre.
3.  **Zéro Saisie Redondante** : Ne demandez jamais une information que l'État possède déjà (Interopérabilité).
4.  **Capture à la Source** : L'usager numérise lui-même son document ; l'agent ne fait que valider.
5.  **Validation au Fil de l'Eau** : Utilisez Form.io pour bloquer les erreurs *pendant* la saisie.
6.  **Transparence Totale** : L'usager doit connaître son statut en temps réel (Notifications).
7.  **Inclusivité** : Le design doit être lisible sur les téléphones les plus basiques.
8.  **Automatisation par Défaut** : Favorisez les Service Tasks aux User Tasks chaque fois que possible.
9.  **Standardisation** : Utilisez les composants et templates ATD certifiés.
10. **Mesurabilité** : Chaque processus TO-BE doit avoir des KPIs intégrés.

---

## 5. Étape 3 : Spécification Technique Requise (Le SRS)

Une fois le TO-BE intellectuellement validé, il faut le "traduire" en spécifications techniques via le **Service Requirement Sheet (SRS)** normé. Le TO-BE ne peut pas se passer du SRS, car le SRS est le plan de montage pour l'Intégrateur Form.io et BPMN.

La logique métier détectée dans la phase de conception TO-BE se déverse dans le SRS de cette façon :
1.  **Dictionnaire de données (Form.io)** : Chaque étape initiale devient un onglet (Panel). Chaque information collectée devient un Composant JSON stricte (Type, Require, Regex Pattern, Custom Error).
2.  **Logique Conditionnelle** : Ce qui était manuel ("Ne payez que si duplicata") devient de l'algorithmie (`customConditional` SI `typeDemande == duplicata`).
3.  **BPMN** : Les actions humaines identifiées dans le TO-BE deviennent des **User Tasks** (Assignation : Agent de Traitement). Les automatisations (Création PDF, Envoi de Mail) deviennent des **Service Tasks**.

---

## 6. Design Thinking et Expérience Utilisateur (UX)

### 6.1. User Journey Mapping (Parcours Citoyen)
Ne vous contentez pas de modéliser des flux de données. Imaginez l'émotion de l'usager à chaque étape :
*   **Moment de doute** : "Ai-je bien soumis ?" ➔ *Accusé de réception immédiat.*
*   **Moment de stress** : "Pourquoi mon dossier est bloqué ?" ➔ *Notification explicite du motif.*

### 6.2. Co-création avec le métier
Impliquez les agents de terrain dans la validation du flux. Ce sont eux qui connaissent les cas particuliers.

---

## 7. Accompagnement au Changement

*   **Formation** : Les agents doivent être formés sur Odoo Traitement avant le "Go-Live".
*   **Communication** : Expliquez aux usagers les bénéfices (gain de temps, économie).
*   **Cycle Pilote** : Démarrez par une session restreinte pour ajuster les réglages.

---

## Synthèse du Processus Analytique

> Kobo Source (Fichiers terrain bruts)
> ⬇ *(Analyse Quali/Quanti & Valeur Ajoutée)*
> **AS-IS** (Ce qui se fait aujourd'hui, et pourquoi c'est lent/cher/imparfait)
> ⬇ *(Application des 10 Règles d'Or & Design Thinking)*
> **TO-BE** (Comment le système gère le flux avec le citoyen connecté)
> ⬇ *(Formalisation de l'Ingénierie)*
> **SRS** (Instructions techniques détaillées pour le développement de la machine)
> ⬇ *(Codage selon standards P-Studio)*
> **Formulaire JSON + Schéma BPMN** (Ce qui est déployé sur XPortal/Camunda 7 GNSPD via Kafka)

---
*Ce guide s'applique impérativement aux projets de niveau de Maturité Digitale 3 et 4.*
