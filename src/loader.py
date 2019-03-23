import yaml
import os


class CustomLoader(yaml.SafeLoader):

    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super().__init__(stream)

    def include(self, node):
        """
        Loads another YAML file. Write '!include path/to/file.yaml'.
        """
        filename = os.path.join(self._root, self.construct_scalar(node))
        print(os.path.split(filename))
        with open(filename, 'r') as f:
            return yaml.load(f, Loader=CustomLoader)


CustomLoader.add_constructor('!include', CustomLoader.include)
