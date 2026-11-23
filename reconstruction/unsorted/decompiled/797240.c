
void FUN_00797240(long param_1)

{
  ulong uVar1;
  ulong uVar2;
  long *plVar3;
  char cVar4;
  byte bVar5;
  int iVar6;
  undefined4 uVar7;
  code *pcVar8;
  undefined4 local_28 [2];
  long local_20;
  
  plVar3 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  FUN_00774980(0,1);
  FUN_00774980(1,1);
  cVar4 = FUN_007754d0(0);
  if (cVar4 != '\0') {
    bVar5 = FUN_0010c8d0();
    FUN_00774dc0(0,bVar5 ^ 1);
  }
  cVar4 = FUN_007754d0(1);
  if (cVar4 != '\0') {
    bVar5 = FUN_0010c8d0();
    FUN_00774dc0(1,bVar5 ^ 1);
  }
  if (*(char *)(param_1 + 0x30) == '\0') {
    cVar4 = FUN_007662f0();
    if (cVar4 == '\0') {
      local_28[0] = 7;
      FUN_00766320(local_28);
      FUN_0077b710(4);
      *(undefined1 *)(param_1 + 0x30) = 1;
    }
  }
  FUN_00797400();
  FUN_00789640();
  FUN_00797550(param_1);
  iVar6 = FUN_00785060(0);
  if (*(char *)(param_1 + 0x32) == '\0') {
    if (iVar6 == 0x1b) {
      uVar7 = FUN_00785080(0);
      FUN_00783ee0(0x19,uVar7,0);
    }
  }
  else {
    FUN_00784e50(0x19,9);
  }
  FUN_007976b0(param_1);
  uVar1 = *(ulong *)(param_1 + 0x68);
  uVar2 = *(ulong *)(param_1 + 0x78);
  if ((((uVar2 != uVar1) && ((uVar1 & 1) != 0)) && ((uVar2 & 1) == 0)) &&
     ((((uint)uVar1 ^ (uint)uVar2) & *(uint *)(param_1 + 0x48) & 1) == 0)) {
    if (*(code **)(param_1 + 0x50) == (code *)0x0) {
      pcVar8 = *(code **)(param_1 + 0x58);
      if (((ulong)pcVar8 & 1) != 0) {
        pcVar8 = *(code **)(pcVar8 + *(long *)(*(long *)(param_1 + 0x60) + param_1) + -1);
      }
      iVar6 = (*pcVar8)();
    }
    else {
      iVar6 = (**(code **)(param_1 + 0x50))();
    }
    if (iVar6 == 1) {
      *(byte *)(param_1 + 0x70) = *(byte *)(param_1 + 0x70) | 1;
    }
    else if (iVar6 == 2) {
      *(byte *)(param_1 + 0x70) = *(byte *)(param_1 + 0x70) | 1;
      *(byte *)(param_1 + 0x78) = *(byte *)(param_1 + 0x78) | 1;
    }
  }
  cVar4 = FUN_00b9ff80();
  if (cVar4 != '\0') {
    FUN_00783e90(0,0x1b,0x3a);
    FUN_00783ee0(0x19,0x3a,0);
  }
  if (*plVar3 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

