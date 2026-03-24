# Workflows — Mode d'emploi

Ce dossier contient les workflows de production des livrables ATD. Chaque workflow est un fichier Markdown structuré qui guide l'agent IA étape par étape.

## Workflow disponible

| Fichier | Description |
|---------|-------------|
| `digitalisation-service-public.md` | Digitalisation complète d'un service public (AS-IS → TO-BE → SRS → Form.io → BPMN → Tests) |

---

## Séquence des étapes

```
STEP:0.5  Pipeline YAML + STATUS.md
STEP:1    Recueil d'informations
STEP:2    Cartographie AS-IS
STEP:3    Cartographie TO-BE
   ┃
 GATE:1   ✋ Validation périmètre (AS-IS + TO-BE + Pipeline)
   ┃
STEP:4    Dossier SRS
   ┃
 GATE:2   ✋ Validation SRS
   ┃
STEP:5    Formulaire Form.io principal
STEP:5a   Formulaires correction + paiement (conditionnels)
STEP:5b   Formulaires userTasks (instruction agent, etc.)
   ┃
 GATE:3a  ✋ Validation Form.io
   ┃
STEP:6    Processus BPMN XML
   ┃
 GATE:3b  ✋ Validation BPMN
   ┃
STEP:6.5  Audit cohérence inter-livrables
STEP:7    Plan de tests + Manuel utilisateur
STEP:8    Personnalisation et adaptation
STEP:8.5  PV de recette
STEP:9    Checklist finale
```

---

## Navigation dans le workflow

Le fichier `digitalisation-service-public.md` fait ~1000 lignes. Trois mécanismes facilitent la navigation :

### 1. Ancres grep-ables

Chaque étape et gate porte un commentaire HTML unique dans son heading :

```
## <!-- STEP:6 --> Étape 6 — Processus BPMN (XML)
## <!-- GATE:1 --> GATE 1 — Validation du périmètre ✋
```

Pour trouver une étape : `grep "STEP:6" digitalisation-service-public.md`
Pour trouver une gate : `grep "GATE:1" digitalisation-service-public.md`

### 2. Bloc de navigation compact

En tête du fichier (dans un commentaire HTML), un tableau résume pour chaque étape :
- Les livrables à produire
- Les fichiers de référence à lire
- La gate suivante

### 3. Blocs `reads_before`

Les étapes nécessitant la lecture de fichiers de référence portent un commentaire YAML structuré :

```html
<!-- reads_before:
  - documentation/guide-transformation-asis-tobe.md   # AVA + 10 Règles d'Or ATD
  - exemples/*/formio-*.json                           # Exemples formulaires (glob)
-->
```

L'agent IA doit lire **tous** les fichiers listés avant de produire le livrable de l'étape.

---

## Gates (points d'arrêt)

Les gates sont des **points d'arrêt obligatoires** où l'agent doit soumettre les livrables à l'utilisateur et **attendre sa validation explicite** avant de continuer.

| Gate | Ce qui est validé | Livrables soumis |
|------|-------------------|------------------|
| GATE:1 | Périmètre fonctionnel | Pipeline YAML, AS-IS, TO-BE |
| GATE:2 | Spécifications techniques | SRS |
| GATE:3a | Formulaires | Tous les JSON Form.io |
| GATE:3b | Processus workflow | BPMN XML |

**Règle** : Ne jamais sauter une gate. Si l'utilisateur demande de "tout faire d'un coup", produire les livrables mais s'arrêter à chaque gate pour validation.

---

## STATUS.md (suivi par projet)

Chaque projet doit avoir un fichier `STATUS.md` dans son dossier :

```
projects/METFP/DECC/demande-diplome-cfa/STATUS.md
```

Ce fichier est :
- **Créé** dès l'étape 0.5 (avec le pipeline YAML)
- **Mis à jour** à chaque changement d'étape ou passage de gate
- **Consulté** en début de conversation pour reprendre le travail là où il a été laissé

---

## Sources de référence

| Source | Usage |
|--------|-------|
| `exemples/` | Patterns validés, niveau de qualité attendu |
| `exemples/templates/` | Templates structurels (SRS, stepIntro, paiement) |
| `.agents/skills/bpmn-integrator/` | Règles BPMN, templates GNSPD, anti-patterns |
| `documentation/` | Guides techniques (Form.io, BPMN, transformation AS-IS→TO-BE) |

**Interdit** : Ne jamais utiliser `projects/` comme source de référence. Les projets existants peuvent contenir des erreurs.
