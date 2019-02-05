import subprocess
import os
import hashlib
import warnings

def parse_singularity_link():
    if not 'SIMG' in os.environ.keys():
        raise RuntimeError("NO $SIMG in Environment!")

def download_simg_from_gsiftp(simg_link):
    img_name = simg_link.split('/')[-1]
    print("Downloading image {0}".format(img_name))
    _dl = subprocess.Popen(['globus-url-copy', simg_link, img_name], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    out,err = _dl.communicate()
    if not out and not err:

        return
    else:
        print("Error downloading image:{1}".format(err))
    
def pull_image_from_shub(shub_link,commit=None):
    print("Pulling image {0} with commit {1}".format(shub_link,commit))
    if not commit:
        _pull = subprocess.Popen(['singularity','pull',shub_link],stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        out,err= _pull.communicate()
        if not err:
            img_path = out.split('/n')[-1].split("Done. Container is at: ")[1].strip()
            if os.path.exists(img_path):
                return img_path
            else:
                raise RuntimeError("Tried to download image to {0} but now it isn't there!".format(img_path))
        else:
            raise RuntimeError("Error {0} occurred when pulling container".format(err))
    else:
        _pull = subprocess.Popen(['singularity','pull',"{0}@{1}".format(shub_link, commit)],stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        out,err= _pull.communicate()
        if not err:
            img_path = out.split('/n')[-1].split("Done. Container is at: ")[1].strip()
            if os.path.exists(img_path):
                img_hash = get_image_file_hash(img_path)
                if img_hash == commit:
                    return img_path
                else:
                    warnings.warn("!!!!!!!!!!!!!\n !!!!!!!!!!!!!!!!\n The image commit and the hash on singularityhub are not the same!")
                    return img_path
            else:
                raise RuntimeError("Tried to download image to {0} but now it isn't there!".format(img_path))


def get_image_file_hash(image_path):
    '''get_image_hash will return an md5 hash of the file based on a criteria level.
    :param level: one of LOW, MEDIUM, HIGH
    :param image_path: full path to the singularity image
    Taken from https://github.com/vsoch/singularity-python/blob/f1f241f285f25d73cff16942a11d2c393d094f48/singularity/analysis/reproduce/hash.py#L173
    '''
    hasher = hashlib.md5()
    with open(image_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()
