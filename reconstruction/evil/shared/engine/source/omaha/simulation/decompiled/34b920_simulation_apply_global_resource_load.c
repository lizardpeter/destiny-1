
byte FUN_0034b920(long param_1,undefined8 param_2)

{
  long lVar1;
  byte *pbVar2;
  long lVar3;
  long lVar4;
  char cVar5;
  byte bVar6;
  short sVar7;
  uint uVar8;
  int iVar9;
  uint uVar10;
  undefined4 uVar11;
  undefined4 *puVar12;
  ulong uVar13;
  long lVar14;
  byte bVar15;
  
  uVar8 = FUN_00072c70(param_2,0x20);
  FUN_00072c70(param_2,4);
  FUN_00072c70(param_2,3);
  FUN_00073170(param_2,0x3d);
  cVar5 = FUN_00072210(param_2);
  if (cVar5 != '\0') {
    return 0;
  }
  iVar9 = FUN_0034b470();
  if ((((int)uVar8 >> 0x1f & 0x3c00U | 0x3ff) & uVar8 >> 0xd) != DAT_02693d04) {
    return 0;
  }
  if (iVar9 != -1) {
    return 0;
  }
  uVar10 = FUN_00349cb0();
  lVar4 = DAT_02693c58;
  if (uVar10 == 0xffffffff) {
    return 0;
  }
  uVar13 = (ulong)((uVar10 & 0x1fff) * DAT_02693c60);
  lVar1 = uVar13 + 0x10 + DAT_02693c58;
  do {
    cVar5 = FUN_00073430(param_2);
    if (cVar5 == '\0') {
      goto LAB_0034bad7;
    }
    uVar11 = FUN_00072c70(param_2,0x20);
    lVar14 = DAT_02693bf8;
    lVar3 = DAT_02693bf8 + 0xc050;
    sVar7 = FUN_00077100(lVar3,1,lVar1);
    if ((sVar7 == -1) ||
       (puVar12 = (undefined4 *)
                  ((ulong)*(ushort *)(lVar4 + 0x12 + uVar13) * *(long *)(lVar14 + 0xc060) +
                  lVar3 + *(long *)(lVar14 + 0xc050)), puVar12 == (undefined4 *)0x0)) {
      if (*(char *)(lVar4 + 6 + uVar13) != '\x02') goto LAB_0034be2f;
      *(int *)(lVar14 + 8) = *(int *)(lVar14 + 8) + -1;
      goto LAB_0034be34;
    }
    *puVar12 = uVar11;
    bVar15 = 0;
  } while (*(char *)(lVar4 + 7 + uVar13) != '\x03');
  goto LAB_0034be41;
  while( true ) {
    *puVar12 = uVar11;
    bVar15 = 0;
    if (*(char *)(lVar4 + 7 + uVar13) == '\x03') break;
LAB_0034bad7:
    cVar5 = FUN_00073430(param_2);
    if (cVar5 == '\0') {
      goto LAB_0034bb7e;
    }
    uVar11 = FUN_00072c70(param_2,0x20);
    lVar14 = DAT_02693bf8;
    lVar1 = DAT_02693bf8 + 0xc050;
    sVar7 = FUN_00077100(lVar1,1,uVar13 + 0x18 + lVar4);
    if ((sVar7 == -1) ||
       (puVar12 = (undefined4 *)
                  ((ulong)*(ushort *)(lVar4 + 0x1a + uVar13) * *(long *)(lVar14 + 0xc060) +
                  lVar1 + *(long *)(lVar14 + 0xc050)), puVar12 == (undefined4 *)0x0)) {
      if (*(char *)(lVar4 + 6 + uVar13) != '\x02') goto LAB_0034be2f;
      *(int *)(lVar14 + 8) = *(int *)(lVar14 + 8) + -1;
      goto LAB_0034be34;
    }
  }
  goto LAB_0034be41;
  while( true ) {
    *puVar12 = uVar11;
    bVar15 = 0;
    if (*(char *)(lVar4 + 7 + uVar13) == '\x03') break;
LAB_0034bb7e:
    cVar5 = FUN_00073430(param_2);
    if (cVar5 == '\0') {
      goto LAB_0034bc18;
    }
    uVar11 = FUN_00072c70(param_2,0x20);
    lVar14 = DAT_02693bf8;
    lVar1 = DAT_02693bf8 + 0xc050;
    sVar7 = FUN_00077100(lVar1,1,uVar13 + 0x20 + lVar4);
    if ((sVar7 == -1) ||
       (puVar12 = (undefined4 *)
                  ((ulong)*(ushort *)(lVar4 + 0x22 + uVar13) * *(long *)(lVar14 + 0xc060) +
                  lVar1 + *(long *)(lVar14 + 0xc050)), puVar12 == (undefined4 *)0x0)) {
      if (*(char *)(lVar4 + 6 + uVar13) != '\x02') goto LAB_0034be2f;
      *(int *)(lVar14 + 8) = *(int *)(lVar14 + 8) + -1;
      goto LAB_0034be34;
    }
  }
  goto LAB_0034be41;
  while( true ) {
    *puVar12 = uVar11;
    bVar15 = 0;
    if (*(char *)(lVar4 + 7 + uVar13) == '\x03') break;
LAB_0034bc18:
    cVar5 = FUN_00073430(param_2);
    if (cVar5 == '\0') {
      goto LAB_0034bccb;
    }
    uVar11 = FUN_00072c70(param_2,0x20);
    lVar14 = DAT_02693bf8;
    lVar1 = DAT_02693bf8 + 0xc050;
    sVar7 = FUN_00077100(lVar1,1,uVar13 + 0x28 + lVar4);
    if ((sVar7 == -1) ||
       (puVar12 = (undefined4 *)
                  ((ulong)*(ushort *)(lVar4 + 0x2a + uVar13) * *(long *)(lVar14 + 0xc060) +
                  lVar1 + *(long *)(lVar14 + 0xc050)), puVar12 == (undefined4 *)0x0)) {
      if (*(char *)(lVar4 + 6 + uVar13) != '\x02') goto LAB_0034be2f;
      *(int *)(lVar14 + 8) = *(int *)(lVar14 + 8) + -1;
      goto LAB_0034be34;
    }
  }
  goto LAB_0034be41;
  while( true ) {
    *puVar12 = uVar11;
    bVar15 = 0;
    if (*(char *)(lVar4 + 7 + uVar13) == '\x03') break;
LAB_0034bccb:
    cVar5 = FUN_00073430(param_2);
    if (cVar5 == '\0') {
      goto LAB_0034bd7b;
    }
    uVar11 = FUN_00072c70(param_2,0x20);
    lVar14 = DAT_02693bf8;
    lVar1 = DAT_02693bf8 + 0xc050;
    sVar7 = FUN_00077100(lVar1,1,uVar13 + 0x30 + lVar4);
    if ((sVar7 == -1) ||
       (puVar12 = (undefined4 *)
                  ((ulong)*(ushort *)(lVar4 + 0x32 + uVar13) * *(long *)(lVar14 + 0xc060) +
                  lVar1 + *(long *)(lVar14 + 0xc050)), puVar12 == (undefined4 *)0x0)) {
      if (*(char *)(lVar4 + 6 + uVar13) != '\x02') goto LAB_0034be2f;
      *(int *)(lVar14 + 8) = *(int *)(lVar14 + 8) + -1;
      goto LAB_0034be34;
    }
  }
  goto LAB_0034be41;
LAB_0034bd7b:
  do {
    cVar5 = FUN_00073430(param_2);
    if (cVar5 == '\0') {
      bVar6 = FUN_00072210(param_2);
      bVar15 = bVar6 ^ 1;
      if (bVar6 == 0) {
        *(uint *)(uVar13 + 0xc + lVar4) = uVar8;
        cVar5 = FUN_0023fc50();
        if (cVar5 != '\0') {
          pbVar2 = (byte *)(uVar13 + 8 + lVar4);
          *pbVar2 = *pbVar2 | 0x10;
          *(int *)(param_1 + 0x14098) = *(int *)(param_1 + 0x14098) + 1;
          FUN_0034a1d0(param_1,uVar10);
          return bVar15;
        }
        cVar5 = FUN_0006ef10(&DAT_02693cd0,uVar8 & 0x1fff,uVar8 >> 0x17 & 0xff);
        if (cVar5 != '\0') {
          *(uint *)((ulong)((uVar8 & 0x1fff) * DAT_02693ce0) + 0xc + DAT_02693cd8) = uVar10;
        }
        FUN_0034a1d0(param_1);
        return bVar15;
      }
      break;
    }
    uVar11 = FUN_00072c70(param_2,0x20);
    lVar14 = DAT_02693bf8;
    lVar1 = DAT_02693bf8 + 0xc050;
    sVar7 = FUN_00077100(lVar1,1,uVar13 + 0x38 + lVar4);
    if ((sVar7 == -1) ||
       (puVar12 = (undefined4 *)
                  ((ulong)*(ushort *)(lVar4 + 0x3a + uVar13) * *(long *)(lVar14 + 0xc060) +
                  lVar1 + *(long *)(lVar14 + 0xc050)), puVar12 == (undefined4 *)0x0)) {
      if (*(char *)(lVar4 + 6 + uVar13) == '\x02') {
        *(int *)(lVar14 + 8) = *(int *)(lVar14 + 8) + -1;
      }
      else {
LAB_0034be2f:
        *(int *)(lVar14 + 4) = *(int *)(lVar14 + 4) + -1;
      }
LAB_0034be34:
      *(undefined1 *)(lVar4 + 7 + uVar13) = 3;
      *(undefined1 *)(lVar4 + 9 + uVar13) = 1;
      bVar15 = 0;
      break;
    }
    *puVar12 = uVar11;
    bVar15 = 0;
  } while (*(char *)(lVar4 + 7 + uVar13) != '\x03');
LAB_0034be41:
  pbVar2 = (byte *)(uVar13 + 8 + lVar4);
  *pbVar2 = *pbVar2 | 1;
  FUN_00349ef0(param_1,&DAT_02693c50,param_1 + 4,uVar10);
  return bVar15;
}

