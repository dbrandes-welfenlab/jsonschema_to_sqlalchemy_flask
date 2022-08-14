import pkgutil
import json
import locale

#TODO: maybe replace with importlib stuff when more stable. See:
# https://stackoverflow.com/a/58941536
# https://gitlab.com/python-devs/importlib_resources/-/issues/58#note_329352693

def txt_load(relative_path):
    data = pkgutil.get_data("jsonschema_to_sqlalchemy_flask", relative_path)
    return data.decode(locale.getpreferredencoding())

def json_load(path, external=True):
    if external:
        with(open(path)) as fh:
            return json.load(fh)
    return json.loads(txt_load(path))

def txt_write(txt, path):
    with open(path, "w") as filehandle:
        filehandle.write(txt)