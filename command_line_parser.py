from argparse import ArgumentParser

class CommandLineParser:
    def __init__(self):
        self.parser = ArgumentParser()
        self.parser.add_argument("input_file", help="Path to input message set file")
        self.parser.add_argument("output_file", help="Path to output DFDL schema file")
        self.parser.add_argument("-t", "--target_namespace", help="Target namespace for DFDL schema")
        self.parser.add_argument("-n", "--schema_name", help="Name of the DFDL schema")
        self.parser.add_argument("-p", "--prefix", help="Namespace prefix for DFDL schema")
        self.parser.add_argument("-c", "--complex_type_name", help="Name of the DFDL complex type")
        self.parser.add_argument("-r", "--root_element_name", help="Name of the DFDL root element")

    def parse_args(self):
        return self.parser.parse_args()
