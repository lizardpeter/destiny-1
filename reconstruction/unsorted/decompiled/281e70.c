
void FUN_00281e70(long param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4,
                 undefined8 param_5,undefined1 param_6,long param_7,long param_8)

{
  code *pcVar1;
  long lVar2;
  char cVar3;
  char cVar4;
  undefined4 uVar5;
  undefined8 uVar6;
  long lVar7;
  long *plVar8;
  long lVar9;
  int *piVar10;
  long lVar11;
  int iVar12;
  undefined1 local_60 [17];
  char local_4f;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  thunk_FUN_012aa986(param_8,0,0x100);
  FUN_00269470(local_60,param_2,param_3,*(undefined1 *)(param_1 + 2));
  if (local_4f != '\0') {
    do {
      cVar3 = FUN_00269440(local_60);
      if (cVar3 == '\0') {
        plVar8 = (long *)FUN_0025a550();
        pcVar1 = *(code **)(*plVar8 + 0x410);
        uVar5 = FUN_00269540(local_60);
        lVar9 = (*pcVar1)(plVar8,uVar5);
        lVar7 = 0;
LAB_00281f45:
        if (lVar9 != 0) {
          FUN_0026fb60(param_5,lVar9,lVar7,1,param_6,param_8);
        }
      }
      else {
        uVar6 = FUN_00269510(local_60);
        lVar7 = FUN_002601c0(param_4,uVar6);
        if (lVar7 != 0) {
          plVar8 = (long *)FUN_0025a550();
          lVar9 = (**(code **)(*plVar8 + 0x410))(plVar8,*(undefined2 *)(lVar7 + 0x24));
          goto LAB_00281f45;
        }
      }
      FUN_00269300(local_60);
    } while (local_4f != '\0');
  }
  plVar8 = (long *)FUN_0025a550();
  piVar10 = (int *)(**(code **)(*plVar8 + 0x240))(plVar8);
  if (0 < *piVar10) {
    cVar3 = '\0';
    do {
      lVar9 = (long)cVar3;
      uVar5 = *(undefined4 *)(param_8 + lVar9 * 4);
      plVar8 = (long *)FUN_0025a550();
      lVar7 = (**(code **)(*plVar8 + 0x4c8))(plVar8,cVar3);
      *(undefined4 *)(param_8 + lVar9 * 4) = uVar5;
      if (((*(char *)(lVar7 + 4) == '\0') && (lVar11 = *(long *)(lVar7 + 8), lVar11 != 0)) &&
         (0 < *(long *)(lVar11 + 0x20 + lVar7 + 8))) {
        lVar11 = lVar11 + lVar7 + 8;
        plVar8 = (long *)(lVar11 + 0x28);
        iVar12 = 0;
        lVar7 = 0;
        do {
          lVar2 = *plVar8;
          cVar4 = FUN_00269e60(*(undefined1 *)((long)plVar8 + lVar7 * 4 + lVar2 + 0x11),param_5);
          if (cVar4 != '\0') {
            iVar12 = iVar12 + *(short *)((long)plVar8 + lVar7 * 4 + lVar2 + 0x12);
          }
          lVar7 = lVar7 + 1;
        } while (lVar7 < *(long *)(lVar11 + 0x20));
        if (0 < iVar12) {
          *(int *)(param_8 + lVar9 * 4) = *(int *)(param_8 + lVar9 * 4) / iVar12;
        }
      }
      cVar3 = cVar3 + '\x01';
    } while ((int)cVar3 < *piVar10);
  }
  if (param_7 != 0) {
    FUN_00281860(param_7 + 0xc,param_8);
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

