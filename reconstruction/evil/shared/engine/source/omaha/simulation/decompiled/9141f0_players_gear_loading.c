
undefined8 FUN_009141f0(void)

{
  long *plVar1;
  uint uVar2;
  char cVar3;
  long lVar4;
  undefined8 uVar5;
  undefined1 uVar6;
  long lVar7;
  undefined1 local_48 [8];
  uint local_40;
  long local_38;
  
  plVar1 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  FUN_00074a80(local_48,DAT_0273ea80);
LAB_0091428d:
  lVar4 = FUN_00074a90(local_48);
  uVar2 = local_40;
  if (lVar4 != 0) goto code_r0x0091429e;
  goto LAB_009142b0;
code_r0x0091429e:
  if ((*(byte *)(lVar4 + 0x610) & 2) == 0) {
LAB_009142b0:
    uVar6 = 0;
    if (lVar4 == 0) {
LAB_009142bb:
      if (*plVar1 != local_38) {
        uVar5 = thunk_FUN_012aa7f6();
        return uVar5;
      }
      return CONCAT71((int7)((ulong)*plVar1 >> 8),uVar6);
    }
    lVar4 = *(long *)(DAT_0273ea80 + 8);
    if (*(int *)(lVar4 + 0x2854 + (ulong)(local_40 & 0xffff) * 0x2af0) != -1) {
      cVar3 = FUN_0063fed0();
      uVar6 = 1;
      if (cVar3 != '\0') goto LAB_009142bb;
    }
    lVar7 = 0;
    do {
      if (*(int *)(lVar4 + 0x285c + (ulong)(uVar2 & 0xffff) * 0x2af0 + lVar7 * 4) != -1) {
        cVar3 = FUN_0063ff50();
        uVar6 = 1;
        if (cVar3 != '\0') goto LAB_009142bb;
      }
      lVar7 = lVar7 + 1;
    } while ((int)lVar7 < 3);
  }
  goto LAB_0091428d;
}

