import json

# with open('webui/configs/default_port_mapping.json') as f:
#     default_port_mapping = json.load(f)

with open('webui/configs/default_port_mapping.json') as f:
    default_port_mapping = f.read()

with open('webui/configs/default_gpio_mapping.json') as f:
    default_gpio_mapping = f.read()

with open('webui/configs/default_sweep_sequence.json') as f:
    default_sweep_sequence = f.read()

with open('webui/configs/default_orch_config.json') as f:
    default_orch_config = f.read()