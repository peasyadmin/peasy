#include <EsPeEsModbusRTU.h>

#define Baudrate 115200
#define Adress  1
#define ModbusWatchDog 500

enum 
{ 
  // Write your register here ... 
  
  // Don't delete these already defined registers.
  CycleTime,
  TotalTimeouts,
  TotalErrors,
  TotalRegisterSize 
};

EsPeEsModbusSlave Slave(Adress);
unsigned int Registers[TotalRegisterSize];
unsigned long CurentModbusWatchDog = 0;

void setup()
{
  // Setup modbus
  Slave.setup(Baudrate);
}

void loop()
{
  // Update modbus process
  if(Slave.loop(Registers, TotalRegisterSize, CycleTime, TotalTimeouts, TotalErrors) > 0)
  {
    CurentModbusWatchDog = millis();
  }
  else
  {
    if((millis() - CurentModbusWatchDog) > ModbusWatchDog)
    {
        reset();
    }
  }
}

void reset()
{
  // Write your reset code here ...
}

void readInput()
{
  // Write your input code here ...
}

void writeOutput()
{
  // Write your output code here ...
}
