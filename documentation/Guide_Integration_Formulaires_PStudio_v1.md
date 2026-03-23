# P-STUDIO — Guide d'intégration des formulaires
### Référentiel Technique pour les Intégrateurs

---

| Paramètre | Valeur |
|---|---|
| **Outil de conception** | Form.io Builder (intégré à P-Studio) |
| **Langues supportées** | Français (FR) — Anglais (EN) |
| **Environnements** | development · sandbox · preprod · production |
| **Version du document** | 1.0 |
| **Statut** | Document de référence — Diffusion restreinte |

---

## Sommaire

1. [Structure générale d'un formulaire P-Studio](#1-structure-générale-dun-formulaire-p-studio)
2. [Mode d'affichage : Wizard vs Form](#2-mode-daffichage--wizard-vs-form)
3. [Étape d'introduction (stepIntro)](#3-étape-dintroduction-stepintro)
4. [Bouton de démarrage (automatique)](#4-bouton-de-démarrage-automatique)
5. [Bloc config — Configuration par environnement](#5-bloc-config--configuration-par-environnement)
6. [Données utilisateur — Connexion standard et e-ID](#6-données-utilisateur--connexion-standard-et-e-id)
7. [Pré-remplissage des champs avec config](#7-pré-remplissage-des-champs-avec-config)
8. [Internationalisation (i18n) — Français / Anglais](#8-internationalisation-i18n--français--anglais)
9. [Données dynamiques via URL (pays, monnaies, listes...)](#9-données-dynamiques-via-url-pays-monnaies-listes)
10. [Contrôles et validations sur les champs](#10-contrôles-et-validations-sur-les-champs)
11. [Le Récapitulatif Intelligent (Composant HTML)](#11-le-récapitulatif-intelligent-composant-html)
12. [Actions sur le formulaire (calcul de coûts & soumission)](#12-actions-sur-le-formulaire-calcul-de-coûts--soumission)
13. [Règles fondamentales — À faire / À ne pas faire](#13-règles-fondamentales--à-faire--à-ne-pas-faire)
14. [Débogage et diagnostic](#14-débogage-et-diagnostic)
15. [Convention de nommage des livrables (Standard ATD)](#15-convention-de-nommage-des-livrables-standard-atd)

---

## 1. Structure générale d'un formulaire P-Studio

Tout formulaire publié sur P-Studio doit respecter une architecture à trois blocs racines : **settings**, **content**, et **actions**. Seul le bloc **content** porte la logique Form.io, tandis que **actions** gère les intégrations asynchrones (ex: RabbitMQ).

### Structure JSON racine (Norme ATD / P-Studio)

```json
{
  "title": "Nom du Formulaire",
  "name": "nomDuFormulaire",
  "path": "nom-du-formulaire",
  "type": "form",
  "display": "wizard",
  "components": [ ... ],
  "config": { ... },
  "i18n": { ... },
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

| Propriété | Obligatoire | Description |
|---|---|---|
| `title`, `name`, `type`, `display`, etc. | Oui | Propriétés racines du formulaire Form.io. |
| `components`, `config`, `i18n` | Oui | Contenu structurel et configuration du formulaire. |
| `actions` | Oui | Tableau d'actions post-soumission (RabbitMQ, Calculate Costs). |

> **✕ Règle absolue**
>
> Le bloc `"config"` doit **TOUJOURS** être placé à l'intérieur de `"content"`, au même niveau que `"components"`.
>
> Placer le `config` à la racine ou dans `"settings"` rendra toutes les variables `config.xxx` non résolues.

---

## 2. Mode d'affichage : Wizard vs Form

### Mode Wizard — Obligatoire pour les démarches

Le mode Wizard est le standard de P-Studio. Il organise le formulaire en étapes séquentielles. Chaque étape est un Panel de premier niveau dans le tableau **components**.

| Comportement | Description |
|---|---|
| Affichage | Une seule étape visible à la fois |
| Navigation | Boutons Précédent / Suivant gérés par P-Studio (ne pas recréer) |
| Dernière étape | Le bouton Soumettre remplace automatiquement le bouton Suivant |
| Sauvegarde | Automatique à chaque changement d'étape et modification de champ |
| Barre de progression | Affichée par P-Studio en haut de l'écran (basée sur le nombre de panels) |
| stepIntro | Exclu du compteur d'étapes (ex : 3 panels dont stepIntro → affiché "2 étapes") |

### Structure d'une étape Wizard

```json
{
  "type": "panel",
  "title": "Informations sur le déclarant",
  "key": "stepDeclarant",
  "components": [
    { /* champs de cette étape */ }
  ]
}
```

> **ℹ Règle de nommage des clés (`key`)**
>
> Chaque panel **DOIT** avoir un `"key"` unique dans tout le formulaire.
>
> Conventions recommandées : `stepIntro` · `stepIdentite` · `stepDetails` · `stepDocuments` · `stepRecapitulatif`
>
> La clé doit être en camelCase, sans espaces, sans caractères spéciaux.

### Mode Form — Formulaire simple (page unique)

À utiliser uniquement pour des formulaires courts ne nécessitant pas de navigation par étapes. Tous les champs sont affichés sur une seule page avec un bouton Soumettre en bas.

---

## 3. Étape d'introduction (stepIntro)

P-Studio gère un affichage spécial pour la première étape d'un formulaire lorsqu'elle est identifiée comme une introduction. Elle permet de présenter la démarche, les pièces requises et la durée estimée.

### Détection automatique par la plateforme

La plateforme détecte automatiquement un `stepIntro` si la clé (**key**) du **premier panel** contient le mot **intro** (ex: `stepIntro`).

### Effets visuels déclenchés par la plateforme

| Élément | Comportement |
|---|---|
| En-tête de la page | Affiche un design spécial avec le titre de la démarche et le bouton vert de démarrage **géré nativement** |
| Boutons de navigation | Précédent / Suivant cachés sur cette étape uniquement |
| Compteur d'étapes | `stepIntro` est exclu du comptage |
| Contenu | Le composant `htmlelement` est affiché sous l'en-tête |
| **Boutons manuels** | **INTERDITS** : Ne pas ajouter de bouton dans ce panel |

### JSON de référence — stepIntro

```json
{
  "type": "panel",
  "title": "Présentation de la démarche",
  "key": "stepIntro",
  "components": [
    {
      "type": "htmlelement",
      "tag": "div",
      "content": "<h2>Demande de passeport</h2><p>Cette démarche vous permet de...</p>"
    }
  ]
}
```

---

## 4. Bouton de démarrage (automatique)

Le bouton de démarrage (ex: "Commencer" ou "Effectuer ma demande") est désormais géré **exclusivement par la plateforme P-Studio**.

### Règles de conformité
- **Ne pas ajouter de bouton** dans le JSON pour l'étape d'introduction.
- P-Studio injecte automatiquement un bouton vert dans l'en-tête natif pour tout panel dont la clé contient "intro".
- Le libellé du bouton peut être configuré via les métadonnées du service ou les traductions `i18n` si un composant caché est utilisé comme référence, mais la recommandation est de **laisser la plateforme piloter l'affichage**.

---

## 5. Bloc config — Configuration par environnement

Le bloc **config** permet de définir des paramètres distincts selon l'environnement d'exécution du formulaire. Il est obligatoire pour le pré-remplissage des données, le pointage des API, et l'identification applicative.

### Les 4 environnements obligatoires

| Environnement | Usage | Caractéristique |
|---|---|---|
| `development` | Développement local du formulaire | API sur environnement local ou dev |
| `sandbox` | Tests, démo, intégration | Données fictives, sans impact production |
| `preprod` | Vérification finale avant mise en prod | Données réelles, environnement miroir |
| `production` | Environnement citoyen en production | Données réelles, API de production |

> **⚠ Règle d'implémentation**
>
> Les 4 environnements **DOIVENT** tous être présents dans le bloc `config`, même s'ils partagent les mêmes valeurs.
>
> La structure interne (`users`, `apiBaseUrl`, `appName`) doit être identique dans chaque environnement.

### Structure complète du bloc config

```json
"config": {
  "sandbox": {
    "apiBaseUrl": "https://api.sandbox.gouv.tg/api/v1/admin",
    "appName": "Sandbox",
    "users": {
      "firstName": "user.firstName",
      "lastName":  "user.lastName",
      "fullName":  "user.fullName",
      "email":     "user.email",
      "username":  "user.username",
      "userId":    "user.userId",
      "accountType": "user.accountType",
      "language":  "user.language",
      "phone":     "user.phone"
    }
  },
  "production": {
    "apiBaseUrl": "https://api.gouv.tg/api/v1/admin",
    "appName": "Production",
    "users": { /* même structure */ }
  },
  "preprod": {
    "apiBaseUrl": "https://api.preprod.gouv.tg/api/v1/admin",
    "appName": "Pré-production",
    "users": { /* même structure */ }
  },
  "development": {
    "apiBaseUrl": "https://api.dev.gouv.tg/api/v1/admin",
    "appName": "Développement",
    "users": { /* même structure */ }
  }
}
```

### Propriétés du bloc config

| Propriété | Type | Description |
|---|---|---|
| `apiBaseUrl` | String (URL) | URL de base de l'API back-office pour l'environnement concerné. Utilisable dans les champs avec `{{ config.apiBaseUrl }}`. |
| `appName` | String | Nom de l'application pour l'environnement (ex : `"Sandbox"`, `"Production"`). Informatif. |
| `users` | Object | Mapping des données de l'utilisateur connecté. Les valeurs (ex : `"user.firstName"`) sont résolues automatiquement par P-Studio. |

---

## 6. Données utilisateur — Connexion standard et e-ID

P-Studio supporte deux modes de connexion qui offrent des niveaux d'information différents sur l'utilisateur. Ces données sont injectées automatiquement dans le bloc **config.users** et accessibles via **`{{ config.users.xxx }}`** dans les champs du formulaire.

### Connexion standard (compte citoyen / entreprise)

| Chemin (`config.users`) | Valeur mappée | Description | Disponibilité |
|---|---|---|---|
| `firstName` | `user.firstName` | Prénom | Toujours disponible |
| `lastName` | `user.lastName` | Nom de famille | Toujours disponible |
| `fullName` | `user.fullName` | Nom complet | Toujours disponible |
| `email` | `user.email` | Adresse email | Toujours disponible |
| `username` | `user.username` | Identifiant de connexion | Toujours disponible |
| `userId` | `user.userId` | Identifiant interne unique | Toujours disponible |
| `accountType` | `user.accountType` | `"CITOYEN"` ou `"ENTREPRISE"` | Toujours disponible |
| `language` | `user.language` | `"fr"` ou `"en"` | Toujours disponible |
| `phone` | `user.phone` | Numéro(s) de téléphone (tableau) | Peut être vide |

### Connexion avec carte e-ID (données étendues)

Lorsque l'utilisateur s'authentifie avec sa carte d'identité électronique (e-ID), un ensemble enrichi de données est disponible dans **config.users**. Ces champs remplacent et étendent les champs standards.

| Champ e-ID | Description |
|---|---|
| `firstName_fra` / `lastName_fra` / `name_fra` | Prénom, nom de famille, nom complet (depuis la carte) |
| `dob` | Date de naissance (format ISO 8601) |
| `gender_fra` | Genre |
| `maritalStatus_fra` | Situation matrimoniale |
| `nationality_fra` | Nationalité |
| `identityNumber_fra` | Numéro d'identité nationale |
| `identityProofType_fra` | Type de pièce d'identité |
| `profession_fra` | Profession |
| `studyLevel_fra` | Niveau d'étude |
| `spokenLanguage_fra` | Langue(s) parlée(s) |
| `emailId` / `phoneNumber` | Email et téléphone enregistrés sur la carte |
| `locality_fra` / `canton_fra` / `commun_fra` | Localité, canton, commune de résidence |
| `prefecture_fra` / `region_fra` | Préfecture et région de résidence |
| `birthLocality_fra` / `birthPrefecture_fra` / `birthCommun_fra` / `birthCanton_fra` | Informations géographiques de naissance |
| `face` | Photo de l'utilisateur (base64) |

> **ℹ Bonne pratique e-ID : Verrouillage des champs**
>
> Pour les démarches nécessitant une identification forte, les données e-ID (nom, prénom, date de naissance) ne doivent pas être modifiables. Deux méthodes sont possibles :
>
> 1. **Verrouillage Statique (Simple)** : Ajouter `"disabled": true` directement dans le JSON. C'est la méthode la plus sûre pour garantir l'intégrité des données e-ID.
> 2. **Verrouillage Dynamique (Logic)** : Permet de verrouiller le champ uniquement s'il est rempli, laissant la main à l'usager en cas de donnée manquante à la source.
>
> Exemple de verrouillage dynamique via un bloc `logic` :
>
> ```json
> {
>   "type": "textfield",
>   "key": "nom",
>   "defaultValue": "{{ config.users.lastName }}",
>   "logic": [
>     {
>       "name": "Verrouillage si rempli",
>       "trigger": {
>         "type": "javascript",
>         "javascript": "result = !!data.nom;"
>       },
>       "actions": [
>         {
>           "name": "Disable",
>           "type": "property",
>           "property": { "label": "Disabled", "value": "disabled", "type": "boolean" },
>           "state": true
>         }
>       ]
>     }
>   ]
> }
> ```

---

## 7. Pré-remplissage des champs avec config

Les variables du bloc **config** sont utilisables directement dans les propriétés des composants Form.io en utilisant la syntaxe de template Nunjucks : **`{{ config.xxx }}`**. Cette résolution est effectuée par P-Studio au moment du rendu.

### Syntaxe de référence

| Variable cible | Syntaxe dans le champ | Exemple de valeur résolue |
|---|---|---|
| Données utilisateur | `{{ config.users.firstName }}` | `"Jean"` |
| URL de l'API | `{{ config.apiBaseUrl }}` | `"https://api.gouv.tg/api/v1/admin"` |
| Nom de l'application | `{{ config.appName }}` | `"Production"` |
| Données e-ID | `{{ config.users.dob }}` | `"1985-04-12"` |

### Propriétés où la syntaxe `{{ }}` fonctionne

| Propriété Form.io | Description | Compatible |
|---|---|---|
| `defaultValue` | Valeur pré-remplie au chargement du formulaire | ✔ Oui |
| `placeholder` | Texte indicatif grisé dans le champ | ✔ Oui |
| `label` | Libellé du champ | ✔ Oui |
| `content` (htmlelement) | Contenu HTML d'un composant HTML | ✔ Oui |
| `data.url` (select) | URL d'une liste dynamique — voir section 9 | ✔ Oui |
| `validate.custom` | Logique de validation personnalisée | ✔ Oui (JS) |

### Alternative : `customDefaultValue` (JavaScript)

Dans certains cas complexes, ou pour des raisons de compatibilité ascendante, il est possible d'utiliser `customDefaultValue` pour injecter directement l'objet utilisateur :

```json
"customDefaultValue": "value = (typeof user !== 'undefined' && user !== null) ? user.firstName : '';"
```

*Note : La méthode recommandée reste l'utilisation du bloc `config` pour une meilleure gestion multi-environnement.*

### Exemple complet — Champ pré-rempli et verrouillé dynamiquement

```json
{
  "type": "textfield",
  "key": "prenomDeclarant",
  "label": "Prénom",
  "defaultValue": "{{ config.users.firstName }}",
  "validate": { "required": true },
  "logic": [
    {
      "name": "Verrouillage si rempli",
      "trigger": {
        "type": "javascript",
        "javascript": "result = !!(data.prenomDeclarant && String(data.prenomDeclarant).trim().length > 0);"
      },
      "actions": [
        {
          "name": "Disable",
          "type": "property",
          "property": { "label": "Disabled", "value": "disabled", "type": "boolean" },
          "state": true
        }
      ]
    }
  ]
}
```

> **❗ Règle de verrouillage**
>
> Tout champ pré-rempli depuis `config.users` doit être protégé contre la modification accidentelle.
>
> L'utilisation de l'attribut statique `"disabled": true` est autorisée et recommandée pour les données e-ID strictes. Si vous souhaitez toutefois permettre à l'usager de compléter une donnée e-ID manquante ou vide, utilisez un bloc `logic` de verrouillage dynamique.
>
> Le trigger JS pour le verrouillage dynamique doit être robuste : `!!(data.champ && String(data.champ).trim().length > 0)`.
>
> Exception : les champs optionnels que l'utilisateur peut compléter librement (pas de verrouillage).

---

## 8. Internationalisation (i18n) — Français / Anglais

P-Studio supporte le changement de langue en temps réel (FR ↔ EN). Le mécanisme repose sur un bloc **i18n** embarqué dans le JSON du formulaire, consommé par Form.io via l'option **`i18n: schema.i18n`** passée lors de l'instanciation.

### Principe de fonctionnement

| Étape | Description |
|---|---|
| 1. Textes français | Le formulaire est conçu en français. Labels, titres, placeholders sont rédigés en FR. |
| 2. Bloc i18n | Un bloc `i18n` est ajouté au JSON. Il contient un dictionnaire `en` dont les clés sont les textes FR et les valeurs sont les traductions EN. |
| 3. Injection au rendu | Form.io résout automatiquement les traductions lorsque la langue active est `"en"`. |
| 4. Changement de langue | Le frontend appelle `form.language = "en"` ou `"fr"` pour basculer la langue sans recharger le formulaire. |

### Éléments à traduire dans le bloc i18n

| Élément | Propriété Form.io | Traduit via i18n ? |
|---|---|---|
| Titre des panels | `panel.title` | ✔ Oui |
| Libellés des champs | `component.label` | ✔ Oui |
| Placeholders | `component.placeholder` | ✔ Oui |
| Options des listes (select) | `values[].label` | ✔ Oui (clé = texte FR entier) |
| Options des boutons radio | `values[].label` | ✔ Oui |
| Messages de validation | `validate.customMessage` | ✔ Oui |
| Contenu HTML | `htmlelement.content` | ✔ Oui (via `{{ t("clé") }}`) |
| Tooltip / description | `tooltip`, `description` | ✔ Oui |

### Règles critiques i18n

- **Labels, titres, placeholders :** Doivent rester en texte français brut. Form.io recherche automatiquement la traduction dans le dictionnaire i18n. Ne jamais écrire `{{ t("xxx") }}` dans ces champs.
- **Contenu HTML (`htmlelement`) :** La syntaxe `{{ t("clé") }}` peut être utilisée dans le champ `content` uniquement, rendu par le moteur Nunjucks de Form.io.
- **Valeurs radio/select avec HTML embarqué :** La clé i18n doit être la chaîne HTML complète. La valeur i18n est la traduction HTML complète.
- **Boutons modals :** Ne pas utiliser `{{ t() }}` dans les overlays de type modal — le rendu Nunjucks n'y est pas disponible. Gérer la traduction via JavaScript.

### Structure du bloc i18n dans le JSON

```json
"i18n": {
  "en": {
    "Prénom":                    "First Name",
    "Nom de famille":            "Last Name",
    "Adresse email":             "Email address",
    "Ce champ est obligatoire":  "This field is required",
    "Célibataire":               "Single",
    "Marié(e)":                  "Married",
    "Veuf / Veuve":              "Widowed",
    "Nationalité togolaise":     "Togolese nationality",
    "Entrez votre numéro de téléphone": "Enter your phone number",
    "Informations personnelles": "Personal information",
    "Détails de la demande":     "Request details",
    "Pièces justificatives":     "Supporting documents"
  }
}
```

> **⚠ Important — i18n non lu automatiquement depuis le schéma**
>
> Form.io ne lit pas toujours le bloc `i18n` directement depuis le JSON du formulaire.
>
> Le bloc doit être passé explicitement lors de la création du formulaire :
>
> ```javascript
> Formio.createForm(element, schema, { i18n: schema.i18n, language: "fr" })
> ```
>
> Le changement de langue s'effectue avec : `form.language = "en"`

### Exemple d'utilisation dans un htmlelement

```json
{
  "type": "htmlelement",
  "tag": "div",
  "content": "<h2>{{ t('Bienvenue sur la plateforme') }}</h2>
              <p>{{ t('Cette démarche vous permet de réaliser votre demande en ligne.') }}</p>"
}
```

---

## 9. Données dynamiques via URL (pays, monnaies, listes...)

Les listes de référence (pays, monnaies, nationalités, préfectures, etc.) ne doivent **jamais** être saisies manuellement dans le formulaire. Elles sont exposées par le back-office P-Studio sous forme de deux types d'endpoints et récupérées dynamiquement par Form.io.

### Types d'endpoints back-office

| Type | Description | Cas d'usage |
|---|---|---|
| **Statics** | Données de référence immuables ou rarement modifiées. Exposées par le back-office et mises en cache. | Liste de pays, monnaies, nationalités, genres, situations matrimoniales |
| **Dynamics** | Données récupérées en temps réel depuis une source métier. Rechargées à chaque affichage du formulaire. | Préfectures, communes, cantons, listes métier spécifiques à une démarche |

### Configuration d'un composant Select avec URL dynamique

Dans Form.io Builder, pour un composant de type **Select** :

1. Onglet Data → Type de données : **URL**
2. Champ **Data Source URL** : saisir l'URL de l'endpoint (les variables config sont supportées).
3. Champ **Value Property** : nom de la propriété JSON utilisée comme valeur soumise (ex : `code`).
4. Champ **Item Template** : template HTML d'affichage de chaque option (ex : `<span>{{ item.label }}</span>`).

```json
{
  "type": "select",
  "key": "pays",
  "label": "Pays",
  "dataSrc": "url",
  "data": {
    "url": "{{ config.apiBaseUrl }}/references/countries",
    "headers": [
      { "key": "Accept", "value": "application/json" }
    ]
  },
  "valueProperty": "code",
  "template": "<span>{{ item.label }}</span>",
  "validate": { "required": true }
}
```

> **✔ Avantage de la variable `config.apiBaseUrl`**
>
> En utilisant `{{ config.apiBaseUrl }}` dans l'URL, le composant pointe automatiquement vers le bon back-office selon l'environnement actif (sandbox, production, etc.).
>
> Cela évite de dupliquer le formulaire pour chaque environnement.

### Listes à toujours charger via URL (jamais en dur)

| Liste | Endpoint recommandé | Type |
|---|---|---|
| Pays | `/references/countries` | Static |
| Monnaies | `/references/currencies` | Static |
| Nationalités | `/references/nationalities` | Static |
| Situations matrimoniales | `/references/marital-statuses` | Static |
| Niveaux d'étude | `/references/study-levels` | Static |
| Régions / Préfectures | `/references/regions`, `/references/prefectures` | Dynamic |
| Communes / Cantons | `/references/communes`, `/references/cantons` | Dynamic |
| Types de pièces d'identité | `/references/identity-types` | Static |

---

## 10. Contrôles et validations sur les champs

Form.io offre plusieurs mécanismes de validation natifs et personnalisables. Toutes les règles de validation sont définies dans le bloc **`"validate": {}`** du composant.

### Validations natives Form.io

| Règle | Propriété JSON | Exemple |
|---|---|---|
| Champ obligatoire | `"required": true` | `{ "validate": { "required": true } }` |
| Longueur minimale | `"minLength": N` | `{ "validate": { "minLength": 3 } }` |
| Longueur maximale | `"maxLength": N` | `{ "validate": { "maxLength": 100 } }` |
| Valeur minimale (nombre) | `"min": N` | `{ "validate": { "min": 0 } }` |
| Valeur maximale (nombre) | `"max": N` | `{ "validate": { "max": 150 } }` |
| Expression régulière | `"pattern": "regex"` | `{ "validate": { "pattern": "^[0-9]{8}$" } }` |
| Message d'erreur personnalisé | `"customMessage": "texte"` | `{ "validate": { "customMessage": "Format invalide" } }` |

### Validation personnalisée (JavaScript)

Pour des règles complexes, utiliser la propriété **`"custom"`** qui accepte du JavaScript. La variable **`input`** contient la valeur saisie. Retourner **`true`** si la validation passe, ou un message d'erreur string sinon.

```json
{
  "validate": {
    "required": true,
    "custom": "valid = (input && input.length >= 8) ? true : 'Le numéro doit contenir au moins 8 caractères';",
    "customMessage": "Valeur invalide"
  }
}
```

### Logique conditionnelle — Affichage / Masquage de champs

La propriété **`"conditional"`** permet d'afficher ou masquer un champ selon la valeur d'un autre champ.

```json
{
  "type": "textfield",
  "key": "autreNationalite",
  "label": "Précisez la nationalité",
  "conditional": {
    "show": true,
    "when": "nationalite",
    "eq": "autre"
  }
}
```

### Logique avancée avec JSON Logic

Pour des conditions impliquant plusieurs champs, utiliser **`"customConditional"`** avec une expression JavaScript :

```json
{
  "customConditional": "show = (data.typeDocument === 'passeport' && data.age >= 18);"
}
```

### Calcul automatique de valeur

La propriété **`"calculateValue"`** permet de calculer automatiquement la valeur d'un champ à partir d'autres champs :

```json
{
  "type": "number",
  "key": "montantTotal",
  "label": "Montant total (FCFA)",
  "calculateValue": "value = data.nombreExemplaires * data.prixUnitaire;",
  "disabled": true
}
```

---

## 11. Le Récapitulatif Intelligent (Composant HTML)

Il est strictement **interdit** de recréer manuellement une vue "lecture seule" des champs à la fin du formulaire. À la place, vous **devez** utiliser le composant "Récapitulatif Intelligent" qui génère dynamiquement un tableau HTML de toutes les saisies.

### Fonctionnement du script
1. **Collecte** : Utilise `utils.eachComponent` pour balayer le formulaire.
2. **Filtrage** : Ignore les boutons, les panels vides, et les clés exclues (ex: `luEtApprouve`).
3. **Résolution** : Extrait les labels des `select` et formate les dates `datetime`.
4. **Injection** : Génère une table HTML stylisée dans un div ciblé (`id="recapDisplay"`).

### JSON de référence (À placer dans le dernier Panel)

```json
{
  "label": "HTML",
  "tag": "div",
  "attrs": [{ "attr": "id", "value": "recapDisplay" }],
  "refreshOnChange": false,
  "key": "htmlRecapitulatifFinal",
  "logic": [
    {
      "name": "logiqueConstruction",
      "trigger": { "type": "javascript", "javascript": "result = true;" },
      "actions": [
        {
          "name": "actionJS",
          "type": "customAction",
          "customAction": "const recapDiv = document.getElementById(\"recapDisplay\"); let list_of_datagrid = []; let data_stock = []; const exclude = [\"button\", \"file\", \"container\", \"panel\", \"datagrid\"]; const excludeKeys = [\"luEtApprouve\"]; const includesLabelForSelect = [\"libelle\", \"label\"]; utils.eachComponent(form.components, (component, path) => { /* ... Logique de collecte ... */ }, false); /* ... Construction HTML ... */ recapDiv.innerHTML = ourTable;"
        }
      ]
    }
  ],
  "type": "htmlelement"
}
```

> **ℹ Organisation finale du formulaire**
>
> La structure doit toujours se conclure par un panel "Récapitulatif et soumission" contenant ce composant, suivi d'une case à cocher de certification. **Aucun bouton Submit** ne doit être ajouté manuellement.

---

## 12. Actions sur le formulaire (calcul de coûts & soumission)

Les actions permettent de définir ce que P-Studio fait lorsque l'utilisateur soumet le formulaire. Deux actions principales sont à configurer : le calcul des coûts de service et la soumission dans la queue de traitement.

### Action 1 — Calculate Costs (Calcul des frais de service)

Cette action est obligatoire pour toute démarche payante. Elle calcule le montant dû avant soumission et l'injecte dans la payload de la demande.

#### Mode : Prix fixe

À utiliser lorsque le tarif de la démarche est identique pour tous les usagers, indépendamment des données saisies.

| Paramètre | Valeur | Description |
|---|---|---|
| Mode de tarification | Prix fixe | Montant invariable |
| Montant | Ex : `5000` | Valeur en FCFA (ou devise locale) |
| Devise | `XOF` | Code ISO 4217 |

#### Mode : Champ dynamique du formulaire

À utiliser lorsque le tarif dépend des saisies de l'usager (ex : nombre d'exemplaires, durée, type de prestation). Le montant est calculé via une expression JavaScript référençant les données du formulaire.

| Paramètre | Valeur | Description |
|---|---|---|
| Mode de tarification | Champ dynamique | Montant calculé |
| Expression | Ex : `data.nbExemplaires * 2500` | Expression JS utilisant les champs du formulaire (via `data.xxx`) |
| Champ de résultat | Ex : `montantTotal` | Clé du champ Form.io contenant le résultat affiché |

```javascript
// Exemple d'expression de calcul dynamique
// Accéder aux données via data.nomDuChamp
data.nombreExemplaires * 2500 + (data.urgence === true ? 5000 : 0)
```


### Action 2 — Publish to RabbitMQ (Soumission dans la queue)

Cette action est obligatoire sur tout formulaire. Elle transmet la demande soumise au moteur de workflows via la queue RabbitMQ de P-Studio.

| Paramètre de configuration | Valeur fixe | Description |
|---|---|---|
| Routing Key | `submissions.topic` | Clé de routage RabbitMQ — ne pas modifier |
| Queue | `workflows-engine.main.queue` | Nom de la queue de réception — ne pas modifier |
| Exchange type | `topic` | Type d'échange RabbitMQ |
| Durabilité | `true` | La queue persiste en cas de redémarrage du broker |



#### Configuration JSON (Action)

```json
{
  "name": "publishToRabbitMQ",
  "type": "rabbitmq",
  "topic": "submissions.topic",
  "payload": "{{ submission.data }}"
}
```

> **⚠ Attention sur le Payload**
>
> Ne jamais utiliser `submission.topic` comme payload. L'expression `{{ submission.data }}` est la seule capable de transmettre l'intégralité des champs saisis au moteur BPMN.


> **ℹ Ordre de configuration des actions**
>
> 1. Configurer **"Calculate Costs"** en premier (si la démarche est payante).
> 2. Configurer **"Publish to RabbitMQ"** en second.
>
> L'action de publication est toujours la dernière dans la chaîne. Elle transmet la payload enrichie (avec les coûts calculés) au moteur de workflows.

### Récapitulatif des actions par type de démarche

| Type de démarche | Calculate Costs | Publish to RabbitMQ |
|---|---|---|
| Démarche gratuite | ✘ Non requis | ✔ Obligatoire |
| Démarche à prix fixe | ✔ Mode : Prix fixe | ✔ Obligatoire |
| Démarche à tarification variable | ✔ Mode : Champ dynamique | ✔ Obligatoire |

---

## 13. Règles fondamentales — À faire / À ne pas faire

### ✔ À faire — Checklist de l'intégrateur

1. **Mode Wizard :** Toujours définir `"display": "wizard"` pour les démarches. Chaque étape est un Panel avec `type`, `title` et `key` uniques.
2. **stepIntro :** Premier panel avec une `key` contenant `"intro"` (recommandé : `stepIntro`). Contient uniquement le `htmlelement` descriptif. Aucun bouton manuel ne doit être ajouté.
4. **Bloc config complet :** Définir les 4 environnements (`development`, `sandbox`, `preprod`, `production`) avec la même structure `users` dans chacun.
5. **Placement du config :** Toujours dans `content`, au même niveau que `components`. Jamais dans `settings`.
6. **Champs pré-remplis :** Verrouiller les champs e-ID de manière statique (`"disabled": true`) ou dynamique via un bloc `logic` (trigger JS : `!!(data.champ && String(data.champ).trim().length > 0)`) pour tout champ pré-rempli depuis `config.users`.
7. **Données de référence :** Toujours charger les listes (pays, monnaies, etc.) via URL pointant sur le back-office. Utiliser `{{ config.apiBaseUrl }}`.
8. **i18n :** Concevoir le formulaire en français. Fournir le bloc `i18n` avec les traductions anglaises de tous les textes visibles.
9. **Récapitulatif Intelligent :** Tout formulaire doit se terminer par un panel contenant le composant `htmlelement` de récapitulation automatique (Section 11).
10. **Actions :** Configurer `Calculate Costs` (si payant) puis `Publish to RabbitMQ` avec les paramètres normalisés.
11. **Clés (`key`) uniques :** Chaque composant doit avoir une `key` unique dans le formulaire. Utiliser des noms explicites en camelCase.

### ✘ À ne pas faire — Erreurs fréquentes

> **✕ Boutons de navigation**
>
> Ne jamais créer de boutons Précédent, Suivant, Annuler ou Soumettre — P-Studio les fournit.
>
> Les boutons natifs Formio sont désactivés et cachés par la plateforme.

---

> **✕ Barre de progression et onglets**
>
> Ne pas utiliser le mode `"Tabs"` ni la barre de progression native de Formio (`breadcrumbSettings`).
>
> P-Studio gère sa propre barre de progression basée sur le nombre de panels.

---

> **✕ Syntaxe de template incorrecte**
>
> Ne jamais écrire `{{ users.firstName }}` — la syntaxe correcte est `{{ config.users.firstName }}`.
>
> Ne pas utiliser `{{ t() }}` dans les champs `label`, `title`, `values[].label` ou `customMessage`.
>
> Ne jamais omettre les doubles accolades ni le préfixe `config.`.

---

> **✕ Données en dur dans le formulaire**
>
> Ne jamais saisir manuellement des listes de pays, monnaies, nationalités ou toute autre donnée de référence.
>
> Toujours récupérer ces données depuis les endpoints back-office via URL.

---

> **✕ Config mal placé ou incomplet**
>
> Ne jamais placer le bloc `config` dans `settings`.
>
> Ne jamais omettre un des 4 environnements dans le bloc `config`.

---

## 14. Débogage et diagnostic

### Accès aux logs de la plateforme

Ouvrir les outils développeur du navigateur (F12) → onglet **Console**. Filtrer les messages avec les préfixes suivants :

| Préfixe de log | Module | Ce qu'il indique |
|---|---|---|
| `[EnvConfig]` | Résolution de la config | Chargement et résolution du bloc `config` par environnement |
| `[FormIoService]` | Rendu du formulaire | Résolution des templates `{{ }}` dans les champs |
| `[i18n]` | Internationalisation | Chargement des traductions et changement de langue |
| `[RabbitMQ]` | Soumission | Envoi de la payload vers la queue (statut, erreurs) |

### Messages de console attendus (formulaire correctement configuré)

```
[EnvConfig] 1. Config brute trouvée dans le formulaire: {sandbox: {...}, ...}
[EnvConfig] 2. Environnement détecté: "development"
[EnvConfig] 3. Config résolue pour "development": {apiBaseUrl: "...", users: {...}}
[EnvConfig] 6. Résolution: firstName = "user.firstName" → "Jean"
[EnvConfig] 7. ✅ Config users résolue: {firstName: "Jean", ...}
[FormIoService] 12. Template résolu: prenomDeclarant.defaultValue = "{{ config.users.firstName }}" → "Jean"
```

### Table de diagnostic — Problèmes courants

---

## 15. Convention de nommage des livrables (Standard ATD)

Afin d'assurer une gestion documentaire cohérente sur la plateforme, tous les fichiers livrables d'un service doivent suivre la convention : **`[type]-[nom-du-service].[ext]`**.

| Type de livrable | Convention de nommage | Exemple |
|---|---|---|
| **Formulaire Form.io** | `formio-[nom-service].json` | `formio-quittance-loyer.json` |
| **Processus BPMN** | `bpmn-[nom-service].bpmn` | `bpmn-quittance-loyer.bpmn` |
| **Spécifications (SRS)** | `srs-[nom-service].md` | `srs-quittance-loyer.md` |
| **Cartographie AS-IS** | `as-is-[nom-service].md` | `as-is-quittance-loyer.md` |
| **Cartographie TO-BE** | `to-be-[nom-service].md` | `to-be-quittance-loyer.md` |
| **Pipeline YAML** | `pipeline-[nom-service].yaml` | `pipeline-quittance-loyer.yaml` |
| **Plan de Tests** | `tests-[nom-service].md` | `tests-quittance-loyer.md` |
| **Manuel Utilisateur** | `manuel-[nom-service].md` | `manuel-quittance-loyer.md` |
| **PV de Recette** | `pv-recette-[nom-service].md` | `pv-recette-quittance-loyer.md` |

> [!IMPORTANT]
> Cette règle doit être appliquée dès la création des fichiers pour faciliter l'indexation et la recherche transverse par les agents et les administrateurs de la plateforme.

| Symptôme observé | Cause probable | Solution |
|---|---|---|
| `{{ config.users.X }}` affiché tel quel (non résolu) | Le bloc `config` n'est pas dans `content` | Vérifier que `config` est au même niveau que `components` dans `content` |
| Pas de bouton vert sur la page d'intro | Le panel n'a pas la clé "intro" | Renommer la clé du premier panel en `"stepIntro"` |
| L'intro n'est pas détectée (pas de design spécial) | La `key` du premier panel ne contient pas `"intro"` | Renommer : `"key": "stepIntro"` |
| Pas de navigation Précédent/Suivant | Le mode d'affichage n'est pas wizard | Vérifier `"display": "wizard"` dans `content` |
| Champ pré-rempli mais modifiable | Le bloc `logic` de verrouillage dynamique n'est pas configuré | Ajouter un bloc `logic` avec trigger JS `!!(data.champ && String(data.champ).trim().length > 0)` qui désactive le champ |
| Valeur pré-remplie vide | Le mapping dans `users` est incorrect | Vérifier le chemin `user.xxx` dans le bloc `users` du `config` |
| Liste déroulante vide | URL de l'endpoint inaccessible ou mal formée | Vérifier l'URL et la résolution de `{{ config.apiBaseUrl }}` |
| Traductions non appliquées | Le bloc `i18n` n'est pas passé en option à `Formio.createForm()` | Passer explicitement `{ i18n: schema.i18n, language: "fr" }` |
| Soumission sans traitement | Action `Publish to RabbitMQ` non configurée ou topic incorrect | Vérifier la présence du bloc `actions` et le topic `"submissions.topic"` |
| Calcul de coûts non déclenché | Action `Calculate Costs` non configurée | Configurer l'action `Calculate Costs` avant l'action RabbitMQ dans le tableau `actions` |

---

## Annexe — JSON de référence complet

*Le JSON ci-dessous illustre la structure complète d'un formulaire de démarche avec toutes les configurations requises : `stepIntro`, `startButton`, `config` multi-environnements, pré-remplissage, champ dynamique, `i18n` et validations.*

```json
{
  "title": "Titre du Formulaire",
  "name": "nomForm",
  "type": "form",
  "display": "wizard",
  "i18n": {
    "en": {
      "Présentation":                 "Presentation",
      "Informations personnelles":    "Personal Information",
      "Prénom":                       "First Name",
      "Nom de famille":               "Last Name",
      "Adresse email":                "Email address",
      "Commencer ma demande":         "Start my request",
      "Ce champ est obligatoire":     "This field is required"
    }
  },
  "config": {
    "sandbox": {
      "apiBaseUrl": "https://api.sandbox.gouv.tg/api/v1/admin",
      "appName": "Sandbox",
      "users": {
        "firstName":   "user.firstName",
        "lastName":    "user.lastName",
        "fullName":    "user.fullName",
        "email":       "user.email",
        "username":    "user.username",
        "userId":      "user.userId",
        "accountType": "user.accountType",
        "language":    "user.language",
        "phone":       "user.phone"
      }
    },
    "production": {
      "apiBaseUrl": "https://api.gouv.tg/api/v1/admin",
      "appName": "Production",
      "users": { /* même mapping que sandbox */ }
    },
    "preprod": {
      "apiBaseUrl": "https://api.preprod.gouv.tg/api/v1/admin",
      "appName": "Pré-production",
      "users": { /* même mapping */ }
    },
    "development": {
      "apiBaseUrl": "https://api.dev.gouv.tg/api/v1/admin",
      "appName": "Développement",
      "users": { /* même mapping */ }
    }
  },
  "components": [
    {
      "type": "panel",
      "key": "stepIntro",
      "title": "Présentation",
      "components": [
        {
          "type": "htmlelement",
          "tag": "div",
          "content": "<h2>{{ t('Bienvenue') }}</h2><p>Description de la démarche...</p>"
        }
      ]
    },
    {
      "type": "panel",
      "key": "stepIdentite",
      "title": "Informations personnelles",
      "components": [
        {
          "type": "textfield",
          "key": "prenom",
          "label": "Prénom",
          "defaultValue": "{{ config.users.firstName }}",
          "disabled": true,
          "validate": { "required": true }
        },
        {
          "type": "select",
          "key": "nationalite",
          "label": "Nationalité",
          "dataSrc": "url",
          "data": {
            "url": "{{ config.apiBaseUrl }}/references/nationalities"
          },
          "valueProperty": "code",
          "template": "<span>{{ item.label }}</span>",
          "validate": { "required": true }
        }
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

*P-Studio — Plateforme de Conception et Publication des Workflows et Formulaires*

*Ce document est à usage exclusif des intégrateurs. Pour toute question technique, contacter l'équipe plateforme.*
