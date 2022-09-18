import numpy as np
from flask import Markup

class HwSpec:
    def __init__(self):
        self.ant_num_tx = 3
        self.ant_num_rx = 3
        self.rfs_num_ctl = 3
        self.rfs_num_port = 8
        self.mcu_num_gpio = 6
        self.dict_ant = {}
        self.dict_gpio = {}
        self.dict_ant_gpio = {}

    def get_info(self):
        print("\n=======================================================")
        print('Information of hardware specification:')
        print('- Antenna: # of TX = {:}, # of RX = {:}'.format(self.ant_num_tx, self.ant_num_rx))
        print('- RF Switch: # of control lane = {:}, # of RF port = {:}'.format(self.rfs_num_ctl, self.rfs_num_port))
        print('- MCU: # of GPIO = {:}'.format(self.mcu_num_gpio))
        print("=======================================================\n")

    # create hardware port mapping table
    def get_wiring_ant_rfs(self):
        def format_ant(num, type_str, rfs_num_ctl, dict_ant):
            base_str = ""
            for i in range(num):
                ant_name = type_str + "_{:}".format(i)
                rfs_name = type_str + "_RF{:}".format(i+1)
                rfs_signal = "{0:b}".format(i).zfill(rfs_num_ctl)[::-1]
                dict_ant[ant_name] = rfs_signal
                sub_str = "<tr><td>{:}</td><td>{:}</td><td>{:}</td></tr>".format(ant_name, rfs_name, rfs_signal)
                base_str += sub_str
            return base_str

        # number of control lane on each RF switch
        rfs_num_ctl = self.rfs_num_ctl

        # init ant to command lookup, key=ANT name, val=control signal
        dict_ant = dict()

        # table elements for ANT to RFS wiring
        wiring_tx = format_ant(self.ant_num_tx, 'TX', rfs_num_ctl, dict_ant)
        wiring_rx = format_ant(self.ant_num_rx, 'RX', rfs_num_ctl, dict_ant)

        table_str = """
            <table><thead><tr>
                <th>Antenna Port</th>
                <th>RF Switch Port</th>
                <th>RF Switch Control Signal</th>
            </tr></thead><tbody>{:}</tbody></table>
        """

        self.dict_ant = dict_ant

        return Markup(table_str.format(wiring_tx + wiring_rx))

    # create wiring table between mcu and rf switches
    def get_wiring_gpio(self, skipped_gpio=()):
        dict_gpio = dict()
        base_str = ""
        curr_gpio = 0
        for port_type in ("TX", "RX"):
            gpio_list = []
            for j in range(self.rfs_num_ctl):
                name_control_ln = port_type + "_" + chr(65 + j)
                while curr_gpio in skipped_gpio:
                    curr_gpio += 1
                name_gpio = "GPIO_" + str(curr_gpio) 
                gpio_list.append(name_gpio)
                curr_gpio += 1
                base_str += "<tr><td>{:}</td><td>{:}</td></tr>".format(name_control_ln, name_gpio)
            dict_gpio[port_type] = gpio_list

        table_str = """
            <table><thead><tr>
                <th>RF Switch Control Lane</th>
                <th>MCU GPIO</th>
            </tr></thead><tbody>{:}</tbody></table>
        """

        self.dict_gpio = dict_gpio

        return Markup(table_str.format(base_str))

    # get GPIO value mapping for each antenna
    def get_ant_gpio_map(self):
        self.dict_ant_gpio = dict()
        for key, val in self.dict_ant.items():
            gpio = self.dict_gpio[key[:2]]
            self.dict_ant_gpio[key] = (gpio, list(val))
        # print(self.dict_ant_gpio)

    #########
    # parse hardware configuration from HTTP POST
    def parse_ant_rfs_post(self, form):
        for key, val in form.items():
            val = int(val)
            if key == 'num_rfs_ctl':  
                self.rfs_num_port = pow(2, val)
                self.mcu_num_gpio = 2 * val
            elif key == 'num_tx':
                self.ant_num_tx = val
            elif key == 'num_rx':
                self.ant_num_rx = val
            else:
                print('Illegal key found. Check html?')
    

###############################################


def get_hw_map_table():
    return None



    