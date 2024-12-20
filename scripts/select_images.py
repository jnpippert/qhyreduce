import pandas as pd
import os
from astropy.io import fits
from pathlib import Path
import numpy as np
import sys
from tqdm import tqdm
import argparse


def select(filename:str,fwhm_limit : float, eps_limit : float) -> list[str]:
    files,nsrcs,fwhm,eps = np.loadtxt(filename,dtype=str,
                                      unpack=True,usecols=(0,1,2,3))
    df = pd.DataFrame(data={"filename" : files, 
                            "fwhm": fwhm.astype(float),
                            "eps" : eps.astype(float)})
    print(f"[INFO] Selecting images with seeing <= {fwhm_limit} arcsec")
    print(f"[INFO] Selecting images with ellipticity <= {eps_limit}")
    sel_df = df[df["fwhm"] <= fwhm_limit]
    sel_df = sel_df[sel_df["eps"] <= eps_limit]
    print(f"[INFO] Throwing out {np.round((1-len(sel_df)/len(df))*100,2)}% of images.")
    print(f"[INFO] {len(sel_df)}/{len(df)} selected.")
    return sel_df["filename"]

def write(files : list[str], filename : str = "selected.txt"):
    with open(filename,"w") as textfile:
        for f in files:
            textfile.write(f+"\n")
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fwhm", type=float,help="",default=2)
    parser.add_argument("--eps", type=float,help="",default=0.2)
    args = parser.parse_args()
    
    files = select(filename="quality.txt",fwhm_limit=args.fwhm,eps_limit=args.eps)
    write(files)        

