# %%
import gradio as gr
import yaml
import os
from importlib import import_module
from webui.configs.config_manager import default_orch_config
import json


default_sensor_test = '''
{
    "example_sensor.main": {}
}
'''

custom_sensor_config = '''
{
    "0.sweep": "none",
    "1.generic_stepper.main": {"n_steps": 5}
}
'''

class SequenceOrchestrator():
    def __init__(self, loaded_module) -> None:
        self.orch_config = {}
        self.loaded_module = loaded_module

    def interface(self):
        opts = [] + list(self.loaded_module.keys())

        enable = gr.Checkbox(value=True, label="Enable")
        orch_config = gr.Code(default_orch_config, language='json', label="Config")
        orch_opts = gr.Dataset(components=[orch_config],
                               samples=[[default_orch_config], [default_sensor_test], [custom_sensor_config]])
        orch_opts.click(self.update_opt, inputs=orch_opts, outputs=orch_config)

        with gr.Row():
            btn = gr.Button("Set hooks")
            test_btn = gr.Button("Test")

        btn.click(fn=self.set_extention_sequence, inputs=orch_config)
        test_btn.click(fn=self.run_orchestrator)

    def update_opt(self, opt):
        print(opt)
        return opt[0]

    def set_extention_sequence(self, config):
        print(config)
        self.orch_config = json.loads(config)

    def run_orchestrator(self):
        res = {}
        print(self.orch_config)
        for i, (k, v) in enumerate(self.orch_config.items()):
            k = '.'.join(k.split('.')[1:])
            if k in self.loaded_module.keys():
                rtn = self.loaded_module[k].hook(**v)
                curr_k = f"step_{i}"
                res[curr_k] = {"data": rtn,
                               'type': k}
            else:
                print(f"skipping {k}")
        print(res)
        return res
    
    def clean_up(self):
        for _, (k, v) in enumerate(self.orch_config.items()):
            if k in self.loaded_module.keys():
                try:
                    self.loaded_module[k].hook_cleanup()
                except Exception as e:
                    print(str(e))

    
    def __call__(self):
        return self.run_orchestrator()



class ExtensionManager():
    def __init__(self) -> None:
        with open('./extensions/config.yaml','r') as f:
            config = yaml.safe_load(f)

        self.loaded_module = {}
        for k, v in config.items():
                if v['enable']:
                    print(f"Loading extension {k}...")
                    curr_module = f"extensions.{v['module']}"
                    if 'requirement' in v.keys():
                        assert v['requirement'] in self.loaded_module.keys(), f"module {v['requirement']} is required but not found. Check config.yaml?"
                    imported = import_module(curr_module)
                    comp = getattr(imported, v['object'])
                    my_comp = comp()
                    self.loaded_module[v['module']] = my_comp
        
        orchestrator = SequenceOrchestrator(self.loaded_module)
        self.loaded_module['orchestrator'] = orchestrator
        

    def interface(self):
        for k, v in self.loaded_module.items():
            with gr.Tab(k):
                 v.interface()   


def module_loader():
    with open('./extensions/config.yaml','r') as f:
        config = yaml.safe_load(f)

    loaded_module = {}
    for k, v in config.items():
            if v['enable']:
                with gr.Accordion(v['label'], open=False):
                    print(f"Loading extension {k}...")
                    curr_module = f"extensions.{v['module']}"
                    if 'requirement' in v.keys():
                        assert v['requirement'] in loaded_module.keys(), f"module {v['requirement']} is required but not found. Check config.yaml?"
                    imported = import_module(curr_module)
                    comp = getattr(imported, v['object'])
                    my_comp = comp()
                    my_comp.interface()
                    loaded_module[v['module']] = my_comp

if __name__ == '__main__':
    with gr.Blocks(title="extension manager", theme=gr.themes.Default()) as demo:
        module_loader()

    demo.launch()
