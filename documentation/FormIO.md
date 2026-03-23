# Documentation Technique Form.io (Référence Exhaustive)

Ce document est la référence technique absolue pour la plateforme **Form.io**. Il couvre le schéma JSON, la logique de composants, les validations, l'API REST et l'intégration SDK.

---

## 1. Structure du Schéma de Formulaire (Root Object)

L'objet racine définit le conteneur du formulaire et ses métadonnées globales.

| Propriété | Type | Description |
| :--- | :--- | :--- |
| `title` | String | Titre d'affichage (ex: "Demande de Visa"). |
| `name` | String | Identifiant machine unique (slug camelCase). |
| `path` | String | URL relative pour l'accès API (ex: "visa-form"). |
| `display` | String | Mode de rendu : `form`, `wizard`, ou `pdf`. |
| `type` | String | `form` (données transactionnelles) ou `resource` (entité réutilisable). |
| `components` | Array | Tableau d'objets définissant les champs. |
| `tags` | Array | Liste de tags pour l'organisation et le filtrage. |
| `access` | Array | Règles d'accès au formulaire (Role-Based Access Control). |
| `submissionAccess` | Array | Règles d'accès aux données soumises. |
| `owner` | String | ID de l'utilisateur propriétaire du formulaire. |
| `machineName` | String | Identifiant unique du projet/formulaire (utilisé en inter-projets). |
| `settings` | Object | Paramètres spécifiques (ex: `pdftk` pour les PDFs). |

---

## 2. Anatomie Exhaustive d'un Composant

Chaque composant dans `components` partage un ensemble de propriétés fondamentales.

### Propriétés de Base & Affichage
- **`type`** : Type technique (`textfield`, `select`, `datagrid`, etc.).
- **`key`** : Clé API unique pour stocker la donnée. **Indispensable**.
- **`label`** : Texte de l'étiquette.
- **`placeholder`** : Texte d'aide à l'intérieur du champ.
- **`input`** : `true` si le champ collecte une donnée, `false` sinon (ex: `htmlelement`).
- **`hidden`** : Masque le composant au chargement.
- **`tableView`** : Affiche ou non la colonne dans la liste des soumissions.
- **`modalEdit`** : Ouvre une fenêtre modale pour l'édition du champ.
- **`prefix` / `suffix`** : Texte ou icône ajouté avant/après l'input.
- **`customClass`** : Classe CSS personnalisée à appliquer sur le wrapper.
- **`description`** : Texte d'aide affiché sous le champ.
- **`tooltip`** : Texte d'aide affiché au survol d'une icône info.

### Persistance & Données
- **`defaultValue`** : Valeur initiale (String, Number, Array ou Object).
- **`persistent`** : Si `false`, la donnée n'est pas stockée en base (champ temporaire).
- **`protected`** : Si `true`, la valeur est masquée dans les requêtes API GET.
- **`multiple`** : Transforme le champ en un tableau de valeurs (UI dynamique pour ajouter des entrées).
- **`clearOnHide`** : Supprime la valeur si le champ devient masqué via une condition.
- **`dbIndex`** : Crée un index MongoDB sur ce champ (Enterprise).
- **`encrypted`** : Chiffrement côté serveur (Enterprise).

---

## 3. Système de Validation

Form.io exécute les validations côté client (UX) et côté serveur (Sécurité).

| Règle | Type | Description |
| :--- | :--- | :--- |
| `required` | Boolean | Le champ ne peut être vide. |
| `minLength` / `maxLength` | Number | Limites de caractères (Text). |
| `min` / `max` | Number | Limites numériques ou dates. |
| `step` | Number | Incrément autorisé (ex: `0.5`). |
| `pattern` | String | Expression régulière (Regex). |
| `unique` | Boolean | Vérifie l'unicité dans toute la base de données (Server-side). |
| `custom` | String | Script JS de validation : `valid = (input > 10) ? true : 'Trop petit';`. |
| `json` | Object | Logique JSONLogic pour la validation. |
| `validateWhenHidden` | Boolean | Continue de valider même si le champ est masqué. |
| `strictDate` | Boolean | Force un format de date strict. |

**Exemple de Validation Complexe :**
```json
{
  "key": "age",
  "type": "number",
  "validate": {
    "required": true,
    "min": 18,
    "customMessage": "Vous devez être majeur pour ce service.",
    "custom": "valid = (input < 120) ? true : 'Âge irréel';"
  }
}
```

---

## 4. Logique Dynamique & Calculs

### Propriété `conditional` (Affichage Simple)
```json
"conditional": {
  "show": true,
  "when": "checkboxKey",
  "eq": "true"
}
```

