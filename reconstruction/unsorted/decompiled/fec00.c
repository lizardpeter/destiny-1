
void FUN_000fec00(long param_1,ulong param_2)

{
  uint *puVar1;
  int *piVar2;
  undefined1 *puVar3;
  int iVar4;
  byte bVar5;
  char cVar6;
  uint uVar7;
  int iVar8;
  long lVar9;
  long lVar10;
  int iVar11;
  long lVar12;
  long lVar13;
  int *piVar14;
  ushort uVar15;
  bool bVar16;
  ushort local_5a;
  uint local_58;
  undefined4 local_54;
  undefined4 local_50;
  undefined4 local_4c;
  undefined4 local_48;
  undefined4 local_44;
  uint local_40;
  undefined4 local_3c;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_000fefd0();
  lVar9 = (param_2 & 0xffffffff) * 0x10;
  if (*(char *)(param_1 + 0x10008 + lVar9) != '\a') {
    *(undefined1 *)(param_1 + 0x10008 + lVar9) = 6;
  }
  lVar9 = (param_2 & 0xffff) * 0x10;
  puVar3 = (undefined1 *)(param_1 + 0x10008 + lVar9);
  if (*(char *)(param_1 + 0x10008 + lVar9) == '\a') {
    *puVar3 = 2;
    FUN_000fe9f0(param_1);
  }
  else {
    lVar12 = (param_2 & 0xffff) * 0x80;
    piVar2 = (int *)(param_1 + lVar12);
    piVar14 = (int *)(param_1 + 0x10000 + lVar9);
    do {
      do {
      } while (*piVar2 != 0);
      LOCK();
      iVar11 = *piVar2;
      if (iVar11 == 0) {
        *piVar2 = 1;
        iVar11 = 0;
      }
      UNLOCK();
    } while (iVar11 != 0);
    LOCK();
    *piVar14 = *piVar14 + 1;
    UNLOCK();
    do {
      iVar4 = *piVar2;
      LOCK();
      iVar11 = *piVar2;
      if (iVar4 == iVar11) {
        *piVar2 = 0;
        iVar11 = iVar4;
      }
      UNLOCK();
    } while (iVar4 != iVar11);
    if (0 < *(int *)(param_1 + 0x50 + lVar12)) {
      lVar9 = param_1 + 0x50 + lVar12;
      cVar6 = FUN_000ff370(lVar9,param_1 + 0x14100,&local_5a);
      if (cVar6 != '\0') {
        bVar16 = false;
        do {
          LOCK();
          piVar14 = (int *)(param_1 + 0x58 + (ulong)local_5a * 0x80);
          iVar11 = *piVar14;
          *piVar14 = *piVar14 + -1;
          UNLOCK();
          if (iVar11 == 1) {
            piVar14 = (int *)(param_1 + 0x58 + (ulong)local_5a * 0x80);
            LOCK();
            iVar11 = *piVar14;
            if (iVar11 == 0) {
              *piVar14 = 0x10000;
              iVar11 = 0;
            }
            UNLOCK();
            bVar5 = 0;
            if (iVar11 == 0) {
              FUN_000fe9f0(param_1);
              bVar5 = 1;
              if (!bVar16) {
                FUN_0100c790(param_1 + 0x14080,0);
              }
            }
            bVar16 = (bool)(bVar5 | bVar16);
          }
          cVar6 = FUN_000ff370(lVar9,param_1 + 0x14100,&local_5a);
        } while (cVar6 != '\0');
        if (bVar16) {
          FUN_0100c790(param_1 + 0x14080,0);
        }
      }
    }
    *puVar3 = 0;
    uVar7 = *(uint *)(param_1 + 0x140c0);
    do {
      local_3c = uVar7;
      uVar15 = 0xffff;
      uVar7 = local_3c;
      if ((ushort)local_3c == 0xffff) goto LAB_000fee33;
      local_44 = CONCAT22(local_3c._2_2_ + 1,
                          *(undefined2 *)
                           (*(long *)(param_1 + 0x140d0) +
                           (long)(int)(*(int *)(param_1 + 0x140cc) * (local_3c & 0xffff))));
      local_40 = local_3c;
      LOCK();
      uVar7 = *(uint *)(param_1 + 0x140c0);
      if (local_3c == uVar7) {
        *(uint *)(param_1 + 0x140c0) = local_44;
        uVar7 = local_3c;
      }
      UNLOCK();
    } while (uVar7 != local_3c);
    if ((ushort)local_3c != 0xffff) {
      LOCK();
      *(int *)(param_1 + 0x140c4) = *(int *)(param_1 + 0x140c4) + -1;
      UNLOCK();
      uVar15 = (ushort)local_3c;
    }
LAB_000fee33:
    local_3c = uVar7;
    lVar9 = *(long *)(param_1 + 0x140d0);
    lVar13 = (long)(int)((uint)uVar15 * *(int *)(param_1 + 0x140cc));
    local_3c = CONCAT22(local_3c._2_2_,0xffff);
    iVar11 = 0;
    *(undefined2 *)(lVar9 + lVar13) = 0xffff;
    *(short *)(lVar9 + 4 + lVar13) = (short)param_2;
    do {
      uVar7 = *(uint *)(*(long *)(param_1 + 0x140d8) + 0x24);
      lVar9 = (long)(int)((uVar7 & 0xffff) * *(int *)(param_1 + 0x140cc));
      iVar4 = *(int *)(*(long *)(param_1 + 0x140d0) + lVar9);
      local_4c._2_2_ = (short)((uint)iVar4 >> 0x10);
      local_50 = CONCAT22(local_4c._2_2_ + 1,uVar15);
      if (uVar7 == *(uint *)(*(long *)(param_1 + 0x140d8) + 0x24)) {
        local_4c._0_2_ = (short)iVar4;
        local_48._2_2_ = (short)(uVar7 >> 0x10);
        if ((short)local_4c == -1) {
          piVar14 = (int *)(*(long *)(param_1 + 0x140d0) + lVar9);
          LOCK();
          iVar8 = *piVar14;
          if (iVar4 == iVar8) {
            *piVar14 = local_50;
            iVar8 = iVar4;
          }
          UNLOCK();
          if (iVar8 == iVar4) {
            local_54 = CONCAT22(local_48._2_2_ + 1,uVar15);
            puVar1 = (uint *)(*(long *)(param_1 + 0x140d8) + 0x24);
            LOCK();
            if (uVar7 == *puVar1) {
              *puVar1 = local_54;
            }
            UNLOCK();
            break;
          }
        }
        else {
          local_58 = CONCAT22(local_48._2_2_ + 1,(short)local_4c);
          puVar1 = (uint *)(*(long *)(param_1 + 0x140d8) + 0x24);
          LOCK();
          if (uVar7 == *puVar1) {
            *puVar1 = local_58;
          }
          UNLOCK();
        }
      }
      iVar11 = iVar11 + 1;
    } while (iVar11 < 10000);
    lVar9 = *(long *)(param_1 + 0x48 + lVar12);
    lVar13 = *(long *)(param_1 + 0x40 + lVar12);
    local_4c = iVar4;
    local_48 = uVar7;
    lVar10 = FUN_00068e90();
    if (lVar10 < lVar9 - lVar13) {
      LOCK();
      puVar1 = (uint *)(param_1 + 0x19980);
      uVar7 = *puVar1;
      *puVar1 = *puVar1 + 1;
      UNLOCK();
      lVar9 = (ulong)(uVar7 & 0xf) * 0x20;
      *(int **)(param_1 + 0x19780 + lVar9) = piVar2;
      *(undefined8 *)(param_1 + 0x19788 + lVar9) = *(undefined8 *)(param_1 + 0x60 + lVar12);
      *(undefined8 *)(param_1 + 0x19790 + lVar9) = *(undefined8 *)(param_1 + 0x40 + lVar12);
      *(undefined8 *)(param_1 + 0x19798 + lVar9) = *(undefined8 *)(param_1 + 0x48 + lVar12);
    }
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

