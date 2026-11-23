
void FUN_00ba6170(long *param_1,ulong param_2)

{
  undefined8 *puVar1;
  char cVar2;
  int iVar3;
  uint uVar4;
  long lVar5;
  long lVar6;
  long lVar7;
  uint uVar8;
  long *plVar9;
  undefined8 local_118;
  long local_110;
  undefined1 local_108 [16];
  uint local_f8 [2];
  undefined4 local_f0 [2];
  long local_e8 [21];
  long local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (*(int *)(*param_1 + 8) != 1) {
    if ((param_2 & 2) == 0) {
      local_f8[0] = 0;
      iVar3 = FUN_00bb58c0();
      lVar6 = 0;
      if (iVar3 != -1) {
        lVar5 = FUN_00bb54d0(*param_1,iVar3);
        if (lVar5 != 0) {
          lVar6 = FUN_0075f130(*(undefined8 *)(lVar5 + 0x10));
        }
      }
      plVar9 = local_e8;
      FUN_00913a60(local_f8,plVar9);
      FUN_00bb6840(*param_1,&local_40);
      uVar4 = 0xffffffff;
      uVar8 = 0;
      do {
        if (((local_f8[0] >> (uVar8 & 0x1f) & 1) != 0) && (*plVar9 == local_40)) {
          uVar4 = uVar8;
        }
        plVar9 = plVar9 + 1;
        uVar8 = uVar8 + 1;
      } while (uVar8 != 0x14);
      if (uVar4 == 0xffffffff) {
        plVar9 = (long *)0x0;
      }
      else {
        plVar9 = local_e8 + (int)uVar4;
      }
      FUN_00913d20(plVar9);
      *(undefined1 *)((long)param_1 + 0x138c) = 1;
      if (((lVar6 != 0) && (*(uint *)(lVar6 + 0x8c48) < 0xb)) &&
         ((0x3f0U >> (*(uint *)(lVar6 + 0x8c48) & 0x1f) & 1) != 0)) {
        lVar6 = FUN_00b74340(lVar6);
        iVar3 = FUN_00b82620(lVar6);
        if (iVar3 != -1) {
          do {
            lVar5 = FUN_000a0430(*(undefined8 *)(&DAT_00001c5c + (long)iVar3 * 0xe8 + lVar6));
            FUN_00074a80(local_108,DAT_0273ea80);
            cVar2 = FUN_009142e0(&local_110);
            if (cVar2 != '\0') {
              do {
                lVar7 = FUN_000a0430(*(undefined8 *)(local_110 + 0x614));
                if (lVar5 == lVar7) {
                  *(undefined8 *)(local_110 + 0x614) =
                       *(undefined8 *)(&DAT_00001c5c + (long)iVar3 * 0xe8 + lVar6);
                }
                cVar2 = FUN_009142e0(&local_110);
              } while (cVar2 != '\0');
            }
            iVar3 = FUN_00b82650(lVar6,iVar3);
          } while (iVar3 != -1);
        }
      }
    }
    else {
      cVar2 = FUN_0090f130(&local_118);
      *(undefined4 *)((long)param_1 + 0x12dc) = 1;
      thunk_FUN_012aa986(param_1 + 0x25d,0,0xa4);
      puVar1 = (undefined8 *)((long)param_1 + 0x12ec);
      if (cVar2 != '\0') {
        *puVar1 = local_118;
      }
      FUN_00bb6850(*param_1,puVar1);
      FUN_000f8520(*param_1,(int)param_1[0x25d]);
      FUN_00913a90(*(undefined4 *)((long)param_1 + 0x12dc),puVar1);
      FUN_00913d20((long)param_1 + (long)(int)param_1[0x25d] * 8 + 0x12ec);
      *(undefined1 *)((long)param_1 + 0x138c) = 0;
    }
    local_f0[0] = 0;
    plVar9 = param_1 + 2;
    FUN_00ba8980(plVar9);
    FUN_00ba89d0(plVar9);
    FUN_00b9b720(plVar9);
    FUN_00913a60(local_f0,(long)param_1 + 0x123c);
    *(undefined4 *)(param_1 + 0x247) = local_f0[0];
    *(undefined4 *)((long)param_1 + 0xc) = 0xffffffff;
    FUN_00bb6ae0(*param_1);
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

