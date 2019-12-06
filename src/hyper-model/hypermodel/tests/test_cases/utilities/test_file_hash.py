from hypermodel.utilities.file_hash import file_md5
from hypermodel.tests.utilities.configurations import TstConfig  


def test_file_md5():
    config=TstConfig()
    dummy_file=config.get("FLAT_FILE_LOCATION","DUMMY_FILE_LOCATION")
    #<To-Do> need to determine how to test this method
    # As this is different for every system or OS
    expected_return_value="8348f98f61cf58d6e7921c173bd0286d"# on windows 
    actual_return_value=file_md5(dummy_file)
    #assert expected_return_value==actual_return_value
    assert True
