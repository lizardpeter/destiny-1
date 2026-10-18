
void FUN_00551400(long *param_1,int *param_2)

{
  uint *puVar1;
  byte bVar2;
  short sVar3;
  uint uVar4;
  char cVar5;
  undefined8 uVar6;
  int *piVar7;
  long lVar8;
  long lVar9;
  int iVar10;
  byte bVar11;
  float fVar12;
  undefined1 local_80 [17];
  char local_6f;
  undefined1 local_58 [8];
  uint auStack_50 [4];
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_40 = 0;
  iVar10 = *param_2;
  if (0 < iVar10) {
    lVar9 = 0;
    do {
      bVar2 = *(byte *)((long)param_2 + lVar9 * 8 + 9);
      puVar1 = (uint *)((long)&local_40 + (long)((int)(char)bVar2 >> 5) * 4);
      *puVar1 = *puVar1 | 1 << (bVar2 & 0x1f);
      lVar9 = lVar9 + 1;
    } while ((int)lVar9 < iVar10);
  }
  uVar6 = (**(code **)(*param_1 + 0x10))();
  FUN_00273e40(local_58,uVar6);
  FUN_00273ef0(local_58);
  cVar5 = FUN_00273d50(local_58);
  if (cVar5 != '\0') {
    do {
      if (*param_2 == 0x10) break;
      lVar9 = FUN_00273ed0(local_58);
      sVar3 = *(short *)(lVar9 + 0xc);
      uVar6 = FUN_005494c0();
      piVar7 = (int *)FUN_0054c020(uVar6);
      bVar2 = 0;
      do {
        bVar11 = bVar2;
        iVar10 = (int)(char)bVar11;
        if (*piVar7 <= iVar10) goto LAB_00551590;
        bVar2 = bVar11 + 1;
      } while ((bVar11 == 0xff) ||
              (*(short *)((long)(piVar7 + 2) + (long)iVar10 * 0x38 + 0x10 + *(long *)(piVar7 + 2))
               != sVar3));
      uVar6 = FUN_00273ed0(local_58);
      fVar12 = (float)FUN_00274d70(uVar6);
      uVar6 = FUN_005494c0();
      lVar9 = FUN_0054c0e0(uVar6,bVar11);
      if ((lVar9 != 0) &&
         ((DAT_01638ea8 < *(float *)(lVar9 + 4) && (*(float *)(lVar9 + 4) <= fVar12)))) {
        uVar4 = *(uint *)((long)&local_40 + (long)(iVar10 >> 5) * 4);
        if ((uVar4 >> (bVar11 & 0x1f) & 1) == 0) {
          lVar9 = (long)*param_2;
          *param_2 = *param_2 + 1;
          param_2[lVar9 * 2 + 1] = (int)fVar12;
          *(undefined1 *)(param_2 + lVar9 * 2 + 2) = 0;
          *(byte *)((long)param_2 + lVar9 * 8 + 9) = bVar11;
          *(uint *)((long)&local_40 + (long)(iVar10 >> 5) * 4) = uVar4 | 1 << (bVar11 & 0x1f);
        }
      }
LAB_00551590:
      FUN_00273e80(local_58);
      cVar5 = FUN_00273d50(local_58);
    } while (cVar5 != '\0');
  }
  lVar9 = (**(code **)(*param_1 + 0x10))(param_1);
  lVar8 = FUN_002601f0(param_1);
  uVar6 = (**(code **)(*param_1 + 0x30))(param_1);
  FUN_00273f90(local_80,lVar9 + 0x2b80,lVar8 + 0x4804,uVar6);
  FUN_002692a0(local_80);
  do {
    if ((local_6f == '\0') || (*param_2 == 0x10)) {
      if (*DAT_01a1f100 == local_38) {
        return;
      }
      thunk_FUN_012aa7f6();
      return;
    }
    lVar9 = FUN_00273fc0(local_80);
    sVar3 = *(short *)(lVar9 + 0xc);
    uVar6 = FUN_005494c0();
    piVar7 = (int *)FUN_0054c020(uVar6);
    bVar2 = 0;
    do {
      bVar11 = bVar2;
      iVar10 = (int)(char)bVar11;
      if (*piVar7 <= iVar10) goto LAB_00551710;
      bVar2 = bVar11 + 1;
    } while ((bVar11 == 0xff) ||
            (*(short *)((long)(piVar7 + 2) + (long)iVar10 * 0x38 + 0x10 + *(long *)(piVar7 + 2)) !=
             sVar3));
    fVar12 = (float)FUN_00274d70(lVar9);
    uVar6 = FUN_005494c0();
    lVar9 = FUN_0054c0e0(uVar6,bVar11);
    if ((lVar9 != 0) &&
       ((DAT_01638ea8 < *(float *)(lVar9 + 4) && (*(float *)(lVar9 + 4) <= fVar12)))) {
      uVar4 = *(uint *)((long)&local_40 + (long)(iVar10 >> 5) * 4);
      if ((uVar4 >> (bVar11 & 0x1f) & 1) == 0) {
        lVar9 = (long)*param_2;
        *param_2 = *param_2 + 1;
        param_2[lVar9 * 2 + 1] = (int)fVar12;
        *(undefined1 *)(param_2 + lVar9 * 2 + 2) = 0;
        *(byte *)((long)param_2 + lVar9 * 8 + 9) = bVar11;
        *(uint *)((long)&local_40 + (long)(iVar10 >> 5) * 4) = uVar4 | 1 << (bVar11 & 0x1f);
      }
    }
LAB_00551710:
    FUN_00269300(local_80);
  } while( true );
}

