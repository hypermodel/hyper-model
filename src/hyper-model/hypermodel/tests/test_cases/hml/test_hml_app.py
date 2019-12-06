
from hypermodel.hml.hml_app import HmlApp
from hypermodel.platform.gcp.services import GooglePlatformServices
from hypermodel.platform.local.services import LocalPlatformServices
from hypermodel.tests.utilities import general


def test_hml_all_init():
    #test if all the required parameters are there
    # if new parameters added we should flag as no test available for these parameters
    #Instantiate HmlApp
    obj,expected_values=general.get_instance_of_HmlApp()
    retBool,retLst=general.check_attributes_in_object(obj,expected_values)

    assert retBool 

def test_register_model():
    hmlapp,hmlapp_attributes=general.get_instance_of_HmlApp()
    model,model_attr=general.get_instance_of_ModelContainer()
    hmlapp.register_model("test",model)
    assert hmlapp.models["test"]==model
    assert "test" in hmlapp.inference.models.keys() 
    assert model in hmlapp.inference.models.values() 


def test_get_model():
    hmlapp,hmlapp_attributes=general.get_instance_of_HmlApp()
    #just instantiated so no models in there
    assert len(hmlapp.models.keys())==0
    model,model_attr=general.get_instance_of_ModelContainer()
    hmlapp.models["test"]=model
    assert model==hmlapp.get_model("test")


def test_get_services():
    hmlapp,hmlapp_attributes=general.get_instance_of_HmlApp()
    #just instantiated so no models in there
    assert type(hmlapp._get_services("GCP"))==type(GooglePlatformServices())
    assert type(hmlapp._get_services("local"))==type(LocalPlatformServices())


