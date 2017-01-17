# Hopefully temporary fix for
# https://bitbucket.org/pypa/setuptools/issues/450/egg_info-command-is-very-slow-if-there-are
import os


TO_OMIT = ['var', '.git', 'parts', 'bower_components', 'node_modules', 'eggs',
           'bin', 'develop-eggs']

orig_os_walk = os.walk

def patched_os_walk(path, *args, **kwargs):
    for (dirpath, dirnames, filenames) in orig_os_walk(path, *args, **kwargs):
        if '.git' in dirnames:
            # We're probably in our own root directory.
#            print("MONKEY PATCH: omitting a few directories like var/...")
            dirnames[:] = list(set(dirnames) - set(TO_OMIT))
        yield (dirpath, dirnames, filenames)

os.walk = patched_os_walk

