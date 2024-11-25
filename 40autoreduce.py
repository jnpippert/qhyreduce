import argparse
import sys
import shutil
from astropype.decorator import *
from astropype.master import *
from astropype.utilities import *
from astropype import database
from pathlib import Path
from astropype.pixelmath import *
from astropype.utilities import *
from astropype.sky import *
from astropype.badpixel import *
from astropype.fitsreduction import *

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--object", type=str, default=True)
parser.add_argument(
    "-f",
    "--filter",
    type=str,
    choices=["L", "g", "r", "i", "O", "H", "S"],
    default=None,
)
parser.add_argument("-d", "--date", type=str, default=None)
parser.add_argument("-t", "--exptime", type=int, default=None)
parser.add_argument("-s", "--steps", type=str, default="bdf")
parser.add_argument("-b", "--bin" , type=int,default=None)
parser.add_argument("--showdatabase", action="store_true")
parser.add_argument("--showobjects", action="store_true")
parser.add_argument("--obsdates", action="store_true")
parser.add_argument("--updatedatabase", action="store_true")
parser.add_argument("--createdatabase", action="store_true")
args = parser.parse_args(args=None if sys.argv[1:] else ["--help"])

if args.createdatabase:
    database.create("/data/wst/u/jpippert/qhyreduce/qhy_database.pkl",overwrite=True)
    database.update("/data/wst/u/jpippert/qhyreduce/qhy_database.pkl", Path("/data/wst/u/wst/archive/wstserver/QHY_43cm"))
    exit()
if args.updatedatabase:
    database.update("/data/wst/u/jpippert/qhyreduce/qhy_database.pkl", Path("/data/wst/u/wst/archive/wstserver/QHY_43cm"))
    exit()

if args.showdatabase:
    # TODO add other keywords (FILTER,OBJECT,EXPTIME)
    database.show("/data/wst/u/jpippert/qhyreduce/qhy_database.pkl",args.date)
    exit()

if args.showobjects:
    database.show_observed_objects(
        "/data/wst/u/jpippert/qhyreduce/qhy_database.pkl", args.object, args.filter, args.date
    )
    exit()

if args.obsdates:
    database.get_observed_dates(
        "/data/wst/u/jpippert/qhyreduce/qhy_database.pkl", args.object, args.filter, float(args.exptime)
    )
    exit()
_OBJECT = args.object.lower()
_FILTER = args.filter
_DATE = args.date
_DATELIST = _DATE.split(",")
_EXPTIME = int(args.exptime)
_BIASCORR = False
_DARKCORR = False
_FLATCORR = False
_BINNING = False
_PREFIX = "co-"
_CWD = Path.cwd()
_TMPPATH = _CWD.joinpath("tmp")
_MASTERPATH = Path("/data/wst/u/jpippert/qhyreduce/master") #_CWD.joinpath("master")
_ISMASTERBIAS = False
_ISMASTERDARK = False
_ISMASTERFLAT = False


@timeit
def create_masterbias():
    global _PREFIX
    global _TMPPATH, _MASTERPATH

    files = get_filepaths(_TMPPATH, f"{_PREFIX}bias*qhy*.fits")
    mb = MasterBias(files, "median")
    mb.writeto(_MASTERPATH.joinpath("masterbias.fits"))
    return mb.path


@timeit
def create_masterdark():
    global _PREFIX
    global _TMPPATH, _MASTERPATH

    files = get_filepaths(_TMPPATH, f"{_PREFIX}dark*qhy*.fits")
    md = MasterDark(files, "median", exptime=_EXPTIME)
    md.writeto(_MASTERPATH.joinpath(f"masterdark_{_EXPTIME}s.fits"))
    return md.path


@timeit
def create_masterflat(flatdate):
    global _PREFIX
    global _TMPPATH, _MASTERPATH

    files = get_filepaths(_TMPPATH, f"{_PREFIX}sky*qhy*.fits")
    if _ISMASTERBIAS:
        files = remove_bad_pixels(
            files,
            _TMPPATH.joinpath("masterbias_bad_pixel_mask.fits"),
            prefix="n",
            value_func="nearest",
        )
    if _ISMASTERDARK:
        files = remove_bad_pixels(
            files,
            _TMPPATH.joinpath("masterdark_bad_pixel_mask.fits"),
            prefix="n",
            value_func="nearest",
        )
    
    # TODO get best refernce flat using median
    files = scale_images(files, files[int(len(files) / 2)])
    maskfiles = create_flat_star_mask(files, k=3, remove = False) # because the scaled_* images are needed for star_clipping()
    maskfiles = expand_and_clean_mask(maskfiles, diameter=7)
    maskfiles = remove_masked_dust(maskfiles)
    files = star_clipping(files, maskfiles)
    mf = MasterFlat(files, "median")
    mf.writeto(_MASTERPATH.joinpath(f"masterflat_{_FILTER}_{flatdate}.fits"))
    return mf.path


