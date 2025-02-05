### TP Noté n°1

#### Mise en place

```shell
git clone https://github.com/ArnaudFB/Projet_Crawler.git
```

```python
python -m venv .venv
./venv/Scripts/activate
pip install -r requirements.txt
python main.py
```

En réalisant ces étapes, le projet est initialisé avec les librairies du projet et en lancant le script dans le main on obtient le fichier results.json disponible dans le repo.

### TP Noté n°2

#### Index des features

Les indexs créés dans ce TP pour les features sont créés de la manière suivante :
1. On récupère la liste de tout les type de features (eg. *colors*, *sizes*, *container*...).
2. Pour chacune des type de features de cette liste, on crée l'index correspondant.
3. On sauvegarde l'index sous format JSON.
4. Pour certains index, il y a des similitidues (*size* = *sizes*, *care instructions* = *care_instructions* et *flavor* = *flavors*) que l'on merge entre elles.

Cela nous permet d'avoir les indexs pour tout les types de features présents.

#### Autres index

Les autres indexs sont créés en fonctions des besoins associés, que ce soit en index inversé, ou en index positionnel. La création de ces indexs se font par les fonctions `build_inverted_index(documents, field)`, `build_positional_index(documents, field)` et `build_review_index(documents)` créant respectivement un index inversé sur un champ donné par la variable `field`, un index positionnel sur un champ donné et un index pour les reviews contenant le nombre de review, le score moyen et la dernière note obtenue.

#### Mise en place

Similaire à celle du premier TP noté, il suffit d'exécuter les commandes suivantes sur son IDE.

```python
python -m venv .venv
./venv/Scripts/activate
pip install -r requirements.txt
python indexation.py
```


