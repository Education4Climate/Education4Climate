# Web interface proof of concept

## Utilisateurs finaux

* Professeurs d'université à la recherche de pairs ayant une expertise dans telle ou telle thématique
* Étudiants en recherche de cours ou cherchant une université

## Cas d'utilisation principaux

* Recherche de cours
* Recherche de professeurs

## Fonctionnalités du POC

### Recherche de cours

* Affichage de la liste des cours dans un tableau :

  * score climat (affiché visuellement avec des étoiles + tooltip avec le nombre)
  * nom de l'université
  * intitulé du cours
  * code du cours (cliquable, redirige vers la page sur le site de l'université)
  * thématiques
  * langues

* Filtres (combinables) :

  * université(s)
  * thématique(s)
  * langue(s)
  * fragment de l'intitulé du cours

* Tri ascendant/descendant :

  * score climat
  * nom de l'université
  * intitulé du cours
  * code du cours

* Affichage du nombre total de cours pour chaque université / thématique / langue directement dans le filtre
* Affichage du nom de cours qui répondent aux filtres utilisés
* Un clic sur une ligne ouvre le détail avec la totalité des informations
* Pagination de la table

### Technique

* Contenu entièrement statique (pas d'API ou quoi que ce soit, tout tourne dans le navigateur)
* Framework CSS [Skeleton](http://getskeleton.com/)
* Librairie pour la table : [Tabulator](http://tabulator.info/)

## Données

* Structure des données consolidée à partir des 3 fichiers disponibles dans ```unicrawl\data\crawling-results```

* 5 jeux de test fictifs de 100 cours (mock disponible [sur mockaroo.com](https://www.mockaroo.com/08293c40))

```
{
  "name": "Transition énergétique",
  "shortName": "LEDPH2131",
  "years": "2020-2021",
  "teachers": [
      "Jungers Raphaël",
      "Soares Frazao Sandra"
  ],
  "credits": 80,
  "languages": [
      "fr"
  ],
  "themes": [
      "écologie",
      "mobilité",
      "transition énergétique"
  ],
  "abstract": "blabla blabla blabla",
  "campus": "Solbosch",
  "shiftScore": 0.431,
  "climateScore": 2.086,
  "url": "https://www.ulb.be/cours/LEDPH2131"
},
```

## Remarques au niveau des données

* Langues : intéressant d'avoir un tableau plutôt qu'une chaîne de caractères (plusieurs cours sont donnés en plusieurs langues)
* Langues : sûrement mieux d'avoir un code ISO à 2 caractères (fr, nl, de, en) plutôt que le nom en entier (plus facile pour traduire)
* Thématiques : comme les langues, prévoir un code pour chaque thématique pour faciliter la traduction
* Professeurs : normaliser la casse des noms/prénoms (+ ordre "Prénom Nom" par exemple)
* URL : ajouter l'URL de chaque cours

## Fonctionnalités qui peuvent être intéressantes

* Pouvoir passer les filtres dans l'URL (pour permettre de faire un lien vers un résultat précis)

## TODO

* Recherche de professeurs (annuaire)
* Lien "signaler une erreur"
* Prévoir page avec la méthodologie