# RB-UPF01: Masked User Plane 1 Health Check Runbook

## Section 1: To check BGP status, they must be UP and connected
- `show router  100 bgp summary`
- `show router  200 bgp summary`
- `show router  1300 bgp summary`
- `show router 300 bgp summary`

## Section 2: To check BFD status, they must be UP
- `show router  Base bfd session`
- `show router  13     bfd session`
- `show router  100 bfd session`
- `show router  101 bfd session`
- `show router  102 bfd session`
- `show router  103 bfd session`
- `show router  104 bfd session`
- `show router  105 bfd session`
- `show router  106 bfd session`
- `show router  107 bfd session`
- `show router  108 bfd session`
- `show router  109 bfd session`
- `show router  200 bfd session`
- `show router  201 bfd session`
- `show router  202 bfd session`

## Section 3: To check interface status, they must be UP
- `show router  Base interface`
- `show router  13     interface`
- `show router  100 interface`
- `show router  101 interface`
- `show router  102 interface`
- `show router  103 interface`
- `show router  104 interface`
- `show router  105 interface`
- `show router  106 interface`
- `show router  107 interface`
- `show router  108 interface`
- `show router  109 interface`
- `show router  200 interface`
- `show router  201 interface`
- `show router  202 interface`

## Section 4: To check mac details, they must not be blank along the interface name
- `show router  Base arp`
- `show router  13  arp`
- `show router  100 arp`
- `show router  101 arp`
- `show router  102 arp`
- `show router  103 arp`
- `show router  104 arp`
- `show router  105 arp`
- `show router  106 arp`
- `show router  107 arp`
- `show router  108 arp`
- `show router  109 arp`
- `show router  200 arp`
- `show router  201 arp`
- `show router  202 arp`

## Section 5: To check system information and active alarms on the node. Highlight if any major alarm observed
- `show system information`
- `show system alarm`
- `show system alarm cleared`

## Section 6: Check NTP status, must be connected
- `show system ntp`

## Section 7: To check fabric status, they must be connected
- `show system virtual-fabric`

## Section 8: Check snmp status
- `show snmp counters`

## Section 9: Check VM/card and MDA status, in case down, kindly report
- `show vm`
- `show mda`
- `show vm 1 detail`
- `show vm 2 detail`
- `show vm 3 detail`
- `show vm 4 detail`
- `show vm 5 detail`
- `show vm 6 detail`
- `show vm 7 detail`
- `show vm 8 detail`
- `show vm 9 detail`
- `show vm 10 detail`
- `show vm 11 detail`
- `show vm 12 detail`
- `show vm 13 detail`

## Section 10: Check Admin State and Oper state are UP, in case any issue seen, kindly highlight
- `show mobile-gateway system`

## Section 11: Check cpu utilization and memory utilization per VM
- `show mobile-gateway ism-mg cpu`
- `show mobile-gateway ism-mg memory-pools`

## Section 12: Check VM/card CPU utilization core wise, in case high, kindly report
- `show vm 1 cpu`
- `show vm 2 cpu`
- `show vm 3 cpu`
- `show vm 4 cpu`
- `show vm 5 cpu`
- `show vm 6 cpu`
- `show vm 7 cpu`
- `show vm 8 cpu`
- `show vm 9 cpu`
- `show vm 10 cpu`
- `show vm 11 cpu`
- `show vm 12 cpu`
- `show vm 13 cpu`
- `show vm 14 cpu`
- `show vm 15 cpu`

## Section 13: Check memory pool utilization
- `show vm 1 memory-pools`
- `show vm 2 memory-pools`
- `show vm 3 memory-pools`
- `show vm 4 memory-pools`
- `show vm 5 memory-pools`
- `show vm 6 memory-pools`
- `show vm 7 memory-pools`
- `show vm 8 memory-pools`
- `show vm 9 memory-pools`
- `show vm 10 memory-pools`
- `show vm 11 memory-pools`
- `show vm 12 memory-pools`
- `show vm 13 memory-pools`
- `show vm 14 memory-pools`
- `show vm 15 memory-pools`

## Section 14: Check core details
- `show vm 1  ht-pairs`
- `show vm 2  ht-pairs`
- `show vm 3  ht-pairs`
- `show vm 4  ht-pairs`
- `show vm 5  ht-pairs`
- `show vm 6  ht-pairs`
- `show vm 7  ht-pairs`
- `show vm 8  ht-pairs`
- `show vm 9  ht-pairs`
- `show vm 10 ht-pairs`
- `show vm 11 ht-pairs`
- `show vm 12 ht-pairs`
- `show vm 13 ht-pairs`
- `show vm 14 ht-pairs`
- `show vm 15 ht-pairs`

