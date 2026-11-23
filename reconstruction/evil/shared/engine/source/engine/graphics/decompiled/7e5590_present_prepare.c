
undefined8 FUN_007e5590(long *param_1,uint6 *param_2)

{
  long *plVar1;
  short *psVar2;
  undefined8 uVar3;
  undefined4 local_38 [2];
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  FUN_007dcb50();
  FUN_00f811c0(param_1[10],*(undefined4 *)(*param_1 + 0x80),*(undefined4 *)(*param_1 + 0xb0));
  FUN_00f7e740(param_1[10],0xffff);
  FUN_00f81c70(local_38);
  FUN_00f81c80(local_38,0);
  FUN_00f804f0(param_1[10],local_38[0]);
  FUN_007dfac0(0,DAT_0165fef0,param_1,0,0,(int)param_1[0x51f],
               *(undefined4 *)((long)param_1 + 0x28fc));
  psVar2 = (short *)FUN_00818ec0(1);
  if (((short)*param_2 != *psVar2) || (*(short *)((long)param_2 + 2) != psVar2[1])) {
    FUN_00818240();
    FUN_00818250((ulong)*param_2);
    FUN_00818300();
  }
  FUN_00818e20((long)param_1 + (ulong)*(uint *)(*param_1 + 0xb0) * 0x2c + 0x2860);
  FUN_00f8f0e0(param_1[10],0,(long)param_1 + (ulong)*(uint *)(*param_1 + 0xb0) * 0x2c + 0x2860);
  if (*plVar1 == local_30) {
    return CONCAT71((int7)((ulong)*plVar1 >> 8),1);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

