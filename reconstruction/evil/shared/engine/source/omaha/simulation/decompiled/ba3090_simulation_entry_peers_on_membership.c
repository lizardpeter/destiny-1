
void FUN_00ba3090(undefined8 *param_1)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  long lVar5;
  long lVar6;
  long *plVar7;
  ulong uVar8;
  uint uVar9;
  uint uVar10;
  long local_110;
  undefined1 local_108 [8];
  long local_100 [26];
  
  local_100[0x14] = *DAT_01a1f100;
  lVar5 = FUN_0029c3b0(*param_1);
  iVar2 = FUN_00057e60(lVar5 + 8);
  lVar6 = FUN_0029c3b0(*param_1);
  uVar3 = FUN_002a55c0(lVar6 + 8);
  if (*(int *)(param_1 + 3) != iVar2) {
    uVar4 = *(uint *)(param_1 + 5);
    *(undefined4 *)((long)param_1 + 0xd4) = 0;
    local_100[0x10] = 0;
    local_100[0x11] = 0;
    local_100[0x12] = 0;
    local_100[0x13] = 0;
    local_100[0xc] = 0;
    local_100[0xd] = 0;
    local_100[0xe] = 0;
    local_100[0xf] = 0;
    local_100[8] = 0;
    local_100[9] = 0;
    local_100[10] = 0;
    local_100[0xb] = 0;
    local_100[4] = 0;
    local_100[5] = 0;
    local_100[6] = 0;
    local_100[7] = 0;
    local_100[0] = 0;
    local_100[1] = 0;
    local_100[2] = 0;
    local_100[3] = 0;
    uVar8 = 0;
    do {
      if ((uVar3 >> ((uint)uVar8 & 0x1f) & 1) != 0) {
        plVar7 = (long *)FUN_002a54b0(lVar5 + 8,uVar8 & 0xffffffff);
        local_100[uVar8] = *plVar7;
      }
      uVar8 = uVar8 + 1;
    } while ((int)uVar8 != 0x14);
    uVar9 = 0;
    plVar7 = local_100;
    do {
      if (((uVar3 >> (uVar9 & 0x1f) & 1) != 0) && (uVar10 = uVar9, *plVar7 == param_1[4])) break;
      plVar7 = plVar7 + 1;
      uVar9 = uVar9 + 1;
      uVar10 = uVar4;
    } while ((int)uVar9 < 0x14);
    if (uVar10 != 0xffffffff) {
      FUN_00ba2590(param_1[1],local_108);
      cVar1 = FUN_00ba25a0(param_1[1],local_108,&local_110);
      if (cVar1 != '\0') {
        do {
          uVar4 = 0;
          plVar7 = local_100;
          do {
            if (((uVar3 >> (uVar4 & 0x1f) & 1) != 0) && (*plVar7 == *(long *)(local_110 + 0x54))) {
              if (uVar4 != 0xffffffff) {
                if (*(uint *)(local_110 + 0x5c) != uVar4) {
                  *(uint *)(local_110 + 0x5c) = uVar4;
                }
                goto LAB_00ba323e;
              }
              break;
            }
            plVar7 = plVar7 + 1;
            uVar4 = uVar4 + 1;
          } while ((int)uVar4 < 0x14);
          FUN_00ba2490(param_1[1]);
LAB_00ba323e:
          cVar1 = FUN_00ba25a0(param_1[1],local_108,&local_110);
        } while (cVar1 != '\0');
      }
      *(int *)(param_1 + 3) = iVar2;
      if (((*(uint *)((long)param_1 + 0x1c) != uVar3) || (*(uint *)(param_1 + 5) != uVar10)) ||
         (iVar2 = thunk_FUN_012aa826((long)param_1 + 0x2c,local_100,0xa0), iVar2 != 0)) {
        *(uint *)((long)param_1 + 0x1c) = uVar3;
        *(uint *)(param_1 + 5) = uVar10;
        thunk_FUN_012aa7c6((long)param_1 + 0x2c,local_100,0xa0);
        *(undefined1 *)((long)param_1 + 0xcc) = 1;
      }
    }
  }
  if (*DAT_01a1f100 != local_100[0x14]) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

