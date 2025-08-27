# Converters Architecture

Cette architecture suit le principe de **séparation des responsabilités** avec une **interface commune** pour tous les converters.

## Structure des Fichiers

```
converters/
├── __init__.py                           # Imports des converters
├── sphinx_makefile_converter.py          # Étape 1: Sphinx avec Makefile
├── sphinx_build_converter.py             # Étape 2: Sphinx sans Makefile
├── nonsphinx_converter.py                # Étape 3: Non-Sphinx (md, docstrings)
├── raw_source_code_converter.py          # Étape 4: Code source brut
├── notebook_converter.py                 # Étape 5: Notebooks uniquement
├── markdown_builder.py                   # Construction Sphinx (utilitaire)
└── utils/
    ├── __init__.py                       # Imports des utilitaires
    ├── detector.py                       # Détection des formats
    └── text_converter.py                 # Conversion MD → TXT
```

## Convention de Nommage

Chaque converter suit le pattern : **`type_conversion_converter.py`**

- **`sphinx_makefile_converter.py`** → Gère la conversion Sphinx **avec** Makefile
- **`sphinx_build_converter.py`** → Gère la conversion Sphinx **sans** Makefile (fallback)
- **`nonsphinx_converter.py`** → Gère la conversion **non-Sphinx** (déjà correct)
- **`raw_source_code_converter.py`** → Gère la conversion du **code source brut**
- **`notebook_converter.py`** → Gère la conversion des **notebooks uniquement**

## Interface Commune

Tous les converters implémentent la même interface :

```python
class BaseConverter:
    def convert(self, input_path: str, output_path: str, library_name: str) -> tuple[str | None, bool]:
        """
        Convertit la documentation.
        
        Returns:
            Tuple[Optional[str], bool]: (chemin_fichier_sortie, succès)
        """
        pass
```

## Flux de Conversion

### 1. **Sphinx Makefile** (Priorité 1)
- Utilise `make` pour construire la documentation
- Convertit en Markdown puis en texte
- **Fichier** : `sphinx_makefile_converter.py`

### 2. **Sphinx Build** (Priorité 2)
- Utilise `sphinx-build` directement (sans Makefile)
- Fallback quand `make` n'est pas disponible
- **Fichier** : `sphinx_build_converter.py`

### 3. **Non-Sphinx** (Priorité 3)
- Traite les notebooks Jupyter
- Extrait les docstrings des fichiers Python
- Combine tout en un fichier texte unique
- **Fichier** : `nonsphinx_converter.py`

### 4. **Raw Source Code** (Priorité 4)
- Extrait le code source brut
- Crée une documentation basique
- **Fichier** : `raw_source_code_converter.py`

### 5. **Notebooks** (Priorité 5)
- Dernier recours : notebooks uniquement
- **Fichier** : `notebook_converter.py`

## Utilitaires

### **`detector.py`**
- Détection automatique du format de documentation
- Recherche des chemins de bibliothèques
- Gestion des cas spéciaux (CAMB, etc.)

### **`text_converter.py`**
- Conversion Markdown → Texte
- Gestion des formats HTML intermédiaires
- Fallbacks en cas d'échec

### **`markdown_builder.py`**
- Construction de documentation Sphinx
- Gestion des formats de sortie
- Utilitaires pour la construction

## Avantages de cette Architecture

1. **Cohérence** : Chaque converter suit le même pattern
2. **Maintenabilité** : Logique de fallback centralisée et claire
3. **Extensibilité** : Facile d'ajouter de nouveaux converters
4. **Testabilité** : Chaque converter peut être testé indépendamment
5. **Séparation des responsabilités** : Chaque fichier a un rôle précis

## Utilisation dans `contextmaker.py`

```python
# ÉTAPE 11: Logique de fallback en cascade
# 1) Sphinx (Makefile) - Priorité haute
if doc_format == 'sphinx_makefile':
    converter = SphinxMakefileConverter()
    output_file, success = converter.convert(input_path, output_path, library_name)

# 2) Sphinx build (fichiers conf.py et .rst) - Fallback Sphinx
if not success and detector.has_documentation(input_path):
    converter = SphinxBuildConverter()
    output_file, success = converter.convert(input_path, output_path, library_name)

# ... et ainsi de suite pour chaque étape
```

Cette architecture élimine les fonctions de fallback locales et centralise toute la logique de conversion dans des converters dédiés et bien nommés.
