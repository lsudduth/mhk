login username: SHK-102-ADMIN
login password: k7kwIfrz1ufp
enable password: k7kwIfrz1ufp

domain name: hospital.com
dmvpn target: 192.0.2.1

3-digit telephony prefix: 102
-------------------------------
tui = 10200
ward hunt = 10201
admin hunt = 10202
hunt range = 10203 - 10209
audio page = 10210
autoreg range = 10211 - 10249
conf phone = 10250
admin phone = 10251 - 10260
manual range = 10261 - 10299

Subnets:
- full: 192.168.4.0/22
- data: 192.168.4.0/23
- biomed: 192.168.6.0/26
- voice: 192.168.6.64/26
- mgmt: 192.168.6.128/27
- special: 192.168.6.160/28
- loopback: 192.168.6.176/28


Addressing on rtr:
- lb0: 192.168.6.177

Addressing on dsw:
- lb0: 192.168.6.178
- data_svi10: 192.168.5.254
- biomed_svi20: 192.168.6.62
- voice_svi30: 192.168.6.126
- mgmt_svi40: 192.168.6.158
- special_svi50: 192.168.6.174

Addressing on wlc:
- data_svi10: 192.168.5.250
- biomed_svi20: 192.168.6.58
- voice_svi30: 192.168.6.122
- mgmt_svi40: 192.168.6.154
- mgmt_svi40_hex: C0A8069A
- special_svi50: 192.168.6.170

Addressing on asw1:
- mgmt_svi40: 192.168.6.131

Addressing on asw2:
- mgmt_svi40: 192.168.6.132

Addressing on asw3:
- mgmt_svi40: 192.168.6.133

Addressing on asw4:
- mgmt_svi40: 192.168.6.134

Addressing on asw5:
- mgmt_svi40: 192.168.6.135



WLANs (SSID and PSK):
- data: SHK-102-DATA / 2DE56Ga1
- biomed: SHK-102-BIOMED / OaeWTyTH
- voice: SHK-102-VOICE / otQf6BQZ
