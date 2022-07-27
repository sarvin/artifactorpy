# Artifacorypy

Python module for working with Artifactory. The goal is to develop a common interface that blends *most* of the Artifactory calls into objects. Repository, Directory, and File all have methods for interacting with them ie ```file.delete()```.

## Usage

ARTIFACTORY_URL: URL of the AF instance (starting with http(s)://)

ARTIFACTORY_API_KEY: API key for the user in the Artifactory instance

### Use AQL to find files:

Access to the aql item domain currently granted through ArtifactsAndStorage but I intend to move AQL queries into their own class.

A generator is returned by the find query.
```python
import src.artifactory
api = src.artifactory.ArtifactsAndStorage(
    ARTIFACTORY_URL,
    ARTIFACTORY_API_KEY)

cursor = api.item().find({
    "repo": "docker",
    "name": {"$eq":"manifest.json"},
    "stat.downloaded": {"$before":"4y"}})

file = next(cursor)

# or

files = [file for file in cursor]
```

### Use artifacts and storage like API calls to retrieve top level repositories

```python
import src.artifactory
api = src.artifactory.ArtifactsAndStorage(
    ARTIFACTORY_URL,
    ARTIFACTORY_API_KEY)
repositories = api.get_repositories()
```

### Use artifacts and storage like API calls to retrieve directories and files

```python
import src.artifactory
api = src.artifactory.ArtifactsAndStorage(
    ARTIFACTORY_URL,
    ARTIFACTORY_API_KEY)

directory = api.get_directory(
    REPO_NAME,
    DIRECTORY_PATH)

children = directory.children()
```
