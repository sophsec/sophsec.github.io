---
layout: page
title: GrimCreeper
---

# GrimCreeper

* Author: [drraid](/drraid/)
* Language: C

## Description

GrimCreeper is a service which SophSec submitted to Kenshoto for their last year of hosting CTF at Defcon.
It contains an interesting integer bug in one of the size checks - this bug only occurs if the bit
shifting used for the size check happens on the same line, if spread into two lines the check works.
Following that is a book-example stack overflow.

## Downloads

* [v0.01](/downloads/code/grimecreeper.c)
  * md5: 093f5f950a308a7ed9cafe30b8945200

