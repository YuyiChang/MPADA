# Extension development guide

## Enable an extension

Modify `./extensions/config.json`

Suppose we have an extension under the folder `rp2040_u2if_interface` with gradio components define in `RP2040Components`

```json
{
    "enabled_modules": 
        {"rp2040_u2if_interface": "RP2040Components"}
}
```

## Required API

Within class `RP2040Components`, we require declearing `interface` method for UI initialization.