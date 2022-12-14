from flask import Flask, render_template, request, redirect, send_file
from mpada import port_mapping, vna_sweep
from mpada_test import test_sweep

app = Flask(__name__)

HwSpec = port_mapping.HwSpec()
VnaSpec = vna_sweep.VnaSweep()

@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        # parse hw config
        # HwSpec.get_info()
        HwSpec.parse_ant_rfs_post(request.form)
        # HwSpec.get_info()
        # navigate to hardware mapping table creation
        return redirect('/hw_map')
    return render_template('index.html')

@app.route("/hw_map", methods=["GET", "POST"])
def create_port_mapping_table():
    # print("switched to mapping table gen")
    print(HwSpec.get_info())
    
    table_ant = HwSpec.get_wiring_ant_rfs()
    table_gpio = HwSpec.get_wiring_gpio()
    HwSpec.get_ant_gpio_map()

    if request.method == "POST":
        return redirect("/sweep_settings")

    # return port_mapping.get_wiring_gpio(HwSpec)
    return render_template('hw_map.html', table_ant=table_ant, table_gpio=table_gpio)

@app.route("/sweep_settings", methods=["GET", "POST"])
def create_sweep_settings():
    HwSpec.get_ant_gpio_map() # make sure hw map is updated

    if request.method == "POST":
        VnaSpec.parse_sweep_post(request.form, (HwSpec.ant_list_tx, HwSpec.ant_list_rx))
        return redirect("/sweeping")

    return render_template("sweep_settings.html")

@app.route("/sweeping", methods=["GET", "POST"])
def create_sweeping():
    HwSpec.get_ant_gpio_map() # make sure hw map is updated
    # print(HwSpec.dict_ant_gpio)
    # print(VnaSpec.sweep_pair)
    table_sweep = VnaSpec.get_sweep_table()
    fig_sweep = test_sweep.get_blank_fig_base64()

    if request.method == "POST":
        print(request.form.keys())
        if "start-sweep-demo" in request.form.keys(): # demo mode sweep
            print("Start sweeping... (Demo)")
            VnaSpec.sweep(HwSpec.dict_ant_gpio, demo=True)
            fig_sweep = VnaSpec.fig
        elif "start-sweep-vna" in request.form.keys():
            print("Start sweeping...")
            VnaSpec.sweep(HwSpec.dict_ant_gpio, demo=False)
            fig_sweep = VnaSpec.fig
        elif "vna-init" in request.form.keys():
            print("Initializing VNA connection")
            VnaSpec.init_vna()
        elif "vna-reset" in request.form.keys():
            print("reste VNA...")
        # save the data if needed
        elif "save-sweep" in request.form.keys():
            print("save the data")
            f = VnaSpec.save_data()
            return send_file(f, download_name="test.csv", as_attachment=True)
    return render_template("sweeping.html", table_sweep=table_sweep, fig_sweep=fig_sweep)

