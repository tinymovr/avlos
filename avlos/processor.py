
from avlos.deserializer import deserialize

def generate(system_instance, output_config):
    for module_name, module_config in output_config.modules.items():
        module = importlib.import_module('generators/{}'.format(module_name))
        module.process(system_instance, module_config)