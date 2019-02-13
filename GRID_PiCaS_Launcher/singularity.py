import subprocess
import sys
import os
import hashlib
import warnings
import json
import pdb

def download_singularity_from_env():
    """download_singularity_from_env
    Downloads the singularity image from environment variables:
    $SIMG: url of the image
    $SIMG_COMMIT: The commit hash of the image"""
    if not 'SIMG' in os.environ.keys():
        raise RuntimeError("NO $SIMG in Environment!")
    simg_url = os.environ['SIMG']
    simg_commit = os.environ.get('SIMG_COMMIT', None)
    return parse_singularity_link(simg_url, simg_commit)

def parse_singularity_link(simg_url, simg_commit=None):
    """parse_singularity_link

    :param simg_url: The url to the singularity image (can be gsiftp:// or shub://, 
                    ideally also http:// will be supported)
    :type simg_url: str
    :param simg_commit: Optional commit hash for singularity hub
    :type simg_commit: str
    """
    if simg_url.split("://")[0] == 'shub':
        return pull_image_from_shub(simg_url, simg_commit)
    if simg_url.split("://")[0] == 'gsiftp':
        return download_simg_from_gsiftp(simg_url) #TODO: If hash is given here, still check if it's ok
    print("Unknown image location {0}".format(simg_url))

def download_simg_from_gsiftp(simg_link):
    """download_simg_from_gsiftp

    :param simg_link: The gsiftp link for the singularity image
    """
    img_name = simg_link.split('/')[-1]
    print("Downloading image {0}".format(img_name))
    _dl = subprocess.Popen(['globus-url-copy', simg_link, img_name], stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    out,err = _dl.communicate()
    if not out and not err:
        return img_name
    else:
        print("Error downloading image:{0}".format(err))



def pull_image_from_shub(shub_link,commit=None):
    """Using the shub url (shub://...), this module downloads the singularity image
    Optionally, a commit hash can be given. If the downloaded image's hash doesn't match, 
    a warning is thrown, however processing continues"""
    print("Pulling image {0} with commit {1}".format(shub_link,commit))
    if not commit:
        _pull = subprocess.Popen(['singularity','pull',shub_link],stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        out,err= _pull.communicate()
        if not err:
            out = out.decode('ascii')
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
            out = out.decode('ascii')
            img_path = out.split('/n')[-1].split("Done. Container is at: ")[1].strip()
            if os.path.exists(img_path):
                img_hash = get_image_file_hash(img_path)
                if img_hash == commit:
                    return img_path
                else:
                    warnings.warn("\n!!!!!!!!!!!!!\n !!!!!!!!!!!!!!!!\n The image commit and the hash on singularityhub are not the same!\n The pulled image has a hash of {0} instead of {1}".format(img_hash, commit))
                    return img_path
            else:
                raise RuntimeError("Tried to download image to {0} but now it isn't there!".format(img_path))


def put_variables_in_env(json_payload):
    """Takes a json payload from a token and puts the variables in the environment"""
    config = parse_json_payload(json_payload)
    os.environ['SIMG'] = config['SIMG']
    if "SIMG_COMMIT" in config.keys():
        os.environ["SIMG_COMMIT"] = config["SIMG_COMMIT"]

def parse_json_payload(json_payload):
    """Takes a json payload from a token and puts the variables in the environment"""
    if 'container' in json_payload.keys():
        json_payload = json_payload['container']
    if 'singularity' in json_payload.keys():
        json_payload = json_payload['singularity']
    if 'SIMG' in json_payload.keys():
        payload = json_payload
    else:
        raise RuntimeError("Could not find SIMG in {0}".format(json_payload))
    simg = payload['SIMG']
    simg_hash = payload.get("SIMG_COMMIT", None)
    return {'SIMG': simg, "SIMG_COMMIT": simg_hash}

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

class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


if __name__ == "__main__":
    with HiddenPrints():
        location = download_singularity_from_env() 
    print(location)
