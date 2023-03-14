from argparse import ArgumentParser
from datetime import datetime
from xml.dom import minidom

from message_set_loader import load_message_set
from dfdl_model_generator import (
    generate_dfdl_model,
    add_message_set_element_to_dfdl_model,
    get_field_type,
    create_dfdl_element,
    create_property,
    create_annotation,
)
from command_line_parser import parse_command_line_args
from constants import NSMAP
from data_type_mappings import MRM_TO_DFDL_DATA_TYPE_MAPPING
from configurations import (
    MODEL_NAME,
    TARGET_NAMESPACE,
    FIELD_NAMING_CONVENTION,
    MAX_OCCURS_UNBOUNDED,
    DATA_TYPE_OVERRIDE,
    COMPLEX_TYPE_NAME,
    ROOT_ELEMENT_NAME,
    NAMESPACE_PREFIX,
)


def main():
    # Parse command line arguments
    args = parse_command_line_args()

    # Load the MRM message set
    message_set_root = load_message_set(args.input_file)

    # Create a new DFDL message model
    dfdl_model = generate_dfdl_model(
        model_name=args.schema_name or MODEL_NAME,
        target_namespace=args.target_namespace or TARGET_NAMESPACE,
        field_naming_convention=args.field_naming_convention or FIELD_NAMING_CONVENTION,
        max_occurs_unbounded=args.max_occurs_unbounded or MAX_OCCURS_UNBOUNDED,
        mrm_to_dfdl_data_type_mapping=MRM_TO_DFDL_DATA_TYPE_MAPPING,
        data_type_override=args.data_type_override or DATA_TYPE_OVERRIDE,
        complex_type_name=args.complex_type_name or COMPLEX_TYPE_NAME,
        root_element_name=args.root_element_name or ROOT_ELEMENT_NAME,
        namespace_prefix=args.prefix or NAMESPACE_PREFIX,
    )

    # Add the message set elements to the DFDL model
    for element in message_set_root:
        add_message_set_element_to_dfdl_model(element, dfdl_model)

    # Format the DFDL model as XML and write it to a file
    dfdl_xml = minidom.parseString(etree.tostring(dfdl_model)).toprettyxml()
    with open(args.output_file, "w") as f:
        f.write(dfdl_xml)


if __name__ == "__main__":
    main()
