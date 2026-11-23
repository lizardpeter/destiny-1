
undefined8 FUN_005909b0(long param_1,undefined8 param_2)

{
  bool bVar1;
  long lVar2;
  bool bVar3;
  char cVar4;
  char cVar5;
  long *plVar6;
  undefined8 uVar7;
  char *pcVar8;
  undefined8 uVar9;
  long lVar10;
  long lVar11;
  char cVar12;
  long lVar13;
  undefined1 auVar14 [16];
  undefined1 local_58 [32];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  plVar6 = (long *)FUN_0025a550();
  uVar7 = FUN_005494c0();
  pcVar8 = (char *)(**(code **)(*plVar6 + 0xb8))(plVar6);
  cVar4 = -1;
  cVar12 = *pcVar8 + -1;
  if (cVar12 < '\0') {
LAB_00590c15:
    if (*DAT_01a1f100 == local_38) {
      return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),cVar4);
    }
    uVar7 = thunk_FUN_012aa7f6();
    return uVar7;
  }
  cVar4 = -1;
  bVar1 = true;
LAB_00590a0d:
  if (cVar4 != -1) {
    do {
      auVar14 = FUN_0054a7d0(uVar7,cVar12);
      lVar13 = auVar14._0_8_;
      cVar5 = FUN_0028eba0(lVar13 + 8);
      if ((cVar5 == '\0') || (cVar5 = FUN_0028e530(param_2,lVar13 + 8), cVar5 != '\0')) {
        lVar10 = auVar14._8_8_ + 0x30;
        cVar5 = FUN_0028eba0(lVar10);
        if (((cVar5 == '\0') || (cVar5 = FUN_0028e530(param_2,lVar10), cVar5 != '\0')) &&
           (*(short *)(param_1 + 0x42e2) != -1)) goto LAB_00590b14;
      }
      cVar12 = cVar12 + -1;
      if (cVar12 < '\0') goto LAB_00590c15;
    } while( true );
  }
  do {
    auVar14 = FUN_0054a7d0(uVar7,cVar12);
    lVar13 = auVar14._0_8_ + 8;
    cVar4 = FUN_0028eba0(lVar13);
    if ((cVar4 == '\0') || (cVar4 = FUN_0028e530(param_2,lVar13), cVar4 != '\0')) {
      lVar13 = auVar14._8_8_ + 0x30;
      cVar5 = FUN_0028eba0(lVar13);
      cVar4 = cVar12;
      if ((cVar5 == '\0') || (cVar5 = FUN_0028e530(param_2,lVar13), cVar5 != '\0'))
      goto LAB_00590b03;
    }
    cVar4 = -1;
    cVar12 = cVar12 + -1;
    if (cVar12 < '\0') goto LAB_00590c15;
  } while( true );
LAB_00590b14:
  uVar9 = (**(code **)(*plVar6 + 0x330))(plVar6,*(undefined1 *)(lVar13 + 4));
  FUN_00263db0(local_58,param_2,uVar9,param_1 + 0x5e8 + (long)*(char *)(lVar13 + 4) * 0x4c);
  FUN_00263dd0(local_58);
  if (bVar1) {
    do {
      cVar5 = FUN_00263eb0(local_58);
      if (cVar5 == '\0') break;
      lVar13 = FUN_00263f70(local_58);
      if (bVar1) {
        lVar10 = -1;
        lVar11 = 0x14;
        do {
          lVar10 = lVar10 + 1;
          if (*(long *)(lVar13 + 8) <= lVar10) break;
          lVar2 = lVar11 + *(long *)(lVar13 + 0x10);
          lVar11 = lVar11 + 0x18;
          cVar5 = cVar12;
          bVar3 = false;
          if (*(short *)(lVar13 + 0x10 + lVar2) != *(short *)(param_1 + 0x42e2)) {
            cVar5 = cVar4;
            bVar3 = bVar1;
          }
          bVar1 = bVar3;
          cVar4 = cVar5;
        } while (bVar1);
      }
      FUN_00263e40(local_58);
    } while (bVar1);
  }
  if (!bVar1) goto LAB_00590c15;
LAB_00590b03:
  cVar12 = cVar12 + -1;
  if (cVar12 < '\0') goto LAB_00590c15;
  goto LAB_00590a0d;
}

