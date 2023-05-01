# PyVPNGate

Simple script for parsing public VPNGate VPN lists and connecting to available VPN servers.

Right now the script uses GNOME's Network Manager to make connections so 
it should work fine everywhere if there is `nmcli` utility.

## Usage

**Install the script**

```bash
git clone https://github.com/ts-vadim/py-vpngate.git
cd py-vpngate
bash install.sh
```

This will copy the script to `/usr/local/bin` folder.

**Download VPN list from releases**
```bash
vpngate -ur
```

**Run the script**
```bash
vpngate -cb
```

> If you see message like `Request to ... failed` run `vpngate -ur` command.
> The error message can be found in `/usr/local/bin/py-vpngate-src/vpngate.log`
> This may happen because of a restricted access to `vpngate.net` in your country.


**Filter unavailable VPN servers**

(This may take a lot of time)

```bash
vpngate -f
```

**More features**

See the help message for more info on how to use the script.
```bash
vpngate -h
```
