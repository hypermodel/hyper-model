from hypermodel.platform.local.services import LocalPlatformServices
from hypermodel.platform.local.config import LocalConfig
from hypermodel.platform.local.data_warehouse import SqliteDataWarehouse
from hypermodel.platform.local.data_lake import LocalDataLake
from hypermodel.platform.gitlab.git_host import GitLabHost


def test_all_attributes_populated():
    classObj=LocalPlatformServices()
    assert classObj._config != None
    assert classObj._lake != None
    assert classObj._warehouse != None
    assert classObj._git != None
    assert isinstance(classObj._config,LocalConfig)
    assert isinstance(classObj._lake,LocalDataLake)
    assert isinstance(classObj._warehouse,SqliteDataWarehouse)
    assert isinstance(classObj._git,GitLabHost)


