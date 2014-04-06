from core import PyCamb
import warnings

def age(**parameters):
    warnings.warn("direct invocation via function is deprecated. Use PyCamb instead", DeprecationWarning)
    return PyCamb(**parameters).age()

def transfers(redshifts=[0],**parameters):
    warnings.warn("direct invocation via function is deprecated. Use PyCamb instead", DeprecationWarning)
    return PyCamb(**parameters).transfers(redshifts)

def matter_power(redshifts=[0],maxk=1.,logk_spacing=0.02,**parameters):
    warnings.warn("direct invocation via function is deprecated. Use PyCamb instead", DeprecationWarning)
    return PyCamb(**parameters).matter_power(redshifts, maxk, logk_spacing)

def angular_diameter(z,**parameters):
    warnings.warn("direct invocation via function is deprecated. Use PyCamb instead", DeprecationWarning)
    return PyCamb(**parameters).angular_diameer(z)