### Propriété `logic` (Actions Complexes)
- **Triggers** : `simple`, `javascript`, `json`, `event`.
- **Actions** : `property`, `value`, `mergeComponentSchema`, `customAction`.

**Exemple de Logique Multi-Actions :**
```json
{
  "logic": [
    {
      "name": "Activation Professionnelle",
      "trigger": {
        "type": "javascript",
        "javascript": "result = (data.statut === 'pro');"
      },
      "actions": [
        {
          "name": "Rendre Requis",
          "type": "property",
          "property": { "label": "validate.required", "type": "boolean" },
          "state": true
        },
        {
          "name": "Changer Label",
          "type": "property",
          "property": { "label": "label", "type": "string" },
          "text": "Numéro SIRET"
        }
      ]
    }
  ]
}
```

### Propriété `calculateValue`
Variables injectées dans le contexte : `data`, `row`, `rowIndex`, `value`, `instance`, `submission`, `form`, `_` (Lodash), `utils`.

**Exemple de Calcul (Calculated Value) :**
```json
{
  "key": "total",
  "calculateValue": "value = data.prixUnitaire * data.quantite * (1 + (data.tva / 100));"
}
```

---

## 5. Focus sur les Composants Complexes

### `Select` (API Dynamique)
Exemple de configuration avec source URL et template d'affichage personnalisé :
```json
{
  "type": "select",
  "key": "ville",
  "label": "Ville",
  "dataSrc": "url",
  "data": {
    "url": "https://api.gouv.tg/villes?search={{ data.recherche }}",
    "headers": [{ "key": "Authorization", "value": "Bearer {{ data.token }}" }]
  },
  "valueProperty": "id",
  "template": "<span><strong>{{ item.nom }}</strong> ({{ item.code_postal }})</span>",
  "selectThreshold": 0.3
}
```

### `EditGrid` (Tableaux avec Templates)
Utilise Lodash pour personnaliser l'aperçu des lignes :
```json
{
  "type": "editgrid",
  "key": "enfants",
  "templates": {
    "header": "<div class='row'><b>Prénom</b></div>",
    "row": "<div class='row'>{{ row.prenomEnfant }} (Âge: {{ row.ageEnfant }})</div>",
    "footer": "Total enfants: {{ value.length }}"
  },
  "components": [
    { "type": "textfield", "key": "prenomEnfant", "label": "Prénom" },
    { "type": "number", "key": "ageEnfant", "label": "Âge" }
  ]
}
```

### `File` (Stockage S3)
```json
{
  "type": "file",
  "key": "pieceJointe",
  "label": "Document (PDF)",
  "storage": "s3",
  "filePattern": "application/pdf",
  "maxSize": "10MB",
  "multipart": true
}
```

### `Wizard` (Navigation)
```json
{
  "display": "wizard",
  "breadcrumbSettings": { "clickable": true },
  "buttonSettings": {
    "previous": { "label": "Étape Précédente" },
    "next": { "label": "Continuer", "customClass": "btn btn-primary" }
  }
}
```

---

## 6. Intégration SDK & API

### Rendu JavaScript (formio.js)
```javascript
Formio.createForm(document.getElementById('formio'), schemaJson, {
  i18n: { "fr": { "Submit": "Valider mon dossier" } },
  readOnly: false,
  noAlerts: true
}).then(form => {
  form.on('submit', (sub) => alert('ID: ' + sub._id));
});
```

### API REST : Filtrage Avancé
Exemple de requête GET filtrée :
`GET /form/:id/submission?data.nom__regex=/dupont/i&limit=10&sort=-created`

---

## 7. Exemples Pratiques (Cas d'Usage)

### Cas 1 : Filtrage Dynamique de Select (Choices.js)
Filtrer le second Select selon le premier via une `Logic` :
```json
{
  "key": "sousCategorie",
  "logic": [{
    "trigger": { "type": "simple", "when": "categorie", "eq": "auto" },
    "actions": [{
      "type": "property",
      "property": { "label": "data.url", "type": "string" },
      "text": "https://api.tg/options?cat=auto"
    }]
  }]
}
```

### Cas 2 : Manipulation du DOM (Sidebar Collante)
Injection JS via `calculateValue` pour fixer une sidebar :
```javascript
if (!window.stickyApplied) {
  var el = document.getElementById('sidebar-info');
  if (el) { el.style.position = 'sticky'; el.style.top = '10px'; window.stickyApplied = true; }
}
```

### Cas 3 : Validation Inter-Champs
Vérifier que la date de fin est après la date de début :
```javascript
valid = (new Date(input) > new Date(data.dateDebut)) ? true : 'La fin doit être après le début';
```

---
*Référence technique enrichie — ATD Digital Services.*