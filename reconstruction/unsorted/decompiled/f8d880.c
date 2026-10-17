
void FUN_00f8d880(long param_1,undefined8 param_2,uint param_3,long param_4,int param_5,long param_6
                 )

{
  byte *pbVar1;
  char cVar2;
  byte bVar3;
  byte bVar4;
  byte bVar5;
  byte bVar6;
  short sVar7;
  short sVar8;
  int iVar9;
  ulong uVar10;
  long lVar11;
  undefined8 uVar12;
  long lVar13;
  undefined4 *puVar14;
  uint uVar15;
  
  if (param_5 != 0) {
    uVar10 = (ulong)param_3;
    cVar2 = *(char *)(param_1 + 0x2f4 + uVar10);
    sVar7 = (short)param_3 * 0x642;
    lVar13 = 0;
    do {
      bVar3 = *(byte *)(param_4 + lVar13 * 4);
      if (0x24 < bVar3) goto switchD_00f8d983_caseD_9;
      bVar4 = *(byte *)(param_4 + 1 + lVar13 * 4);
      bVar5 = *(byte *)(param_4 + 3 + lVar13 * 4);
      bVar6 = *(byte *)(param_4 + 2 + lVar13 * 4);
      uVar15 = (uint)bVar6;
      switch(bVar3) {
      case 0:
        sVar8 = sVar7;
        goto joined_r0x00f8d9fe;
      case 1:
        if (bVar6 < 0x10) {
          FUN_00f80150(param_2,param_3,uVar15,
                       *(long *)(param_1 + 8) +
                       (ulong)(ushort)(sVar7 + 0x480 + (ushort)bVar4 * 4) * 4);
        }
        break;
      case 2:
        sVar8 = sVar7 + 0x540;
        goto joined_r0x00f8d9dd;
      case 3:
        sVar8 = sVar7 + 0x4c0;
joined_r0x00f8d9dd:
        if (0xf < bVar6) break;
        lVar11 = *(long *)(param_1 + 8) + (ulong)(ushort)(sVar8 + (ushort)bVar4 * 4) * 4;
        goto LAB_00f8da21;
      case 4:
        sVar8 = sVar7 + 0x400;
joined_r0x00f8d9fe:
        if (bVar6 < 0x10) {
          lVar11 = (ulong)(ushort)(sVar8 + (ushort)bVar4 * 8) * 4 + *(long *)(param_1 + 8);
          if ((bVar5 & 1) == 0) {
LAB_00f8da21:
            FUN_00f7ffe0(param_2,param_3,uVar15,lVar11);
          }
          else {
            FUN_00f80080(param_2,param_3,uVar15,lVar11);
          }
        }
        break;
      case 5:
        sVar8 = sVar7 + 0x5a0;
        goto joined_r0x00f8da48;
      case 6:
        sVar8 = sVar7 + 0x590;
joined_r0x00f8da48:
        if (bVar6 < 0x10) {
LAB_00f8da6f:
          iVar9 = *(int *)(*(long *)(param_1 + 8) + (ulong)(ushort)(sVar8 + (ushort)bVar4) * 4);
LAB_00f8dacf:
          FUN_00f802a0(param_2,param_3,uVar15,iVar9);
        }
        break;
      case 7:
        sVar8 = sVar7 + 0x5b0;
        goto joined_r0x00f8da66;
      case 8:
        sVar8 = sVar7 + 0x641;
joined_r0x00f8da66:
        if (0xf < bVar6) break;
        goto LAB_00f8da6f;
      case 10:
        iVar9 = bVar5 + 1;
        puVar14 = (undefined4 *)(uVar10 * 0x20 + 0x168 + param_1);
        do {
          FUN_00f802a0(param_2,param_3,uVar15,*puVar14);
          uVar15 = uVar15 + 1;
          puVar14 = puVar14 + 1;
          iVar9 = iVar9 + -1;
        } while (iVar9 != 0);
        break;
      case 0xd:
        if (0xf < bVar6) break;
        iVar9 = (uint)*(ushort *)(param_1 + 0xba6) * (uint)*(ushort *)(param_1 + 0xba4);
        goto LAB_00f8dacf;
      case 0x13:
        if (bVar6 < 0x10) {
          if ((*(char *)(param_1 + 0x2ec + uVar10) == '\0') &&
             ((*(byte *)((ulong)(bVar4 >> 3) + 0x10 + param_1 + uVar10) >> (bVar4 & 7) & 1) == 0))
          break;
          FUN_00f80210(param_2,param_3,uVar15,*(undefined8 *)(param_6 + lVar13 * 8));
        }
        *(byte *)((ulong)(bVar4 >> 3) + 0x10 + param_1 + uVar10) =
             ~(byte)(1 << (bVar4 & 7)) & *(byte *)((ulong)(bVar4 >> 3) + 0x10 + param_1 + uVar10);
        break;
      case 0x15:
        if (bVar6 < 0x10) {
          if ((*(char *)(param_1 + 0x2ec + uVar10) == '\0') &&
             ((*(byte *)((ulong)(bVar4 >> 3) + 0x1e + param_1 + uVar10) >> (bVar4 & 7) & 1) == 0))
          break;
          FUN_00f80210(param_2,param_3,uVar15,*(undefined8 *)(param_6 + lVar13 * 8));
        }
        *(byte *)((ulong)(bVar4 >> 3) + 0x1e + param_1 + uVar10) =
             ~(byte)(1 << (bVar4 & 7)) & *(byte *)((ulong)(bVar4 >> 3) + 0x1e + param_1 + uVar10);
        break;
      case 0x16:
        if (bVar6 < 0x10) {
          if ((*(char *)(param_1 + 0x2ec + uVar10) == '\0') &&
             ((*(byte *)((ulong)(bVar4 >> 3) + 0x2c + param_1 + uVar10) >> (bVar4 & 7) & 1) == 0))
          break;
          FUN_00f80210(param_2,param_3,uVar15,*(undefined8 *)(param_6 + lVar13 * 8));
        }
        *(byte *)((ulong)(bVar4 >> 3) + 0x2c + param_1 + uVar10) =
             ~(byte)(1 << (bVar4 & 7)) & *(byte *)((ulong)(bVar4 >> 3) + 0x2c + param_1 + uVar10);
        break;
      case 0x17:
        if (bVar6 < 0x10) {
          if ((*(char *)(param_1 + 0x2ec + uVar10) == '\0') &&
             ((*(byte *)((ulong)(bVar4 >> 3) + 0x25 + param_1 + uVar10) >> (bVar4 & 7) & 1) == 0))
          break;
          FUN_00f80210(param_2,param_3,uVar15,*(undefined8 *)(param_6 + lVar13 * 8));
        }
        *(byte *)((ulong)(bVar4 >> 3) + 0x25 + param_1 + uVar10) =
             ~(byte)(1 << (bVar4 & 7)) & *(byte *)((ulong)(bVar4 >> 3) + 0x25 + param_1 + uVar10);
        break;
      case 0x18:
        if (bVar6 < 0x10) {
          if ((*(char *)(param_1 + 0x2ec + uVar10) == '\0') &&
             ((*(byte *)((ulong)(bVar4 >> 3) + 0x33 + param_1 + uVar10) >> (bVar4 & 7) & 1) == 0))
          break;
          FUN_00f80210(param_2,param_3,uVar15,*(undefined8 *)(param_6 + lVar13 * 8));
        }
        *(byte *)((ulong)(bVar4 >> 3) + 0x33 + param_1 + uVar10) =
             ~(byte)(1 << (bVar4 & 7)) & *(byte *)((ulong)(bVar4 >> 3) + 0x33 + param_1 + uVar10);
        break;
      case 0x19:
        if (bVar6 < 0x10) {
          if ((*(char *)(param_1 + 0x2ec + uVar10) == '\0') &&
             ((*(byte *)((ulong)(bVar4 >> 3) + 0x17 + param_1 + uVar10) >> (bVar4 & 7) & 1) == 0))
          break;
          FUN_00f80210(param_2,param_3,uVar15,*(undefined8 *)(param_6 + lVar13 * 8));
        }
        *(byte *)((ulong)(bVar4 >> 3) + 0x17 + param_1 + uVar10) =
             ~(byte)(1 << (bVar4 & 7)) & *(byte *)((ulong)(bVar4 >> 3) + 0x17 + param_1 + uVar10);
        break;
      case 0x1a:
        if (bVar6 < 0x10) {
          uVar12 = *(undefined8 *)(param_6 + lVar13 * 8);
          goto LAB_00f8de81;
        }
        break;
      case 0x1b:
        if (cVar2 != '\0') {
          uVar12 = *(undefined8 *)(param_1 + 0x130 + uVar10 * 8);
          goto LAB_00f8de81;
        }
        if ((*(char *)(param_1 + 0x2ec + uVar10) != '\0') ||
           ((*(byte *)(param_1 + 0x3a + uVar10) & 1) != 0)) {
          FUN_00f80210(param_2,param_3,uVar15,*(undefined8 *)(param_6 + lVar13 * 8));
          pbVar1 = (byte *)(param_1 + 0x3a + uVar10);
          *pbVar1 = *pbVar1 & 0xfe;
        }
        break;
      case 0x24:
        uVar12 = *(undefined8 *)(param_1 + 0x318);
LAB_00f8de81:
        FUN_00f80210(param_2,param_3,uVar15,uVar12);
      }
switchD_00f8d983_caseD_9:
      lVar13 = lVar13 + 1;
    } while ((int)lVar13 != param_5);
  }
  return;
}