@timeit
def reduce(flatdate):
    global _PREFIX
    global _TMPPATH, _MASTERPATH
    global _ISMASTERBIAS, _ISMASTERDARK, _ISMASTERFLAT

    if _BIASCORR and not _ISMASTERBIAS:
        files = get_filepaths(_TMPPATH, f"bias_*.fits")
        files = subtract_overscan(files,prefix="o-")
        cropfits(files)
    if _DARKCORR and not _ISMASTERDARK:
        files = get_filepaths(_TMPPATH, f"dark_*.fits")
        files = subtract_overscan(files,prefix="o-")
        cropfits(files)
    if _FLATCORR and not _ISMASTERFLAT:
        files = get_filepaths(_TMPPATH, f"sky_*.fits")
        files = subtract_overscan(files,prefix="o-")
        cropfits(files)

    files = get_filepaths(_TMPPATH, f"{_OBJECT}_*.fits")
    files = subtract_overscan(files,prefix="o-")
    
    cropfits(files)
    

    if _BIASCORR:
        if not _ISMASTERBIAS:
            print("creating masterbias")
            masterbiaspath = create_masterbias()
        else:
            print("loading 'masterbias.fits'")
            masterbiaspath = _MASTERPATH.joinpath("masterbias.fits")
        if not _ISMASTERFLAT:
            create_bad_pixel_mask(
                masterbiaspath,
                output=_TMPPATH.joinpath("masterbias_bad_pixel_mask.fits"),
                k=5,
            )
        if not _ISMASTERDARK and _DARKCORR:
            files = get_filepaths(_TMPPATH, f"{_PREFIX}dark*qhy*.fits")
            subtractfits(files, masterbiaspath, prefix="b")
        if not _ISMASTERFLAT and _FLATCORR:
            files = get_filepaths(_TMPPATH, f"{_PREFIX}sky_{_FILTER}*qhy*{flatdate}*.fits")
            subtractfits(files, masterbiaspath, prefix="b")
        _PREFIX = "b" + _PREFIX
        

    if _ISMASTERBIAS and not _ISMASTERFLAT and _FLATCORR and not _BIASCORR:
        create_bad_pixel_mask(
            _MASTERPATH.joinpath("masterbias.fits"),
            output=_TMPPATH.joinpath("masterdark_bad_pixel_mask.fits"),
            k=10,
        )

    if _DARKCORR:
        if not _ISMASTERDARK:
            print(f"creating {_EXPTIME}s masterdark ...")
            masterdarkpath = create_masterdark()
        else:
            print(f"loading 'masterdark_{_EXPTIME}s.fits'")
            masterdarkpath = _MASTERPATH.joinpath(f"masterdark_{_EXPTIME}s.fits")
        if not _ISMASTERFLAT:
            create_bad_pixel_mask(
                masterdarkpath,
                output=_TMPPATH.joinpath("masterdark_bad_pixel_mask.fits"),
                k=10,
            )

    if _ISMASTERDARK and not _ISMASTERFLAT and _FLATCORR:
        create_bad_pixel_mask(
            _MASTERPATH.joinpath(f"masterdark_{_EXPTIME}s.fits"),
            output=_TMPPATH.joinpath("masterdark_bad_pixel_mask.fits"),
            k=10,
        )

    if _FLATCORR:
        if not _ISMASTERFLAT:
            print(f"creating {_FILTER} masterflat for {flatdate} ...")
            masterflatpath = create_masterflat(flatdate)
        else:
            print(f"loading 'masterflat_{_FILTER}_{flatdate}.fits'")
            masterflatpath = _MASTERPATH.joinpath(
                f"masterflat_{_FILTER}_{flatdate}.fits"
            )
    # REMOVE all bias, darks and flats (no masterfiles)  TODO use remove_files()
    for f in get_filepaths(_TMPPATH, f"*bias_*.fits"):
        if "master" not in f.name:
            print(f"removing {f} from {_TMPPATH}\r")
            os.remove(f)
    for f in get_filepaths(_TMPPATH, f"*dark_*.fits"):
        if "master" not in f.name:
            print(f"removing {f} from {_TMPPATH}\r")
            os.remove(f)
    for f in get_filepaths(_TMPPATH, f"*sky_*.fits"):
        if "master" not in f.name:
            print(f"removing {f} from {_TMPPATH}\r")
            os.remove(f)

    # reduce light frames
    prefix = "co-"
    files = get_filepaths(_TMPPATH, f"{prefix}{_OBJECT}_{_FILTER}*{_DATE}*.fits")
    if len(files) == 0:
        print("[WARNING] No Files specified!")
        return

    if _BIASCORR:
        files = subtractfits(files, masterbiaspath, prefix="b")
        prefix = "b" + prefix
        
        
    if _DARKCORR:
        files = subtractfits(files, masterdarkpath, prefix="d")
        prefix = "d" + prefix
        
    if _FLATCORR:
        files = dividefits(files, masterflatpath, prefix="f")
        prefix = "f" + prefix
         

    files = rotatefits(files, prefix="r")
    prefix = "r" + prefix
    
    
    if _BINNING:
        files = binfits(files,bin_factor=args.bin)
        prefix = f"b{args.bin}" + prefix
        

