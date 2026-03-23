# Guide Complet : Validation et Logique des Champs dans Form.io

Ce guide ultra-détaillé recense l'ensemble des mécanismes de validation disponibles dans Form.io, allant des attributs basiques aux logiques avancées basées sur JavaScript et JSONLogic. Il est conçu pour servir de référence lors de l'intégration des règles métier dans l'écosystème P-Studio et XFlow.

---

## 1. L'Objet de Validation Basique (`validate`)

Chaque composant Form.io peut déclarer un objet `"validate"` contenant les attributs suivants :

### A. Validations Textuelles et de Longueur
*   **`required`** (booléen) : Rend le champ obligatoire. La soumission est bloquée si ce champ est laissé vide.
*   **`minLength`** (entier) : Le nombre minimum de caractères que l'utilisateur doit saisir (ex: 8 pour un numéro local).
*   **`maxLength`** (entier) : Le nombre maximum de caractères autorisés. Le composant empêche souvent la saisie au-delà de cette limite.
*   **`minWords`** / **`maxWords`** (entiers) : Limite la validation au nombre de mots (utile pour les champs de type *Text Area*).
*   **`pattern`** (chaine) : Expression régulière (Regex) permettant de forcer un format spécifique.
    *   *Exemple (Code Postal Togolais)* : `"^BP[0-9]{4}$"`

### B. Validations Numériques et Temporelles
*   **`min`** (nombre / chaine) : Fixe la valeur minimale. S'applique aux `number` et aux `datetime` (ex : `"2020-01-01"`).
*   **`max`** (nombre / chaine) : Fixe la valeur maximale.
*   **`strictDateValidation`** (booléen) : S'assure (notamment pour l'affichage de calendrier) que la valeur d'entrée est strictement une date valide selon le masque temporel.

### C. Validations par Sélection
*   **`minSelectedCount`** / **`maxSelectedCount`** (entiers) : Utilisé pour les composants `select` avec la propriété `"multiple": true` ou pour les `datagrid`. Définit le nombre d'éléments qu'on peut/doit sélectionner.

---

## 2. Personnalisation des Messages d'Erreur (`errors` et `customMessage`)

Plutôt que d'afficher les messages système génériques de Form.io (ex: *"nom is required"*), deux mécanismes permettent de localiser ou redéfinir les erreurs :

1.  **Le dictionnaire `errors`** : Il est recommandé dans P-Studio.
    ```json
    "validate": { "required": true, "maxLength": 50 },
    "errors": {
      "required": "Le nom de famille est strictement obligatoire.",
      "maxLength": "Le texte est trop long (50 max)."
    }
    ```
2.  **`customMessage`** : Message global qui écrase toute erreur issue des validations standards d'un composant. Si la validation échoue (peu importe la raison), c'est ce message qui s'affiche.
    ```json
    "validate": {
      "required": true,
      "customMessage": "L'entrée de ce champ est invalide ou manquante."
    }
    ```

---

## 3. Comportement de Déclenchement (`validateOn`)

Par défaut, Form.io valide les champs à chaque frappe du clavier (`"change"`). Ceci peut dégrader l'expérience utilisateur ou surcharger l'interface d'erreurs prématurées. 

*   **`"validateOn": "change"`** (Défaut) : L'erreur apparaît en temps réel dès le premier caractère.
*   **`"validateOn": "blur"`** (Recommandé P-Studio) : L'erreur n'apparaît que lorsque le curseur quitte le champ. C'est l'approche standard en matière d'ergonomie, notamment pour les mots de passe ou les champs complexes (email, numéro de SIRET).
*   **`"validateOn": "submit"`** : La validation ne se lance que si l'utilisateur appuie sur le bouton "Soumettre". Utile pour les checkboxes comme *"Je certifie sur l'honneur"*.

---

## 4. Validations Avancées : JavaScript (`custom`)

