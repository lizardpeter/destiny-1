
void FUN_00796e50(long param_1)

{
  char cVar1;
  undefined2 uVar2;
  int iVar3;
  undefined8 uVar4;
  long lVar5;
  undefined8 uVar6;
  long *plVar7;
  int *piVar8;
  long lVar9;
  undefined4 uVar10;
  undefined4 local_170 [2];
  undefined4 local_168 [2];
  undefined4 local_160 [80];
  long local_20;
  
  local_20 = *DAT_01a1f100;
  uVar4 = thunk_FUN_00768060();
  FUN_0076ef00(uVar4);
  FUN_00770710(uVar4);
  *(undefined1 *)(param_1 + 0x30) = 0;
  *(undefined1 *)(param_1 + 0x31) = 0;
  *(undefined1 *)(param_1 + 0x32) = 0;
  *(undefined8 *)(param_1 + 0x38) = 0xffffffffffffffff;
  FUN_00797160(param_1);
  FUN_0078c010();
  local_160[0] = 0;
  local_168[0] = 6;
  local_170[0] = 1;
  FUN_00766200(local_160,local_168,local_170);
  FUN_0078c600();
  FUN_0076aa30();
  FUN_0076aab0();
  lVar5 = FUN_0034e3c0();
  if (*(char *)(lVar5 + 0x82) != '\0') {
    lVar5 = FUN_00574ef0();
    FUN_002459c0(*(char *)(lVar5 + 300) == '\0');
  }
  FUN_00aeb030(s__Enter_in_world_0165ad9f + 1);
  uVar6 = FUN_00574ef0();
  thunk_FUN_01018280(uVar6);
  *(undefined8 *)(param_1 + 0x78) = 0;
  *(undefined8 *)(param_1 + 0x70) = 0;
  *(undefined8 *)(param_1 + 0x68) = 0;
  FUN_00954790(1);
  FUN_000c5b20(2);
  FUN_000af380();
  lVar5 = FUN_0034e540();
  if (*(char *)(lVar5 + 0xf0) != '\0') {
    lVar5 = FUN_0034e540();
    if (*(char *)(lVar5 + 0xfc) == '\0') {
      uVar2 = FUN_00777280(0);
      plVar7 = (long *)FUN_0025a550();
      piVar8 = (int *)(**(code **)(*plVar7 + 0x328))
                                (plVar7,CONCAT62((int6)((ulong)uVar4 >> 0x10),uVar2) & 0xffffffff);
      lVar5 = FUN_0034e540();
      lVar9 = 0;
      do {
        iVar3 = *(int *)(lVar5 + 0x100 + lVar9 * 4);
        if ((iVar3 != -0x7ee3623b) && (*piVar8 == iVar3)) {
          cVar1 = FUN_000e4d70(6,3);
          if (cVar1 == '\0') goto LAB_007970c4;
          if ((DAT_026cfcf8 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026cfcf8), iVar3 != 0)) {
            DAT_026cfcf0 = FUN_000e4a10(s_networking_world_controller_stat_0165ae0d);
            thunk_FUN_012aa7e6(&DAT_026cfcf8);
          }
          uVar4 = FUN_00079a30(&DAT_01620037,*piVar8);
          FUN_01008290(local_160,s_networking_world_controller_stat_0165ae0d,uVar4,*piVar8);
          uVar10 = DAT_026cfcf0;
          goto LAB_007970bc;
        }
        lVar9 = lVar9 + 1;
      } while ((int)lVar9 < 8);
    }
    else {
      cVar1 = FUN_000e4d70(6,3);
      if (cVar1 != '\0') {
        if ((DAT_026cfce8 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026cfce8), iVar3 != 0)) {
          DAT_026cfce0 = FUN_000e4a10(s_networking_world_controller_stat_0165adaf);
          thunk_FUN_012aa7e6(&DAT_026cfce8);
        }
        FUN_01008290(local_160,s_networking_world_controller_stat_0165adaf);
        uVar10 = DAT_026cfce0;
LAB_007970bc:
        FUN_000e4aa0(uVar10,local_160);
      }
LAB_007970c4:
      cVar1 = FUN_000e4d70(6,3);
      if (cVar1 != '\0') {
        if ((DAT_026cfd08 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026cfd08), iVar3 != 0)) {
          DAT_026cfd00 = FUN_000e4a10(s_networking_world_controller_stat_0165ae7a);
          thunk_FUN_012aa7e6(&DAT_026cfd08);
        }
        FUN_01008290(local_160,s_networking_world_controller_stat_0165ae7a);
        FUN_000e4aa0(DAT_026cfd00,local_160);
      }
      FUN_00b9c2e0();
    }
  }
  if (*DAT_01a1f100 != local_20) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

