
void FUN_002991e0(long *param_1)

{
  byte *pbVar1;
  undefined4 *puVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  int iVar6;
  undefined4 uVar7;
  byte *pbVar8;
  ulong uVar9;
  undefined8 uVar10;
  long lVar11;
  long lVar12;
  uint uVar13;
  ulong uVar14;
  undefined *puVar15;
  undefined *puVar16;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if ((((char)param_1[0xd78] != '\0') &&
      (cVar3 = (**(code **)(*param_1 + 0x18))(param_1), cVar3 != '\0')) &&
     ((*(byte *)((long)param_1 + 0x131) & 1) != 0)) {
    cVar3 = FUN_0029d440(param_1,param_1 + 0xd73);
    if (cVar3 == '\0') {
      if ((DAT_02655598 == '\0') && (iVar6 = thunk_FUN_012aa7d6(&DAT_02655598), iVar6 != 0)) {
        DAT_02655590 = FUN_000e4a10(s_networking_activity_client___AC___016229fe);
        thunk_FUN_012aa7e6(&DAT_02655598);
      }
      cVar3 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
      cVar4 = (**(code **)(*param_1 + 0x18))(param_1);
      cVar5 = (**(code **)(*param_1 + 0x18))(param_1);
      puVar15 = &DAT_01621de5;
      puVar16 = &DAT_01621de5;
      if (cVar3 != '\0') {
        puVar16 = &DAT_01621de3;
      }
      if (cVar4 != '\0') {
        puVar15 = &DAT_01621de3;
      }
      if (cVar5 == '\0') {
        uVar10 = FUN_00001df0();
      }
      else {
        uVar10 = (**(code **)(*param_1 + 0x10))(param_1);
      }
      uVar7 = FUN_00057e60(param_1 + 0x1ce);
      lVar11 = param_1[0xce8];
      lVar12 = DAT_026553b0;
      if (DAT_026553a8 == '\0') {
        lVar12 = FUN_000694d0();
      }
      FUN_01008290(local_178,s_networking_activity_client___AC___016229fe,param_1 + 4,puVar16,
                   puVar15,uVar10,uVar7,lVar12 - lVar11);
      FUN_000e4aa0(DAT_02655590,local_178);
    }
    else {
      *(undefined1 *)(param_1 + 0xd78) = 0;
      if (DAT_026553a8 == '\0') {
        lVar11 = FUN_000694d0();
        param_1[0xce8] = lVar11;
      }
      else {
        param_1[0xce8] = DAT_026553b0;
      }
    }
  }
  pbVar1 = (byte *)(param_1 + 0xd71);
  uVar13 = ((int)param_1[0xd72] << 0x12) >> 0x12;
  if ((uVar13 & 0xfffffffe) == 0xfffffffe) {
    if ((((int)param_1[0xd72] << 4) >> 0x12) + 0x1f >> 5 < 1) goto LAB_002995be;
    pbVar8 = *(byte **)pbVar1;
  }
  else {
    pbVar8 = pbVar1;
    if (uVar13 != 0) goto LAB_002995be;
  }
  if ((((*pbVar8 & 1) != 0) && (cVar3 = (**(code **)(*param_1 + 0x18))(param_1), cVar3 != '\0')) &&
     ((*(byte *)((long)param_1 + 0x131) & 1) != 0)) {
    cVar3 = FUN_0029d620(param_1);
    if (cVar3 == '\0') {
      if ((DAT_026555a8 == '\0') && (iVar6 = thunk_FUN_012aa7d6(&DAT_026555a8), iVar6 != 0)) {
        DAT_026555a0 = FUN_000e4a10(s_networking_activity_client___AC___01622a9d);
        thunk_FUN_012aa7e6(&DAT_026555a8);
      }
      cVar3 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
      cVar4 = (**(code **)(*param_1 + 0x18))(param_1);
      cVar5 = (**(code **)(*param_1 + 0x18))(param_1);
      puVar15 = &DAT_01621de5;
      puVar16 = &DAT_01621de5;
      if (cVar3 != '\0') {
        puVar16 = &DAT_01621de3;
      }
      if (cVar4 != '\0') {
        puVar15 = &DAT_01621de3;
      }
      if (cVar5 == '\0') {
        uVar10 = FUN_00001df0();
      }
      else {
        uVar10 = (**(code **)(*param_1 + 0x10))(param_1);
      }
      uVar7 = FUN_00057e60(param_1 + 0x1ce);
      lVar11 = param_1[0xce7];
      lVar12 = DAT_026553b0;
      if (DAT_026553a8 == '\0') {
        lVar12 = FUN_000694d0();
      }
      FUN_01008290(local_178,s_networking_activity_client___AC___01622a9d,param_1 + 4,puVar16,
                   puVar15,uVar10,uVar7,lVar12 - lVar11);
      FUN_000e4aa0(DAT_026555a0,local_178);
    }
    else {
      thunk_FUN_012aa7c6(param_1 + 0xce9,param_1 + 0xd2d,0x220);
      if ((((int)param_1[0xd72] << 0x12) >> 0x12 & 0xfffffffeU) == 0xfffffffe) {
        puVar2 = *(undefined4 **)pbVar1;
        uVar9 = (ulong)((((int)param_1[0xd72] << 4) >> 0x12) + 0x1f >> 5);
        if ((uVar9 * 4 < 0x21) && (((ulong)puVar2 & 3) == 0)) {
          if (((uVar9 & 0x3fffffffffffffff) != 0) &&
             (*puVar2 = 0, (uVar9 & 0x3fffffffffffffff) != 1)) {
            uVar14 = 1;
            do {
              *(undefined4 *)(*(long *)pbVar1 + uVar14 * 4) = 0;
              uVar14 = uVar14 + 1;
            } while ((uVar9 & 0x3fffffffffffffff) != uVar14);
          }
        }
        else {
          thunk_FUN_012aa986(puVar2,0);
        }
      }
      else {
        pbVar1[0] = 0;
        pbVar1[1] = 0;
        pbVar1[2] = 0;
        pbVar1[3] = 0;
      }
      if (DAT_026553a8 == '\0') {
        lVar11 = FUN_000694d0();
        param_1[0xce7] = lVar11;
      }
      else {
        param_1[0xce7] = DAT_026553b0;
      }
    }
  }
LAB_002995be:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

