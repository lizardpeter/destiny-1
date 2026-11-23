
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_007652e0(long param_1,undefined4 *param_2)

{
  byte bVar1;
  undefined1 auVar2 [16];
  undefined1 auVar3 [16];
  long lVar4;
  char cVar5;
  int iVar6;
  int iVar7;
  long lVar8;
  long lVar9;
  undefined8 uVar10;
  undefined8 local_8a8;
  undefined8 uStack_8a0;
  undefined1 local_898 [16];
  undefined4 local_888 [2];
  undefined4 local_880 [2];
  undefined8 local_878;
  undefined4 local_870 [2];
  undefined4 local_868 [2];
  undefined8 local_860;
  undefined8 local_858;
  undefined4 local_850;
  undefined8 local_848;
  undefined8 local_840;
  undefined8 local_838;
  long local_30;
  
  lVar4 = DAT_026c9d30;
  local_30 = *DAT_01a1f100;
  bVar1 = *(byte *)((long)param_2 + 5);
  if ((bVar1 & 2) != 0) {
    if ((bVar1 & 0x20) == 0) {
      iVar6 = FUN_00071f60(param_1 + 0x80);
      if (iVar6 != -1) {
        FUN_00764f60(param_1);
      }
      *(undefined4 *)(param_1 + 0x80) = 0xffffffff;
      *(undefined4 *)(param_1 + 0x84) = 0xffffffff;
      *(undefined1 *)(param_1 + 0x88) = 0;
      *(undefined8 *)(param_1 + 0x8c) = 0xffffffffffffffff;
      *(byte *)(lVar4 + 8) = *(byte *)(lVar4 + 8) & 0xfb;
    }
    else {
      local_880[0] = *param_2;
      FUN_004e4330(local_880);
      *(byte *)(lVar4 + 8) = *(byte *)(lVar4 + 8) & 0xfb;
    }
    goto LAB_0076562d;
  }
  if ((bVar1 & 1) == 0) {
    if ((bVar1 & 4) == 0) {
      if ((bVar1 & 8) != 0) {
        *(undefined4 *)(param_1 + 0x98) = 0;
      }
    }
    else {
      uVar10 = FUN_0033fa20();
      local_888[0] = *param_2;
      iVar6 = FUN_0033fc20(uVar10,local_888);
      if (iVar6 != -1) {
        local_840 = 0x10;
        local_848 = 0x800;
        local_838 = 0;
        local_858 = 0;
        local_850 = 0xffffffff;
        local_860 = 0;
        cVar5 = FUN_00308ca0(&local_860,iVar6);
        if (cVar5 != '\0') {
          lVar8 = FUN_0100fd30(&local_860);
          lVar9 = FUN_003090d0(&local_860,*(undefined4 *)PTR_DAT_0191ae38,
                               *(undefined4 *)PTR_DAT_0191ae18);
          *(byte *)(lVar8 + 0x78) = *(byte *)(lVar8 + 0x78) | 0x23;
          local_8a8 = _DAT_0164ca00;
          uStack_8a0 = uRam000000000164ca08;
          auVar2 = vandps_avx(_DAT_01ac62b0,_DAT_0164ca10);
          auVar3._8_8_ = uRam000000000164ca08;
          auVar3._0_8_ = _DAT_0164ca00;
          auVar3 = vandnps_avx(_DAT_01ac62b0,auVar3);
          local_898 = vorps_avx(auVar3,auVar2);
          FUN_00308960(lVar8,&local_8a8);
          if (lVar9 != 0) {
            *(undefined1 *)(lVar9 + 0xe) = 1;
          }
          iVar6 = FUN_0032dbf0(lVar8);
          if (iVar6 != -1) {
            iVar7 = *(int *)(param_1 + 0x98);
            *(int *)(param_1 + 0x98) = iVar7 + 1;
            FUN_00072050(&local_878,iVar6);
            *(undefined8 *)(param_1 + 0x9c + (long)iVar7 * 8) = local_878;
          }
        }
      }
      *(byte *)(lVar4 + 8) = *(byte *)(lVar4 + 8) & 0xf7;
    }
    goto LAB_0076562d;
  }
  if ((bVar1 & 0x40) == 0) {
    if ((bVar1 & 0x20) != 0) {
      if ((bVar1 & 0x10) == 0) {
        local_870[0] = *param_2;
        iVar7 = FUN_004e3f20(local_870);
        iVar6 = FUN_00071f60(param_1 + 0x80);
        if (iVar6 != -1) {
          FUN_00764f60(param_1);
        }
        *(undefined4 *)(param_1 + 0x80) = 0xffffffff;
        *(undefined4 *)(param_1 + 0x84) = 0xffffffff;
        *(undefined1 *)(param_1 + 0x88) = 0;
        *(undefined8 *)(param_1 + 0x8c) = 0xffffffffffffffff;
        if ((DAT_018dcac8 != '\0') && (iVar7 != -1)) {
          uVar10 = 0;
          goto LAB_00765622;
        }
      }
      else {
        local_868[0] = *param_2;
        iVar7 = FUN_004e3f20(local_868);
        iVar6 = FUN_00071f60(param_1 + 0x80);
        if (iVar6 != -1) {
          FUN_00764f60(param_1);
        }
        *(undefined4 *)(param_1 + 0x80) = 0xffffffff;
        *(undefined4 *)(param_1 + 0x84) = 0xffffffff;
        *(undefined1 *)(param_1 + 0x88) = 0;
        *(undefined8 *)(param_1 + 0x8c) = 0xffffffffffffffff;
        if ((DAT_018dcac8 != '\0') && (iVar7 != -1)) {
          uVar10 = 1;
LAB_00765622:
          FUN_00764950(param_1,iVar7,0,uVar10);
        }
      }
    }
  }
  else if (*(int *)(param_1 + 0x94) != -1) {
    FUN_00764d20(param_1,*(int *)(param_1 + 0x94),(int)*(char *)(param_2 + 1));
    *(byte *)(lVar4 + 8) = *(byte *)(lVar4 + 8) & 0xfd;
    goto LAB_0076562d;
  }
  *(byte *)(lVar4 + 8) = *(byte *)(lVar4 + 8) & 0xfd;
LAB_0076562d:
  if (*DAT_01a1f100 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

