from flask import Flask, render_template, request, redirect
from mpada import port_mapping

app = Flask(__name__)

HwSpec = port_mapping.HwSpec()

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
    return render_template("sweep_settings.html")
