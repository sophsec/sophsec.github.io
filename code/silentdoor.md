---
layout: page
title: SilentDoor
---

# SilentDoor

* Author: [drraid](/drraid/)
* Language: C

## Description

silentdoor is a proof-of-concept connectionless, PCAP-based backdoor for linux that uses packet sniffing
to bypass netfilter. It sniffs for UDP packets on port 53, runs each packet against a decryption scheme,
if the packet validates than it runs a command.

## Downloads

* [v1.0](/downloads/code/silentdoor.tar.gz)
  * md5: 5a8f02eb1e1d7ca1ff8e7a30603286a3

