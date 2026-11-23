
ulong FUN_002a20c0(long param_1,undefined8 param_2)

{
  ulong *puVar1;
  char cVar2;
  long *plVar3;
  ulong uVar4;
  undefined1 local_68 [8];
  undefined1 local_60 [8];
  undefined1 local_58 [32];
  ulong local_38;
  
  puVar1 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  cVar2 = FUN_002592d0();
  if ((cVar2 != '\0') && (*(int *)(param_1 + 0xd9c) != -1)) {
    FUN_0024c4f0(local_58,1);
    FUN_0024b360(local_60,param_2);
    FUN_002c7e10(local_68,0xfffffffe);
    plVar3 = (long *)FUN_0024c1c0();
    (**(code **)(*plVar3 + 0x98))(plVar3,param_2);
    FUN_002c7e20(local_68);
    FUN_0024c560(local_58);
  }
  if (*puVar1 == local_38) {
    return *puVar1 & 0xffffffffffffff00;
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

