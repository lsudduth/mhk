[![Build Status](https://travis-ci.com/nickrusso42518/mhk.svg?branch=master)](https://travis-ci.com/nickrusso42518/mhk)

# Cisco Surge Hospital Kit (SHK)
Experimental script to build configurations for all devices in the kit.

After running the script, the `telephony_prefix` specified for each
node definition is represented by a subdirectory in `outputs/`. Within
that subdirectory are the configuration files in a given SHK.

Given this `inputs.yml` file:
```
---
node_list:
  - telephony_prefix: 1000
    ipv4_network: 172.16.0.0/22
    index_offset: 0
  - telephony_prefix: 2000
    ipv4_network: 172.16.4.0/22
    index_offset: 20
...
```

You will see this result in the file system:
```
$ tree outputs/
outputs/
|-- 1000
|   |-- asw1.txt
|   |-- asw2.txt
|   |-- asw3.txt
|   |-- asw4.txt
|   |-- asw5.txt
|   |-- dsw.txt
|   `-- rtr.txt
`-- 2000
    |-- asw1.txt
    |-- asw2.txt
    |-- asw3.txt
    |-- asw4.txt
    |-- asw5.txt
    |-- dsw.txt
    `-- rtr.txt
```