@timeit
def main():
    global _BIASCORR, _DARKCORR, _FLATCORR, _BINNING, _PREFIX
    global _OBJECT, _FILTER, _DATE, _EXPTIME
    global _ISMASTERBIAS, _ISMASTERDARK, _ISMASTERFLAT
    _ARCHIVEPATH = Path("/data/wst/u/wst/PIMA3/rawdata/")
    if isinstance(args.bin,int):
        _BINNING = True
    
    #try:
    database.update("/data/wst/u/jpippert/qhyreduce/qhy_database.pkl", _ARCHIVEPATH)
    #except:
    #    raise FileNotFoundError("no database found. Use --createdatabase")
    database.sort("/data/wst/u/jpippert/qhyreduce/qhy_database.pkl", ["date", "object"], [True, True])
    

    if "master" not in os.listdir(_CWD):
        Path.mkdir(_CWD.joinpath("master"))

    for _DATE in _DATELIST:
        #try:
        #    Path.mkdir(_CWD.joinpath(f"{_OBJECT.upper()}_{_FILTER}_{_DATE}_reduced"))
        #except:
        #    pass
        _ISMASTERBIAS = len(get_filepaths(_MASTERPATH, f"masterbias.fits")) == 1
        _ISMASTERDARK = (
            len(get_filepaths(_MASTERPATH, f"masterdark_{_EXPTIME}s.fits")) == 1
        )
        _ISMASTERFLAT = (
            len(get_filepaths(_MASTERPATH, f"masterflat_{_FILTER}_{_DATE}.fits")) == 1
        )

        if "tmp" not in os.listdir(_CWD):
            Path.mkdir(_CWD.joinpath("tmp"))

        objectfiles = database.select_lights(
            "/data/wst/u/jpippert/qhyreduce/qhy_database.pkl", _OBJECT, _FILTER, _DATE, _EXPTIME
        )
        if len(objectfiles) == 0:
            print(f"[INFO] No {_OBJECT} observations found with:")
            print(f"[INFO]    Exposure Time = {_EXPTIME} seconds")
            print(f"[INFO]    Filter = {_FILTER}")
            print(f"[INFO]    Date = {_DATE}")
            continue
        copy_files(objectfiles, _TMPPATH)

        prefix = "co-"

        if "b" in args.steps:
            if not _ISMASTERBIAS:
                biasfiles = database.select_bias("/data/wst/u/jpippert/qhyreduce/qhy_database.pkl")
                if len(biasfiles) == 0:
                    _BIASCORR = False
                else:
                    _BIASCORR = True
                    prefix = "b" + prefix
                    copy_from_archive(biasfiles, _TMPPATH)
            else:
                _BIASCORR = True
                prefix = "b" + prefix

        if "d" in args.steps:
            if not _ISMASTERDARK:
                darkfiles = database.select_darks("/data/wst/u/jpippert/qhyreduce/qhy_database.pkl", _EXPTIME)
                if len(darkfiles) == 0:
                    _DARKCORR = False
                else:
                    _DARKCORR = True
                    prefix = "d" + prefix
                    copy_files(darkfiles, _TMPPATH)
            else:
                _DARKCORR = True
                prefix = "d" + prefix

        if "f" in args.steps:

            flatfiles, flatdate = database.select_flats(
                "/data/wst/u/jpippert/qhyreduce/qhy_database.pkl", _FILTER, _DATE
            )

            if (
                flatdate != _DATE
                and len(
                    get_filepaths(_MASTERPATH, f"masterflat_{_FILTER}_{flatdate}.fits")
                )
                == 1
            ):
                print(
                    "[INFO] observation date and date of nearest flats are different!"
                )
                _FLATCORR = True
                _ISMASTERFLAT = True
                prefix = "f" + prefix
                print(f"[INFO] Using masterflat from {flatdate}.")
            if not _ISMASTERFLAT:
                if len(flatfiles) == 0:
                    _FLATCORR = False
                else:
                    _FLATCORR = True
                    prefix = "f" + prefix
                    print(f"[INFO] Using flats from {flatdate}.")
                    copy_files(flatfiles, _TMPPATH)
            else:
                _FLATCORR = True
                if "f" not in prefix:
                    prefix = "f" + prefix

        prefix = "r" + prefix
        if _BINNING:
            prefix = f"b{args.bin}" + prefix
        rename_files(_TMPPATH, _DATE, flatdate)
        reduce(flatdate=flatdate)
        print(f"[INFO] Finished reducing {_DATE}.")
        print(f"[INFO] Reduced images saved in {_OBJECT.upper()}_{_FILTER}_{_DATE}_reduced/")
        #TODO handle verison of reduced dirs
        os.rename("tmp/",f"{_OBJECT.upper()}_{_FILTER}_{_DATE}_reduced/")
        #copy_files(get_filepaths(_TMPPATH,f"{prefix}*.fits"), f"{_OBJECT.upper()}_{_FILTER}_{_DATE}_reduced/")
        #print(f"[INFO] Trashing {_TMPPATH}")
        #shutil.rmtree(_TMPPATH)


if __name__ == "__main__":
    main()
