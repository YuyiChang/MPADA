# %%
import pyvisa

rm = pyvisa.ResourceManager('@py')
rest_list = rm.list_resources() # show all equipments
print("Resource found: ", rest_list)

# %%
ins = rm.open_resource(rest_list[1])
print(ins.query('*IDN?'))

