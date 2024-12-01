import numpy as np
import sys
import os

def calc_quality(catalog : str) -> tuple[float,float]:
    fwhm,eps,star = np.loadtxt(catalog,usecols=(5,6,7),unpack=True)
    stars = star>0.8
    return np.median(fwhm[stars]) * 3600,np.median(eps[stars]),len(eps[stars])

def set_quality(fwhm : float,eps :float,nsrcs : float, filename : str) -> None:
    os.system(f"sethead MED-FWHM={fwhm} {filename}")
    os.system(f"sethead MED--EPS={eps} {filename}")
    os.system(f"sethead NSOURCES={nsrcs} {filename}")
    
if __name__ == "__main__":
    filename = sys.argv[1]
    catalog = sys.argv[2]
    fwhm, eps, nsrcs = calc_quality(catalog)
    if nsrcs == 0:
        fwhm = eps = "None"
    set_quality(fwhm,eps,nsrcs,filename)
              
        




