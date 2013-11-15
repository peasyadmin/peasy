/*
 * Copyright © 2011 Stéphane Raimbault <stephane.raimbault@gmail.com>
 *
 * License ISC, see LICENSE for more details.

 * This library implements the Modbus protocol.
 * http://libmodbus.org/
 *
 */

#ifndef EsPeEsModbusSlave_h
#define EsPeEsModbusSlave_h

#include <inttypes.h>
#if defined(ARDUINO) && ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
  #include <pins_arduino.h>
#endif

#define MODBUS_BROADCAST_ADDRESS 0

/* Protocol exceptions */
#define MODBUS_EXCEPTION_ILLEGAL_FUNCTION     1
#define MODBUS_EXCEPTION_ILLEGAL_DATA_ADDRESS 2
#define MODBUS_EXCEPTION_ILLEGAL_DATA_VALUE   3

#define MODBUS_TIMEOUT_MICROSECONDS 10
#define MODBUS_TIMEOUT_RETRIES 1000

class EsPeEsModbusSlave {
public:
    EsPeEsModbusSlave(uint8_t slave);
    void setup(long baud);
    int loop(uint16_t* tab_reg, uint16_t nb_reg, char averageCycleIndex, char cycleIndex, char timeoutIndex, char errorIndex);
private:
    int _slave;
    unsigned int _totalTimeouts;
    unsigned int _totalErrors;
    unsigned long _lastCycleTime;
    unsigned long _averageCycleTime;
    unsigned long _currentCycleTime;
    unsigned long long _averageFullValue;
    unsigned long long _averageCounter;
    char _currentError;
};

void readInput();
void writeOutput();

#endif