L'attribut `"custom"` permet d'injecter du code JavaScript exécuté côté client pour évaluer la validité du champ.
*   La variable `valid` agit comme "return".
*   Affectez `valid = true` si l'entrée est bonne.
*   Affectez `valid = "Votre message d'erreur"` (une string) si l'entrée est fausse.

**Variables disponibles dans l'environnement JS Custom :**
*   `input` : La valeur actuelle que l'usager vient de saisir.
*   `data` : Contient l'objet complet avec toutes les valeurs du formulaire (`data.champ1`, `data.champ2`).
*   `instance` : L'instance Form.io complète du composant, permettant d'appeler ses méthodes internes.

### Exemples JavaScript `custom`
*Comparaison entre deux champs (ex: Confirmer le mot de passe)* :
```javascript
"custom": "valid = (input === data.motDePasse) ? true : 'Les mots de passe ne correspondent pas.';"
```
*Validation d'âge basée sur la date de naissance (Superieur à 18 ans)* :
```javascript
"custom": "var birthDate = new Date(input); var today = new Date(); var age = today.getFullYear() - birthDate.getFullYear(); var m = today.getMonth() - birthDate.getMonth(); if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) { age--; } valid = (age >= 18) ? true : 'Vous devez être majeur pour continuer.';"
```

---

## 5. Validations JSONLogic (`json`)

Pour des questions de portabilité et de sécurité (éviter l'injection JS côté serveur si le JSON navigue), Form.io supporte les règles **JSONLogic**. Il s'agit d'un langage déclaratif sous forme de JSON décrivant une logique d'évaluation.

*Si le résultat du bloc JSON vaut `true`, la validation est réussie.*

### Exemple JSONLogic
*Valider que le salaire d'entrée (input) est bien supérieur à 50000 :*
```json
"validate": {
  "json": {
    ">": [
      { "var": "data.salaire" },
      50000
    ]
  }
}
```

---

## 6. Interaction avec la Logique Conditionnelle (Hidden state)

Un concept crucial de Form.io réside dans la propriété **`clearOnHide`** et les dépendances temporelles de bout de validation :

1.  **Composants cachés (`conditional: { "show": false... }`)** :
    Par nature, Form.io **ignore** la validation de tout composant qui est actuellement masqué (hidden) pour l'utilisateur. Ainsi, si un champ X est requis, mais qu'un composant parent le masque, le formulaire pourra quand même être soumis.
2.  **`clearOnHide` (Défaut : `true`)** :
    Dès qu'un composant devient invisible (via logic ou conditional), sa valeur interne est immédiatement vidée (`null`). Ceci est essentiel pour éviter de transmettre au back-office des données orphelines (ex: un champ "Précisez votre maladie" alors que l'utilisateur a redécoché la case "Êtes-vous malade ?").
3.  **`validateWhenHidden`** (Propriété racine) :
    Il est possible de forcer Form.io à valider un sous-arbre de champs invisibles (rarement utilisé, mais existant) en déclarant `"validateWhenHidden": true` sur le champ source, rendant active l'obligation de s'y conformer.

---

## 7. Propriété Unique (`unique`)

Cette validation nécessite un lien avec l'API backend (souvent le serveur Form.io natif) :
*   **`"unique": true`** demande au moteur d'interroger la base de données de manière asynchrone pour vérifier si la valeur saisie existe déjà dans d'autres soumissions du même formulaire (ex: adresse email ou numéro SIRET exclusif).

*Dans le contexte P-Studio / XFlow, cette fonctionnalité nécessite que l'API de validation supporte l'appel unifié asynchrone, rendant l'utilisation des custom JS ou d'un worker Camunda plus fréquent pour l'unicité.*

---

## Checklist Récapitulative d'Architecture pour Formio

*   [ ] Verrouiller les champs e-ID de manière statique (`"disabled": true`) ou dynamique via un bloc `logic` de type trigger JS.
