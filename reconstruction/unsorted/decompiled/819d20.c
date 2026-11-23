
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
FUN_00819d20(undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4,
            undefined2 param_5,int *param_6)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  undefined8 uVar4;
  undefined4 local_b0 [2];
  undefined4 local_a8 [2];
  undefined1 local_a0 [48];
  undefined1 local_70 [56];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (DAT_02707d48 == '\0') {
    iVar2 = thunk_FUN_012aa7d6(&DAT_02707d48);
    if (iVar2 != 0) {
      _DAT_02707d10 = 0x204001;
      _DAT_02707d14 = 0x22c003;
      _DAT_02707d18 = 0xfac00a;
      _DAT_02707d1c = 0xfac00a;
      _DAT_02707d20 = 0xfac90a;
      _DAT_02707d24 = 0xf2e009;
      _DAT_02707d28 = 0x22c705;
      _DAT_02707d2c = 0x204704;
      _DAT_02707d30 = 0x204704;
      _DAT_02707d34 = 0x204704;
      _DAT_02707d38 = 0xfac70c;
      _DAT_02707d3c = 0x22c70b;
      _DAT_02707d40 = 0xfac70e;
      thunk_FUN_012aa7e6(&DAT_02707d48);
    }
  }
  uVar1 = *(undefined4 *)(&DAT_02707d10 + (ulong)param_4 * 4);
  if (param_4 - 7 < 2) {
    local_a8[0] = uVar1;
    uVar4 = FUN_00819f80(param_1,param_2,uVar1,local_70,0);
    if (param_6 == (int *)0x0) goto LAB_00819ebe;
    iVar2 = FUN_00f7e540(local_70);
    iVar2 = iVar2 * 8 + 8;
    iVar3 = FUN_00f7d730(local_a8);
  }
  else {
    uVar4 = FUN_0081a0e0(param_1,param_2,param_3,uVar1,local_a0,0,param_5);
    if (param_6 == (int *)0x0) goto LAB_00819ebe;
    local_b0[0] = FUN_00f82b00(local_a0);
    iVar2 = FUN_00f7d730(local_b0);
    iVar3 = FUN_00f82ad0(local_a0);
    iVar3 = iVar3 * 8 + 8;
  }
  *param_6 = iVar3 * iVar2;
LAB_00819ebe:
  if (*DAT_01a1f100 == local_38) {
    return uVar4;
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

