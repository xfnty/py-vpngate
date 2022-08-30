# PyVPNGate

Simple script for parsing public VPNGate VPN lists and connecting to available VPN servers.

Right now the script uses GNOME's Network Manager to make connections so 
it should work fine everywhere if there is `nmcli` utility.

<!-- However support for connecting using **OpenVPN** and **PowerShell** will be added soon. -->

## Usage

**Install the script**

```bash
git clone https://github.com/ts-vadim/py-vpngate.git
cd py-vpngate
bash install.sh
```

This will copy the script to `/usr/local/bin` folder.

**Run the script**

```bash
vpngate -cb
```

This command will download VPN list from [VPNGate](https://www.vpngate.net/api/iphone) 
and attempt to connect to best VPN by host speed specified in downloaded CSV list.

> If you see message like `Request to ... failed`
> try to [downloading](https://github.com/ts-vadim/py-vpngate/releases) 
> VPN list from releases page 
> and later updating it *after* connecting to the VPN.
> 
> Also the error message could be found in `/usr/local/bin/py-vpngate-src/vpngate.log`

**More features**

See the help message for more info on how to use the script.
```bash
vpngate -h
```
