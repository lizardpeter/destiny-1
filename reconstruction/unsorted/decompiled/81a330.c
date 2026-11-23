
void FUN_0081a330(uint *param_1,undefined4 *param_2)

{
  uint *puVar1;
  undefined2 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  
  if (param_2[1] == 1) {
    uVar4 = *param_2;
    uVar2 = *(undefined2 *)((long)param_1 + 6);
    uVar6 = param_1[1];
    uVar3 = FUN_00f7e4b0(param_1 + 0x15);
    FUN_00f83530(param_1 + 0x2d,(short)uVar6,uVar2,1,1,uVar4,uVar3,0,0);
    uVar4 = FUN_00079280(param_1 + 0x15);
    FUN_00f841b0(param_1 + 0x2d,uVar4);
  }
  else {
    uVar6 = *param_1;
    if ((uVar6 & 0x100000) == 0) {
      iVar5 = FUN_00263ef0(param_1 + 0x22);
      if (iVar5 != 0) {
        puVar1 = param_1 + 0x2d;
        FUN_00f83e80(puVar1,param_1 + 0x22,0);
        FUN_00f841b0(puVar1,*(ulong *)(param_1 + 0x10) >> 8);
        if (1 < (ushort)param_1[2]) {
          FUN_00f839e0(puVar1,10);
        }
        goto LAB_0081a467;
      }
      uVar6 = *param_1;
    }
    else if ((short)param_1[0x21] != 0) {
      FUN_00f84200(param_1 + 0x2d,param_1 + 0x15,0);
      FUN_00f841b0(param_1 + 0x2d,*(ulong *)(param_1 + 0x10) >> 8);
      goto LAB_0081a467;
    }
    FUN_0081a480((short)param_1[1],*(undefined2 *)((long)param_1 + 6),(short)param_1[2],*param_2,
                 param_1 + 0x2d,*(undefined8 *)(param_1 + 0x10),uVar6 & 0xffff);
  }
LAB_0081a467:
  *(byte *)((long)param_1 + 2) = *(byte *)((long)param_1 + 2) | 2;
  return;
}

