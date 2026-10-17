
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00301470(long param_1,undefined8 *param_2,byte param_3,undefined4 param_4,
                 undefined4 param_5,undefined4 param_6)

{
  undefined8 uVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined1 uVar5;
  int iVar6;
  long lVar7;
  
  *(undefined4 *)(param_1 + 0x44) = param_4;
  *(undefined4 *)(param_1 + 0x48) = param_5;
  *(undefined4 *)(param_1 + 0x4c) = param_6;
  uVar1 = param_2[2];
  uVar2 = param_2[3];
  uVar3 = param_2[4];
  uVar4 = param_2[5];
  *(undefined8 *)(param_1 + 0x38) = param_2[6];
  *(undefined8 *)(param_1 + 0x30) = uVar4;
  *(undefined8 *)(param_1 + 0x28) = uVar3;
  *(undefined8 *)(param_1 + 0x20) = uVar2;
  *(undefined8 *)(param_1 + 0x18) = uVar1;
  uVar1 = *param_2;
  *(undefined8 *)(param_1 + 0x10) = param_2[1];
  *(undefined8 *)(param_1 + 8) = uVar1;
  *(byte *)(param_1 + 0x40) = param_3 | 2;
  *(undefined4 *)(param_1 + 0x54) = 0xffffffff;
  *(undefined4 *)(param_1 + 0x150) = 0xffffffff;
  *(undefined4 *)(param_1 + 0x154) = 0xffffffff;
  FUN_001d3770(param_1 + 0x58);
  uVar2 = uRam0000000001629ed8;
  uVar1 = _DAT_01629ed0;
  *(undefined1 *)(param_1 + 0x1b0) = 0;
  *(undefined8 *)(param_1 + 400) = 0;
  *(undefined8 *)(param_1 + 0x198) = 0;
  *(undefined1 *)(param_1 + 0x1b1) = 0;
  *(undefined8 *)(param_1 + 0x1a0) = uVar1;
  *(undefined8 *)(param_1 + 0x1a8) = uVar2;
  *(undefined4 *)(param_1 + 0x50) = 0xffffffff;
  *(undefined8 *)(param_1 + 0x100) = uVar1;
  *(undefined8 *)(param_1 + 0x108) = uVar2;
  *(undefined1 *)(param_1 + 0x110) = 0;
  iVar6 = FUN_00240840();
  *(undefined1 *)(param_1 + 4) = 0xff;
  if (iVar6 != -1) {
    lVar7 = FUN_002a00c0(iVar6);
    if (lVar7 != 0) {
      lVar7 = FUN_002a2d40(lVar7);
      uVar5 = FUN_002a5520(lVar7 + 8,param_1 + 8);
      *(undefined1 *)(param_1 + 4) = uVar5;
    }
  }
  FUN_00301580(param_1);
  return;
}

