
undefined8 FUN_00b5a220(long param_1,uint param_2,long param_3)

{
  undefined8 *puVar1;
  char *pcVar2;
  uint *puVar3;
  ushort uVar4;
  byte *pbVar5;
  char cVar6;
  int iVar7;
  uint uVar8;
  ulong uVar9;
  long *plVar10;
  long lVar11;
  undefined8 uVar12;
  byte bVar13;
  int iVar14;
  char cVar15;
  long lVar16;
  long lVar17;
  long lVar18;
  undefined1 local_4d;
  undefined8 local_48;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar9 = (ulong)(param_2 & 0x3fff);
  lVar17 = (long)*(short *)(param_1 + 0xb4 + uVar9 * 6);
  lVar18 = lVar17 * 0x80;
  plVar10 = (long *)FUN_00bb2bf0(*(undefined8 *)(param_1 + 0x10),(int)(char)(&DAT_028832d8)[lVar18])
  ;
  iVar7 = (**(code **)(*plVar10 + 0xd0))(plVar10,(&DAT_028832dc)[lVar17 * 0x20]);
  local_4d = 0;
  if ((iVar7 != 1) && ((*(byte *)((long)&DAT_02883328 + lVar18 + 1) & 0x14) == 0)) {
    if ((&DAT_028832d9)[lVar18] == -3) {
      lVar16 = (long)*(short *)(param_1 + 0xb4 + uVar9 * 6);
      puVar1 = &DAT_02883348 + lVar16 * 0x10;
      lVar11 = -1;
      if ((char *)(&DAT_02883348)[lVar16 * 0x10] != (char *)0x0) {
        lVar11 = (long)*(char *)(&DAT_02883348)[lVar16 * 0x10];
      }
      FUN_00b5ee90(*(undefined8 *)(param_1 + 0x18 + lVar11 * 8),(&DAT_028832e0)[lVar16 * 0x20]);
      pbVar5 = (byte *)*puVar1;
      bVar13 = 0xff;
      if (pbVar5 != (byte *)0x0) {
        bVar13 = *pbVar5;
      }
      *(uint *)(pbVar5 + 4) = *(uint *)(pbVar5 + 4) & ~(1 << (bVar13 & 0x1f));
      *(undefined1 *)*puVar1 = 0xff;
      *(byte *)(&DAT_02883328 + lVar16 * 0x40) = *(byte *)(&DAT_02883328 + lVar16 * 0x40) & 0x7f;
      if (((&DAT_028832d9)[lVar16 * 0x80] | 2) == 0xff) {
        FUN_00b5f3d0(*puVar1);
        *puVar1 = 0;
      }
      (&DAT_028832d9)[lVar16 * 0x80] = 0xfe;
    }
    local_4d = 0;
    cVar6 = FUN_00b57050(param_1,&DAT_028832d8 + lVar18,0xffffffff);
    if (cVar6 != '\0') {
      pcVar2 = (char *)(param_1 + 0xb8 + uVar9 * 6);
      *(undefined4 *)((&DAT_02883348)[lVar17 * 0x10] + 4) = 0;
      cVar6 = *pcVar2;
      if (cVar6 == '\0') {
        *pcVar2 = '\x02';
        cVar6 = '\x02';
      }
      cVar15 = '\x02';
      if ((char)(cVar6 + '\x01') != '\0') {
        cVar15 = cVar6 + '\x01';
      }
      *pcVar2 = cVar15;
      puVar3 = (uint *)(param_1 + 0x12e40 + (ulong)((param_2 & 0x3fff) >> 5) * 4);
      *puVar3 = *puVar3 | 1 << ((byte)param_2 & 0x1f);
      uVar4 = (&DAT_02883350)[lVar17 * 0x40];
      lVar18 = 0;
      (&DAT_02883350)[lVar17 * 0x40] = uVar4 & 0xfff7;
      if ((uVar4 & 0xff7) == 0) {
        (&DAT_02883352)[lVar17 * 0x40] = 0;
      }
      do {
        if (*(long *)(param_1 + 0x18 + lVar18 * 8) != 0) {
          *(uint *)((&DAT_02883348)[lVar17 * 0x10] + 4) =
               *(uint *)((&DAT_02883348)[lVar17 * 0x10] + 4) | 1 << ((byte)lVar18 & 0x1f);
          FUN_00b5eba0(*(undefined8 *)(param_1 + 0x18 + lVar18 * 8),param_2);
        }
        lVar18 = lVar18 + 1;
      } while ((int)lVar18 != 0x13);
      if ((&DAT_028832dc)[lVar17 * 0x20] != -1) {
        iVar7 = FUN_00ba7f80();
        if (iVar7 != -1) {
          lVar18 = FUN_00ae39e0();
          local_40 = *(undefined8 *)(lVar18 + 0x14);
          local_48 = *(undefined8 *)(lVar18 + 0xc);
          uVar8 = (uint)(short)(&DAT_028832da)[lVar17 * 0x40];
          if ((uVar8 == 0xffffffff) ||
             ((*(uint *)((long)&local_48 + (long)((int)uVar8 >> 5) * 4) >> (uVar8 & 0x1f) & 1) != 0)
             ) {
            (&DAT_02883352)[lVar17 * 0x40] = 0;
            (&DAT_02883350)[lVar17 * 0x40] = 0;
            if (((int)((&DAT_028832f8)[lVar17 * 0x20] << 0x12) >> 0x12 & 0xfffffffeU) == 0xfffffffe)
            {
              FUN_002c7690();
            }
            else {
              iVar14 = (int)((&DAT_028832f8)[lVar17 * 0x20] << 4) >> 0x12;
              iVar7 = -1;
              if ((iVar14 + 0x1fU & 0x1f) != 0x1f) {
                iVar7 = (int)(1L << ((byte)iVar14 & 0x1f)) + -1;
              }
              *(int *)(&DAT_028832f0 + lVar17 * 0x10) = iVar7;
            }
            cVar6 = FUN_00b54010(param_1,param_2,0,0);
            if (cVar6 != '\0') {
              iVar7 = FUN_00ba8300((&DAT_028832dc)[lVar17 * 0x20]);
              puVar3 = (uint *)(param_3 + (long)(iVar7 >> 5) * 4);
              *puVar3 = *puVar3 | 1 << ((byte)iVar7 & 0x1f);
              local_4d = 1;
            }
          }
        }
      }
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),local_4d);
  }
  uVar12 = thunk_FUN_012aa7f6();
  return uVar12;
}

