
undefined8
FUN_00b34ad0(long param_1,byte param_2,long param_3,undefined1 *param_4,int param_5,int *param_6)

{
  undefined4 uVar1;
  short sVar2;
  undefined8 uVar3;
  byte bVar4;
  long lVar5;
  undefined8 *puVar6;
  int iVar7;
  undefined8 local_168;
  undefined8 local_160;
  undefined1 local_148 [272];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar5 = *(long *)(param_3 + 0x18);
  sVar2 = *(short *)(lVar5 + 0xc);
  if (sVar2 == 0x19) {
    param_2 = 0;
    bVar4 = 2;
  }
  else {
    param_2 = sVar2 != 0x1e & param_2;
    bVar4 = 2;
    if (sVar2 != 0x1e) {
      bVar4 = param_2;
    }
  }
  uVar1 = swap_bytes((uint)param_2 * 0x10 + *(int *)(lVar5 + 0x110) + *(int *)(lVar5 + 0x118));
  *(undefined4 *)(param_4 + 2) = uVar1;
  param_4[1] = bVar4;
  *param_4 = 1;
  if (param_2 == 0) {
    lVar5 = 6;
    puVar6 = (undefined8 *)0x0;
  }
  else {
    puVar6 = (undefined8 *)(param_4 + 6);
    lVar5 = 0x16;
  }
  iVar7 = (int)lVar5 + *(int *)(*(long *)(param_3 + 0x18) + 0x110);
  uVar3 = 0;
  if (iVar7 <= param_5) {
    param_4 = param_4 + lVar5;
    thunk_FUN_012aa7c6(param_4,*(long *)(param_3 + 0x18) + 0x90);
    if (param_2 != 0) {
      if (*(char *)(param_1 + 0x33) == '\0') {
        lVar5 = *(long *)(param_3 + 0x18);
        FUN_0006cd20(param_1,param_4,(long)*(int *)(lVar5 + 0x110),*(undefined8 *)(lVar5 + 0x120),
                     (long)*(int *)(lVar5 + 0x118),puVar6);
      }
      else {
        FUN_00f69950(local_148);
        FUN_00f699b0(local_148,param_4,(long)*(int *)(*(long *)(param_3 + 0x18) + 0x110));
        FUN_00f699b0(local_148,*(undefined8 *)(*(long *)(param_3 + 0x18) + 0x120),
                     (long)*(int *)(*(long *)(param_3 + 0x18) + 0x118));
        FUN_00f69ad0(local_148,&local_168);
        puVar6[1] = local_160;
        *puVar6 = local_168;
      }
    }
    *param_6 = iVar7;
    uVar3 = 1;
  }
  if (*DAT_01a1f100 == local_38) {
    return uVar3;
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

