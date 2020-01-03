import tarfile
from logger import Logger
import scan
import StringIO


def plugin(filename, data=None):
        if data is not None:
            try:
                # filelike_obj = StringIO.StringIO(data)
                filelike_obj = StringIO.StringIO(data)
                tar = tarfile.open(fileobj=filelike_obj)
            except tarfile.TarError as e:
                Logger().log_error(e)
                return
        else:
            try:
                tar = tarfile.open(filename)
            except tarfile.TarError as e:
                Logger().log_error(e)
                return
        """ For each file in the tarball, run it through the scanner """
        for file in tar.getmembers():
            try:
                inner_file = tar.extractfile(file)
            except Exception as e:
                Logger().log_error(e)
                continue

            if not inner_file:
                continue
            try:
                inner_file_content = inner_file.read()
            except tarfile.TarError as e:
                Logger().log_error(e)
                continue
            if not inner_file_content:
                continue
            scan.Scanner().scan(filename + "/" + file.name, inner_file_content)

        tar.close()
