
void FUN_0028cbf0(undefined8 *param_1,long param_2,long param_3,undefined8 param_4,
                 undefined8 param_5,undefined8 param_6,long param_7,long param_8,undefined1 *param_9
                 )

{
  bool bVar1;
  bool bVar2;
  char cVar3;
  long *plVar4;
  long lVar5;
  long lVar6;
  long lVar7;
  long lVar8;
  short *psVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  long lVar13;
  long lVar14;
  undefined **local_58;
  long local_50;
  int local_48;
  char local_44;
  undefined4 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  plVar4 = (long *)FUN_0025a550();
  lVar5 = (**(code **)(*plVar4 + 0x98))(plVar4);
  iVar12 = *(int *)(lVar5 + 0x84);
  if (0 < iVar12) {
    lVar14 = 0;
    do {
      lVar13 = (long)*(short *)(lVar5 + 0x94 + lVar14 * 0x14);
      if (lVar13 != -1) {
        cVar3 = *(char *)(lVar5 + 0x98 + lVar14 * 0x14);
        lVar8 = param_3 + 8;
        if ((cVar3 != '\0') && (lVar8 = 0, cVar3 == '\x01')) {
          lVar8 = param_2 + 8;
        }
        iVar10 = *(int *)(lVar5 + 0x90 + lVar14 * 0x14);
        if (0 < iVar10) {
          iVar11 = *(int *)(lVar5 + 0x8c + lVar14 * 0x14);
          iVar10 = iVar10 + iVar11;
          psVar9 = (short *)(lVar8 + (long)iVar11 * 0x20);
          bVar1 = true;
          do {
            iVar11 = iVar11 + 1;
            bVar2 = false;
            if (*psVar9 == -1) {
              bVar2 = bVar1;
            }
          } while ((bVar2) && (psVar9 = psVar9 + 0x10, bVar1 = bVar2, iVar11 < iVar10));
          if (!bVar2) {
            *(undefined1 *)(param_8 + lVar13) = *(undefined1 *)(lVar5 + 0x96 + lVar14 * 0x14);
            iVar12 = *(int *)(lVar5 + 0x84);
          }
        }
      }
      lVar14 = lVar14 + 1;
    } while ((int)lVar14 < iVar12);
  }
  local_44 = '\0';
  local_58 = &PTR_FUN_01910140;
  local_40 = 0;
  local_48 = 0;
  local_50 = param_3;
  FUN_01016840(&local_58);
  lVar5 = local_50;
  do {
    local_50 = lVar5;
    if (local_44 == '\0') {
      if (*DAT_01a1f100 == local_38) {
        return;
      }
      thunk_FUN_012aa7f6();
      return;
    }
    lVar13 = (long)local_48 * 0x20;
    plVar4 = (long *)FUN_0025a550();
    lVar14 = (**(code **)(*plVar4 + 0x410))(plVar4,*(undefined2 *)(lVar5 + 8 + lVar13));
    if (lVar14 == 0) {
LAB_0028ce1b:
      if (param_9 != (undefined1 *)0x0) {
        *param_9 = 0;
      }
    }
    else {
      if ((param_7 == 0) || (lVar8 = *(long *)(param_7 + 8), lVar8 == 0)) {
LAB_0028cde0:
        if (*(long *)(lVar5 + 0x10 + lVar13) != 0) {
          lVar6 = (**(code **)*param_1)(param_1,lVar5 + 0x10 + lVar13);
          bVar1 = false;
          goto LAB_0028ce16;
        }
        lVar6 = 0;
        bVar1 = false;
      }
      else {
        lVar6 = 0;
        if (*(long *)(lVar14 + 0x18) != 0) {
          lVar6 = *(long *)(lVar14 + 0x18) + lVar14 + 0x18;
        }
        if ((((*(long *)(lVar8 + 0x18) == 0) || (lVar6 == 0)) ||
            (lVar7 = *(long *)(lVar8 + 0x18) + lVar8 + 0x18, lVar7 == 0)) ||
           (*(char *)(lVar6 + 0x18) != *(char *)(lVar7 + 0x18))) goto LAB_0028cde0;
        lVar6 = *(long *)(param_7 + 0x10);
        bVar1 = true;
        lVar14 = lVar8;
LAB_0028ce16:
        if (lVar6 == 0) goto LAB_0028ce1b;
      }
      if (((*(long *)(lVar14 + 0x18) == 0) || (bVar1)) ||
         (cVar3 = FUN_002697c0(param_4,param_5,lVar5 + 0x10 + lVar13,lVar14), cVar3 != '\0')) {
        FUN_0028d730(lVar14,lVar6,param_6,param_8,param_9);
      }
    }
    local_48 = local_48 + 1;
    (*(code *)local_58[2])(&local_58);
    lVar5 = local_50;
  } while( true );
}

