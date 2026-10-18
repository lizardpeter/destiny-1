
void FUN_001e5fb0(long param_1,undefined4 param_2,undefined8 param_3)

{
  long lVar1;
  long *plVar2;
  undefined4 uVar3;
  undefined8 uVar4;
  long lVar5;
  long lVar6;
  undefined1 local_138 [256];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_001e81d0();
  *(undefined8 *)(param_1 + 0x328) = param_3;
  uVar3 = FUN_001e7760(1);
  *(undefined4 *)(param_1 + 0x348) = uVar3;
  uVar4 = FUN_001e7840(1,0);
  *(undefined8 *)(param_1 + 0x338) = uVar4;
  uVar4 = FUN_001e7840(1,1);
  *(undefined8 *)(param_1 + 0x340) = uVar4;
  lVar5 = FUN_000b7d80(param_2);
  lVar1 = *(long *)(lVar5 + 0x10);
  FUN_001e88c0(*(undefined8 *)(param_1 + 0x328),(long)(int)(float)*(uint *)(lVar1 + 0x88));
  lVar5 = param_1 + 0x1e;
  lVar6 = FUN_0034e3c0();
  if (*(char *)(lVar6 + 0x7f) == '\0') {
    FUN_00065030(lVar5,lVar1 + 4,0x100);
  }
  else {
    lVar6 = FUN_0034e3f0();
    FUN_00065030(lVar5,lVar6 + 0x125,0x100);
    FUN_00065140(lVar5,lVar1 + 4,0x100);
  }
  *(undefined8 *)(param_1 + 0x360) = 0;
  FUN_000b8220(param_2,local_138);
  FUN_00065140(local_138,&DAT_0161be4b,0x100);
  FUN_000ba0e0(param_1 + 0x120);
  FUN_000884f0(param_1 + 0x120,local_138);
  uVar4 = thunk_FUN_012aacb6(0x18);
  FUN_0009ddc0(uVar4);
  *(undefined8 *)(param_1 + 0x350) = uVar4;
  uVar4 = thunk_FUN_012aacb6(0x178);
  FUN_001e6880(uVar4,*(undefined4 *)(param_1 + 0x348),param_1 + 0x338,
               *(undefined8 *)(param_1 + 0x328));
  plVar2 = DAT_01a1f100;
  *(undefined8 *)(param_1 + 0x358) = uVar4;
  *(undefined4 *)(param_1 + 0x330) = 1;
  if (*plVar2 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

