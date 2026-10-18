
void FUN_0056ba70(long param_1,int param_2,long *param_3,long param_4)

{
  undefined1 *puVar1;
  char cVar2;
  ushort uVar3;
  undefined4 uVar4;
  long lVar5;
  long lVar6;
  long lVar7;
  undefined8 *puVar8;
  long lVar9;
  long lVar10;
  uint uVar11;
  ulong uVar12;
  undefined1 *local_38;
  
  lVar6 = 0;
  while ((lVar9 = lVar6 * 0x40, *(char *)(param_1 + 0x60 + lVar9) != (char)param_2 ||
         (*(long *)(param_1 + 0x80 + lVar9) != *param_3))) {
    lVar6 = lVar6 + 1;
    if ((int)lVar6 == 0x101) {
      return;
    }
  }
  if ((param_4 == 0) || (*(short *)(param_4 + 0xc) != 0xcc)) {
    local_38 = (undefined1 *)(param_1 + 0x88 + lVar9);
    if (*(char *)(param_1 + 0x88 + lVar9) == '\x03') {
      FUN_00543f70(param_1 + 0x8c + lVar9,0);
    }
    else {
      cVar2 = *(char *)(param_1 + 0x8a + lVar9);
      lVar6 = FUN_0034e490();
      if ((cVar2 == '\0') && (param_2 == 2)) {
        uVar4 = *(undefined4 *)(lVar6 + 0x20);
      }
      else {
        uVar4 = *(undefined4 *)(lVar6 + 0x24);
      }
      FUN_00543f70(param_1 + 0x8c + lVar9,uVar4);
    }
  }
  else {
    FUN_00543ee0(param_1 + 0x8c + lVar9);
    local_38 = (undefined1 *)(param_1 + 0x88 + lVar9);
  }
  FUN_00543ee0(param_1 + 0x94 + lVar9);
  *local_38 = 4;
  *(undefined1 *)(param_1 + 0x89 + lVar9) = 1;
  puVar1 = (undefined1 *)(param_1 + 0x89 + lVar9);
  if (param_4 == 0) {
    *puVar1 = 7;
  }
  else {
    uVar3 = *(ushort *)(param_4 + 0xc);
    if (uVar3 < 0x1f7) {
      if (uVar3 < 0x12d) {
        if (uVar3 == 0xcc) {
          *puVar1 = 2;
        }
      }
      else if (uVar3 == 0x12d) {
        *puVar1 = 3;
      }
      else if (uVar3 == 0x191) {
        *puVar1 = 6;
      }
      else if (uVar3 == 0x194) {
        *puVar1 = 4;
      }
    }
    else if (uVar3 == 0x1f7) {
      *puVar1 = 5;
    }
  }
  lVar6 = 0;
  lVar7 = lVar9 + param_1;
  do {
    if (0 < *(short *)(lVar7 + 100 + lVar6 * 4)) {
      lVar5 = (long)*(char *)(param_1 + 0x60 + lVar9) * 0x60 + param_1;
      lVar10 = (long)*(int *)(lVar6 * 0x10 + 0x4fd98 + lVar5);
      uVar12 = (ulong)*(uint *)(lVar6 * 0x10 + 0x4fd90 + lVar5);
      lVar5 = 0;
      if (uVar12 != 0xffffffff) {
        lVar5 = uVar12 + param_1 + 0x40a0;
      }
      uVar12 = (ulong)*(short *)(lVar7 + 0x62 + lVar6 * 4);
      puVar8 = (undefined8 *)(uVar12 * lVar10 + lVar5);
      do {
        thunk_FUN_012aa986(puVar8,0,lVar10);
        *puVar8 = 0;
        puVar8 = (undefined8 *)((long)puVar8 + lVar10);
        uVar11 = (int)uVar12 + 1;
        uVar12 = (ulong)uVar11;
      } while ((int)uVar11 <
               (int)*(short *)(lVar7 + 100 + lVar6 * 4) + (int)*(short *)(lVar7 + 0x62 + lVar6 * 4))
      ;
    }
    lVar6 = lVar6 + 1;
  } while ((int)lVar6 != 6);
  return;
}

