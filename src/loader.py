import os

import yaml


class CustomLoader(yaml.SafeLoader):
    def __init__(self, stream):
        if hasattr(stream, "name"):
            self._root = os.path.split(stream.name)[0]
        else:
            self._root = None
        super().__init__(stream)

    def include(self, node):
        """
        Loads another YAML file. Write '!include path/to/file.yaml'.
        """
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, "r") as f:
            return yaml.load(f, Loader=CustomLoader)


CustomLoader.add_constructor("!include", CustomLoader.include)
