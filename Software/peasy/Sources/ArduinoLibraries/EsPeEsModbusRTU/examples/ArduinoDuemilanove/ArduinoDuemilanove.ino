#include <EsPeEsModbusRTU.h>

#define Baudrate 115200
#define Adress  1
#define ModbusWatchDog 500

enum 
{ 
  AnalogIn0,     
  AnalogIn1,        
  AnalogIn2,        
  AnalogIn3,        
  AnalogIn4,        
  AnalogIn5,
  PinMode,
  DigitalInput,
  DigitalOutput,
  LastCycleTime,
  AverageCycleTime,
  TotalTimeouts,
  TotalErrors,
  TotalRegisterSize 
};

EsPeEsModbusSlave Slave(Adress);
unsigned int Registers[TotalRegisterSize];
unsigned long CurentModbusWatchDog = 0;

unsigned int OldPinMode = 0;
unsigned int OldPinDigitalOutput = 0;
char i = 0;

void setup()
{
  // Setup modbus
  Slave.setup(Baudrate);
}

void loop()
{
  // Update modbus process
  if(Slave.loop(Registers, TotalRegisterSize, AverageCycleTime, LastCycleTime, TotalTimeouts, TotalErrors) > 0)
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
    for (i = 2; i < 14; i++)
    {
      digitalWrite(i, LOW);
      pinMode(i, LOW);
    }
    OldPinMode = 0;
    OldPinDigitalOutput = 0;
}

void readInput()
{
  i = i + 1;
  if(i > 5) i = 0;
  Registers[i] = analogRead(i);
  
  // Read all digital input pins
  for (i = 2; i < 14; i++)
  {
    if(!bitRead(Registers[PinMode], i))
    {
      bitWrite(Registers[DigitalInput], i, digitalRead(i));
    }
  }
}

void writeOutput()
{
  // Set all pin modes
  if(Registers[PinMode] != OldPinMode)
  {
    for (i = 2; i < 14; i++)
    {
      pinMode(i, bitRead(Registers[PinMode], i));
    }
    OldPinMode = Registers[PinMode];
  }
  
  // Write all digital outputs pins
  if(Registers[DigitalOutput] != OldPinDigitalOutput)
  {
    for (i = 2; i < 14; i++)
    {
      if(bitRead(Registers[PinMode], i))
      {
        digitalWrite(i, bitRead(Registers[DigitalOutput], i));
      }
    }
    OldPinDigitalOutput = Registers[DigitalOutput];
  }
}
