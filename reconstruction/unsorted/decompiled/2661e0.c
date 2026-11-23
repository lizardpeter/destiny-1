
ulong FUN_002661e0(undefined8 param_1,long param_2,undefined8 param_3,undefined8 param_4,
                  undefined8 param_5,undefined1 param_6,char param_7,long param_8,int *param_9)

{
  code *pcVar1;
  char cVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  undefined8 uVar6;
  long lVar7;
  long *plVar8;
  long lVar9;
  ulong uVar10;
  uint uVar11;
  undefined1 local_68 [16];
  char local_58;
  char local_57;
  uint local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_40[0] = 0;
  if ((param_8 == 0) || (*(char *)(param_8 + 0xc) == '\0')) {
LAB_0026624e:
    FUN_00269470(local_68,param_3,param_4,*(undefined1 *)(param_2 + 2));
    uVar11 = 0;
    if (local_57 != '\0') {
      do {
        lVar7 = 0;
        do {
          if (*param_9 <= (int)lVar7) {
            cVar2 = FUN_00269440(local_68);
            if (cVar2 == '\0') {
              plVar8 = (long *)FUN_0025a550();
              pcVar1 = *(code **)(*plVar8 + 0x410);
              uVar3 = FUN_00269540(local_68);
              lVar9 = (*pcVar1)(plVar8,uVar3);
              lVar7 = 0;
            }
            else {
              uVar6 = FUN_00269510(local_68);
              lVar7 = FUN_002601c0(param_5,uVar6);
              if (lVar7 == 0) break;
              plVar8 = (long *)FUN_0025a550();
              lVar9 = (**(code **)(*plVar8 + 0x410))(plVar8,*(undefined2 *)(lVar7 + 0x24));
            }
            if (lVar9 != 0) {
              iVar4 = FUN_00281930(lVar9,param_7,param_1);
              iVar5 = FUN_0026fa00(lVar9,lVar7,param_7,param_6,0);
              local_40[0] = local_40[0] + iVar5 * iVar4;
            }
            break;
          }
          lVar9 = lVar7 + 4;
          lVar7 = lVar7 + 1;
        } while (local_58 != *(char *)((long)param_9 + lVar9));
        FUN_00269300(local_68);
        uVar11 = local_40[0];
      } while (local_57 != '\0');
    }
    FUN_00281d80(param_1,param_7,uVar11,local_40,0);
  }
  else {
    lVar7 = 0;
    do {
      if (6 < (int)lVar7) goto LAB_0026624e;
      lVar9 = lVar7 * 8;
      lVar7 = lVar7 + 1;
    } while (*(char *)(param_8 + 0x10 + lVar9) != param_7);
    local_40[0] = *(uint *)(param_8 + 0xc + lVar7 * 8);
  }
  if (*DAT_01a1f100 != local_38) {
    uVar10 = thunk_FUN_012aa7f6();
    return uVar10;
  }
  return (ulong)local_40[0];
}

