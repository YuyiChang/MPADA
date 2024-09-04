import gradio as gr


class SingleSweepComponents():
    def __init__(self) -> None:
        # self.mpada = mpada
        pass

    def set_device(self, ins):
        self.ins = ins

    def single_sweep_tab(self, ins):
        gr.Markdown("# Single sweep")

        with gr.Row():
            with gr.Column():
                num = gr.Number(value=1, label="Number of trigger")
                btn = gr.Button("Start")
            out = gr.Plot()
        btn.click(fn=self.get_data, inputs=ins, outputs=out)

    def get_data(self, ins):
        # self.ins = self.mpada.ins

        ins.write("SENS:SWE:MODE SING;*WAI")
        ins.write("CALC:DATA? SDATA")
        data = self.ins.read()

        print(data)