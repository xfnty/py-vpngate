#!/bin/bash

rm -r /usr/local/bin/py-vpngate-src &> /dev/null
rm -r /usr/local/bin/vpngate &> /dev/null
cp -f -r ./src /usr/local/bin/py-vpngate-src
cp -f ./vpngate /usr/local/bin/vpngate
chmod +x /usr/local/bin/vpngate
