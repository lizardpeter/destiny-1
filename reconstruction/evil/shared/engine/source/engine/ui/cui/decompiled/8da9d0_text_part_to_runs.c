
long * FUN_008da9d0(long *param_1,undefined8 *param_2,uint *param_3,long param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined1 auVar4 [16];
  char cVar5;
  char cVar6;
  char cVar7;
  uint uVar8;
  long lVar9;
  uint *puVar10;
  undefined8 in_RAX;
  uint7 uVar13;
  long *plVar11;
  int *piVar12;
  long *plVar14;
  uint *puVar15;
  long *plVar16;
  ulong uVar17;
  
  uVar13 = (uint7)((ulong)in_RAX >> 8);
  plVar11 = (long *)(CONCAT71(uVar13,*(undefined1 *)((long)param_1 + 0x1b)) & 0xffffffffffffff03);
  if ((char)plVar11 == '\x01') {
    plVar11 = (long *)((ulong)uVar13 << 8);
    if (*(char *)((long)param_1 + 0x1a) != -1) {
      return plVar11;
    }
  }
  else if ((char)plVar11 == '\x02') {
    uVar8 = *(uint *)(param_1 + 2);
    plVar11 = (long *)(ulong)uVar8;
    if (uVar8 != 0x811c9dc5) {
      puVar10 = param_3;
      do {
        puVar15 = puVar10;
        if (param_3 + param_4 * 4 <= puVar15) goto LAB_008dac26;
        puVar10 = puVar15 + 4;
      } while (*puVar15 != uVar8);
      plVar11 = *(long **)(puVar15 + 2);
      plVar14 = (long *)0x0;
      if (*plVar11 != 0) {
        plVar14 = (long *)(*plVar11 + (long)plVar11);
      }
      plVar16 = plVar14 + (ulong)*(uint *)(plVar11 + 1) * 4;
      for (; plVar14 != plVar16; plVar14 = plVar14 + 4) {
        plVar11 = (long *)(CONCAT71((int7)((ulong)plVar11 >> 8),
                                    *(undefined1 *)((long)plVar14 + 0x1b)) & 0xffffffffffffff03);
        if ((char)plVar11 == '\x01') {
          plVar11 = (long *)CONCAT71((int7)((ulong)plVar11 >> 8),*(char *)((long)plVar14 + 0x1a));
          if (*(char *)((long)plVar14 + 0x1a) == -1) {
LAB_008dab60:
            uVar17 = (ulong)*(ushort *)((long)plVar14 + 0x16);
            if (uVar17 != 0) {
              piVar12 = (int *)FUN_008da760(uVar17);
              if (piVar12 == (int *)0x0) {
                return (long *)((ulong)piVar12 & 0xffffffffffffff00);
              }
              lVar9 = *plVar14;
              if (lVar9 != 0) {
                auVar4 = *(undefined1 (*) [16])(lVar9 + 0x40 + (long)plVar14);
                cVar5 = *(char *)(lVar9 + 0x30 + (long)plVar14);
                iVar1 = *(int *)(lVar9 + 0x1c + (long)plVar14);
                cVar6 = *(char *)(lVar9 + 0x18 + (long)plVar14);
                cVar7 = *(char *)(lVar9 + 0x10 + (long)plVar14);
                iVar2 = *(int *)(lVar9 + 0xc + (long)plVar14);
                iVar3 = *(int *)(lVar9 + 0x14 + (long)plVar14);
                *piVar12 = (int)*(char *)(lVar9 + 8 + (long)plVar14);
                piVar12[1] = iVar2;
                piVar12[2] = (int)cVar7;
                piVar12[3] = iVar3;
                piVar12[4] = (int)cVar6;
                piVar12[5] = iVar1;
                piVar12[6] = (int)cVar5;
                piVar12[7] = auVar4._0_4_;
                iVar1 = vextractps_avx(auVar4,1);
                piVar12[8] = iVar1;
                iVar1 = vextractps_avx(auVar4,2);
                piVar12[9] = iVar1;
                iVar1 = vextractps_avx(auVar4,3);
                piVar12[10] = iVar1;
              }
              FUN_008d5530(plVar14,*(undefined8 *)(piVar12 + 0xe),uVar17 + 1);
              plVar11 = (long *)*param_2;
              *(long *)(piVar12 + 0x12) = *plVar11;
              *plVar11 = (long)(piVar12 + 0x12);
            }
          }
        }
        else if (((char)plVar11 != '\x02') ||
                (plVar11 = (long *)(ulong)*(uint *)(plVar14 + 2),
                *(uint *)(plVar14 + 2) == 0x811c9dc5)) goto LAB_008dab60;
      }
      goto LAB_008dac26;
    }
  }
  uVar17 = (ulong)*(ushort *)((long)param_1 + 0x16);
  if (uVar17 == 0) {
    return (long *)CONCAT71((int7)((ulong)plVar11 >> 8),1);
  }
  piVar12 = (int *)FUN_008da760(uVar17);
  if (piVar12 == (int *)0x0) {
    return (long *)((ulong)piVar12 & 0xffffffffffffff00);
  }
  lVar9 = *param_1;
  if (lVar9 != 0) {
    auVar4 = *(undefined1 (*) [16])(lVar9 + 0x40 + (long)param_1);
    cVar5 = *(char *)(lVar9 + 0x30 + (long)param_1);
    iVar1 = *(int *)(lVar9 + 0x1c + (long)param_1);
    cVar6 = *(char *)(lVar9 + 0x18 + (long)param_1);
    cVar7 = *(char *)(lVar9 + 0x10 + (long)param_1);
    iVar2 = *(int *)(lVar9 + 0xc + (long)param_1);
    iVar3 = *(int *)(lVar9 + 0x14 + (long)param_1);
    *piVar12 = (int)*(char *)(lVar9 + 8 + (long)param_1);
    piVar12[1] = iVar2;
    piVar12[2] = (int)cVar7;
    piVar12[3] = iVar3;
    piVar12[4] = (int)cVar6;
    piVar12[5] = iVar1;
    piVar12[6] = (int)cVar5;
    piVar12[7] = auVar4._0_4_;
    iVar1 = vextractps_avx(auVar4,1);
    piVar12[8] = iVar1;
    iVar1 = vextractps_avx(auVar4,2);
    piVar12[9] = iVar1;
    iVar1 = vextractps_avx(auVar4,3);
    piVar12[10] = iVar1;
  }
  FUN_008d5530(param_1,*(undefined8 *)(piVar12 + 0xe),uVar17 + 1);
  plVar11 = (long *)*param_2;
  *(long *)(piVar12 + 0x12) = *plVar11;
  *plVar11 = (long)(piVar12 + 0x12);
LAB_008dac26:
  return (long *)CONCAT71((int7)((ulong)plVar11 >> 8),1);
}

