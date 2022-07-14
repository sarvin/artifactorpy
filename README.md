# Artifacorypy

Python module for working with Artifactory. The goal is to develop a common interface that blends *most* of the Artifactory calls into objects. Repository, Directory, and File all have methods for interacting with them ie ```file.delete()```.

## Usage

ARTIFACTORY_URL: URL of the AF instance (starting with http(s)://)

ARTIFACTORY_API_KEY: API key for the user in the Artifactory instance

### Use AQL to find files:

```python
import src.aql
aql = src.aql.Items(
    ARTIFACTORY_URL,
    ARTIFACTORY_API_KEY)

cursor = aql.find({
    "repo": "docker-dev-local",
    "name": {"$eq":"manifest.json"},
    "stat.downloaded": {"$before":"4y"}})
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
