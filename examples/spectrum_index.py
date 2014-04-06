import pycamb
import pylab
lmax=2000
ns_values = [0.8,0.9,1.0,1.1]
ell = pylab.arange(1,lmax)
camb = pycamb.PyCamb()
for ns in ns_values:
    camb['n_s'] = ns
    T,E,B,X = camb(lmax)
    pylab.semilogx(ell,T,label="%.2f"%ns)
    pylab.legend()
    pylab.xlabel("$\ell$", fontsize=20)
    pylab.ylabel("$\ell (\ell+1) C_\ell / 2\pi \quad [\mu K^2]$",
            fontsize=20)
    pylab.title("Varying Spectral Index $n_s$")
    pylab.xlim(1,2000)
    pylab.savefig("spectral_index.eps")

