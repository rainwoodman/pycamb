from numpy.distutils.core import setup, Extension
from numpy import get_include
import os.path
from nonstopf2py import f2py
from sys import path
path.append('src')

from config import PARAMS

def makeFortranParamSetter(params):
    code="""
    subroutine makeParameters(paramVec,P)
        use camb
        implicit none
        real, intent(in) :: paramVec(1024)
        type(CAMBparams) P
    """
    for i, p in enumerate(params):
        if p.type == bool:
            code += """ 
            if(.not. isnan(paramVec(%(ind)d))) %(varname)s = paramVec(%(ind)d) /= 0.0 
            """ % dict(varname=p.fname, ind=i+1)
        else:
            code += """ 
            if(.not. isnan(paramVec(%(ind)d))) %(varname)s = paramVec(%(ind)d) 
            """ % dict(varname=p.fname, ind=i+1)

    code += """
    end subroutine makeParameters
    """
    
    return code

modulestart = """
module pycamb_parameters
    contains
"""
moduleend = """
endmodule pycamb_parameters
"""

def makeparametersf90():
    with file('src/parameters.f90', 'w') as output:
        output.write(modulestart)
        output.write(makeFortranParamSetter(PARAMS))
        output.write(moduleend)

# Get CAMB from http://camb.info, untar and copy *.[fF]90 to src/
# this is done by the script extract_camb.sh

cambsources = ['camb/%s' % f for f in [
    'constants.f90',
    'utils.F90',
    'subroutines.f90',
    'inifile.f90',
    'power_tilt.f90',
    'recfast.f90',
    'reionization.f90',
    'modules.f90',
    'bessels.f90',
    'equations.f90',
    'halofit.f90',
    'lensing.f90',
    'SeparableBispectrum.F90',
    'cmbmain.f90',
    'camb.f90',
]]

for f in cambsources:
  if not os.path.exists('camb/Makefile'):
    raise Exception("At least one of CAMB code file: '%s' is not found. Download and extract to camb/" % f)

makeparametersf90()

f2py.run_main(['--debug-capi', '-m', '_pycamb', '-h', 
    '--overwrite-signature', 'src/pycamb_main.pyf', 
         'src/pycamb_main.f90', 'camb/constants.f90'])

setup(name="pycamb", version="0.2",
      author="Joe Zuntz",
      author_email="jaz@astro.ox.ac.uk",
      description="python binding of camb, you need sign agreement and obtain camb source code to build this. Thus we can not GPL this code.",
      url="http://github.com/rainwoodman/#",
      download_url="http://web.phys.cmu.edu/~yfeng1/#",
      zip_safe=False,
      install_requires=['numpy'],
      requires=['numpy'],
      packages = [ 'pycamb' ],
      package_dir = {'pycamb': 'src'},
      data_files = [('pycamb/camb', ['camb/HighLExtrapTemplate_lenspotentialCls.dat'])],
      scripts = [],
      ext_modules = [
        Extension("pycamb._pycamb", 
             ['src/pycamb_main.pyf'] + cambsources +['src/parameters.f90',
             'src/pycamb_main.f90'],
             extra_f90_compile_args=['-O3', '-g'],
             extra_compile_args=['-O3', '-g', '-Dintp=npy_intp'],
#             libraries = {'noexit': ['src/noexit.c']},
             include_dirs=[get_include()],
        )]
    )

