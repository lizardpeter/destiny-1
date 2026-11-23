
undefined8 FUN_0094be40(long *param_1,long *param_2,undefined4 param_3)

{
  long *plVar1;
  undefined8 *puVar2;
  char cVar3;
  byte bVar4;
  undefined7 uVar10;
  long *plVar5;
  long *plVar6;
  ulong uVar7;
  long *plVar8;
  undefined8 uVar9;
  bool bVar11;
  long *plVar12;
  undefined8 *puVar13;
  byte bVar14;
  undefined8 local_b8;
  undefined8 uStack_b0;
  undefined8 local_a8;
  undefined4 local_a0;
  undefined4 local_9c;
  undefined4 local_98;
  undefined4 local_94;
  undefined4 local_90;
  undefined4 local_80 [2];
  undefined4 local_78 [2];
  long *local_70;
  undefined8 local_68;
  undefined8 uStack_60;
  undefined8 local_58;
  undefined4 local_50;
  undefined4 local_4c;
  undefined4 local_48;
  undefined4 local_44;
  undefined4 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar10 = (undefined7)((ulong)local_38 >> 8);
  puVar2 = (undefined8 *)*param_1;
  bVar14 = (puVar2 == (undefined8 *)0x0) != (param_2 == (long *)0x0);
  if (((!(bool)bVar14) && (puVar2 != (undefined8 *)0x0)) && (param_2 != (long *)0x0)) {
    puVar13 = (undefined8 *)*puVar2;
    plVar5 = (long *)0x0;
    if (*param_2 != 0) {
      plVar5 = (long *)(*param_2 + (long)param_2);
    }
    plVar6 = plVar5 + (ulong)*(uint *)(param_2 + 1) * 4;
    plVar8 = plVar6;
    do {
      if ((puVar13 == puVar2) || (plVar5 == plVar6)) break;
      if ((*plVar5 == 0) || (*plVar5 + (long)plVar5 == 0)) {
        local_68 = 0;
        uStack_60 = 0;
        local_50 = 0;
        local_58 = 0;
        local_4c = 0x3f800000;
        local_48 = 0x3f800000;
        local_44 = 0x3f800000;
        local_40 = 0x3f800000;
      }
      else {
        plVar8 = (long *)FUN_008da200(&local_68);
      }
      uVar7 = CONCAT71((int7)((ulong)plVar8 >> 8),*(undefined1 *)((long)plVar5 + 0x1b)) &
              0xffffffffffffff03;
      cVar3 = (char)uVar7;
      if (cVar3 == '\x01') {
        plVar8 = (long *)CONCAT71((int7)(uVar7 >> 8),*(char *)((long)plVar5 + 0x1a));
        if (*(char *)((long)plVar5 + 0x1a) == -1) {
LAB_0094bf60:
          bVar4 = FUN_008da310(puVar13 + -9,&local_68);
          plVar8 = (long *)FUN_008d5690(plVar5,puVar13[-2],*(undefined4 *)(puVar13 + -1),param_3);
          bVar14 = bVar14 & 1 | bVar4 | (byte)plVar8;
          plVar5 = plVar5 + 4;
          puVar13 = (undefined8 *)*puVar13;
        }
      }
      else {
        if ((cVar3 != '\x02') || ((int)plVar5[2] == -0x7ee3623b)) goto LAB_0094bf60;
        plVar8 = (long *)(ulong)*(uint *)(plVar5 + 2);
        if (*(uint *)(plVar5 + 2) != 0x811c9dc5) {
          local_78[0] = 0x811c9dc5;
          local_70 = (long *)0x0;
          local_80[0] = 0x811c9dc5;
          if ((*(byte *)((long)plVar5 + 0x1b) & 3) == 2) {
            local_80[0] = (undefined4)plVar5[2];
          }
          plVar8 = (long *)FUN_0094b0f0(local_80,local_78);
          if ((char)plVar8 != '\0') {
            plVar12 = (long *)0x0;
            if (*local_70 != 0) {
              plVar12 = (long *)(*local_70 + (long)local_70);
            }
            uVar7 = (ulong)*(uint *)(local_70 + 1);
            plVar8 = (long *)(uVar7 * 0x20);
            bVar11 = false;
            if (plVar12 != plVar12 + uVar7 * 4) {
              plVar1 = plVar12 + -4;
              while( true ) {
                if ((*plVar12 == 0) || (*plVar12 + (long)plVar12 == 0)) {
                  local_b8 = 0;
                  uStack_b0 = 0;
                  local_a0 = 0;
                  local_a8 = 0;
                  local_9c = 0x3f800000;
                  local_98 = 0x3f800000;
                  local_94 = 0x3f800000;
                  local_90 = 0x3f800000;
                }
                else {
                  FUN_008da200(&local_b8);
                }
                bVar4 = FUN_008da310(puVar13 + -9,&local_b8);
                plVar8 = (long *)FUN_008d5690(plVar12,puVar13[-2],*(undefined4 *)(puVar13 + -1),
                                              param_3);
                bVar11 = true;
                bVar14 = bVar14 & 1 | bVar4 | (byte)plVar8;
                if (bVar14 != 0) break;
                bVar14 = 0;
                bVar11 = plVar1 + uVar7 * 4 != plVar12;
                puVar13 = (undefined8 *)*puVar13;
                if ((plVar1 + uVar7 * 4 == plVar12) || (plVar12 = plVar12 + 4, puVar13 == puVar2))
                break;
              }
            }
            bVar14 = bVar14 & 1 | bVar11;
          }
          plVar5 = plVar5 + 4;
        }
      }
    } while ((bVar14 & 1) == 0);
    uVar10 = (undefined7)((ulong)plVar8 >> 8);
    bVar14 = bVar14 & 1 | (puVar13 != puVar2 || plVar5 != plVar6);
  }
  if (*DAT_01a1f100 != local_38) {
    uVar9 = thunk_FUN_012aa7f6();
    return uVar9;
  }
  return CONCAT71(uVar10,(bool)bVar14 != false);
}

