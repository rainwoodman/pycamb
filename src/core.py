from _pycamb import pycamb_mod as _f
from _pycamb import errors 

from config import PARAMS
import os.path
import numpy

__all__ = ['PyCamb']

_f.setcltemplatepath(
     os.path.join(
        os.path.dirname(__file__),
        'camb/HighLExtrapTemplate_lenspotentialCls.dat')
)
class PyCambError(Exception):
    def __init__(self):
        Exception.__init__(self, errors.global_error_message.tostring().strip())

class PyCamb(object):
    """ A CAMB wrapper object. """
    def __init__(self, **kwargs):
        self.pvec = PARAMS(**kwargs)
    __init__.__doc__ = """ Create a CAMB wrapper object.

    The list of supported kwargs is:
%s
    to see the current values of the parameters, print the object.
    """ % str(PARAMS)

    def __repr__(self):
        return """CAMB wrapper object with parameters: \n%s\n""" % repr(self.pvec)

    def __getitem__(self, index):
        return self.pvec[index]

    def __setitem__(self, index, value):
        self.pvec[index] = value

    def __call__(self, lmax, max_eta_k=None):
        return self.camb(lmax, max_eta_k)

    def camb(self, lmax, max_eta_k=None):
        """
        Run camb up to the given lmax, with the given parameters and return the Cls.  Parameter names are case-insensitive.
        """
        if max_eta_k is None: max_eta_k = 2*lmax
        cls=_f.getcls(self.pvec, lmax, max_eta_k)
        if errors.global_error_flag:
            raise PyCambError()
        return cls.T

    def age(self):
        """ Get the age of the universe with the given parameters. """
        age = _f.getage(self.pvec)
        return age

    def transfers(self, z=0, lmax=1000):
        """ 
            z can be a list. 
            returns transfer function as K, T, S
            S.shape is same as z
            T.shape is x, len(K), len(z)
        """
        if numpy.isscalar(z):
            redshift = [z]
        else:
            redshift = z

        unique, inv = numpy.unique(-numpy.assarray(redshift), return_inverse=True)

        if len(unique)>500: 
            raise ValueError("At most 500 redshifts can be computed without changing the hardcoded camb value")

        _f.gentransfers(self.pvec, lmax, -unique)
        if errors.global_error_flag:
            raise PyCambError()

        K = _f.transfers_k.copy()
        T = _f.transfers.copy()[..., inv]
        S = _f.transfers_sigma8.copy()[inv]
        _f.freetransfers()

        if numpy.isscalar(z):
            K, T, S = K, T[..., 0], S[0]
        return K, T, S

    def matter_power(self, z=0, maxk=1., logk_spacing=0.02):
        """
            redshift can be a list. 
            returns kh, power
            power has shape (len(kh), len(z)) 
        """
        if numpy.isscalar(z):
            redshift = [z]
        else:
            redshift = z
        unique, inv = numpy.unique(-numpy.asarray(redshift), return_inverse=True)

        if len(unique)>500: 
            raise ValueError("At most 500 redshifts can be computed without changing the hardcoded camb value")
        _f.getpower(self.pvec, maxk, logk_spacing, -unique)
        if errors.global_error_flag:
            raise PyCambError()

        power=_f.matter_power.copy()[..., inv]
        kh=_f.matter_power_kh.copy()[..., inv]
        _f.freepower()

        if self.pvec['N_ps'] == 1:
            power = power[:, 0, :]

        if numpy.isscalar(z):
            return kh[..., 0], power[..., 0]
        else:
            return kh, power
        
    def angular_diameter(self, z):
        if numpy.isscalar(z):
            redshift = [z]
        else:
            redshift = z
        unique, inv = numpy.unique(-numpy.asarray(redshift), return_inverse=True)
        da = _f.angulardiametervector(self.pvec, -unique)[inv]
        if errors.global_error_flag:
            raise PyCambError()
        if numpy.isscalar(z):
            return da[0]
        else:
            return da
            
