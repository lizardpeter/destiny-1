
void FUN_00409710(long param_1,undefined4 *param_2)

{
  long *plVar1;
  long lVar2;
  char cVar3;
  char cVar4;
  int iVar5;
  bool bVar6;
  long lVar7;
  char cVar8;
  uint uVar9;
  int iVar10;
  undefined4 *puVar11;
  long lVar12;
  undefined4 *puVar13;
  byte bVar14;
  long local_50;
  undefined8 local_48;
  undefined8 local_40;
  long local_38;
  
  bVar14 = 0;
  local_38 = *DAT_01a1f100;
  local_40 = *(undefined8 *)(param_2 + 2);
  local_48 = CONCAT44(local_48._4_4_,*param_2);
  puVar11 = (undefined4 *)FUN_00078970(&local_48,*(undefined4 *)PTR_DAT_019b2ad8);
  local_50 = *(long *)(param_1 + 600);
  cVar3 = *(char *)((long)puVar11 + 0x49);
  cVar4 = *(char *)(param_1 + 0x261);
  if (*(int *)(param_1 + 0x264) == puVar11[0x13]) {
    lVar12 = 0;
    bVar6 = false;
    do {
      if (*(int *)(param_1 + 0x264) <= (int)lVar12) goto LAB_00409799;
      lVar2 = lVar12 * 4;
      lVar7 = lVar12 + 0x14;
      lVar12 = lVar12 + 1;
    } while (*(int *)(param_1 + 0x268 + lVar2) == puVar11[lVar7]);
  }
  bVar6 = true;
LAB_00409799:
  if ((*(int *)(param_1 + 0x1f0) != -1) && (cVar4 != cVar3)) {
    thunk_FUN_003f4cd0(*(int *)(param_1 + 0x1f0),cVar4,cVar3);
  }
  plVar1 = (long *)(param_1 + 600);
  puVar13 = (undefined4 *)(param_1 + 0x218);
  for (lVar12 = 0x1e; lVar12 != 0; lVar12 = lVar12 + -1) {
    *puVar13 = *puVar11;
    puVar11 = puVar11 + (ulong)bVar14 * -2 + 1;
    puVar13 = puVar13 + (ulong)bVar14 * -2 + 1;
  }
  if (*plVar1 != local_50) {
    *(undefined4 *)(param_1 + 0x1f0) = 0xffffffff;
    local_48 = 0;
    if (local_50 != 0) {
      FUN_001195f0(&local_50);
    }
    local_48 = 0;
    if (*plVar1 != 0) {
      FUN_001195f0(plVar1);
    }
  }
  uVar9 = FUN_00129570(param_1);
  if (uVar9 != 0xffffffff) {
    iVar5 = *(int *)((ulong)((uVar9 & 0x1fff) * DAT_02689590) + 0x50 + DAT_02689588);
    iVar10 = FUN_00108cb0(param_1);
    if (iVar5 == iVar10) {
      FUN_00116ad0(param_1);
      cVar8 = FUN_001293b0(param_1);
      if (cVar8 == '\0') {
        FUN_00116ad0(param_1);
        FUN_006396f0();
      }
    }
  }
  if ((*(int *)(param_1 + 0x1f0) != -1) && (cVar4 != cVar3)) {
    FUN_003deed0(*(int *)(param_1 + 0x1f0),cVar4,cVar3);
    FUN_003db5c0();
  }
  if (bVar6) {
    thunk_FUN_003ce550();
  }
  FUN_00116ad0(param_1);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

