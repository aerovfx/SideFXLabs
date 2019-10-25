import xml.etree.ElementTree as ET
import glob
import os

import logging

logging.basicConfig(level=logging.DEBUG)
current_folder = os.path.dirname(__file__)
repo_dir = os.getenv("WORKSPACE", "C:\\SideFXLabs")

NODES_TO_IGNORE = ["sop_rc_register_images", "rc_texture_model"]

def check_gamedev_namespace(node):
    # print("Checking GameDev Namespace")
    return node.type().nameComponents()[1] == "labs"


def check_gamedev_prefix(node):

    return node.type().description().split()[0] == "Labs"


def check_icon(node):
    # print("Checking Icon")
    return node.type().icon() != "SOP_subnet"


def check_output_node(node):
    # print("Checking Output Node")
    if node.type().category().name() != "Sop":
        return True

    for child in node.children():
        if child.type().name() == "output":
            return True

    return False


def check_input_names(node):

    for name in node.inputLabels():
        if "Sub-Network" in name:
            return False

    return True


def check_tab_submenu(node):
    # print("Checking Tab SubMenu")
    xml_data = node.type().definition().sections()['Tools.shelf'].contents()
    root = ET.fromstring(xml_data)

    submenu_name = None
    for submenu in root.iter("toolSubmenu"):
        submenu_name = submenu.text
        break

    if "Labs" not in submenu_name or submenu_name == None:
        return False

    return True


def check_version(node):
    # print("Checking Version")

    version = node.type().definition().version()
    if version != "":
        return True
    return False


def check_analytics(node):
    sections = node.type().definition().sections()
    if "OnCreated" in sections:
        if "analytics" in sections["OnCreated"].contents():
            return True

def check_parm_names(node):
    parmTemplates = list(node.type().parmTemplates())

    for parmtemplate in parmTemplates:
        name = parmtemplate.name()
    
        if name.startswith('newparameter') or name.startswith('parm') or name.startswith('folder'):
            return False
    return True


def run_tests(node):
    node_name = node.type().description() + "(" + node.type().name() + ")"

    if not check_gamedev_namespace(node):
        print(node_name + ": __SmoketestError__ : Incorrect Namespace")

    if not check_icon(node):
        print(node_name + ": __SmoketestWarning__ : Generic Icon")

    if not check_output_node(node):
        print(node_name + ":  __SmoketestWarning__ : Missing Output Node")

    if not check_input_names(node):
        print(node_name + ":  __SmoketestWarning__ : Generic Input Name ")

    if not check_tab_submenu(node):
        print(node_name + ": __SmoketestError__ : Wrong Tab Menu Entry")

    if not check_analytics(node):
        print(node_name + ": __SmoketestWarning__ : No Analytics Code")

    if not check_parm_names(node):
        print(node_name + ": __SmoketestNote__ : Contains Invalid Parm Names")


if __name__ == '__main__':
    import hou

    # node = hou.selectedNodes()[0]

    hda_files = glob.glob(os.path.join(repo_dir, "otls/*.hda"))

    cop_node = hou.node("/img").createNode("img")
    obj_node = hou.node("/obj")
    geo_node = hou.node("/obj").createNode("geo")
    rop_node = hou.node("/out")
    shop_node = hou.node("/shop")

    categories = {"Cop2": cop_node, "Object": obj_node, "Driver": rop_node, "Sop": geo_node, "Shop": shop_node}
    for hda_file in hda_files:

        hda_file = hda_file.replace("\\", "/")
        hou.hda.installFile(hda_file)
        definitions = hou.hda.definitionsInFile(hda_file)
        for definition in definitions:
            name = definition.nodeType().name()

            if name not in NODES_TO_IGNORE:
                print("Attempting to Create Node : " + name)
                try:
                    category = definition.nodeType().category().name()
                    new_node = categories[category].createNode(name)
                    run_tests(new_node)
                    new_node.destroy()
                except Exception as e:
                    print(e)
                print("Tests Completed on : " + name)

            # run_tests(node)
    hou.exit()

