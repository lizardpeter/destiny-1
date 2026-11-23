
/* WARNING: Removing unreachable block (ram,0x0101cff3) */
/* WARNING: Removing unreachable block (ram,0x0101d010) */
/* WARNING: Type propagation algorithm not settling */

void FUN_0101c940(long *param_1,undefined8 *param_2)

{
  ushort uVar1;
  long lVar2;
  uint *puVar3;
  uint uVar4;
  long lVar5;
  ulong uVar6;
  uint uVar7;
  uint uVar8;
  long lVar9;
  long *plVar10;
  char cVar11;
  long lVar12;
  uint uVar13;
  long lVar14;
  bool bVar15;
  long local_6b8;
  long local_6b0;
  int local_6a4;
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
  local_6b0 = (long)(int)param_1[3];
  cVar11 = 0 < local_6b0;
  if (local_6b0 < 1) {
    local_6b0 = *param_1;
  }
  lVar2 = param_2[3];
  puVar3 = (uint *)*param_2;
  local_6a4 = *(int *)((long)param_2 + 0xc);
  lVar14 = 0;
  local_6b8 = param_2[2];
LAB_0101ca34:
  do {
    for (; local_6b0 <= lVar14; lVar14 = alStack_660[lVar14 * 6 + 1] + 1) {
      if (local_668 == 0) {
        if (*DAT_01a1f100 != local_60) {
          thunk_FUN_012aa7f6();
          return;
        }
        return;
      }
      lVar14 = (long)(local_668 + -1);
      cVar11 = (&cStack_648)[lVar14 * 0x30];
      local_6b0 = alStack_660[lVar14 * 6 + 2];
      param_1 = (long *)alStack_660[lVar14 * 6];
      local_66a = auStack_641[lVar14 * 0x30];
      local_66c = (&uStack_643)[lVar14 * 0x18];
      local_670 = (&uStack_647)[lVar14 * 0xc];
      local_6a4 = (int)alStack_638[lVar14 * 6];
      local_6b8 = alStack_638[lVar14 * 6 + -1];
      local_668 = local_668 + -1;
    }
    if (cVar11 != '\0') {
      uVar1 = *(ushort *)(param_1 + 6);
      uVar4 = *(uint *)((long)param_1 + 0x34);
      uStack_688 = param_1[7];
      local_680 = param_1[8];
      local_6a0 = (int)param_1[4];
      local_6a0 = local_6a0 * (int)lVar14;
      iStack_698 = (int)param_1[5];
      iStack_698 = iStack_698 * (int)lVar14;
      do {
        lVar5 = lVar14;
        bVar15 = true;
        cStack_68f = (char)(uVar1 >> 8);
        if (cStack_68f == '\0') {
LAB_0101cc34:
          if ((char)uVar1 == '\x01') {
            if (bVar15 != false) {
              lVar14 = (long)local_668;
              local_668 = local_668 + 1;
              alStack_660[lVar14 * 6] = (long)param_1;
              alStack_660[lVar14 * 6 + 1] = lVar5;
              alStack_660[lVar14 * 6 + 2] = local_6b0;
              param_1 = (long *)0x0;
              (&cStack_648)[lVar14 * 0x30] = cVar11;
              auStack_641[lVar14 * 0x30] = local_66a;
              (&uStack_643)[lVar14 * 0x18] = local_66c;
              (&uStack_647)[lVar14 * 0xc] = local_670;
              alStack_638[lVar14 * 6 + -1] = local_6b8;
              *(int *)(alStack_638 + lVar14 * 6) = local_6a4;
              uVar7 = (int)uVar4 >> 0xd;
              lVar9 = (ulong)((uVar7 >> 0x12 | 0x3ff) & uVar7) * 0x40;
              lVar14 = *DAT_01a238a0;
              lVar5 = *(long *)(lVar14 + 0x10 + lVar9);
              uVar6 = (ulong)((uVar4 & 0x1fff) * *(int *)(lVar14 + 0x30 + lVar9));
              lVar5 = (lVar5 + uVar6) -
                      ((long)*(int *)(lVar14 + 0x34 + lVar9) & *(ulong *)(lVar5 + 8 + uVar6));
              lVar14 = *(long *)(lVar5 + 0x48);
              if (lVar14 != 0) {
                param_1 = (long *)(lVar5 + 0x48 + lVar14);
              }
              local_6b0 = (long)(int)param_1[3];
              cVar11 = 0 < local_6b0;
              if (local_6b0 < 1) {
                local_6b0 = *param_1;
              }
              if ((char)uStack_688 == '\x01') {
                local_6b0 = (long)*(int *)(local_6b8 + uStack_688._4_4_);
              }
              local_6b8 = local_6b8 + local_6a0;
              local_6a4 = local_6a4 + iStack_698 + (uint)(uVar1 >> 8);
              lVar14 = 0;
              goto LAB_0101ca34;
            }
          }
          else {
            (*(code *)(&PTR_FUN_01912b20)[(uint)(int)(char)uVar1])
                      (local_6a0 + local_6b8,puVar3,iStack_698 + local_6a4,&uStack_688,lVar2);
          }
        }
        else {
          uVar7 = iStack_698 + local_6a4;
          uVar13 = uVar7 >> 5 & 0xffff;
          uVar8 = (int)(puVar3[2] << 0x12) >> 0x12;
          if ((uVar8 & 0xfffffffe) == 0xfffffffe) {
            bVar15 = false;
            if ((int)uVar13 < ((int)(puVar3[2] << 4) >> 0x12) + 0x1f >> 5) {
              uVar8 = *(uint *)(*(long *)puVar3 + (ulong)(ushort)(uVar7 >> 5) * 4);
LAB_0101cbeb:
              bVar15 = (uVar8 & (uint)(1L << ((byte)uVar7 & 0x1f))) != 0;
            }
          }
          else {
            bVar15 = false;
            if (uVar13 == uVar8) {
              uVar8 = *puVar3;
              goto LAB_0101cbeb;
            }
          }
          if (*(uint *)(lVar2 + 0x30) < 0x40) {
            *(uint *)(lVar2 + 0x30) = *(uint *)(lVar2 + 0x30) + 1;
            *(int *)(lVar2 + 0x24) = *(int *)(lVar2 + 0x24) + 1;
            *(ulong *)(lVar2 + 0x28) = *(long *)(lVar2 + 0x28) * 2 | (ulong)bVar15;
          }
          else {
            FUN_000733a0(lVar2,bVar15,1);
          }
          if (bVar15 != false) goto LAB_0101cc34;
        }
        local_6a0 = local_6a0 + (int)param_1[4];
        iStack_698 = iStack_698 + (int)param_1[5];
        lVar14 = lVar5 + 1;
      } while (lVar5 + 1 < local_6b0);
      lVar14 = lVar5 + 2;
      goto LAB_0101ca34;
    }
    bVar15 = true;
    if (*(char *)((long)param_1 + lVar14 * 0x28 + 0x31) == '\0') {
LAB_0101ce4e:
      if ((long)(char)param_1[lVar14 * 5 + 6] == 1) {
        cVar11 = '\0';
        if (bVar15 == false) {
          lVar14 = lVar14 + 1;
        }
        else {
          lVar5 = (long)local_668;
          local_668 = local_668 + 1;
          alStack_660[lVar5 * 6] = (long)param_1;
          alStack_660[lVar5 * 6 + 1] = lVar14;
          alStack_660[lVar5 * 6 + 2] = local_6b0;
          plVar10 = (long *)0x0;
          (&cStack_648)[lVar5 * 0x30] = '\0';
          auStack_641[lVar5 * 0x30] = local_66a;
          (&uStack_643)[lVar5 * 0x18] = local_66c;
          (&uStack_647)[lVar5 * 0xc] = local_670;
          alStack_638[lVar5 * 6 + -1] = local_6b8;
          *(int *)(alStack_638 + lVar5 * 6) = local_6a4;
          uVar4 = *(uint *)((long)param_1 + lVar14 * 0x28 + 0x34);
          uVar7 = (int)uVar4 >> 0xd;
          lVar12 = (ulong)((uVar7 >> 0x12 | 0x3ff) & uVar7) * 0x40;
          lVar5 = *DAT_01a238a0;
          lVar9 = *(long *)(lVar5 + 0x10 + lVar12);
          uVar6 = (ulong)((uVar4 & 0x1fff) * *(int *)(lVar5 + 0x30 + lVar12));
          lVar9 = (lVar9 + uVar6) -
                  ((long)*(int *)(lVar5 + 0x34 + lVar12) & *(ulong *)(lVar9 + 8 + uVar6));
          lVar5 = *(long *)(lVar9 + 0x48);
          if (lVar5 != 0) {
            plVar10 = (long *)(lVar9 + 0x48 + lVar5);
          }
          local_6b0 = (long)(int)plVar10[3];
          cVar11 = 0 < local_6b0;
          if (local_6b0 < 1) {
            local_6b0 = *plVar10;
          }
          if ((char)param_1[lVar14 * 5 + 7] == '\x01') {
            local_6b0 = (long)*(int *)(local_6b8 + *(int *)((long)param_1 + lVar14 * 0x28 + 0x3c));
          }
          local_6a4 = local_6a4 + (int)param_1[lVar14 * 5 + 5] +
                      (uint)*(byte *)((long)param_1 + lVar14 * 0x28 + 0x31);
          local_6b8 = local_6b8 + (int)param_1[lVar14 * 5 + 4];
          lVar14 = 0;
          param_1 = plVar10;
        }
      }
      else {
        (*(code *)(&PTR_FUN_01912b20)[(long)(char)param_1[lVar14 * 5 + 6] & 0xffffffff])
                  ((int)param_1[lVar14 * 5 + 4] + local_6b8,puVar3,
                   (int)param_1[lVar14 * 5 + 5] + local_6a4,param_1 + lVar14 * 5 + 7,lVar2);
        cVar11 = '\0';
        lVar14 = lVar14 + 1;
      }
    }
    else {
      uVar4 = (int)param_1[lVar14 * 5 + 5] + local_6a4;
      uVar8 = uVar4 >> 5 & 0xffff;
      uVar7 = (int)(puVar3[2] << 0x12) >> 0x12;
      if ((uVar7 & 0xfffffffe) == 0xfffffffe) {
        bVar15 = false;
        if ((int)uVar8 < ((int)(puVar3[2] << 4) >> 0x12) + 0x1f >> 5) {
          uVar7 = *(uint *)(*(long *)puVar3 + (ulong)(ushort)(uVar4 >> 5) * 4);
LAB_0101cdf7:
          bVar15 = (uVar7 & (uint)(1L << ((byte)uVar4 & 0x1f))) != 0;
        }
      }
      else {
        bVar15 = false;
        if (uVar8 == uVar7) {
          uVar7 = *puVar3;
          goto LAB_0101cdf7;
        }
      }
      if (*(uint *)(lVar2 + 0x30) < 0x40) {
        *(uint *)(lVar2 + 0x30) = *(uint *)(lVar2 + 0x30) + 1;
        *(int *)(lVar2 + 0x24) = *(int *)(lVar2 + 0x24) + 1;
        *(ulong *)(lVar2 + 0x28) = *(long *)(lVar2 + 0x28) * 2 | (ulong)bVar15;
      }
      else {
        FUN_000733a0(lVar2,bVar15,1);
      }
      cVar11 = '\0';
      if (bVar15 != false) goto LAB_0101ce4e;
      lVar14 = lVar14 + 1;
    }
  } while( true );
}

