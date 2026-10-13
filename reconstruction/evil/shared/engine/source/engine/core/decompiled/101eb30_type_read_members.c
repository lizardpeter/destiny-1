
/* WARNING: Removing unreachable block (ram,0x0101f166) */
/* WARNING: Removing unreachable block (ram,0x0101f180) */
/* WARNING: Type propagation algorithm not settling */

void FUN_0101eb30(long *param_1,undefined8 *param_2)

{
  uint *puVar1;
  byte *pbVar2;
  ushort uVar3;
  uint *puVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  char cVar7;
  long lVar8;
  long lVar9;
  long lVar10;
  uint uVar11;
  uint uVar12;
  int iVar13;
  ulong uVar14;
  uint uVar15;
  uint uVar16;
  char cVar17;
  long *plVar18;
  uint uVar19;
  long lVar20;
  uint uVar21;
  bool bVar22;
  long local_6b8;
  int local_6a0;
  int iStack_698;
  char cStack_68f;
  undefined8 uStack_688;
  long local_680;
  undefined4 local_670;
  undefined2 local_66c;
  undefined1 local_66a;
  int local_668;
  long alStack_660 [3];
  char cStack_648;
  undefined4 uStack_647;
  undefined2 uStack_643;
  undefined1 auStack_641 [9];
  long alStack_638 [187];
  long local_60;
  
  local_60 = *DAT_01a1f100;
  local_668 = 0;
  lVar8 = (long)(int)param_1[3];
  cVar17 = 0 < lVar8;
  if (lVar8 < 1) {
    lVar8 = *param_1;
  }
  if (param_2[1] != param_2[2]) {
    thunk_FUN_012aa7c6(param_2[2],param_2[1],(long)*(int *)((long)param_1 + 0xc));
  }
  uVar21 = *(uint *)(param_2 + 3);
  puVar4 = (uint *)param_2[4];
  uVar15 = uVar21 >> 5;
  uVar16 = puVar4[2];
  uVar11 = (int)(uVar16 << 0x12) >> 0x12;
  uVar19 = (uint)(1L << ((byte)uVar21 & 0x1f));
  if (((uVar11 & 0xfffffffe) == 0xfffffffe) ||
     ((uVar12 = *puVar4, (uVar15 & 0xffff) != uVar11 && (bVar22 = uVar12 != 0, uVar12 = 0, bVar22)))
     ) {
    if ((uVar16 & 0x3fff) != 0x3ffe) {
      thunk_FUN_002c72d0(puVar4,uVar21 + 1);
    }
    puVar1 = (uint *)(*(long *)puVar4 + (ulong)(uVar15 & 0xffff) * 4);
    *puVar1 = *puVar1 | uVar19;
    uVar16 = puVar4[2];
  }
  else {
    *puVar4 = uVar12 | uVar19;
    uVar16 = uVar15 & 0x3fff | uVar16 & 0xffffc000;
    puVar4[2] = uVar16;
  }
  uVar21 = uVar21 * 0x10000 + 0x10000;
  if ((int)(uVar16 << 4) >> 0x12 < (int)uVar21 >> 0x10) {
    puVar4[2] = uVar21 >> 2 & 0xfffc000 | uVar16 & 0xf0003fff;
  }
  iVar13 = *(int *)((long)param_2 + 0x1c);
  uVar5 = *param_2;
  local_6b8 = param_2[2];
  uVar6 = param_2[4];
  lVar20 = 0;
LAB_0101ecfc:
  do {
    for (; lVar8 <= lVar20; lVar20 = alStack_660[lVar20 * 6 + 1] + 1) {
      if (local_668 == 0) {
        if (*DAT_01a1f100 == local_60) {
          return;
        }
        thunk_FUN_012aa7f6();
        return;
      }
      lVar20 = (long)(local_668 + -1);
      cVar17 = (&cStack_648)[lVar20 * 0x30];
      lVar8 = alStack_660[lVar20 * 6 + 2];
      param_1 = (long *)alStack_660[lVar20 * 6];
      local_66a = auStack_641[lVar20 * 0x30];
      local_66c = (&uStack_643)[lVar20 * 0x18];
      local_670 = (&uStack_647)[lVar20 * 0xc];
      iVar13 = (int)alStack_638[lVar20 * 6];
      local_6b8 = alStack_638[lVar20 * 6 + -1];
      local_668 = local_668 + -1;
    }
    if (cVar17 == '\0') {
      cVar7 = '\x01';
      if (*(char *)((long)param_1 + lVar20 * 0x28 + 0x31) != '\0') {
        cVar7 = FUN_00073430(uVar5);
        FUN_010265d0(uVar6,(int)param_1[lVar20 * 5 + 5] + iVar13,cVar7);
        cVar17 = '\0';
        if (cVar7 == '\0') {
          lVar20 = lVar20 + 1;
          goto LAB_0101ecfc;
        }
      }
      pbVar2 = (byte *)((long)param_1 + lVar20 * 0x28 + 0x31);
      if ((char)param_1[lVar20 * 5 + 6] == '\x01') {
        cVar17 = '\0';
        if (cVar7 == '\0') {
          lVar20 = lVar20 + 1;
        }
        else {
          lVar9 = (long)local_668;
          local_668 = local_668 + 1;
          alStack_660[lVar9 * 6] = (long)param_1;
          alStack_660[lVar9 * 6 + 1] = lVar20;
          alStack_660[lVar9 * 6 + 2] = lVar8;
          plVar18 = (long *)0x0;
          (&cStack_648)[lVar9 * 0x30] = '\0';
          auStack_641[lVar9 * 0x30] = local_66a;
          (&uStack_643)[lVar9 * 0x18] = local_66c;
          (&uStack_647)[lVar9 * 0xc] = local_670;
          alStack_638[lVar9 * 6 + -1] = local_6b8;
          *(int *)(alStack_638 + lVar9 * 6) = iVar13;
          uVar21 = *(uint *)((long)param_1 + lVar20 * 0x28 + 0x34);
          uVar16 = (int)uVar21 >> 0xd;
          lVar10 = (ulong)((uVar16 >> 0x12 | 0x3ff) & uVar16) * 0x40;
          lVar8 = *DAT_01a238a0;
          lVar9 = *(long *)(lVar8 + 0x10 + lVar10);
          uVar14 = (ulong)((uVar21 & 0x1fff) * *(int *)(lVar8 + 0x30 + lVar10));
          lVar9 = (lVar9 + uVar14) -
                  ((long)*(int *)(lVar8 + 0x34 + lVar10) & *(ulong *)(lVar9 + 8 + uVar14));
          lVar8 = *(long *)(lVar9 + 0x48);
          if (lVar8 != 0) {
            plVar18 = (long *)(lVar9 + 0x48 + lVar8);
          }
          lVar8 = (long)(int)plVar18[3];
          cVar17 = 0 < lVar8;
          if (lVar8 < 1) {
            lVar8 = *plVar18;
          }
          if ((char)param_1[lVar20 * 5 + 7] == '\x01') {
            lVar8 = (long)*(int *)(local_6b8 + *(int *)((long)param_1 + lVar20 * 0x28 + 0x3c));
          }
          iVar13 = (uint)*pbVar2 + iVar13 + (int)param_1[lVar20 * 5 + 5];
          local_6b8 = local_6b8 + (int)param_1[lVar20 * 5 + 4];
          lVar20 = 0;
          param_1 = plVar18;
        }
      }
      else {
        (*(code *)(&PTR_FUN_019131b0)[(uint)(int)(char)param_1[lVar20 * 5 + 6]])
                  ((int)param_1[lVar20 * 5 + 4] + local_6b8,
                   (uint)*pbVar2 + (int)param_1[lVar20 * 5 + 5] + iVar13,param_1 + lVar20 * 5 + 7,
                   uVar5,uVar6);
        cVar17 = '\0';
        lVar20 = lVar20 + 1;
      }
      goto LAB_0101ecfc;
    }
    uVar3 = *(ushort *)(param_1 + 6);
    uVar21 = *(uint *)((long)param_1 + 0x34);
    uStack_688 = param_1[7];
    local_680 = param_1[8];
    local_6a0 = (int)param_1[4];
    local_6a0 = local_6a0 * (int)lVar20;
    iStack_698 = (int)param_1[5];
    iStack_698 = iStack_698 * (int)lVar20;
    do {
      lVar9 = lVar20;
      cVar7 = '\x01';
      cStack_68f = (char)(uVar3 >> 8);
      if (cStack_68f == '\0') {
LAB_0101ee4d:
        if ((char)uVar3 == '\x01') {
          if (cVar7 != '\0') {
            lVar20 = (long)local_668;
            local_668 = local_668 + 1;
            alStack_660[lVar20 * 6] = (long)param_1;
            alStack_660[lVar20 * 6 + 1] = lVar9;
            alStack_660[lVar20 * 6 + 2] = lVar8;
            param_1 = (long *)0x0;
            (&cStack_648)[lVar20 * 0x30] = cVar17;
            auStack_641[lVar20 * 0x30] = local_66a;
            (&uStack_643)[lVar20 * 0x18] = local_66c;
            (&uStack_647)[lVar20 * 0xc] = local_670;
            alStack_638[lVar20 * 6 + -1] = local_6b8;
            *(int *)(alStack_638 + lVar20 * 6) = iVar13;
            uVar16 = (int)uVar21 >> 0xd;
            lVar9 = (ulong)((uVar16 >> 0x12 | 0x3ff) & uVar16) * 0x40;
            lVar8 = *DAT_01a238a0;
            lVar20 = *(long *)(lVar8 + 0x10 + lVar9);
            uVar14 = (ulong)((uVar21 & 0x1fff) * *(int *)(lVar8 + 0x30 + lVar9));
            lVar20 = (lVar20 + uVar14) -
                     ((long)*(int *)(lVar8 + 0x34 + lVar9) & *(ulong *)(lVar20 + 8 + uVar14));
            lVar8 = *(long *)(lVar20 + 0x48);
            if (lVar8 != 0) {
              param_1 = (long *)(lVar20 + 0x48 + lVar8);
            }
            lVar8 = (long)(int)param_1[3];
            cVar17 = 0 < lVar8;
            if (lVar8 < 1) {
              lVar8 = *param_1;
            }
            if ((char)uStack_688 == '\x01') {
              lVar8 = (long)*(int *)(local_6b8 + uStack_688._4_4_);
            }
            local_6b8 = local_6b8 + local_6a0;
            iVar13 = (uint)(uVar3 >> 8) + iVar13 + iStack_698;
            lVar20 = 0;
            goto LAB_0101ecfc;
          }
        }
        else {
          (*(code *)(&PTR_FUN_019131b0)[(uint)(int)(char)uVar3])
                    (local_6a0 + local_6b8,iStack_698 + iVar13 + (uint)(uVar3 >> 8),&uStack_688,
                     uVar5,uVar6);
        }
      }
      else {
        cVar7 = FUN_00073430(uVar5);
        FUN_010265d0(uVar6,iStack_698 + iVar13,cVar7);
        if (cVar7 != '\0') goto LAB_0101ee4d;
      }
      local_6a0 = local_6a0 + (int)param_1[4];
      iStack_698 = iStack_698 + (int)param_1[5];
      lVar20 = lVar9 + 1;
    } while (lVar9 + 1 < lVar8);
    lVar20 = lVar9 + 2;
  } while( true );
}

