# %%
import gradio as gr
import serial
import serial.tools.list_ports
import time


class SerialManager():
    def __init__(self, port='COM21', auto_init=True, device='pico') -> None:
        if port is not None:
            self.ser = serial.Serial(timeout=5, baudrate=9600)
            self.ser.port = port
        else:
            if auto_init:
                self.auto_init(device=device)
            else:
                raise NotImplementedError
    
    def auto_init(self, device='pico'):
        for a in list(serial.tools.list_ports.comports()):
            if device in a.description.lower():
                port = a
                break
        print('auto select port: ', port)
        self.ser = serial.Serial(timeout=5, baudrate=9600)
        self.ser.port = port.device

    def toggle_serial(self, state):
        if state:
            self.ser.open()
        else:
            self.ser.close()

    def interface(self):
        ser_enable = gr.Checkbox(value=False)
        with gr.Row():
            with gr.Column():
                text_in = gr.Text(label='input', value="1")
                dataset = gr.Dataset(components=[text_in], samples=[["SEN:ANGLE 5"], ["SEN:TOF 5"], ["ACT:STEPPER 1"]])
            
            text_out = gr.Text(label='output')

        btn = gr.Button()
        btn.click(self.query, inputs=text_in, outputs=text_out)
        dataset.click(lambda a: a[0], inputs=dataset, outputs=text_in)
        
        ser_enable.change(self.toggle_serial, inputs=ser_enable)

    def query(self, input):
        input = bytes(input + '\n', 'utf-8')
        print(input)
        self.ser.reset_input_buffer()
        self.ser.write(input)

        # input_buffer = []
        # for i in range(10):
        #     aa = self.ser.read(128)
        #     print(aa)

        # time.sleep(1)
        # response = self.ser.readline()
        # print(response)
        # max_line = 0
        # while response != "EOT" and max_line < 10:
        #     response = self.ser.readline()
        #     print(response)
        #     max_line += 1

        # response = self.ser.read(128)
        # response = self.ser.read(self.ser.inWaiting()).decode('ascii') 
        response = self.ser.read_until(expected=b'EOT').decode('ascii') 
        
        return response
    
    def flush(self):
        self.ser.read(self.ser.inWaiting()).decode('ascii') 

    def hook(self, command):
        if not self.ser.isOpen(): self.toggle_serial(True)
        response = self.query(command)
        return response


if __name__ == '__main__':
    sm = SerialManager(port='COM21')
    
    with gr.Blocks() as demo:
        sm.interface()
    demo.launch()

# # %%
# ser.close()