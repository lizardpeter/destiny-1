
byte FUN_005795a0(long param_1)

{
  char cVar1;
  byte bVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  byte bVar6;
  byte bVar7;
  
  cVar1 = *(char *)(param_1 + 0x5c1c);
  bVar3 = 0;
  bVar2 = 0;
  if (*(int *)(param_1 + 0x8000) != -1) {
    bVar2 = FUN_0063fed0();
  }
  if (*(int *)(param_1 + 0x8004) != -1) {
    bVar3 = FUN_0063fed0();
  }
  bVar6 = 0;
  bVar4 = 0;
  if (*(int *)(param_1 + 0x8008) != -1) {
    bVar4 = FUN_0063fed0();
  }
  if (*(int *)(param_1 + 0x800c) != -1) {
    bVar6 = FUN_0063fed0();
  }
  bVar7 = 0;
  bVar5 = 0;
  if (*(int *)(param_1 + 0x8010) != -1) {
    bVar5 = FUN_0063fed0();
  }
  if (*(int *)(param_1 + 0x8014) != -1) {
    bVar7 = FUN_0063fed0();
  }
  return cVar1 != '\0' | bVar2 | bVar3 | bVar4 | bVar6 | bVar5 | bVar7;
}