## Section 15: Check virtual fabric core utilization status
- `show vm 1  virtual fp`
- `show vm 2  virtual fp`
- `show vm 3  virtual fp`
- `show vm 4  virtual fp`
- `show vm 5  virtual fp`
- `show vm 6  virtual fp`
- `show vm 7  virtual fp`
- `show vm 8  virtual fp`
- `show vm 9  virtual fp`
- `show vm 10 virtual fp`
- `show vm 11 virtual fp`
- `show vm 12 virtual fp`
- `show vm 13 virtual fp`
- `show vm 14 virtual fp`
- `show vm 15 virtual fp`

## Section 16: Check peer status for all the interfaces listed below status
- `show mobile-gateway pdn ref-point-peer s1u`
- `show mobile-gateway pdn ref-point-peer s11u`
- `show mobile-gateway pdn ref-point-peer gpu`
- `show mobile-gateway pdn ref-point-peer gnu`
- `show mobile-gateway pdn ref-point-peer s4u`
- `show mobile-gateway pdn ref-point-peer s5u`
- `show mobile-gateway pdn ref-point-peer s8u`
- `show mobile-gateway pdn ref-point-peer sx-n4`
- `show mobile-gateway pdn ref-point-stats s2bu`
- `show mobile-gateway pdn ref-point-stats sx-n4`
- `show mobile-gateway pdn statistics summary`

## Section 17: Check group wise stats as per requirement
- `show mobile-gateway pdn statistics group 1`
- `show mobile-gateway pdn statistics group 2`
- `show mobile-gateway pdn statistics group 3`
- `show mobile-gateway pdn statistics group 4`
- `show mobile-gateway pdn statistics group 5`
- `show mobile-gateway pdn statistics group 6`
- `show mobile-gateway pdn statistics group 7`
- `show mobile-gateway pdn statistics group 8`
- `show mobile-gateway pdn statistics group 9`

## Section 18: Check failure statistics as per requirement
- `show mobile-gateway pdn statistics attach-failure-statistics gateway 1`

## Section 19: Check PDN statistics summary as per requirement
- `show mobile-gateway pdn statistics summary | match "PDN" context all`

## Section 20: Check LTE statistics summary as per requirement
- `show mobile-gateway pdn statistics | match "LTE" context all`
  Check APN wise statistics as per requirement

## Section 21: (Note: kindly cross validate mnc-mcc before running command site wise. Do not just copy paste).
- `show mobile-gateway pdn apn "www" statistics`
- `show mobile-gateway pdn apn "iphone" statistics`
- `show mobile-gateway pdn apn "wwwpre" statistics`
- `show mobile-gateway pdn apn "wwwpost" statistics`
- `show mobile-gateway pdn apn "internet" statistics`
- `show mobile-gateway pdn apn "internetpre" statistics`
- `show mobile-gateway pdn apn  "internetpost" statistics`
  Check APN wise statistics as per requirement

## Section 22: (Note: kindly cross validate mnc-mcc before running command site wise. Do not just copy paste).
- `show mobile-gateway pdn apn "ims" statistics >> [MASKED-OP-A] & [MASKED-OP-B]`
- `show mobile-gateway pdn apn "imshome_opA" statistics >> [MASKED-OP-A]`
- `show mobile-gateway pdn apn "imshome_opB" statistics >> [MASKED-OP-A]`
- `show mobile-gateway pdn apn "imsroam_opB" statistics >> Visiting [MASKED-OP-B]`
- `show mobile-gateway pdn apn "imsroam_opA" statistics >> Visiting [MASKED-OP-A]`

## Section 23: Check stats as per requirement
- `show mobile-gateway pdn call-flow-stats summary`

## Section 24: Check sx interface stats as per requirement
- `show mobile-gateway pdn ref-point-stats sx failure-codes`

## Section 25: Check log for major event or alarm
- `show log log-id 99`
- `show log log-id 100`
- `show log log-id 98`
- `show log log-id 45`

## Section 26: Check IP-pool utilization (You can check block size, Used, Free and Held count)
- `show router 1301 ip-local-pool-stats`
- `show router 1302 ip-local-pool-stats`
- `show router 1303 ip-local-pool-stats`
- `show router 1304 ip-local-pool-stats`
- `show router 1305 ip-local-pool-stats`
- `show router 1306 ip-local-pool-stats`
- `show router 1307 ip-local-pool-stats`
- `show router 1308 ip-local-pool-stats`
- `show router 1309 ip-local-pool-stats`
- `show router 301 ip-local-pool-stats`
- `show router 302 ip-local-pool-stats`
- `show router 303 ip-local-pool-stats`
- `show router 304 ip-local-pool-stats`
- `show router 305 ip-local-pool-stats`
- `show router 306 ip-local-pool-stats`
