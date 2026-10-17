
void FUN_00581e90(long param_1,int param_2)

{
  long lVar1;
  ushort *puVar2;
  byte *pbVar3;
  int iVar4;
  ushort *puVar5;
  long *plVar6;
  int iVar7;
  long lVar8;
  undefined1 local_a8 [96];
  long local_48;
  undefined4 local_40;
  int local_3c;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_48 = *(long *)(param_1 + 0x14 + (long)param_2 * 8);
  local_40 = 8;
  iVar4 = 0;
  plVar6 = (long *)(DAT_026bc448 + 0x14);
  pbVar3 = (byte *)(DAT_026bc448 + 0x88);
  do {
    if (0 < iVar4) goto LAB_00581f2f;
    pbVar3 = pbVar3 + 2;
    iVar4 = iVar4 + 1;
    lVar8 = *plVar6;
    plVar6 = plVar6 + 1;
  } while (local_48 != lVar8);
  if ((iVar4 != 0) && (0 < *(int *)(DAT_026bc448 + 0x20))) {
    local_3c = 0;
    do {
      if ((*pbVar3 & 8) != 0) {
        if (local_3c == -1) goto LAB_00581f36;
        goto LAB_00581f75;
      }
      pbVar3 = pbVar3 + 0x68;
      local_3c = local_3c + 1;
    } while (local_3c < *(int *)(DAT_026bc448 + 0x20));
  }
LAB_00581f2f:
  local_3c = -1;
  goto LAB_00581f36;
  while( true ) {
    iVar4 = local_3c;
    while ((*puVar5 & (ushort)local_40) == 0) {
      if (iVar4 == -3) goto LAB_00582025;
      iVar7 = iVar4 + 2;
      iVar4 = iVar4 + 1;
      puVar5 = puVar5 + 0x34;
      if (*(int *)(DAT_026bc448 + 0x20) <= iVar7) goto LAB_00582025;
    }
    local_3c = iVar4 + 1;
    if (iVar4 == -2) break;
LAB_00581f75:
    FUN_0057f9d0(DAT_026bc448,&local_48,local_3c,local_a8);
    FUN_00582600(param_1,param_1 + 0x14 + (long)param_2 * 8,local_a8);
    lVar8 = 0;
    iVar4 = local_3c + 1;
    puVar2 = (ushort *)(DAT_026bc448 + 0x8a + (long)iVar4 * 0x68);
    do {
      puVar5 = puVar2;
      iVar7 = (int)lVar8;
      if (0 < iVar7) goto LAB_00582025;
      lVar1 = lVar8 * 8;
      lVar8 = lVar8 + 1;
      puVar2 = puVar5 + 1;
    } while (local_48 != *(long *)(DAT_026bc448 + 0x14 + lVar1));
    if (((iVar7 == -1) || (iVar4 == -1)) || (*(int *)(DAT_026bc448 + 0x20) <= iVar4)) {
LAB_00582025:
      local_3c = -1;
      break;
    }
  }
LAB_00581f36:
  (&DAT_00005e5d)[param_1] = 0;
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

