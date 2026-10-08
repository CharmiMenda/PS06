# RB-UPF02: Masked User Plane 2 Health Check Runbook

## Section 1: To check BGP status, they must be UP and connected
- `show router  1000 bgp summary`
- `show router  2000 bgp summary`
- `show router  1400 bgp summary`
- `show router  3000 bgp summary`

## Section 2: To check BFD status, they must be UP
- `show router  Base bfd session`
- `show router  14 bfd session`
- `show router  1000 bfd session`
- `show router  1001 bfd session`
- `show router  1002 bfd session`
- `show router  1003 bfd session`
- `show router  1004 bfd session`
- `show router  1005 bfd session`
- `show router  1006 bfd session`
- `show router  1007 bfd session`
- `show router  1008 bfd session`
- `show router  1009 bfd session`
- `show router  2000 bfd session`
- `show router  2001 bfd session`
- `show router  2002 bfd session`

## Section 3: To check interface status, they must be UP
- `show router  Base interface`
- `show router 14 interface`
- `show router  1000 interface`
- `show router  1001 interface`
- `show router  1002 interface`
- `show router  1003 interface`
- `show router  1004 interface`
- `show router  1005 interface`
- `show router  1006 interface`
- `show router  1007 interface`
- `show router  1008 interface`
- `show router  1009 interface`
- `show router  1400 interface`
- `show router  1401 interface`
- `show router  1402 interface`

## Section 4: To check mac details, they must not be blank along the interface name
- `show router  Base arp`
- `show router 14 arp`
- `show router  1000 arp`
- `show router  1001 arp`
- `show router  1002 arp`
- `show router  1003 arp`
- `show router  1004 arp`
- `show router  1005 arp`
- `show router  1006 arp`
- `show router  1007 arp`
- `show router  1008 arp`
- `show router  1009 arp`
- `show router  1400 arp`
- `show router  1401 arp`
- `show router  1402 arp`

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

## Section 13: Check VM/card Scheduling Health
- `show vm 1 cpu   virtual cpu-scheduling`
- `show vm 2 cpu   virtual cpu-scheduling`
- `show vm 3 cpu   virtual cpu-scheduling`
- `show vm 4 cpu   virtual cpu-scheduling`
- `show vm 5 cpu   virtual cpu-scheduling`
- `show vm 6 cpu   virtual cpu-scheduling`
- `show vm 7 cpu   virtual cpu-scheduling`
- `show vm 8 cpu   virtual cpu-scheduling`
- `show vm 9 cpu   virtual cpu-scheduling`
- `show vm 10 cpu  virtual cpu-scheduling`
- `show vm 11 cpu  virtual cpu-scheduling`
- `show vm 12 cpu  virtual cpu-scheduling`
- `show vm 13 cpu  virtual cpu-scheduling`
- `show vm 14 cpu  virtual cpu-scheduling`
- `show vm 15 cpu  virtual cpu-scheduling`

## Section 14: Check memory pool utilization
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

## Section 15: Check core details
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

## Section 16: Check virtual fabric core utilization status
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

## Section 17: Check peer status for all the interfaces listed below status
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

## Section 18: Check group wise stats as per requirement
- `show mobile-gateway pdn statistics group 1`
- `show mobile-gateway pdn statistics group 2`
- `show mobile-gateway pdn statistics group 3`
- `show mobile-gateway pdn statistics group 4`
- `show mobile-gateway pdn statistics group 5`
- `show mobile-gateway pdn statistics group 6`
- `show mobile-gateway pdn statistics group 7`
- `show mobile-gateway pdn statistics group 8`
- `show mobile-gateway pdn statistics group 9`

## Section 19: Check failure statistics as per requirement
- `show mobile-gateway pdn statistics attach-failure-statistics gateway 1`
  Check APN wise statistics as per requirement

## Section 20: (Note: kindly cross validate mnc-mcc before running command site wise. Do not just copy paste).
- `show mobile-gateway pdn apn "www" statistics`
- `show mobile-gateway pdn apn "iphone" statistics`
- `show mobile-gateway pdn apn "wwwpre" statistics`
- `show mobile-gateway pdn apn "wwwpost" statistics`
- `show mobile-gateway pdn apn "internet" statistics`
- `show mobile-gateway pdn apn "internetpre" statistics`
- `show mobile-gateway pdn apn  "internetpost" statistics`
- `show mobile-gateway pdn apn "ims" statistics >> [MASKED-OP-A] & [MASKED-OP-B]`
- `show mobile-gateway pdn apn "imshome_opA" statistics >> [MASKED-OP-A]`
- `show mobile-gateway pdn apn "imshome_opB" statistics >> [MASKED-OP-A]`
- `show mobile-gateway pdn apn "imsroam_opB" statistics >> Visiting [MASKED-OP-B]`
- `show mobile-gateway pdn apn "imsroam_opA" statistics >> Visiting [MASKED-OP-A]`

## Section 21: check and Ensure no active debug sessions are listed.
- `show debug`
- `show mobile-gateway call-insight ue`

## Section 22: Check stats as per requirement
- `show mobile-gateway pdn call-flow-stats summary`

## Section 23: Check sx interface stats as per requirement
- `show mobile-gateway pdn ref-point-stats sx failure-codes`

## Section 24: Check log for major event or alarm
- `show log log-id 99`
- `show log log-id 100`
- `show log log-id 98`
- `show log log-id 45`

## Section 25: Check IP-pool utilization (You can check block size, Used, Free and Held count)
- `show router 1401 ip-local-pool-stats`
- `show router 1402 ip-local-pool-stats`
- `show router 1403 ip-local-pool-stats`
- `show router 1404 ip-local-pool-stats`
- `show router 1405 ip-local-pool-stats`
- `show router 1406 ip-local-pool-stats`
- `show router 1407 ip-local-pool-stats`
- `show router 1408 ip-local-pool-stats`
- `show router 1409 ip-local-pool-stats`
- `show router 3001 ip-local-pool-stats`
- `show router 3002 ip-local-pool-stats`
- `show router 3003 ip-local-pool-stats`
- `show router 3004 ip-local-pool-stats`
- `show router 3005 ip-local-pool-stats`
- `show router 3006 ip-local-pool-stats`
