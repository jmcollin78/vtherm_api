Pour publier cette librairie sur les dépôts Python, le flux standard est : construire le package, le vérifier, puis l’envoyer sur TestPyPI et enfin sur PyPI. Dans votre cas, la base est déjà prête dans pyproject.toml : backend setuptools, métadonnées projet et découverte des packages sous vtherm_api.

La procédure concrète :

1. Créer un compte sur PyPI et TestPyPI.
2. Générer un token API sur chaque site.
3. Installer les outils de publication dans votre environnement :

  > `python -m pip install --upgrade build twine`

4. Construire les artefacts depuis la racine du repo :
Vous obtiendrez en général un sdist et une wheel dans dist/.
  > `python -m build`

5. Vérifier les artefacts :
  > `python -m twine check dist/*`

6. Publier d’abord sur TestPyPI :
  > `python -m twine upload --repository testpypi dist/*`

7. Tester l’installation :
  > `pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple vtherm_api`

8. Si tout est bon, publier sur PyPI :
    > `python -m twine upload dist/*`

Points spécifiques à ce dépôt avant publication :

La version est dupliquée entre pyproject.toml et __init__.py. Il vaut mieux n’avoir qu’une seule source de vérité, sinon vous finirez avec une incohérence de release.
Le champ requires-python est fixé à 3.14+ dans pyproject.toml. PyPI l’acceptera, mais cela limitera fortement l’installation. Si ce n’est pas intentionnel, baissez-le à la vraie version minimale supportée.
Il manque des métadonnées utiles pour PyPI, par exemple project.urls pour le dépôt, la documentation et l’issue tracker. Ce n’est pas bloquant, mais c’est préférable.
build et twine ne sont pas déclarés dans les dépendances de dev. Ce n’est pas obligatoire, mais pratique pour fiabiliser la publication.