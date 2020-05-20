# STM32F072 Sample Circuit

This is a tried and true MCU circuit for an STM32F072.

Things to be aware of:

* The library of parts is available here: https://github.com/clueboard/eagle_libs
* Decoupling caps should be placed near the pins they are connected to in the schematic.
* There is some debate about how necessary the tantalum caps are. I have successfully omitted them.
* The RESET circuit allows you to provide a 1-button entry to DFU, similar to how AVR works.
