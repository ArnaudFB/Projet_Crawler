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

### TP Noté n°3

#### Mise en place

Similaire à celle du premier TP noté, il suffit d'exécuter les commandes suivantes sur son IDE.

```python
python -m venv .venv
./venv/Scripts/activate
pip install -r requirements.txt
python browser.py
```

Il suffit de changer la valeur de la variable query en fin de script pour effectuer un recherche sur une query différente.

#### Objectif

L'objectif est de créer son propre moteur de recherche sur les différents indexs créés au préalable. Le moteur de recherche utilise le score BM25, les notes données par les utilisateurs, ainsi que d'autres indicateurs tels que le matching parfait entre la query et le titre pour affecter un score et un ranking à chaque document pour une requête donnéee.

#### Données

Les données du TP 3 sont toutes disponibles dans le folder data_3 du repo Git. On y trouve les indexs des marques, des descriptions, des origines, des reviews ainsi que des titres en plus d'avoir les synonymes des origines et le fichier JSONL de base.

#### Détails

Le fonctionnement de chaque méthode est rappelé dans le fichier `browser.py` avec une documentation pour chacune des méthodes et des commentaires annexes.

#### Configuration

##### BM25

Les paramètres de BM25 `k1` et `b` peuvent être ajustés pour régler l'influence de la fréquence des tokens et de la longueur des documents, par défaut, ces valeurs sont prises respectivement à 1,5 et 0,75.

##### Poids des tokens

Les tokens ont un poids différent selon si il se trouve dans le titre, la description, l'origine ou encore la marque (respectivement 5, 3, 1 et 2). Nous considérons qu'un token présent dans le titre à une grande importance, de même pour la description, alors que l'origine importe moins et que la marque, bien qu'elle ait une importance, elle reste tout de même moins importante que le titre et la description qui sont discriminant pour la pertinence d'un résultat. 

##### Poids des scores et bonus

Des bonus sont ajoutés au score afin de valoriser des bons scores pour les reviews ou pour récompenser le fait qu'un query présente un matching exact avec un titre. nous additionnons ensuite ces deux bonus avec le score du BM25 avec les poids suivants :
* BM25: Poids par défaut 1
* Bonus review : Poids par défaut 0,5
* Matching parfait titre : Poids par défaut 1,5

Ces poids peuvent être modifiés par l'utilisateur.

#### Résultat d'une requête

Le résultat d'une requête apparait sous la forme suivante:

```json

{
    "total_documents": nombre_de_documents,
    "filtered_documents": nombre_de_document_apres_filtrage,
    "results": [
        {
            "Titre": titre_du_document,
            "URL": url_du_document,
            "Description": description_du_document,
            "score": score_du_document
        },
...
                ]
}

```
