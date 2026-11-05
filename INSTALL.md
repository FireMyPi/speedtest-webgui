# Speedtest Web GUI Installation Instructions

## Warning - ```speedtest``` User
### ```install.sh``` creates a new ```speedtest``` user and ```uninstall.sh``` deletes the ```speedtest``` user.  If you already have a ```speedtest``` user on your system, do not run ```install.sh``` or ```uninstall.sh``` without reviewing ```/usr/lib/speedtest-webgui/swg-install.sh``` and editing it to suit your needs.

(The Pakfire ```install.sh``` and ```uninstall.sh``` scripts call the Speedtest Web GUI ```swg-install.sh``` script.)
<br/>


## Preparation

Copy the speedtest-webgui-{version}.ipfire file to your IPFire /root directory using whatever file transfer utility suits you.


## Install

Extract speedtest-webgui-{version}.ipfire to /opt/pakfire/tmp and run install.


>    ```cd /opt/pakfire/tmp```

>    ```tar -xf ~/speedtest-webgui-{version}.ipfire```

>    ```cp ROOTFILES ../db/rootfiles/speedtest-webgui```

>    ```NAME=speedtest-webgui ./install.sh```


## Uninstall

Uninstalling the Speedtest Web GUI will not delete the speedtest log files.

Extract speedtest-webgui-{version}.ipfire to /opt/pakfire/tmp and run uninstall.


>    ```cd /opt/pakfire/tmp```

>    ```tar -xf ~/speedtest-webgui-{version}.ipfire```

>    ```NAME=speedtest-webgui ./uninstall.sh```

>    ```rm ../db/rootfiles/speedtest-webgui```

